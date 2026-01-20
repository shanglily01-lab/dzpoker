#!/bin/bash
# 诊断脚本 - 检查服务器状态

echo "================================"
echo "德州扑克系统诊断"
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

echo "1️⃣  检查 Git 状态"
echo "--------------------------------"
git log --oneline -3
echo ""
git status --short
echo ""

echo "2️⃣  检查本地文件（backend/app/models.py）"
echo "--------------------------------"
grep -A 2 "class Action" backend/app/models.py | grep -E "(street|action_type)" | head -2
echo ""

echo "3️⃣  检查容器内文件（/app/app/models.py）"
echo "--------------------------------"
docker exec poker-api grep -A 2 "class Action" /app/app/models.py 2>/dev/null | grep -E "(street|action_type)" | head -2 || echo "容器未运行或文件不存在"
echo ""

echo "4️⃣  检查数据库字段定义"
echo "--------------------------------"
docker exec poker-db psql -U postgres -d poker -c "SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name IN ('street', 'action_type');" 2>/dev/null || echo "数据库未运行"
echo ""

echo "5️⃣  检查后端日志（最近 20 行）"
echo "--------------------------------"
$DC logs --tail=20 api
echo ""

echo "6️⃣  检查容器状态"
echo "--------------------------------"
$DC ps
echo ""

echo "================================"
echo "诊断建议"
echo "================================"
echo ""

# 检查本地和容器内代码是否一致
LOCAL_CODE=$(grep "String(20)" backend/app/models.py | wc -l)
CONTAINER_CODE=$(docker exec poker-api grep "String(20)" /app/app/models.py 2>/dev/null | wc -l || echo "0")

if [ "$LOCAL_CODE" -ge "2" ] && [ "$CONTAINER_CODE" -ge "2" ]; then
    echo "✓ 本地和容器内代码都已更新"
    echo ""
    echo "下一步: 检查数据库是否已迁移"
    echo "运行: ./force-restart.sh"
elif [ "$LOCAL_CODE" -ge "2" ] && [ "$CONTAINER_CODE" -lt "2" ]; then
    echo "⚠ 本地代码已更新，但容器内代码未更新"
    echo ""
    echo "原因可能是："
    echo "  1. Volume 映射失败"
    echo "  2. 容器需要重启"
    echo ""
    echo "解决方案:"
    echo "  运行: ./force-restart.sh"
elif [ "$LOCAL_CODE" -lt "2" ]; then
    echo "✗ 本地代码未更新"
    echo ""
    echo "解决方案:"
    echo "  运行: git pull"
else
    echo "⚠ 无法确定状态"
    echo ""
    echo "解决方案:"
    echo "  1. 运行: git pull"
    echo "  2. 运行: ./force-restart.sh"
fi
echo ""
