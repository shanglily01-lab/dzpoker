#!/bin/bash

################################################################################
# DZPoker - Amazon Linux 自动化部署脚本
# 适用于: Amazon Linux 2 / Amazon Linux 2023
# 功能: 自动安装依赖、配置环境、部署应用
################################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}[STEP]${NC} $1"
    echo -e "${BLUE}===================================================${NC}"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo bash $0"
        exit 1
    fi
}

# 检测系统版本
detect_system() {
    log_step "检测系统版本"

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        log_info "系统: $OS $VER"
    else
        log_error "无法检测系统版本"
        exit 1
    fi

    # 检查是否为Amazon Linux
    if [[ ! "$OS" =~ "Amazon Linux" ]]; then
        log_warn "此脚本专为Amazon Linux优化，当前系统: $OS"
        read -p "是否继续? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 更新系统
update_system() {
    log_step "更新系统软件包"
    yum update -y --allowerasing
    yum install -y git curl wget vim net-tools
}

# 安装Docker
install_docker() {
    log_step "安装Docker"

    if command -v docker &> /dev/null; then
        log_info "Docker已安装: $(docker --version)"
        return 0
    fi

    log_info "开始安装Docker..."

    # Amazon Linux 2023
    if [[ "$VER" == "2023" ]]; then
        log_info "检测到Amazon Linux 2023，使用DNF安装Docker..."
        # 尝试使用allowerasing解决依赖冲突
        yum install -y docker --allowerasing || {
            log_warn "标准安装失败，尝试跳过冲突包..."
            yum install -y docker --skip-broken
        }
    # Amazon Linux 2
    else
        log_info "检测到Amazon Linux 2，使用amazon-linux-extras安装Docker..."
        amazon-linux-extras install docker -y
    fi

    # 启动Docker服务
    systemctl start docker
    systemctl enable docker

    # 添加当前用户到docker组
    if [ -n "$SUDO_USER" ]; then
        usermod -aG docker $SUDO_USER
        log_info "用户 $SUDO_USER 已添加到docker组"
    fi

    log_info "Docker安装完成: $(docker --version)"
}

# 安装Docker Compose
install_docker_compose() {
    log_step "安装Docker Compose"

    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装: $(docker-compose --version)"
        return 0
    fi

    log_info "开始安装Docker Compose..."

    # 下载最新版本
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')
    log_info "下载Docker Compose $COMPOSE_VERSION"

    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

    chmod +x /usr/local/bin/docker-compose

    # 创建软链接
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

    log_info "Docker Compose安装完成: $(docker-compose --version)"
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙"

    # 检查firewalld是否运行
    if systemctl is-active --quiet firewalld; then
        log_info "配置firewalld规则..."
        firewall-cmd --permanent --add-port=80/tcp
        firewall-cmd --permanent --add-port=443/tcp
        firewall-cmd --permanent --add-port=3000/tcp
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --reload
        log_info "防火墙规则已更新"
    else
        log_warn "firewalld未运行，跳过防火墙配置"
        log_warn "请确保AWS安全组已开放端口: 80, 443, 3000, 8000"
    fi
}

# 创建项目目录
setup_project_directory() {
    log_step "设置项目目录"

    PROJECT_DIR="/opt/dzpoker"

    read -p "请输入项目部署目录 [默认: $PROJECT_DIR]: " input_dir
    if [ -n "$input_dir" ]; then
        PROJECT_DIR=$input_dir
    fi

    log_info "项目目录: $PROJECT_DIR"

    if [ -d "$PROJECT_DIR" ]; then
        log_warn "目录已存在: $PROJECT_DIR"
        read -p "是否删除并重新创建? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf $PROJECT_DIR
            mkdir -p $PROJECT_DIR
        fi
    else
        mkdir -p $PROJECT_DIR
    fi

    cd $PROJECT_DIR
}

# 上传代码 (手动或Git)
upload_code() {
    log_step "获取项目代码"

    echo "请选择代码获取方式:"
    echo "1) 从Git仓库克隆"
    echo "2) 手动上传 (使用scp)"
    echo "3) 跳过 (代码已存在)"
    read -p "请选择 [1-3]: " -n 1 -r
    echo

    case $REPLY in
        1)
            read -p "请输入Git仓库地址: " git_repo
            if [ -n "$git_repo" ]; then
                log_info "克隆仓库: $git_repo"
                git clone $git_repo .
            else
                log_error "Git仓库地址不能为空"
                exit 1
            fi
            ;;
        2)
            log_info "请使用以下命令上传代码到服务器:"
            echo ""
            echo "  scp -r dzpoker/ $(whoami)@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):$PROJECT_DIR"
            echo ""
            read -p "上传完成后按Enter继续..."
            ;;
        3)
            log_info "跳过代码上传"
            ;;
        *)
            log_error "无效选择"
            exit 1
            ;;
    esac
}

# 配置环境变量
configure_environment() {
    log_step "配置环境变量"

    # 检查.env文件
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.example" ]; then
            log_info "复制环境变量模板..."
            cp backend/.env.example backend/.env
        else
            log_warn ".env.example不存在，创建新的.env文件"
            cat > backend/.env <<EOF
# 应用配置
APP_NAME=德州扑克AI系统
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/poker

# Redis配置
REDIS_URL=redis://redis:6379/0

# JWT配置
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF
        fi
    fi

    # 生成随机密钥
    log_info "生成安全密钥..."
    SECRET_KEY=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)

    # 更新配置
    sed -i "s/DEBUG=true/DEBUG=false/" backend/.env
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" backend/.env

    # 更新docker-compose中的数据库密码
    if [ -f "docker-compose.yml" ]; then
        sed -i "s/POSTGRES_PASSWORD: password/POSTGRES_PASSWORD: $DB_PASSWORD/" docker-compose.yml
        sed -i "s/:password@db/:$DB_PASSWORD@db/" docker-compose.yml
    fi

    log_info "环境配置完成"
    log_warn "数据库密码: $DB_PASSWORD (请妥善保管)"
}

# 创建生产环境的docker-compose配置
create_production_compose() {
    log_step "创建生产环境配置"

    if [ ! -f "docker-compose.prod.yml" ]; then
        log_info "生成docker-compose.prod.yml..."
        cat > docker-compose.prod.yml <<'EOF'
version: '3.8'

services:
  # 后端API服务
  api:
    build: ./backend
    container_name: poker-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/poker
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=false
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./backend:/app
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL数据库
  db:
    image: postgres:15-alpine
    container_name: poker-db
    environment:
      POSTGRES_DB: poker
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: always

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: poker-redis
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: poker-frontend
    ports:
      - "80:80"
    depends_on:
      - api
    restart: always

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: poker-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
      - frontend
    restart: always

volumes:
  postgres_data:
  redis_data:
EOF
    fi
}

# 安装Nginx (可选)
install_nginx() {
    log_step "安装Nginx (可选)"

    read -p "是否安装Nginx作为反向代理? (推荐) (y/n): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "跳过Nginx安装"
        return 0
    fi

    yum install -y nginx

    # 配置Nginx
    log_info "配置Nginx..."

    cat > /etc/nginx/conf.d/dzpoker.conf <<'EOF'
upstream api_backend {
    server 127.0.0.1:8000;
}

upstream frontend_backend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    # API代理
    location /api {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket代理
    location /ws {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API文档
    location /docs {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
    }

    # 前端代理
    location / {
        proxy_pass http://frontend_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

    # 启动Nginx
    systemctl start nginx
    systemctl enable nginx

    log_info "Nginx配置完成"
}

# 部署应用
deploy_application() {
    log_step "部署应用"

    cd $PROJECT_DIR

    # 停止已运行的容器
    if [ -f "docker-compose.yml" ]; then
        log_info "停止现有容器..."
        docker-compose down 2>/dev/null || true
    fi

    # 构建并启动
    log_info "构建Docker镜像..."
    docker-compose build --no-cache

    log_info "启动服务..."
    docker-compose up -d

    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10

    # 检查服务状态
    docker-compose ps
}

# 健康检查
health_check() {
    log_step "服务健康检查"

    # 检查API
    log_info "检查后端API..."
    if curl -f http://localhost:8000/docs &> /dev/null; then
        log_info "✓ 后端API运行正常"
    else
        log_warn "✗ 后端API可能未正常启动"
    fi

    # 检查前端
    log_info "检查前端服务..."
    if curl -f http://localhost:3000 &> /dev/null; then
        log_info "✓ 前端服务运行正常"
    else
        log_warn "✗ 前端服务可能未正常启动"
    fi

    # 检查数据库
    log_info "检查数据库..."
    if docker-compose exec -T db pg_isready -U postgres &> /dev/null; then
        log_info "✓ 数据库运行正常"
    else
        log_warn "✗ 数据库可能未正常启动"
    fi

    # 检查Redis
    log_info "检查Redis..."
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        log_info "✓ Redis运行正常"
    else
        log_warn "✗ Redis可能未正常启动"
    fi
}

# 创建系统服务
create_systemd_service() {
    log_step "创建Systemd服务"

    read -p "是否创建系统服务以便开机自启? (y/n): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 0
    fi

    cat > /etc/systemd/system/dzpoker.service <<EOF
[Unit]
Description=DZPoker Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable dzpoker.service

    log_info "系统服务已创建并启用"
}

# 显示部署信息
show_deployment_info() {
    log_step "部署完成"

    # 获取服务器IP
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_SERVER_IP")
    PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null || hostname -I | awk '{print $1}')

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    DZPoker 部署成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "访问地址:"
    echo "  前端页面: http://$PUBLIC_IP:3000"
    echo "  后端API:  http://$PUBLIC_IP:8000"
    echo "  API文档:  http://$PUBLIC_IP:8000/docs"
    echo ""
    echo "内网地址:"
    echo "  内网IP:   $PRIVATE_IP"
    echo ""
    echo "常用命令:"
    echo "  查看状态: cd $PROJECT_DIR && docker-compose ps"
    echo "  查看日志: cd $PROJECT_DIR && docker-compose logs -f"
    echo "  重启服务: cd $PROJECT_DIR && docker-compose restart"
    echo "  停止服务: cd $PROJECT_DIR && docker-compose down"
    echo "  启动服务: cd $PROJECT_DIR && docker-compose up -d"
    echo ""
    echo "数据备份:"
    echo "  备份数据库: docker-compose exec db pg_dump -U postgres poker > backup_\$(date +%Y%m%d).sql"
    echo "  恢复数据库: cat backup.sql | docker-compose exec -T db psql -U postgres poker"
    echo ""
    log_warn "请确保AWS安全组已开放以下端口: 80, 443, 3000, 8000"
    log_warn "建议配置SSL证书以启用HTTPS"
    echo ""
}

# 主函数
main() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║      DZPoker - Amazon Linux 自动化部署脚本              ║
║                                                          ║
║      德州扑克发牌算法AI测试系统                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    # 执行部署步骤
    check_root
    detect_system
    update_system
    install_docker
    install_docker_compose
    configure_firewall
    setup_project_directory
    upload_code
    configure_environment
    install_nginx
    deploy_application
    health_check
    create_systemd_service
    show_deployment_info

    log_info "部署流程已完成！"
}

# 运行主函数
main "$@"
