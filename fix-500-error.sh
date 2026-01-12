#!/bin/bash
# 修复 500 错误的完整脚本

echo "======================================"
echo "  修复 AI 500 错误"
echo "======================================"
echo ""

echo "步骤 1: 清理 Python 缓存"
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find backend -type f -name "*.pyc" -delete 2>/dev/null
echo "✓ Python 缓存已清理"
echo ""

echo "步骤 2: 验证关键文件"
echo "检查 decision_maker.py:"
if [ -f "backend/app/ai/decision_maker.py" ]; then
    lines=$(wc -l < backend/app/ai/decision_maker.py)
    echo "✓ 文件存在 ($lines 行)"

    # 检查是否有 ai_decision_maker 导出
    if grep -q "ai_decision_maker = AIDecisionMaker()" backend/app/ai/decision_maker.py; then
        echo "✓ ai_decision_maker 已导出"
    else
        echo "✗ 警告：未找到 ai_decision_maker 导出"
    fi
else
    echo "✗ 错误：文件不存在！"
    exit 1
fi
echo ""

echo "步骤 3: 检查 games.py 导入"
if grep -q "from ..ai.decision_maker import ai_decision_maker" backend/app/routers/games.py; then
    echo "✓ games.py 已导入 ai_decision_maker"
else
    echo "✗ 错误：games.py 未导入 ai_decision_maker"
    exit 1
fi
echo ""

echo "步骤 4: 检查 ai-action 端点"
if grep -q "def ai_single_action" backend/app/routers/games.py; then
    echo "✓ ai-action 端点存在"
else
    echo "✗ 错误：ai-action 端点不存在"
    exit 1
fi
echo ""

echo "步骤 5: 停止所有容器"
docker-compose down
echo "✓ 容器已停止"
echo ""

echo "步骤 6: 删除旧容器和镜像（可选但推荐）"
read -p "是否删除旧镜像以确保完全重建？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose rm -f
    docker rmi dzpoker-backend dzpoker-frontend 2>/dev/null || true
    echo "✓ 旧镜像已删除"
fi
echo ""

echo "步骤 7: 重新构建（这可能需要几分钟）"
docker-compose build --no-cache backend
echo "✓ 后端构建完成"
echo ""

echo "步骤 8: 启动所有服务"
docker-compose up -d
echo "✓ 服务已启动"
echo ""

echo "步骤 9: 等待服务就绪"
echo "等待 10 秒..."
sleep 10
echo ""

echo "步骤 10: 检查容器状态"
docker-compose ps
echo ""

echo "步骤 11: 查看后端日志"
echo "最近 30 行:"
docker logs backend --tail 30
echo ""

echo "======================================"
echo "  修复完成！"
echo "======================================"
echo ""
echo "现在测试 AI 端点:"
echo ""
echo "1. 创建游戏:"
echo "   curl -X POST http://localhost:8000/api/games \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"num_players\": 4, \"small_blind\": 10, \"big_blind\": 20}'"
echo ""
echo "2. 获取 game_id 后测试:"
echo "   curl -X POST http://localhost:8000/api/games/\$GAME_ID/start"
echo "   curl -X POST http://localhost:8000/api/games/\$GAME_ID/ai-action"
echo ""
