# 修复 500 错误 - 部署指南

## 🎯 问题已修复

**问题**: `/api/games/{id}/ai-action` 返回 500 Internal Server Error

**原因**: `PokerGame.get_current_player()` 方法不存在

**修复**: 已在 `backend/app/core/poker.py` 中添加该方法

**Commit**: `917efce 修复 500 错误：添加 get_current_player() 方法`

---

## 📋 在 EC2 服务器上部署修复

### 1️⃣ SSH 连接服务器

```bash
ssh user@13.212.252.171
cd dzpoker
```

### 2️⃣ 拉取最新代码

```bash
git pull origin master
```

**应该看到**:
```
Updating xxxxx..917efce
Fast-forward
 backend/app/core/poker.py | 29 +++++++++++++++++++++++++++++
 1 file changed, 29 insertions(+)
```

### 3️⃣ 验证代码已更新

```bash
# 检查最新 commit
git log -1 --oneline
# 应显示: 917efce 修复 500 错误：添加 get_current_player() 方法

# 验证方法已添加
grep -n "def get_current_player" backend/app/core/poker.py
# 应显示行号（大约在 305 行左右）
```

### 4️⃣ 清理 Python 缓存（重要！）

```bash
# 删除所有 __pycache__ 目录
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# 删除所有 .pyc 文件
find backend -type f -name "*.pyc" -delete 2>/dev/null

echo "✓ Python 缓存已清理"
```

### 5️⃣ 停止容器

```bash
docker-compose down
```

### 6️⃣ 重新构建后端（无缓存）

```bash
# 注意：服务名是 api，不是 backend
docker-compose build --no-cache api
```

**预计时间**: 2-3 分钟（取决于网络速度）

### 7️⃣ 启动所有服务

```bash
docker-compose up -d
```

### 8️⃣ 等待服务启动

```bash
# 等待 10 秒让服务完全启动
sleep 10

# 检查容器状态
docker-compose ps
```

**所有容器应该显示 "Up"**

---

## ✅ 验证修复成功

### 方法 1: 查看后端日志

```bash
# 注意：容器名可能是 poker-api 或 api，不是 backend
docker logs api --tail 50

# 或者使用完整容器名
docker logs poker-api --tail 50
```

**应该看到**:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**不应该看到**:
```
AttributeError: 'PokerGame' object has no attribute 'get_current_player'
ModuleNotFoundError
ImportError
```

### 方法 2: 测试 API 端点

#### a) 创建游戏

```bash
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 4, "small_blind": 10, "big_blind": 20}'
```

**复制返回的 `game_id`** (例如: `abc123`)

#### b) 开始游戏

```bash
# 替换 YOUR_GAME_ID 为实际的 game_id
GAME_ID="YOUR_GAME_ID"

curl -X POST http://localhost:8000/api/games/$GAME_ID/start
```

**应该返回**:
```json
{
  "success": true,
  "message": "游戏已开始",
  "game_state": { ... }
}
```

#### c) 测试 AI 动作（关键测试！）

```bash
curl -X POST http://localhost:8000/api/games/$GAME_ID/ai-action
```

**如果修复成功，应该返回**:
```json
{
  "success": true,
  "player_id": 1,
  "player_type": "TAG",
  "action": "call",
  "amount": 20,
  "game_state": { ... }
}
```

**如果还是 500 错误**:
```
Internal Server Error
```

则需要查看后端日志排查问题。

### 方法 3: 从外部测试（在本地电脑）

```bash
# 替换 YOUR_GAME_ID
curl -X POST http://13.212.252.171:8000/api/games/YOUR_GAME_ID/ai-action
```

---

## 🐛 常见问题

### Q1: git pull 显示 "Already up to date"

**可能原因**: 本地有未提交的更改

**解决**:
```bash
# 查看状态
git status

# 如果有修改，暂存它们
git stash

# 再次拉取
git pull origin master

# 恢复本地更改（如果需要）
git stash pop
```

### Q2: docker-compose build 报错

**查看错误详情**:
```bash
docker-compose build api 2>&1 | tee build.log
```

**常见错误**:
- **网络问题**: 重试或使用镜像加速
- **磁盘空间不足**: `docker system prune -f`
- **权限问题**: 确认 Docker 守护进程运行正常

### Q3: 容器启动后立即退出

```bash
# 查看退出原因
docker-compose logs api

# 查看最近的错误
docker logs poker-api --tail 100 | grep -i error
```

### Q4: 端口被占用

```bash
# 检查端口占用
netstat -tulpn | grep 8000
netstat -tulpn | grep 3000

# 如果有旧进程，停止它们
docker-compose down
```

### Q5: 还是 500 错误

**检查列表**:

1. **确认代码已更新**:
   ```bash
   git log -1 --oneline
   # 必须显示: 917efce
   ```

2. **确认 Python 缓存已清理**:
   ```bash
   find backend -name "*.pyc" -o -name __pycache__
   # 应该没有输出
   ```

3. **确认容器已重建**:
   ```bash
   docker images | grep poker
   # 查看镜像创建时间，应该是最近几分钟
   ```

4. **查看详细错误日志**:
   ```bash
   docker logs api --tail 200 > error.log
   cat error.log
   ```

5. **手动测试导入**:
   ```bash
   docker exec -it api python3 -c "
   from app.core.poker import PokerGame
   game = PokerGame('test-game')
   print('✓ PokerGame imported')
   print('✓ get_current_player method:', hasattr(game, 'get_current_player'))
   "
   ```

   **应该输出**:
   ```
   ✓ PokerGame imported
   ✓ get_current_player method: True
   ```

---

## 📊 预期结果对比

### 修复前（500 错误）

```bash
$ curl -X POST http://localhost:8000/api/games/xxx/ai-action
Internal Server Error

$ docker logs api --tail 20
ERROR: Exception in ASGI application
...
AttributeError: 'PokerGame' object has no attribute 'get_current_player'
```

### 修复后（正常）

```bash
$ curl -X POST http://localhost:8000/api/games/xxx/ai-action
{
  "success": true,
  "player_id": 1,
  "player_type": "TAG",
  "action": "raise",
  "amount": 40,
  "game_state": { ... }
}

$ docker logs api --tail 20
INFO: 127.0.0.1 - "POST /api/games/xxx/ai-action HTTP/1.1" 200 OK
```

---

## ⏱️ 预计时间

- **代码更新**: 30 秒
- **清理缓存**: 10 秒
- **重新构建**: 2-3 分钟
- **启动服务**: 10 秒
- **验证测试**: 1 分钟

**总计**: 约 4-5 分钟

---

## 📞 如果还有问题

如果按照以上步骤操作后仍然出现 500 错误，请提供以下信息：

1. **Git commit 确认**:
   ```bash
   git log -3 --oneline
   ```

2. **完整后端日志**:
   ```bash
   docker logs api > backend-full.log
   cat backend-full.log
   ```

3. **容器状态**:
   ```bash
   docker-compose ps
   docker inspect poker-api | grep -A 10 "State"
   ```

4. **方法验证**:
   ```bash
   docker exec -it api python3 -c "
   from app.core.poker import PokerGame
   import inspect
   print(inspect.getsourcelines(PokerGame.get_current_player))
   "
   ```

---

生成时间: 2026-01-12
紧急程度: 🔴🔴🔴 最高
状态: ✅ 代码已修复，等待部署
