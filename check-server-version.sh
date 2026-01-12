#!/bin/bash
# 检查服务器代码版本

echo "======================================"
echo "  检查 EC2 服务器代码版本"
echo "======================================"

echo ""
echo "本地最新 commit:"
git log -1 --oneline

echo ""
echo "===================="
echo ""
echo "服务器需要更新！请执行以下命令："
echo ""
echo "ssh user@13.212.252.171 \"cd dzpoker && git pull origin master && docker-compose restart\""
echo ""
echo "或者分步执行："
echo "  ssh user@13.212.252.171"
echo "  cd dzpoker"
echo "  git pull origin master"
echo "  docker-compose restart"
echo ""
echo "更新后测试："
echo "  curl -X POST http://13.212.252.171:8000/api/games/{GAME_ID}/ai-action"
echo ""
