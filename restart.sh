#!/bin/bash
# 快速部署脚本 - 前端需要重新构建，后端只需重启

echo "=== 快速部署 ==="

# 拉取最新代码
echo "1. 拉取最新代码..."
git fetch origin
git reset --hard origin/master

# 清理 Python 缓存（防止旧代码残留）
echo "2. 清理缓存..."
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find backend -type f -name "*.pyc" -delete 2>/dev/null

# 停止服务
echo "3. 停止服务..."
docker-compose down

# 只重新构建前端（前端是编译型的，必须重新构建）
echo "4. 重新构建前端..."
docker-compose build --no-cache frontend

# 启动所有服务
echo "5. 启动服务..."
docker-compose up -d

# 检查状态
echo "6. 检查状态..."
sleep 5
docker-compose ps

echo ""
echo "=== 部署完成 ==="
echo ""
echo "前端已重新构建，后端使用现有镜像"
echo ""
echo "如果后端也需要重新构建，请运行："
echo "  bash deploy.sh"
