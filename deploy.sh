#!/bin/bash
# 快速部署脚本 - 智能判断是否需要重新构建

echo "=== 开始部署 ==="

# 获取当前提交
OLD_COMMIT=$(git rev-parse HEAD)

# 拉取最新代码
echo "1. 拉取最新代码..."
git fetch origin
git reset --hard origin/master

# 获取新提交
NEW_COMMIT=$(git rev-parse HEAD)

# 检查是否有代码变化
if [ "$OLD_COMMIT" = "$NEW_COMMIT" ]; then
    echo "✓ 代码无变化，跳过构建"
    docker-compose restart api frontend
    echo "=== 部署完成（仅重启） ==="
    exit 0
fi

echo "✓ 检测到代码更新: $OLD_COMMIT -> $NEW_COMMIT"

# 检查哪些文件发生了变化
echo "2. 检查变化的文件..."
CHANGED_FILES=$(git diff --name-only $OLD_COMMIT $NEW_COMMIT)
echo "$CHANGED_FILES"

# 判断是否需要重新构建后端
if echo "$CHANGED_FILES" | grep -q "^backend/"; then
    echo "3. 后端代码有变化，重新构建 API..."
    REBUILD_API=true
else
    echo "3. 后端代码无变化，跳过构建"
    REBUILD_API=false
fi

# 判断是否需要重新构建前端
if echo "$CHANGED_FILES" | grep -q "^frontend/"; then
    echo "4. 前端代码有变化，重新构建 Frontend..."
    REBUILD_FRONTEND=true
else
    echo "4. 前端代码无变化，跳过构建"
    REBUILD_FRONTEND=false
fi

# 清理 Python 缓存
if [ "$REBUILD_API" = true ]; then
    echo "5. 清理 Python 缓存..."
    find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
    find backend -type f -name "*.pyc" -delete 2>/dev/null
fi

# 停止容器
echo "6. 停止容器..."
docker-compose down

# 重新构建需要更新的服务
BUILD_SERVICES=""
if [ "$REBUILD_API" = true ]; then
    BUILD_SERVICES="$BUILD_SERVICES api"
fi
if [ "$REBUILD_FRONTEND" = true ]; then
    BUILD_SERVICES="$BUILD_SERVICES frontend"
fi

if [ -n "$BUILD_SERVICES" ]; then
    echo "7. 重新构建服务:$BUILD_SERVICES"
    docker-compose build --no-cache $BUILD_SERVICES
else
    echo "7. 无需重新构建"
fi

# 启动所有服务
echo "8. 启动服务..."
docker-compose up -d

# 等待服务启动
echo "9. 等待服务启动..."
sleep 5

# 检查服务状态
echo "10. 检查服务状态..."
docker-compose ps

echo ""
echo "=== 部署完成 ==="
echo ""
echo "检查日志："
echo "  docker logs api --tail 50"
echo "  docker logs frontend --tail 50"
echo ""
echo "访问："
echo "  前端: http://13.212.252.171:3000"
echo "  API文档: http://13.212.252.171:8000/docs"
