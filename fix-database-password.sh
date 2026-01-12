#!/bin/bash

# 修复数据库密码问题
# 用途: 解决 "password authentication failed for user postgres" 错误

echo "=========================================="
echo "  数据库密码问题修复脚本"
echo "=========================================="
echo ""
echo "⚠️  警告: 此脚本会重置数据库，所有游戏数据将被清空！"
echo "   如果是生产环境，请先备份数据库。"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 询问确认
read -p "是否继续？这会清空数据库中的所有数据！(yes/N) " -r
echo
if [[ ! $REPLY == "yes" ]]; then
    echo -e "${RED}❌ 操作已取消${NC}"
    echo "提示: 输入 'yes' 以确认操作"
    exit 1
fi

echo ""

# 步骤1: 停止所有服务
echo -e "${YELLOW}[1/6] 停止所有服务...${NC}"
docker-compose down
echo -e "${GREEN}✅ 服务已停止${NC}"
echo ""

# 步骤2: 删除数据库卷
echo -e "${YELLOW}[2/6] 删除数据库卷...${NC}"
docker volume rm dzpoker_postgres_data 2>/dev/null || true
docker volume rm dzpoker_redis_data 2>/dev/null || true
echo -e "${GREEN}✅ 数据库卷已删除${NC}"
echo ""

# 步骤3: 检查环境变量
echo -e "${YELLOW}[3/6] 检查环境变量...${NC}"
echo "Docker Compose 配置:"
grep -A 3 "POSTGRES_PASSWORD" docker-compose.yml
echo ""
grep "DATABASE_URL" docker-compose.yml
echo -e "${GREEN}✅ 环境变量检查完成${NC}"
echo ""

# 步骤4: 重新启动数据库
echo -e "${YELLOW}[4/6] 重新启动数据库...${NC}"
docker-compose up -d db
echo "等待数据库初始化（30秒）..."
sleep 30
echo -e "${GREEN}✅ 数据库已启动${NC}"
echo ""

# 步骤5: 验证数据库连接
echo -e "${YELLOW}[5/6] 验证数据库连接...${NC}"
if docker-compose exec -T db pg_isready -U postgres 2>/dev/null | grep -q "accepting connections"; then
    echo -e "${GREEN}✅ 数据库连接正常${NC}"

    # 测试登录
    echo ""
    echo "测试数据库登录:"
    docker-compose exec -T db psql -U postgres -d poker -c "SELECT version();" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 数据库登录成功${NC}"
    else
        echo -e "${RED}❌ 数据库登录失败${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ 数据库连接异常${NC}"
    exit 1
fi
echo ""

# 步骤6: 启动所有服务
echo -e "${YELLOW}[6/6] 启动所有服务...${NC}"
docker-compose up -d
echo "等待服务启动（15秒）..."
sleep 15
echo -e "${GREEN}✅ 所有服务已启动${NC}"
echo ""

# 检查服务状态
echo "=========================================="
echo "  服务状态检查"
echo "=========================================="
docker-compose ps
echo ""

# 检查后端日志
echo "=========================================="
echo "  后端日志 (最后20行)"
echo "=========================================="
docker-compose logs --tail=20 api
echo ""

# 测试端点
echo "=========================================="
echo "  测试API端点"
echo "=========================================="
echo ""
sleep 5

echo -e "${YELLOW}测试健康检查:${NC}"
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 健康检查通过${NC}"
else
    echo -e "${RED}❌ 健康检查失败${NC}"
fi

echo ""
echo -e "${YELLOW}测试统计端点:${NC}"
if curl -sf http://localhost:8000/api/games/stats > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 统计端点正常${NC}"
    curl -s http://localhost:8000/api/games/stats | python3 -m json.tool 2>/dev/null
else
    echo -e "${RED}❌ 统计端点异常${NC}"
fi

echo ""
echo "=========================================="
echo "  修复完成"
echo "=========================================="
echo ""
echo "如果仍有问题，请检查:"
echo "  1. docker-compose logs -f api"
echo "  2. docker-compose exec db psql -U postgres -d poker"
echo "  3. docker-compose exec api env | grep DATABASE"
echo ""
