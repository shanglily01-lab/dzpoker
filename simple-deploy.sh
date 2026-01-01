#!/bin/bash

################################################################################
# DZPoker 简易部署脚本 (兼容旧版Docker)
# 使用传统方式构建，不依赖新版Buildx
################################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DZPoker 简易部署${NC}"
echo -e "${GREEN}  (兼容旧版Docker)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装"
    exit 1
fi

log_info "Docker版本: $(docker --version)"
echo ""

# 生成环境配置
if [ ! -f "backend/.env" ]; then
    log_info "生成环境配置..."

    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "change-me-in-production-$(date +%s)")
    DB_PASSWORD=$(openssl rand -base64 16 2>/dev/null | tr -d "=+/" | cut -c1-16 || echo "poker_pass_$(date +%s)")

    cat > backend/.env <<EOF
# 应用配置
APP_NAME=德州扑克AI系统
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/poker

# Redis配置
REDIS_URL=redis://redis:6379/0

# JWT配置
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF

    export DB_PASSWORD
    export SECRET_KEY

    log_info "✓ 环境配置已生成"
    log_warn "数据库密码: ${DB_PASSWORD} (请妥善保管)"
else
    log_info "✓ 环境配置已存在"
    source backend/.env 2>/dev/null || true
fi

echo ""
log_info "停止现有容器..."
docker-compose down 2>/dev/null || docker stop poker-api poker-frontend poker-db poker-redis 2>/dev/null || true

echo ""
log_info "==================== 方式1: 使用 docker-compose build (推荐) ===================="
log_info "尝试使用 docker-compose 构建..."

if docker-compose build 2>&1 | tee /tmp/compose-build.log; then
    log_info "✓ docker-compose build 成功"

    log_info "启动服务..."
    docker-compose up -d

    BUILD_METHOD="docker-compose"
else
    log_warn "docker-compose build 失败，切换到方式2"

    echo ""
    log_info "==================== 方式2: 分别构建镜像 (兼容方式) ===================="

    # 构建后端
    log_info "构建后端镜像..."
    cd backend
    docker build -t dzpoker-api . || {
        log_error "后端构建失败"
        exit 1
    }
    cd ..

    # 构建前端
    log_info "构建前端镜像..."
    cd frontend
    docker build -t dzpoker-frontend . || {
        log_error "前端构建失败"
        exit 1
    }
    cd ..

    log_info "✓ 镜像构建完成"

    # 创建网络
    log_info "创建Docker网络..."
    docker network create dzpoker-network 2>/dev/null || log_info "网络已存在"

    # 启动数据库
    log_info "启动PostgreSQL..."
    docker run -d \
        --name poker-db \
        --network dzpoker-network \
        -e POSTGRES_DB=poker \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=${DB_PASSWORD:-password} \
        -p 5432:5432 \
        -v poker_db_data:/var/lib/postgresql/data \
        --restart unless-stopped \
        postgres:15-alpine

    # 启动Redis
    log_info "启动Redis..."
    docker run -d \
        --name poker-redis \
        --network dzpoker-network \
        -p 6379:6379 \
        -v poker_redis_data:/data \
        --restart unless-stopped \
        redis:7-alpine redis-server --appendonly yes

    # 等待数据库就绪
    log_info "等待数据库就绪..."
    sleep 10

    # 启动后端
    log_info "启动后端API..."
    docker run -d \
        --name poker-api \
        --network dzpoker-network \
        -e DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD:-password}@poker-db:5432/poker \
        -e REDIS_URL=redis://poker-redis:6379/0 \
        -e SECRET_KEY=${SECRET_KEY} \
        -e DEBUG=false \
        -p 8000:8000 \
        -v $(pwd)/backend:/app \
        --restart unless-stopped \
        dzpoker-api

    # 启动前端
    log_info "启动前端..."
    docker run -d \
        --name poker-frontend \
        --network dzpoker-network \
        -p 3000:80 \
        --restart unless-stopped \
        dzpoker-frontend

    BUILD_METHOD="manual"
fi

# 等待服务启动
echo ""
log_info "等待服务启动..."
sleep 15

# 健康检查
echo ""
log_info "========================================${NC}"
log_info "  健康检查${NC}"
log_info "========================================${NC}"

check_passed=true

# 检查容器
log_info "检查容器状态..."
if [ "$BUILD_METHOD" = "docker-compose" ]; then
    docker-compose ps
else
    docker ps --filter "name=poker-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

echo ""

# 检查API
log_info "检查后端API..."
if curl -sf http://localhost:8000/docs > /dev/null 2>&1; then
    log_info "✓ API正常"
else
    log_warn "✗ API异常"
    check_passed=false
fi

# 检查前端
log_info "检查前端..."
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    log_info "✓ 前端正常"
else
    log_warn "✗ 前端异常"
    check_passed=false
fi

# 检查数据库
log_info "检查数据库..."
if docker exec poker-db pg_isready -U postgres 2>/dev/null | grep -q "accepting"; then
    log_info "✓ 数据库正常"
else
    log_warn "✗ 数据库异常"
    check_passed=false
fi

# 检查Redis
log_info "检查Redis..."
if docker exec poker-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    log_info "✓ Redis正常"
else
    log_warn "✗ Redis异常"
    check_passed=false
fi

# 获取服务器IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_SERVER_IP")

echo ""
log_info "========================================${NC}"
log_info "  部署完成${NC}"
log_info "========================================${NC}"
echo ""

if $check_passed; then
    echo -e "${GREEN}✓ 所有服务运行正常！${NC}"
else
    echo -e "${YELLOW}⚠ 部分服务异常，请查看上述检查结果${NC}"
fi

echo ""
echo "访问地址:"
echo "  前端: http://${PUBLIC_IP}:3000"
echo "  API:  http://${PUBLIC_IP}:8000/docs"
echo ""
echo "管理命令:"
if [ "$BUILD_METHOD" = "docker-compose" ]; then
    echo "  查看日志: docker-compose logs -f"
    echo "  重启服务: docker-compose restart"
    echo "  停止服务: docker-compose down"
else
    echo "  查看日志: docker logs -f poker-api"
    echo "  重启服务: docker restart poker-api poker-frontend poker-db poker-redis"
    echo "  停止服务: docker stop poker-api poker-frontend poker-db poker-redis"
fi
echo ""

if ! $check_passed; then
    echo "故障排查:"
    echo "  docker logs poker-api"
    echo "  docker logs poker-frontend"
    echo "  docker logs poker-db"
fi
