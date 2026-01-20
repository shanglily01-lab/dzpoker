#!/bin/bash
# 快速查看后端错误

echo "================================"
echo "查看最新错误"
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

echo "最近 50 行日志（包含错误信息）:"
echo "--------------------------------"
$DC logs --tail=50 api | grep -A 10 "ERROR\|Exception\|Traceback\|Failed"

echo ""
echo "================================"
echo "finish API 相关错误:"
echo "--------------------------------"
$DC logs api | grep -A 20 "finish" | tail -30

echo ""
echo "================================"
echo "数据库迁移状态:"
echo "--------------------------------"
docker exec poker-db psql -U postgres -d poker -c "SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name IN ('street', 'action_type');"

echo ""
