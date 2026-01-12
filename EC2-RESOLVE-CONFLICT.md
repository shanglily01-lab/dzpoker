# 解决 EC2 Git 冲突

## 问题

执行 `git pull` 时出现错误：

```
error: Your local changes to the following files would be overwritten by merge:
	fix-500-error.sh
Please commit your changes or stash them before you merge.
```

## 原因

EC2 服务器上的 `fix-500-error.sh` 有本地修改，与远程更新冲突。

---

## 🚀 快速解决方案

### 方法 1: 放弃本地更改（推荐）

如果本地修改不重要，直接使用远程版本：

```bash
cd dzpoker

# 放弃本地修改
git checkout -- fix-500-error.sh

# 拉取最新代码
git pull origin master

# 继续部署
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
docker-compose down
docker-compose build --no-cache api
docker-compose up -d
```

### 方法 2: 保存本地更改

如果想保留本地修改：

```bash
cd dzpoker

# 暂存本地修改
git stash

# 拉取最新代码
git pull origin master

# 恢复本地修改（可能有冲突需要手动解决）
git stash pop

# 继续部署
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
docker-compose down
docker-compose build --no-cache api
docker-compose up -d
```

### 方法 3: 强制重置（最干净）

完全重置到远程版本：

```bash
cd dzpoker

# 强制重置到远程版本
git fetch origin
git reset --hard origin/master

# 继续部署
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
docker-compose down
docker-compose build --no-cache api
docker-compose up -d
```

---

## ✅ 一键完整解决脚本

复制整段执行（使用方法 3 - 强制重置）：

```bash
cd dzpoker && \
git fetch origin && \
git reset --hard origin/master && \
git status && \
echo "========================================" && \
echo "代码已更新到最新版本" && \
echo "========================================" && \
git log -3 --oneline && \
echo "========================================" && \
echo "开始部署..." && \
echo "========================================" && \
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
find backend -type f -name "*.pyc" -delete 2>/dev/null && \
docker-compose down && \
docker-compose build --no-cache api && \
docker-compose up -d && \
sleep 10 && \
echo "========================================" && \
echo "部署完成！容器状态：" && \
echo "========================================" && \
docker-compose ps && \
echo "========================================" && \
echo "后端日志（最近 30 行）：" && \
echo "========================================" && \
docker logs api --tail 30
```

---

## 🔍 验证部署成功

```bash
# 1. 检查最新 commit
git log -1 --oneline
# 应该显示: 3e56197 添加 500 错误修复快速指南

# 2. 验证方法已添加
grep -n "def get_current_player" backend/app/core/poker.py
# 应该显示行号

# 3. 测试 API
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 4, "small_blind": 10, "big_blind": 20}'

# 复制 game_id，然后：
GAME_ID="YOUR_GAME_ID"
curl -X POST http://localhost:8000/api/games/$GAME_ID/start
curl -X POST http://localhost:8000/api/games/$GAME_ID/ai-action
```

---

## 📊 预期结果

### Git 重置后：

```bash
$ git log -1 --oneline
3e56197 添加 500 错误修复快速指南

$ git status
On branch master
Your branch is up to date with 'origin/master'.

nothing to commit, working tree clean
```

### 容器启动后：

```bash
$ docker-compose ps
NAME                IMAGE               STATUS
poker-api           dzpoker-backend     Up 10 seconds
frontend            dzpoker-frontend    Up 10 seconds
postgres            postgres:14         Up 10 seconds
redis               redis:7             Up 10 seconds
```

### API 测试成功：

```bash
$ curl -X POST http://localhost:8000/api/games/$GAME_ID/ai-action
{
  "success": true,
  "player_id": 1,
  "player_type": "TAG",
  "action": "call",
  "amount": 20,
  ...
}
```

---

## 🐛 如果还有问题

查看完整日志：

```bash
docker logs api --tail 200 > /tmp/backend.log
cat /tmp/backend.log
```

查找错误：

```bash
docker logs api --tail 200 | grep -i error
docker logs api --tail 200 | grep -i "attributeerror"
```

手动测试导入：

```bash
docker exec -it api python3 -c "
from app.core.poker import PokerGame
g = PokerGame('test')
print('✓ Has method:', hasattr(g, 'get_current_player'))
print('✓ Callable:', callable(g.get_current_player))
print('✓ Result:', g.get_current_player())
"
```

---

生成时间: 2026-01-12
