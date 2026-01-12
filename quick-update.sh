#!/bin/bash
# 快速更新脚本 - 只重启服务，不重新构建

echo "======================================"
echo "  快速更新和重启"
echo "======================================"

# 检查是否有代码变更
echo "1. 拉取最新代码..."
git pull origin master

if [ $? -ne 0 ]; then
    echo "❌ Git pull 失败"
    exit 1
fi

echo ""
echo "2. 重启服务（不重新构建）..."
docker-compose restart

echo ""
echo "3. 检查服务状态..."
docker-compose ps

echo ""
echo "4. 查看后端日志（最近20行）..."
docker logs backend --tail 20

echo ""
echo "======================================"
echo "✅ 更新完成！"
echo "======================================"
echo ""
echo "提示："
echo "- 如果只是 Python/JS 代码改动，不需要 rebuild"
echo "- 如果改了 Dockerfile 或依赖，才需要 rebuild"
echo ""
echo "需要完整重新构建时，运行："
echo "  docker-compose down && docker-compose up -d --build"
