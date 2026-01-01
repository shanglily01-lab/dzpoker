#!/bin/bash

################################################################################
# DZPoker 健康检查脚本
# 用于快速检查所有服务是否正常运行
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
echo -e "${BLUE}║           DZPoker 系统健康检查工具                      ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 切换到项目目录
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
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  1. Docker 环境检查${NC}"
echo -e "${YELLOW}========================================${NC}"

# 检查Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}[✓]${NC} Docker已安装: $(docker --version | awk '{print $3}')"
else
    echo -e "${RED}[✗]${NC} Docker未安装"
    exit 1
fi

# 检查Docker服务
if systemctl is-active --quiet docker; then
    echo -e "${GREEN}[✓]${NC} Docker服务运行正常"
else
    echo -e "${RED}[✗]${NC} Docker服务未运行"
    echo "    请执行: sudo systemctl start docker"
    exit 1
fi

# 检查Docker Compose
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}[✓]${NC} Docker Compose已安装: $(docker-compose --version | awk '{print $4}')"
else
    echo -e "${RED}[✗]${NC} Docker Compose未安装"
    exit 1
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  2. 容器状态检查${NC}"
echo -e "${YELLOW}========================================${NC}"

# 检查docker-compose.yml是否存在
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}[✗]${NC} docker-compose.yml 文件不存在"
    exit 1
fi

# 获取容器状态
CONTAINERS=$(docker-compose ps --format json 2>/dev/null || docker-compose ps -q 2>/dev/null)

if [ -z "$CONTAINERS" ]; then
    echo -e "${RED}[✗]${NC} 没有运行中的容器"
    echo "    请执行: docker-compose up -d"
    exit 1
fi

echo ""
echo "容器状态:"
docker-compose ps
echo ""

# 检查各个服务
services=("api" "frontend" "db" "redis")
all_healthy=true

for service in "${services[@]}"; do
    container_status=$(docker-compose ps $service 2>/dev/null | grep -v "NAME" | awk '{print $3}')

    if echo "$container_status" | grep -q "Up"; then
        echo -e "${GREEN}[✓]${NC} $service: 运行正常"
    else
        echo -e "${RED}[✗]${NC} $service: 状态异常 ($container_status)"
        all_healthy=false
    fi
done

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  3. 服务健康检查${NC}"
echo -e "${YELLOW}========================================${NC}"

# 检查后端API
echo -n "检查后端API... "
if curl -sf http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}[✓]${NC} 正常"
else
    echo -e "${RED}[✗]${NC} 异常"
    echo "    URL: http://localhost:8000/docs"
    all_healthy=false
fi

# 检查前端服务
echo -n "检查前端服务... "
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}[✓]${NC} 正常"
else
    echo -e "${RED}[✗]${NC} 异常"
    echo "    URL: http://localhost:3000"
    all_healthy=false
fi

# 检查数据库
echo -n "检查PostgreSQL... "
if docker-compose exec -T db pg_isready -U postgres 2>/dev/null | grep -q "accepting connections"; then
    echo -e "${GREEN}[✓]${NC} 正常"
else
    echo -e "${RED}[✗]${NC} 异常"
    all_healthy=false
fi

# 检查Redis
echo -n "检查Redis缓存... "
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}[✓]${NC} 正常"
else
    echo -e "${RED}[✗]${NC} 异常"
    all_healthy=false
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  4. 端口监听检查${NC}"
echo -e "${YELLOW}========================================${NC}"

# 检查端口
ports=(3000 8000 5432 6379)
port_names=("前端" "API" "数据库" "Redis")

for i in "${!ports[@]}"; do
    port=${ports[$i]}
    name=${port_names[$i]}

    echo -n "检查端口 $port ($name)... "
    if netstat -tlnp 2>/dev/null | grep -q ":$port " || ss -tlnp 2>/dev/null | grep -q ":$port "; then
        echo -e "${GREEN}[✓]${NC} 正在监听"
    else
        echo -e "${RED}[✗]${NC} 未监听"
        all_healthy=false
    fi
done

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  5. 资源使用情况${NC}"
echo -e "${YELLOW}========================================${NC}"

# 显示容器资源使用
echo ""
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  6. 访问地址${NC}"
echo -e "${YELLOW}========================================${NC}"

# 获取服务器IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_SERVER_IP")
PRIVATE_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

echo ""
echo "外网访问地址:"
echo "  前端页面: http://$PUBLIC_IP:3000"
echo "  API文档:  http://$PUBLIC_IP:8000/docs"
echo "  API接口:  http://$PUBLIC_IP:8000"
echo ""
echo "内网访问地址:"
echo "  前端页面: http://$PRIVATE_IP:3000"
echo "  API文档:  http://$PRIVATE_IP:8000/docs"
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  检查结果总结${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

if $all_healthy; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}║       ✓ 所有服务运行正常！系统健康！                   ║${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "您现在可以访问系统了！"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}║       ✗ 部分服务异常，请检查上述错误！                 ║${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "故障排查命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  重启服务: docker-compose restart"
    echo "  完全重启: docker-compose down && docker-compose up -d"
    echo ""
    exit 1
fi
