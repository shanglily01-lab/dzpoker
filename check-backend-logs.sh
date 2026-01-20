#!/bin/bash
# 查看后端错误日志

echo "================================"
echo "查看后端最新日志"
echo "================================"
echo ""

# 检测 Docker Compose 命令
if command -v docker-compose &> /dev/null; then
    DC="docker-compose"
elif docker compose version &> /dev/null; then
    DC="docker compose"
else
    echo "错误: 未找到 docker-compose 命令"
    exit 1
fi

echo "最近 50 行后端日志:"
echo "--------------------------------"
$DC logs --tail=50 api

echo ""
echo "================================"
echo "查看数据库字段定义"
echo "================================"
docker exec poker-db psql -U postgres -d poker -c "SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name IN ('street', 'action_type');"

echo ""
echo "================================"
echo "检查 models.py 是否已更新"
echo "================================"
docker exec poker-api grep "String(20)" /app/app/models.py | grep -E "(street|action_type)"
