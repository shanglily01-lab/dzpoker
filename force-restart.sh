#!/bin/bash
# 强制重启后端 - 确保代码重新加载

set -e

echo "================================"
echo "强制重启后端（含数据库迁移）"
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

# 1. 数据库迁移
echo "[1/4] 执行数据库迁移..."
echo "正在增加字段长度..."

docker exec poker-db psql -U postgres -d poker <<'EOSQL'
-- 增加字段长度
ALTER TABLE actions ALTER COLUMN street TYPE VARCHAR(20);
ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);

-- 验证修改
SELECT
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'actions'
AND column_name IN ('street', 'action_type');
EOSQL

if [ $? -eq 0 ]; then
    echo "✓ 数据库迁移成功"
else
    echo "注意: 数据库迁移可能已执行过（忽略错误）"
fi
echo ""

# 2. 验证代码已同步
echo "[2/4] 验证容器内代码是否已更新..."
MODELS_CHECK=$(docker exec poker-api grep -c "String(20)" /app/app/models.py 2>/dev/null || echo "0")
if [ "$MODELS_CHECK" -ge "2" ]; then
    echo "✓ 容器内代码已更新 (找到 $MODELS_CHECK 处 String(20))"
else
    echo "⚠ 容器内代码可能未更新，将强制停止重启"
fi
echo ""

# 3. 强制停止并删除容器
echo "[3/4] 强制停止并删除后端容器..."
$DC stop api
$DC rm -f api
echo ""

# 4. 重新创建并启动
echo "[4/4] 重新创建并启动后端容器..."
$DC up -d api

echo ""
echo "等待服务启动（10秒）..."
sleep 10

echo ""
echo "================================"
echo "检查启动日志"
echo "================================"
$DC logs --tail=30 api

echo ""
echo "================================"
echo "验证修复"
echo "================================"

# 验证数据库
echo "数据库字段定义:"
docker exec poker-db psql -U postgres -d poker -c "SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name IN ('street', 'action_type');"

echo ""
echo "容器内 models.py:"
docker exec poker-api grep "action_type" /app/app/models.py | grep "Column"

echo ""
echo "================================"
echo "重启完成！"
echo "================================"
echo ""
echo "测试步骤:"
echo "  1. 访问 http://your-server:3000"
echo "  2. 开始新游戏"
echo "  3. 查看是否还有 500 错误"
echo "  4. 检查数据分析页面是否有动作记录"
echo ""
