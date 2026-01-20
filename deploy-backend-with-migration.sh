#!/bin/bash
# 德州扑克系统 - 后端更新与数据库迁移
# 用途：修复 action_type VARCHAR 长度限制问题

set -e  # 遇到错误立即退出

echo "================================"
echo "后端更新与数据库迁移"
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

# 1. 停止后端容器
echo "[1/6] 停止后端容器..."
$DC stop api
echo ""

# 2. 执行数据库迁移
echo "[2/6] 执行数据库迁移（增加 action_type 字段长度）..."
echo "正在连接数据库..."

# 使用 docker exec 在数据库容器中执行 SQL
docker exec -i dzpoker-db-1 psql -U dzpoker_user -d dzpoker_db <<'EOF'
-- 增加 actions 表字段长度
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

\echo '数据库迁移完成！'
EOF

if [ $? -ne 0 ]; then
    echo "错误: 数据库迁移失败！"
    echo "提示: 请检查数据库容器名称（可能不是 dzpoker-db-1）"
    echo "运行 'docker ps' 查看正确的容器名称"
    exit 1
fi
echo ""

# 3. 删除旧的后端容器和镜像
echo "[3/6] 删除旧的后端容器和镜像..."
$DC rm -f api
docker rmi dzpoker-api 2>/dev/null || true
echo ""

# 4. 重新构建后端
echo "[4/6] 重新构建后端容器（这可能需要几分钟）..."
$DC build api
if [ $? -ne 0 ]; then
    echo "错误: 后端构建失败！"
    exit 1
fi
echo ""

# 5. 启动后端
echo "[5/6] 启动后端服务..."
$DC up -d api
if [ $? -ne 0 ]; then
    echo "错误: 启动失败！"
    exit 1
fi
echo ""

# 6. 等待启动并检查
echo "[6/6] 等待后端启动（10秒）..."
sleep 10

echo ""
echo "检查后端日志..."
$DC logs --tail=30 api

echo ""
echo "================================"
echo "容器状态:"
echo "================================"
$DC ps

echo ""
echo "================================"
echo "后端部署完成！"
echo "================================"
echo ""
echo "修复内容:"
echo "  ✓ 增加 action_type 字段长度 VARCHAR(10) → VARCHAR(20)"
echo "  ✓ 增加 street 字段长度 VARCHAR(10) → VARCHAR(20)"
echo "  ✓ 修复 'small_blind' 和 'big_blind' 保存问题"
echo ""
echo "测试步骤:"
echo "  1. 开始一局新游戏"
echo "  2. 让游戏自动完成"
echo "  3. 访问数据分析页面: http://localhost:3000/analytics"
echo "  4. 点击游戏详情，展开玩家手牌"
echo "  5. 查看动作记录中是否包含【小盲注】和【大盲注】"
echo ""
echo "如果遇到问题:"
echo "  - 查看后端日志: $DC logs -f api"
echo "  - 查看数据库日志: docker logs dzpoker-db-1"
echo ""
