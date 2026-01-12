# 500 错误修复总结

## ✅ 问题已解决

**错误**: `/api/games/{id}/ai-action` 返回 500 Internal Server Error

**根本原因**: `PokerGame` 类缺少 `get_current_player()` 方法

**修复**: 在 [poker.py:305](backend/app/core/poker.py#L305) 添加了该方法

**Commits**:
- `917efce` - 修复 500 错误：添加 get_current_player() 方法
- `a789895` - 添加 500 错误修复部署指南和更新脚本
- `fa4268e` - 添加 EC2 快速修复命令参考文件

---

## 📂 新增文件

1. **[DEPLOY-FIX-500.md](DEPLOY-FIX-500.md)** - 详细部署指南（含常见问题排查）
2. **[EC2-QUICK-COMMANDS.txt](EC2-QUICK-COMMANDS.txt)** - 快速命令参考（可直接复制粘贴）

## 🔧 更新文件

1. **[backend/app/core/poker.py](backend/app/core/poker.py)** - 添加 `get_current_player()` 方法
2. **[get-backend-logs.sh](get-backend-logs.sh)** - 使用正确容器名 `api/poker-api`
3. **[debug-500-error.sh](debug-500-error.sh)** - 同上
4. **[fix-500-error.sh](fix-500-error.sh)** - 构建命令改为 `docker-compose build api`

---

## 🚀 下一步操作

### 在 EC2 服务器上部署：

```bash
# 1. 连接服务器
ssh user@13.212.252.171
cd dzpoker

# 2. 一键更新（复制整段）
git pull origin master && \
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
find backend -type f -name "*.pyc" -delete 2>/dev/null && \
docker-compose down && \
docker-compose build --no-cache api && \
docker-compose up -d && \
sleep 10 && \
docker-compose ps
```

### 验证修复：

```bash
# 创建游戏并测试 AI 动作
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 4, "small_blind": 10, "big_blind": 20}'

# 复制返回的 game_id，然后：
GAME_ID="YOUR_GAME_ID"
curl -X POST http://localhost:8000/api/games/$GAME_ID/start
curl -X POST http://localhost:8000/api/games/$GAME_ID/ai-action

# 如果返回 JSON（包含 success、action 等），说明修复成功！
```

---

## 📊 技术细节

### 问题分析

1. **被调用位置**:
   - [games.py:313](backend/app/routers/games.py#L313)
   - [simulation.py:147](backend/app/routers/simulation.py#L147)
   - [simulation.py:239](backend/app/routers/simulation.py#L239)

2. **错误类型**: `AttributeError: 'PokerGame' object has no attribute 'get_current_player'`

3. **影响端点**:
   - `POST /api/games/{id}/ai-action`
   - `POST /api/simulation/{id}/auto-play`
   - `POST /api/simulation/{id}/single-action`

### 解决方案

添加了 `get_current_player()` 方法，逻辑如下：

```python
def get_current_player(self) -> Optional[PlayerState]:
    """获取当前应该行动的玩家"""
    if not self.players:
        return None

    # 找到所有活跃且未all-in的玩家
    active_players = [p for p in self.players if p.is_active and not p.is_all_in]

    if len(active_players) <= 1:
        return None  # 没有或只有一个活跃玩家

    # 从current_player_idx开始查找需要行动的玩家
    for i in range(len(self.players)):
        idx = (self.current_player_idx + i) % len(self.players)
        player = self.players[idx]

        if player.is_active and not player.is_all_in:
            # 检查该玩家是否需要行动
            if not player.has_acted or player.current_bet < self.current_bet:
                return player

    return None  # 所有玩家都已完成行动
```

**关键特性**:
- 只返回活跃且未 all-in 的玩家
- 检查玩家是否已行动或需要跟注
- 循环查找从 `current_player_idx` 开始
- 如果所有玩家都已行动，返回 `None`

---

## 🔍 容器名称说明

**重要**: 容器名不是 `backend`，而是 `api` 或 `poker-api`

### docker-compose.yml 配置：

```yaml
services:
  api:                      # ← 服务名
    container_name: poker-api  # ← 容器名
```

### 正确的命令：

```bash
# 查看日志
docker logs api
# 或
docker logs poker-api

# 重新构建
docker-compose build api
# 不是 docker-compose build backend
```

---

## ⏱️ 预计部署时间

- 代码更新: 30 秒
- 清理缓存: 10 秒
- 重新构建: 2-3 分钟
- 启动服务: 10 秒
- 验证测试: 1 分钟

**总计**: 约 4-5 分钟

---

## 📞 相关文档

- 详细部署指南: [DEPLOY-FIX-500.md](DEPLOY-FIX-500.md)
- 快速命令: [EC2-QUICK-COMMANDS.txt](EC2-QUICK-COMMANDS.txt)
- 服务器状态检查: [CHECK-SERVER-STATUS.md](CHECK-SERVER-STATUS.md)
- 游戏持久化问题: [GAME-PERSISTENCE-ISSUE.md](GAME-PERSISTENCE-ISSUE.md)

---

生成时间: 2026-01-12
状态: ✅ 代码已修复并提交，等待 EC2 部署
