# 完整修复流程（服务器端执行）

## 🎯 修复内容总览

1. ✅ VARCHAR 长度限制（small_blind/big_blind）
2. ✅ Redis 游戏持久化（容器重启不丢失）
3. ✅ simulation.py 导入错误
4. ✅ action_history 兼容性处理
5. ✅ 增强错误日志

---

## 📋 服务器执行步骤

### 步骤 1: 拉取最新代码

```bash
cd /path/to/dzpoker
git pull
```

预期输出：
```
From https://github.com/...
   ...
Updating ...
Fast-forward
 backend/app/core/redis_storage.py      | ...
 backend/app/routers/games.py           | ...
 backend/app/routers/simulation.py      | ...
 ...
```

---

### 步骤 2: 执行快速部署

```bash
chmod +x quick-update.sh
./quick-update.sh
```

脚本会自动完成：
- ✓ 数据库迁移（VARCHAR 20）
- ✓ 重启后端容器
- ✓ 等待服务启动

预期输出：
```
================================
快速热更新（10秒完成）
================================

[1/3] 执行数据库迁移...
ALTER TABLE
  - action_type 字段已是 VARCHAR(20)

[2/3] 重启后端容器（利用 volume 映射，代码已自动更新）...
Restarting poker-api ... done

[3/3] 等待服务启动（5秒）...

================================
更新完成！
================================
```

---

### 步骤 3: 验证部署

```bash
chmod +x verify-backend.sh
./verify-backend.sh
```

预期输出：
```
✅ Redis 游戏存储初始化成功
✅ 应用启动完成
✅ 没有导入错误
✅ 没有发现错误
✅ API 正常响应 (HTTP 200)
   创建的游戏 ID: a1b2c3d4

🎉 后端部署成功！
```

---

### 步骤 4: 如果有错误，查看详细日志

```bash
chmod +x check-error.sh
./check-error.sh
```

这会显示：
- 最近 50 行日志中的错误
- finish API 相关错误
- 数据库迁移状态

---

## 🔍 验证修复成功

### 验证 1: 检查数据库迁移

```bash
docker exec poker-db psql -U postgres -d poker -c "SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name = 'action_type';"
```

预期输出：
```
 column_name  | character_maximum_length
--------------+--------------------------
 action_type  |                       20
(1 row)
```

### 验证 2: 检查 Redis 连接

```bash
docker-compose logs api | grep "Redis"
```

预期输出：
```
✅ Redis 游戏存储初始化成功: redis://redis:6379/0
```

### 验证 3: 检查应用启动

```bash
docker-compose logs api | grep "startup complete"
```

预期输出：
```
INFO:     Application startup complete.
```

### 验证 4: 测试 API

```bash
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 6, "small_blind": 1, "big_blind": 2}'
```

预期输出（HTTP 200）：
```json
{
  "game_id": "a1b2c3d4",
  "num_players": 6,
  "small_blind": 1.0,
  "big_blind": 2.0,
  "status": "waiting",
  "pot": 0.0
}
```

---

## 🧪 功能测试

### 测试 1: 新游戏完整流程

1. **清除浏览器缓存**（重要！）
   - Chrome: Ctrl+Shift+Delete
   - 或使用无痕模式

2. **访问首页**
   ```
   http://your-server:3000
   ```

3. **开始游戏并等待完成**

4. **检查控制台**（F12）
   - 不应该有 404 错误
   - 不应该有 500 错误（finish API）

5. **查看数据分析**
   ```
   http://your-server:3000/analytics
   ```
   - 点击游戏详情
   - 展开玩家手牌
   - 查看动作记录（应包含小盲注、大盲注）

### 测试 2: 容器重启恢复

1. **开始游戏**（不要完成）

2. **记录游戏 ID**（在 URL 中）

3. **重启后端**
   ```bash
   docker-compose restart api
   ```

4. **刷新浏览器**
   - 游戏应该继续
   - 不会显示 404

### 测试 3: 数据完整性

1. **完成一局游戏**

2. **查询数据库**
   ```bash
   # 检查游戏记录
   docker exec poker-db psql -U postgres -d poker -c "SELECT COUNT(*) FROM games WHERE status = 'finished';"

   # 检查手牌记录
   docker exec poker-db psql -U postgres -d poker -c "SELECT COUNT(*) FROM hands;"

   # 检查动作记录（包含盲注）
   docker exec poker-db psql -U postgres -d poker -c "SELECT COUNT(*) FROM actions WHERE action_type IN ('small_blind', 'big_blind');"
   ```

所有查询应返回 > 0

---

## ❌ 常见问题排查

### 问题 1: ImportError

**症状**：
```
ImportError: cannot import name 'games' from 'app.routers.games'
```

**原因**：代码未更新

**解决**：
```bash
git pull
docker-compose restart api
```

---

### 问题 2: Redis 连接失败

**症状**：
```
⚠️  Redis 连接失败，使用内存存储
```

**影响**：游戏可正常进行，但容器重启会丢失

**解决**：
```bash
# 检查 Redis
docker-compose ps redis

# 启动 Redis
docker-compose up -d redis

# 重启后端
docker-compose restart api
```

---

### 问题 3: 仍然 500 错误（finish API）

**可能原因**：

#### 原因 A: 数据库迁移未成功

**检查**：
```bash
docker exec poker-db psql -U postgres -d poker -c "SELECT character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name = 'action_type';"
```

如果返回 `10`，说明迁移未成功。

**解决**：
```bash
# 手动执行迁移
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN street TYPE VARCHAR(20);"
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);"

# 重启后端
docker-compose restart api
```

#### 原因 B: 游戏对象序列化错误

**检查**：
```bash
./check-error.sh
```

查看是否有 pickle 相关错误。

**解决**：
```bash
# 强制删除并重建容器
docker-compose stop api
docker-compose rm -f api
docker-compose up -d api
```

#### 原因 C: 其他数据库错误

**检查**：
```bash
docker-compose logs api | grep -A 10 "finish"
```

根据具体错误信息解决。

---

### 问题 4: 看不到动作记录

**原因**：旧游戏没有 action_history

**解决**：
- 只测试新游戏
- 清除浏览器缓存
- 开始新游戏

---

### 问题 5: 容器重启后仍然 404

**原因**：

#### 可能 1: Redis 未连接

检查日志是否有：
```
✅ Redis 游戏存储初始化成功
```

#### 可能 2: 浏览器缓存了旧游戏 ID

**解决**：清除浏览器缓存或无痕模式

---

## 📊 部署成功标志

### ✅ 后端日志

```
✅ Redis 游戏存储初始化成功: redis://redis:6379/0
✅ 数据库初始化完成
✅ Redis连接成功
INFO:     Application startup complete.
```

### ✅ 容器状态

```bash
docker-compose ps
```

输出：
```
   Name                 State           Ports
--------------------------------------------------------
poker-api        Up      0.0.0.0:8000->8000/tcp
poker-db         Up      0.0.0.0:5432->5432/tcp
poker-frontend   Up      0.0.0.0:3000->80/tcp
poker-redis      Up      0.0.0.0:6379->6379/tcp
```

### ✅ API 响应

```bash
curl -s http://localhost:8000/api/games/stats | python3 -m json.tool
```

输出：
```json
{
  "total_games": 1,
  "active_games": 0,
  "finished_games": 0,
  ...
}
```

### ✅ 前端可访问

```
http://your-server:3000
```

显示游戏界面，点击"开始游戏"正常运行。

---

## 🎉 部署完成检查清单

- [ ] git pull 成功
- [ ] ./quick-update.sh 执行成功
- [ ] ./verify-backend.sh 所有检查通过
- [ ] 数据库字段已迁移（VARCHAR 20）
- [ ] Redis 连接成功
- [ ] 应用启动完成
- [ ] API 正常响应（HTTP 200）
- [ ] 前端可访问
- [ ] 新游戏可正常完成
- [ ] finish API 不返回 500
- [ ] 数据分析显示完整动作记录
- [ ] 容器重启后游戏不丢失

---

## 📝 更新内容

### 代码变更

| 文件 | 变更 |
|------|------|
| backend/app/models.py | VARCHAR(10) → VARCHAR(20) |
| backend/app/core/redis_storage.py | 新增 Redis 存储 |
| backend/app/routers/games.py | 使用 Redis 替代内存 |
| backend/app/routers/simulation.py | 修复导入错误 |

### 新增脚本

| 脚本 | 用途 |
|------|------|
| quick-update.sh | 快速部署（10秒） |
| verify-backend.sh | 验证部署 |
| check-error.sh | 查看错误 |
| diagnose.sh | 完整诊断 |
| force-restart.sh | 强制重启 |

---

## 🔗 相关文档

- [DEPLOY_NOW.md](DEPLOY_NOW.md) - 简化部署指南
- [FINAL_DEPLOYMENT.md](FINAL_DEPLOYMENT.md) - 完整部署文档
- [QUICK_FIX.md](QUICK_FIX.md) - 快速修复说明
- [RESTART_ISSUE.md](RESTART_ISSUE.md) - 容器重启问题说明

---

## 💬 获取帮助

如果遇到问题：

1. **收集日志**
   ```bash
   docker-compose logs api > backend.log
   docker logs poker-db > db.log
   ./check-error.sh > error.log
   ```

2. **检查环境**
   ```bash
   docker --version
   docker-compose --version
   docker-compose ps
   ```

3. **提供完整错误信息**

---

## ⚡ 一键部署命令

```bash
cd /path/to/dzpoker && \
git pull && \
chmod +x quick-update.sh && \
./quick-update.sh && \
chmod +x verify-backend.sh && \
./verify-backend.sh
```

**完成！** 🎉
