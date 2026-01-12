#!/bin/bash
# 在 EC2 服务器上更新并重启服务

echo "======================================"
echo "  EC2 服务器代码更新脚本"
echo "======================================"

# 服务器地址
SERVER="13.212.252.171"

# 显示说明
cat << 'EOF'

请在 EC2 服务器上执行以下命令来更新代码：

1. SSH 登录到服务器：
   ssh user@13.212.252.171

2. 进入项目目录：
   cd dzpoker

3. 拉取最新代码：
   git pull origin master

4. 重启服务：
   docker-compose down
   docker-compose up -d --build

5. 检查服务状态：
   docker-compose ps
   docker logs backend --tail 50

或者，复制下面的一键命令：

ssh user@13.212.252.171 "cd dzpoker && git pull origin master && docker-compose down && docker-compose up -d --build && docker-compose ps"

更新后，自动游戏功能将可用：
- API: http://13.212.252.171:8000/api/simulation/{game_id}/auto-play
- 前端: http://13.212.252.171/simulation
- Dashboard 一键按钮: http://13.212.252.171/dashboard

EOF

echo ""
echo "======================================"
echo "提示：需要在 EC2 服务器上手动执行"
echo "======================================"
