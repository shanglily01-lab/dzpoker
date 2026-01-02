#!/bin/bash

################################################################################
# DZPoker 快速重启脚本
# 用于快速重启所有服务或单个服务
################################################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 项目目录
PROJECT_DIR="${1:-/opt/dzpoker}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║           DZPoker 服务重启工具                          ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查项目目录
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR" || exit 1
    echo -e "${GREEN}[✓]${NC} 项目目录: $PROJECT_DIR"
else
    echo -e "${RED}[✗]${NC} 项目目录不存在: $PROJECT_DIR"
    echo ""
    echo "用法: $0 [项目目录路径]"
    echo "示例: $0 /opt/dzpoker"
    exit 1
fi

echo ""
echo "请选择重启方式:"
echo "1) 重启所有服务 (推荐)"
echo "2) 仅重启后端 API"
echo "3) 仅重启前端"
echo "4) 仅重启数据库"
echo "5) 仅重启Redis"
echo "6) 完全重启 (停止->删除->重新创建)"
echo "7) 快速重启 (不重新构建镜像)"
read -p "请选择 [1-7]: " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  重启所有服务${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo ""

        echo -e "${GREEN}[INFO]${NC} 停止所有容器..."
        docker-compose stop

        echo ""
        echo -e "${GREEN}[INFO]${NC} 启动所有容器..."
        docker-compose start

        echo ""
        echo -e "${GREEN}[INFO]${NC} 等待服务启动..."
        sleep 5

        echo ""
        echo -e "${GREEN}[INFO]${NC} 检查容器状态..."
        docker-compose ps
        ;;

    2)
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  重启后端 API${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo ""

        docker-compose restart api

        echo ""
        echo -e "${GREEN}[✓]${NC} 后端 API 已重启"
        echo ""
        echo "查看日志: docker-compose logs -f api"
        ;;

    3)
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  重启前端服务${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo ""

        docker-compose restart frontend

        echo ""
        echo -e "${GREEN}[✓]${NC} 前端服务已重启"
        echo ""
        echo "查看日志: docker-compose logs -f frontend"
        ;;

    4)
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  重启数据库${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo ""

        echo -e "${RED}[警告]${NC} 重启数据库会暂时中断所有游戏！"
        read -p "确认继续? (y/n): " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose restart db

            echo ""
            echo -e "${GREEN}[INFO]${NC} 等待数据库启动..."
            sleep 10

            echo -e "${GREEN}[INFO]${NC} 检查数据库状态..."
            docker-compose exec db pg_isready -U postgres

            echo ""
            echo -e "${GREEN}[✓]${NC} 数据库已重启"
        else
            echo "已取消"
        fi
        ;;

    5)
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  重启Redis缓存${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo ""

        docker-compose restart redis

        echo ""
        echo -e "${GREEN}[INFO]${NC} 等待Redis启动..."
        sleep 3

        echo -e "${GREEN}[INFO]${NC} 检查Redis状态..."
        docker-compose exec redis redis-cli ping

        echo ""
        echo -e "${GREEN}[✓]${NC} Redis已重启"
        ;;

    6)
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  完全重启 (停止->删除->重建)${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo ""

        echo -e "${RED}[警告]${NC} 这将:"
        echo "  - 停止所有容器"
        echo "  - 删除所有容器"
        echo "  - 重新创建所有容器"
        echo "  - 但不会删除数据卷(数据会保留)"
        echo ""
        read -p "确认继续? (y/n): " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo -e "${GREEN}[INFO]${NC} 停止并删除容器..."
            docker-compose down

            echo ""
            echo -e "${GREEN}[INFO]${NC} 重新创建并启动容器..."
            docker-compose up -d

            echo ""
            echo -e "${GREEN}[INFO]${NC} 等待服务启动..."
            sleep 10

            echo ""
            echo -e "${GREEN}[INFO]${NC} 检查容器状态..."
            docker-compose ps

            echo ""
            echo -e "${GREEN}[✓]${NC} 完全重启完成"
        else
            echo "已取消"
        fi
        ;;

    7)
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  快速重启 (不重新构建)${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo ""

        echo -e "${GREEN}[INFO]${NC} 停止所有容器..."
        docker-compose down

        echo ""
        echo -e "${GREEN}[INFO]${NC} 启动所有容器..."
        docker-compose up -d

        echo ""
        echo -e "${GREEN}[INFO]${NC} 等待服务启动..."
        sleep 5

        echo ""
        echo -e "${GREEN}[INFO]${NC} 检查容器状态..."
        docker-compose ps

        echo ""
        echo -e "${GREEN}[✓]${NC} 快速重启完成"
        ;;

    *)
        echo -e "${RED}[ERROR]${NC} 无效选择"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  服务健康检查${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# 检查后端API
echo -n "检查后端API... "
if curl -sf http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}[✓]${NC} 正常"
else
    echo -e "${RED}[✗]${NC} 异常"
    echo "    查看日志: docker-compose logs api"
fi

# 检查前端
echo -n "检查前端服务... "
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}[✓]${NC} 正常"
else
    echo -e "${RED}[✗]${NC} 异常"
    echo "    查看日志: docker-compose logs frontend"
fi

# 检查数据库
echo -n "检查数据库... "
if docker-compose exec -T db pg_isready -U postgres 2>/dev/null | grep -q "accepting connections"; then
    echo -e "${GREEN}[✓]${NC} 正常"
else
    echo -e "${RED}[✗]${NC} 异常"
    echo "    查看日志: docker-compose logs db"
fi

# 检查Redis
echo -n "检查Redis... "
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}[✓]${NC} 正常"
else
    echo -e "${RED}[✗]${NC} 异常"
    echo "    查看日志: docker-compose logs redis"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║           重启完成！                                    ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 获取访问地址
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_SERVER_IP")
PRIVATE_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

echo "访问地址:"
echo "  前端: http://$PRIVATE_IP:3000"
echo "  API:  http://$PRIVATE_IP:8000/docs"
echo ""
echo "常用命令:"
echo "  查看所有日志: docker-compose logs -f"
echo "  查看单个服务: docker-compose logs -f [api|frontend|db|redis]"
echo "  查看容器状态: docker-compose ps"
echo "  停止所有服务: docker-compose stop"
echo "  启动所有服务: docker-compose start"
echo ""
