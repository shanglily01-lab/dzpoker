#!/bin/bash
# 快速更新 - 无需重新构建镜像（仅适用于代码修改，不包括依赖变更）
# 原理：利用 volume 映射直接更新容器内代码

set -e

echo "================================"
echo "快速热更新（10秒完成）"
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

# 1. 数据库迁移（只执行一次，如果已执行可跳过）
echo "[1/3] 执行数据库迁移..."
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN street TYPE VARCHAR(20);" 2>/dev/null || echo "  - street 字段已是 VARCHAR(20)"
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);" 2>/dev/null || echo "  - action_type 字段已是 VARCHAR(20)"
echo ""

# 2. 重启后端容器（不重新构建）
echo "[2/3] 重启后端容器（利用 volume 映射，代码已自动更新）..."
$DC restart api
echo ""

# 3. 等待启动
echo "[3/3] 等待服务启动（5秒）..."
sleep 5

echo ""
echo "================================"
echo "更新完成！"
echo "================================"
echo ""
echo "用时: ~10秒"
echo ""
echo "检查日志:"
$DC logs --tail=20 api
echo ""
echo "测试地址: http://localhost:3000"
echo ""
