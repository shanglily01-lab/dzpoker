#!/bin/bash
# 调试 500 错误脚本

echo "======================================"
echo "  调试 500 错误"
echo "======================================"
echo ""

echo "1. 检查代码版本"
echo "当前 commit:"
git log -1 --oneline
echo ""

echo "2. 检查关键文件是否存在"
echo ""
echo "检查 decision_maker.py:"
if [ -f "backend/app/ai/decision_maker.py" ]; then
    echo "✓ 文件存在"
    wc -l backend/app/ai/decision_maker.py
else
    echo "✗ 文件不存在！"
fi
echo ""

echo "3. 检查 games.py 是否有 ai-action 端点"
if grep -q "ai-action" backend/app/routers/games.py; then
    echo "✓ ai-action 端点存在"
    echo "代码行数:"
    grep -n "def ai_single_action" backend/app/routers/games.py
else
    echo "✗ ai-action 端点不存在！"
fi
echo ""

echo "4. 检查 games.py 是否导入了 ai_decision_maker"
if grep -q "from.*ai_decision_maker import" backend/app/routers/games.py; then
    echo "✓ ai_decision_maker 已导入"
    grep -n "ai_decision_maker" backend/app/routers/games.py | head -3
else
    echo "✗ ai_decision_maker 未导入！"
fi
echo ""

echo "5. 检查容器状态"
docker-compose ps
echo ""

echo "6. 查看后端最近日志（最后 30 行）"
if docker ps | grep -q "poker-api"; then
    docker logs poker-api --tail 30
else
    docker logs api --tail 30
fi
echo ""

echo "======================================"
echo "  诊断完成"
echo "======================================"
echo ""
echo "如果看到错误，请执行:"
echo "  docker-compose down"
echo "  docker-compose up -d --build"
echo ""
