#!/bin/bash
# 德州扑克系统 - 完整修复部署脚本
# 用途：重新部署系统并修复历史数据

echo "================================"
echo "德州扑克系统 - 完整修复部署"
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

# 1. 停止现有容器
echo "[1/5] 停止现有容器..."
$DC down
echo ""

# 2. 重新构建前端（强制无缓存）
echo "[2/5] 重新构建前端容器（无缓存，这可能需要几分钟）..."
$DC build --no-cache frontend
if [ $? -ne 0 ]; then
    echo "错误: 前端构建失败！"
    exit 1
fi
echo ""

# 3. 重新构建后端
echo "[3/5] 重新构建后端容器..."
$DC build --no-cache api
if [ $? -ne 0 ]; then
    echo "错误: 后端构建失败！"
    exit 1
fi
echo ""

# 4. 启动所有服务
echo "[4/5] 启动所有服务..."
$DC up -d
if [ $? -ne 0 ]; then
    echo "错误: 启动失败！"
    exit 1
fi
echo ""

# 5. 等待服务启动
echo "[5/5] 等待服务启动（15秒）..."
sleep 15

# 检查容器状态
echo ""
echo "================================"
echo "容器状态:"
echo "================================"
$DC ps

echo ""
echo "================================"
echo "部署完成！"
echo "================================"
echo ""

# 询问是否修复历史数据
echo "是否需要修复历史游戏数据？(y/n)"
read -r fix

if [ "$fix" = "y" ] || [ "$fix" = "Y" ]; then
    echo ""
    echo "================================"
    echo "修复历史游戏数据"
    echo "================================"
    echo ""

    echo "正在修复历史游戏..."
    $DC exec api python /app/fix_old_games.py

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 历史数据修复完成！"
    else
        echo ""
        echo "⚠️ 历史数据修复失败，请检查日志"
    fi
fi

echo ""
echo "================================"
echo "访问地址:"
echo "================================"
echo "  前端: http://localhost:3000"
echo "  后端API: http://localhost:8000/docs"
echo ""
echo "查看后端日志:"
echo "  $DC logs api --tail=50 -f"
echo ""
echo "测试步骤:"
echo "  1. 访问 http://localhost:3000"
echo "  2. 创建新游戏并开启自动模式"
echo "  3. 打开浏览器控制台（F12）查看是否有 [Finish] 日志"
echo "  4. 等待游戏结束"
echo "  5. 查看数据分析页面，确认:"
echo "     - 游戏状态为 '已完成'"
echo "     - 手牌数不为 0"
echo ""
