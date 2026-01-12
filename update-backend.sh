#!/bin/bash

# 更新后端服务脚本
# 用途: 在代码更新后重新构建并重启后端容器

echo "=========================================="
echo "  DZPoker 后端更新脚本"
echo "=========================================="
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

# 步骤1: 拉取最新代码
echo -e "${YELLOW}[1/5] 拉取最新代码...${NC}"
git pull origin master
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 代码更新成功${NC}"
else
    echo -e "${RED}❌ 代码拉取失败${NC}"
    exit 1
fi

echo ""

# 步骤2: 停止后端容器
echo -e "${YELLOW}[2/5] 停止后端容器...${NC}"
docker-compose stop api
echo -e "${GREEN}✅ 后端容器已停止${NC}"

echo ""

# 步骤3: 重新构建后端镜像
echo -e "${YELLOW}[3/5] 重新构建后端镜像...${NC}"
docker-compose build --no-cache api
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 后端镜像构建成功${NC}"
else
    echo -e "${RED}❌ 镜像构建失败${NC}"
    exit 1
fi

echo ""

# 步骤4: 启动后端容器
echo -e "${YELLOW}[4/5] 启动后端容器...${NC}"
docker-compose up -d api
echo -e "${GREEN}✅ 后端容器已启动${NC}"

echo ""

# 步骤5: 等待服务启动并检查
echo -e "${YELLOW}[5/5] 等待服务启动...${NC}"
sleep 10

echo ""
echo "=========================================="
echo "  检查服务状态"
echo "=========================================="

# 检查容器状态
echo ""
echo -e "${YELLOW}容器状态:${NC}"
docker-compose ps api

echo ""

# 检查后端日志
echo -e "${YELLOW}最近日志 (最后20行):${NC}"
docker-compose logs --tail=20 api

echo ""
echo "=========================================="
echo "  测试新端点"
echo "=========================================="

# 测试统计端点
echo ""
echo -e "${YELLOW}测试 /api/games/stats 端点:${NC}"
if curl -sf http://localhost:8000/api/games/stats > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 统计端点正常${NC}"
    curl -s http://localhost:8000/api/games/stats | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/games/stats
else
    echo -e "${RED}❌ 统计端点异常${NC}"
fi

echo ""

# 测试列表端点
echo -e "${YELLOW}测试 /api/games/list 端点:${NC}"
if curl -sf http://localhost:8000/api/games/list > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 列表端点正常${NC}"
    curl -s http://localhost:8000/api/games/list | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/games/list
else
    echo -e "${RED}❌ 列表端点异常${NC}"
fi

echo ""
echo "=========================================="
echo "  更新完成"
echo "=========================================="
echo ""
echo "如果端点测试失败，请运行以下命令查看详细日志:"
echo "  docker-compose logs -f api"
echo ""
echo "访问以下地址测试前端:"
echo "  http://13.212.252.171:3000"
echo ""
