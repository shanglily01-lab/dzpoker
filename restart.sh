#!/bin/bash
# 快速重启脚本 - 不重新构建，仅重启服务

echo "=== 快速重启 ==="

# 拉取最新代码
echo "1. 拉取最新代码..."
git fetch origin
git reset --hard origin/master

# 清理 Python 缓存（防止旧代码残留）
echo "2. 清理缓存..."
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find backend -type f -name "*.pyc" -delete 2>/dev/null

# 重启服务
echo "3. 重启服务..."
docker-compose restart

# 检查状态
echo "4. 检查状态..."
sleep 3
docker-compose ps

echo ""
echo "=== 重启完成 ==="
echo ""
echo "如果服务异常，请运行完整部署："
echo "  bash deploy.sh"
