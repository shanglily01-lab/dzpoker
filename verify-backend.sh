#!/bin/bash
# 验证后端是否成功启动

echo "================================"
echo "验证后端启动状态"
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

echo "[1/3] 检查容器状态..."
$DC ps api
echo ""

echo "[2/3] 检查后端日志（最近 30 行）..."
echo "--------------------------------"
$DC logs --tail=30 api
echo ""

echo "[3/3] 验证关键启动信息..."
echo "--------------------------------"

# 检查 Redis 连接
if $DC logs api | grep -q "Redis 游戏存储初始化成功"; then
    echo "✅ Redis 游戏存储初始化成功"
else
    echo "⚠️  未找到 Redis 初始化成功信息"
fi

# 检查应用启动
if $DC logs api | grep -q "Application startup complete"; then
    echo "✅ 应用启动完成"
else
    echo "❌ 应用未成功启动"
fi

# 检查导入错误
if $DC logs api | grep -q "ImportError"; then
    echo "❌ 发现导入错误"
    $DC logs api | grep "ImportError" -A 3
else
    echo "✅ 没有导入错误"
fi

# 检查其他错误
ERROR_COUNT=$($DC logs api | grep -c "ERROR\|Exception\|Traceback" || echo "0")
if [ "$ERROR_COUNT" -gt "0" ]; then
    echo "⚠️  发现 $ERROR_COUNT 个错误，请检查日志"
else
    echo "✅ 没有发现错误"
fi

echo ""
echo "================================"
echo "测试 API 响应"
echo "================================"

# 测试健康检查端点（如果有）
# 测试创建游戏 API
echo "测试游戏创建 API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 6, "small_blind": 1, "big_blind": 2}' \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API 正常响应 (HTTP $HTTP_CODE)"
    GAME_ID=$(echo "$RESPONSE" | grep -o '"game_id":"[^"]*"' | cut -d'"' -f4)
    echo "   创建的游戏 ID: $GAME_ID"
elif [ -z "$HTTP_CODE" ]; then
    echo "❌ 无法连接到 API (检查容器是否运行)"
else
    echo "⚠️  API 返回错误 (HTTP $HTTP_CODE)"
    echo "$RESPONSE" | grep -v "HTTP_CODE"
fi

echo ""
echo "================================"
echo "总结"
echo "================================"

if $DC logs api | grep -q "Application startup complete" && [ "$HTTP_CODE" = "200" ]; then
    echo "🎉 后端部署成功！"
    echo ""
    echo "下一步："
    echo "  1. 清除浏览器缓存或使用无痕模式"
    echo "  2. 访问 http://your-server:3000"
    echo "  3. 开始新游戏测试"
else
    echo "❌ 后端部署失败，请检查上方错误信息"
    echo ""
    echo "常见问题："
    echo "  - ImportError: 运行 git pull 更新代码"
    echo "  - Redis 连接失败: 检查 Redis 容器是否运行"
    echo "  - API 无响应: 检查端口映射和防火墙"
fi
echo ""
