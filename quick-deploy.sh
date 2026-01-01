#!/bin/bash

################################################################################
# DZPoker - 快速部署脚本 (Amazon Linux)
# 适用场景: 代码已上传到服务器，需要快速启动
################################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DZPoker 快速部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    echo "请先运行完整部署脚本: sudo bash deploy-amazon-linux.sh"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装${NC}"
    echo "请先运行完整部署脚本: sudo bash deploy-amazon-linux.sh"
    exit 1
fi

# 生成环境变量
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}生成环境配置...${NC}"

    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)

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

    echo -e "${GREEN}✓ 环境配置已生成${NC}"
    echo -e "${YELLOW}数据库密码: ${DB_PASSWORD}${NC}"

    # 导出环境变量供docker-compose使用
    export DB_PASSWORD
    export SECRET_KEY
else
    echo -e "${GREEN}✓ 环境配置已存在${NC}"
    # 从.env文件加载变量
    source backend/.env
    export DB_PASSWORD SECRET_KEY
fi

# 停止现有服务
echo -e "${YELLOW}停止现有服务...${NC}"
docker-compose down 2>/dev/null || true

# 拉取最新镜像
echo -e "${YELLOW}拉取Docker镜像...${NC}"
docker-compose pull || true

# 构建镜像
echo -e "${YELLOW}构建应用镜像...${NC}"
docker-compose build --no-cache

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 15

# 显示状态
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}服务状态:${NC}"
echo -e "${GREEN}========================================${NC}"
docker-compose ps

# 健康检查
echo ""
echo -e "${YELLOW}执行健康检查...${NC}"

# 检查API
if curl -f http://localhost:8000/docs &> /dev/null; then
    echo -e "${GREEN}✓ 后端API: 运行正常${NC}"
else
    echo -e "${RED}✗ 后端API: 启动失败${NC}"
    echo "查看日志: docker-compose logs api"
fi

# 检查前端
if curl -f http://localhost:3000 &> /dev/null; then
    echo -e "${GREEN}✓ 前端服务: 运行正常${NC}"
else
    echo -e "${RED}✗ 前端服务: 启动失败${NC}"
    echo "查看日志: docker-compose logs frontend"
fi

# 检查数据库
if docker-compose exec -T db pg_isready -U postgres &> /dev/null; then
    echo -e "${GREEN}✓ 数据库: 运行正常${NC}"
else
    echo -e "${RED}✗ 数据库: 启动失败${NC}"
    echo "查看日志: docker-compose logs db"
fi

# 检查Redis
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis: 运行正常${NC}"
else
    echo -e "${RED}✗ Redis: 启动失败${NC}"
    echo "查看日志: docker-compose logs redis"
fi

# 获取服务器IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_SERVER_IP")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "访问地址:"
echo "  前端: http://${PUBLIC_IP}:3000"
echo "  API:  http://${PUBLIC_IP}:8000"
echo "  文档: http://${PUBLIC_IP}:8000/docs"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  重启服务: docker-compose restart"
echo "  停止服务: docker-compose down"
echo ""
