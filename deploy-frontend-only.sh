#!/bin/bash
# 德州扑克系统 - 仅重建前端
# 用途：在旧版本Docker Compose上部署前端更新

echo "================================"
echo "重建前端容器"
echo "================================"
echo ""

# 检测使用 docker-compose 还是 docker compose
if command -v docker-compose &> /dev/null; then
    DC="docker-compose"
    echo "使用 docker-compose 命令"
elif docker compose version &> /dev/null; then
    DC="docker compose"
    echo "使用 docker compose 命令"
else
    echo "错误: 未找到 docker-compose 或 docker compose 命令"
    exit 1
fi
echo ""

# 1. 停止前端容器
echo "[1/4] 停止前端容器..."
$DC stop frontend
echo ""

# 2. 删除前端容器和镜像
echo "[2/4] 删除旧的前端容器和镜像..."
$DC rm -f frontend
docker rmi dzpoker-frontend 2>/dev/null || true
echo ""

# 3. 重新构建前端
echo "[3/4] 重新构建前端容器（这可能需要几分钟）..."
$DC build frontend
if [ $? -ne 0 ]; then
    echo "错误: 前端构建失败！"
    exit 1
fi
echo ""

# 4. 启动前端
echo "[4/4] 启动前端服务..."
$DC up -d frontend
if [ $? -ne 0 ]; then
    echo "错误: 启动失败！"
    exit 1
fi
echo ""

# 等待启动
echo "等待前端启动（5秒）..."
sleep 5

# 检查容器状态
echo ""
echo "================================"
echo "容器状态:"
echo "================================"
$DC ps

echo ""
echo "================================"
echo "前端部署完成！"
echo "================================"
echo ""
echo "访问地址: http://localhost:3000"
echo ""
echo "测试步骤:"
echo "  1. 清除浏览器缓存或使用无痕模式"
echo "  2. 访问数据分析页面"
echo "  3. 点击游戏详情，展开玩家手牌"
echo "  4. 查看动作记录（小盲注、跟注、加注等）"
echo ""
