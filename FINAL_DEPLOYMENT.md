# 最终部署指南 - Redis 持久化 + VARCHAR 修复

## ✅ 已完成的修复

### 1. VARCHAR 长度限制问题
- ✅ 增加 `action_type` 字段：VARCHAR(10) → VARCHAR(20)
- ✅ 增加 `street` 字段：VARCHAR(10) → VARCHAR(20)
- ✅ 修复 'small_blind' 和 'big_blind' 无法保存的问题

### 2. Redis 游戏状态持久化
- ✅ 游戏状态保存到 Redis
- ✅ 容器重启后游戏不丢失
- ✅ Redis 不可用时自动降级到内存存储
- ✅ 1 小时 TTL 自动清理过期游戏

---

## 🚀 Linux 服务器部署（10秒）

### 方法一：快速部署（推荐）

```bash
# 1. 拉取最新代码
cd /path/to/dzpoker
git pull

# 2. 执行快速更新脚本
chmod +x quick-update.sh
./quick-update.sh
```

脚本会自动完成：
- ✓ 数据库迁移（VARCHAR 20）
- ✓ 重启后端容器
- ✓ 代码通过 volume 自动同步
- ✓ Redis 持久化自动生效

---

## 🔍 验证部署

### 1. 检查后端日志

```bash
docker-compose logs --tail=20 api
```

应该看到：
```
✅ Redis 游戏存储初始化成功: redis://redis:6379/0
INFO:     Application startup complete.
```

### 2. 测试游戏持久化

```bash
# A. 开始一局新游戏
# 访问 http://your-server:3000
# 记录游戏 ID（在 URL 中）

# B. 重启后端容器
docker-compose restart api

# C. 刷新页面
# 游戏应该继续，不会显示 404
```

### 3. 验证 VARCHAR 修复

```bash
# A. 完成一局游戏

# B. 检查后端日志
docker-compose logs api | grep "finish"

# 应该看到：
# [Database] Game xxx finished and data saved successfully
# 而不是 500 错误

# C. 查看数据分析
# 访问 http://your-server:3000/analytics
# 点击游戏详情
# 展开玩家手牌
# 查看动作记录（应包含小盲注、大盲注等）
```

### 4. 验证数据库

```bash
# 检查字段长度
docker exec poker-db psql -U postgres -d poker -c "SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name = 'action_type';"

# 应该输出：
#  column_name  | character_maximum_length
# --------------+--------------------------
#  action_type  |                       20

# 检查动作记录
docker exec poker-db psql -U postgres -d poker -c "SELECT COUNT(*) FROM actions WHERE action_type IN ('small_blind', 'big_blind');"

# 应该 > 0
```

---

## 🎯 完整功能测试

### 测试 1: 新游戏完整流程

1. **清除浏览器缓存**（重要！）
   - Chrome: Ctrl+Shift+Delete
   - 或使用无痕模式：Ctrl+Shift+N

2. **开始新游戏**
   - 访问 http://your-server:3000
   - 点击"开始游戏"

3. **查看控制台**（F12 → Console）
   - 不应该有 404 错误
   - 不应该有 500 错误

4. **等待游戏完成**
   - AI 自动完成游戏

5. **查看数据分析**
   - 访问 http://your-server:3000/analytics
   - 最新游戏应该有完整数据

### 测试 2: 容器重启恢复

1. **开始游戏但不完成**
   - 访问 http://your-server:3000
   - 开始游戏
   - 记录游戏 ID（在 URL 中，如 `a1b2c3d4`）

2. **重启后端**
   ```bash
   docker-compose restart api
   ```

3. **刷新页面**
   - 游戏应该继续，不会 404
   - 可以继续操作

### 测试 3: 动作记录完整性

1. **完成一局游戏**

2. **查看动作记录**
   - 数据分析 → 游戏详情 → 展开玩家

3. **验证动作类型**
   - ✓ 小盲注 (small_blind)
   - ✓ 大盲注 (big_blind)
   - ✓ 跟注 (call)
   - ✓ 加注 (raise)
   - ✓ 弃牌 (fold)
   - ✓ 过牌 (check)

---

## 🔧 故障排查

### 问题 1: Redis 连接失败

**症状**：
```
⚠️  Redis 连接失败，使用内存存储: ...
```

**影响**：游戏仍可正常进行，但重启后会丢失

**解决**：
```bash
# 检查 Redis 容器
docker-compose ps redis

# 如果未运行，启动
docker-compose up -d redis

# 重启后端
docker-compose restart api
```

### 问题 2: 仍然看到 404 错误

**原因**：浏览器缓存了旧游戏 ID

**解决**：
1. 清除浏览器缓存
2. 或使用无痕模式
3. 或直接访问首页（会创建新游戏）

### 问题 3: finish API 仍返回 500

**原因**：数据库迁移未成功

**解决**：
```bash
# 手动执行迁移
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);"

# 重启后端
docker-compose restart api
```

### 问题 4: 看不到动作记录

**原因**：旧游戏数据没有 action_history

**解决**：
- 只有新游戏才有完整动作记录
- 清除浏览器缓存，开始新游戏

---

## 📊 技术架构变更

### 之前（内存存储）

```python
# backend/app/routers/games.py
games: Dict[str, PokerGame] = {}  # 内存字典

# 问题：
# ❌ 容器重启 → 游戏丢失
# ❌ 无法横向扩展
# ❌ 无法恢复进行中的游戏
```

### 现在（Redis 持久化）

```python
# backend/app/core/redis_storage.py
class RedisGameStorage:
    def save_game(self, game_id, game):
        self.redis_client.setex(f"game:{game_id}", 3600, pickle.dumps(game))

    def load_game(self, game_id):
        data = self.redis_client.get(f"game:{game_id}")
        return pickle.loads(data) if data else None

# 优点：
# ✓ 容器重启 → 游戏保留
# ✓ 支持多后端实例
# ✓ 自动过期清理（1小时）
# ✓ Redis 故障自动降级
```

---

## 🎉 部署成功标志

### 后端日志

```
✅ Redis 游戏存储初始化成功: redis://redis:6379/0
✅ 数据库初始化完成
✅ Redis连接成功
INFO:     Application startup complete.
```

### 游戏流程

```
[Frontend] 开始游戏
  ↓
[Backend] 创建游戏 → 保存到 Redis
  ↓
[Frontend] 执行动作
  ↓
[Backend] 更新状态 → 保存到 Redis
  ↓
[Frontend] 游戏完成
  ↓
[Backend] 保存到数据库（包含 small_blind/big_blind）
  ↓
[Database] 成功保存所有动作
```

### 数据验证

```bash
# 游戏记录
SELECT COUNT(*) FROM games WHERE status = 'finished';  # > 0

# 手牌记录
SELECT COUNT(*) FROM hands;  # > 0

# 动作记录（包含盲注）
SELECT COUNT(*) FROM actions WHERE action_type IN ('small_blind', 'big_blind');  # > 0
```

---

## 📝 更新日志

### 2025-01-20

**修复**：
1. ✅ VARCHAR(10) → VARCHAR(20) 修复 small_blind 保存错误
2. ✅ 实现 Redis 游戏状态持久化
3. ✅ 容器重启不丢失游戏

**新增**：
1. ✅ RedisGameStorage 封装类
2. ✅ 自动降级机制（Redis 不可用时）
3. ✅ 游戏过期清理（TTL 1小时）

**部署**：
1. ✅ 快速部署脚本（10秒）
2. ✅ 诊断脚本
3. ✅ 完整部署文档

---

## 🔗 相关文件

- [QUICK_FIX.md](QUICK_FIX.md) - 3秒快速修复指南
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 完整部署文档
- [RESTART_ISSUE.md](RESTART_ISSUE.md) - 容器重启问题说明
- [quick-update.sh](quick-update.sh) - 快速更新脚本
- [diagnose.sh](diagnose.sh) - 诊断脚本
- [force-restart.sh](force-restart.sh) - 强制重启脚本

---

## ⚡ 一键部署

```bash
git pull && chmod +x quick-update.sh && ./quick-update.sh
```

就这么简单！10秒完成。
