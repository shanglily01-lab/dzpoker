# ⚠️ 必须立即部署到 EC2

## 当前状态

您正在测试生产服务器 (http://13.212.252.171)，但看到的错误说明：

**EC2 服务器还在运行旧代码！**

看到的错误：
- ❌ 400 Bad Request on `/deal`
- ❌ CORS error on `/showdown`

这些错误是因为 EC2 服务器上的代码还没有更新。

---

## 🚀 立即执行以下命令

### 1. SSH 连接到 EC2

```bash
ssh user@13.212.252.171
```

### 2. 执行一键部署脚本

复制整段，粘贴到终端：

```bash
cd dzpoker && \
echo "========================================" && \
echo "开始部署最新代码..." && \
echo "========================================" && \
git fetch origin && \
git reset --hard origin/master && \
echo "" && \
echo "✓ 代码已更新到: $(git log -1 --oneline)" && \
echo "" && \
echo "清理 Python 缓存..." && \
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
find backend -type f -name "*.pyc" -delete 2>/dev/null && \
echo "✓ Python 缓存已清理" && \
echo "" && \
echo "停止容器..." && \
docker-compose down && \
echo "✓ 容器已停止" && \
echo "" && \
echo "重新构建（这需要 3-5 分钟，请耐心等待）..." && \
docker-compose build --no-cache api && \
echo "✓ API 构建完成" && \
docker-compose build --no-cache frontend && \
echo "✓ Frontend 构建完成" && \
echo "" && \
echo "启动所有服务..." && \
docker-compose up -d && \
echo "✓ 服务已启动" && \
echo "" && \
echo "等待服务就绪..." && \
sleep 10 && \
echo "" && \
echo "========================================" && \
echo "部署完成！" && \
echo "========================================" && \
echo "" && \
docker-compose ps
```

### 3. 验证部署成功

```bash
# 查看日志
docker logs api --tail 50

# 应该看到：
# ✓ 无错误信息
# ✓ "Application startup complete"
# ✓ "Uvicorn running on http://0.0.0.0:8000"
```

### 4. 测试 API

```bash
# 创建游戏
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 4, "small_blind": 10, "big_blind": 20}'

# 复制返回的 game_id
GAME_ID="YOUR_GAME_ID"

# 开始游戏
curl -X POST http://localhost:8000/api/games/$GAME_ID/start

# 测试 AI 动作（关键！）
curl -X POST http://localhost:8000/api/games/$GAME_ID/ai-action

# 如果返回 JSON（包含 success、action 等），说明修复成功！
```

---

## ✅ 部署后的预期结果

### 在浏览器中 (http://13.212.252.171:3000)

1. 打开开发者工具（F12）
2. 创建新游戏 → 点击"开始游戏"
3. 点击"自动游戏"

**应该看到**：
- ✅ 游戏自动进行
- ✅ 无 500 错误（AI 动作成功）
- ✅ 无 400 错误（不再重复发牌）
- ✅ 无 CORS 错误（所有端点正常工作）
- ✅ 游戏顺利进行到 showdown

**不应该看到**：
- ❌ Failed to load resource: 400
- ❌ Failed to load resource: 500
- ❌ CORS policy error

---

## 📊 当前代码版本

GitHub 上的最新代码：`1bd0c8a`

包含的修复：
1. ✅ 500 错误修复：添加 `get_current_player()` 方法
2. ✅ 400 错误修复：移除前端重复发牌调用
3. ✅ CORS 配置正确：允许所有来源
4. ✅ Showdown 端点存在且正常工作

**这些修复都已经在 GitHub 上，只需要部署到 EC2！**

---

## ⏱️ 预计时间

- SSH 连接：10 秒
- 代码更新和清理：30 秒
- 重新构建：**3-5 分钟**（最耗时）
- 启动和验证：1 分钟

**总计**：约 5-7 分钟

---

## 🔍 如果遇到 Git 冲突

如果看到：
```
error: Your local changes to the following files would be overwritten by merge:
```

**不用担心**，这是因为服务器上有本地修改。

解决方法已包含在上面的脚本中：
```bash
git reset --hard origin/master
```

这会强制使用 GitHub 上的最新版本。

---

## 📞 部署后如果还有问题

### 验证代码版本

```bash
git log -1 --oneline
# 应该显示: 1bd0c8a 添加完整更新总结文档 2026-01-12
```

### 验证方法已添加

```bash
grep -n "def get_current_player" backend/app/core/poker.py
# 应该显示行号（305 左右）
```

### 手动测试导入

```bash
docker exec -it api python3 -c "
from app.core.poker import PokerGame
g = PokerGame('test')
print('✓ Has get_current_player:', hasattr(g, 'get_current_player'))
print('✓ Callable:', callable(g.get_current_player))
"
```

### 查看详细错误

```bash
docker logs api --tail 200 | grep -i error
```

---

## 📚 更多帮助

- [LATEST-UPDATE-2026-01-12.md](LATEST-UPDATE-2026-01-12.md) - 完整更新说明
- [EC2-RESOLVE-CONFLICT.md](EC2-RESOLVE-CONFLICT.md) - Git 冲突详细解决方案
- [EC2-QUICK-COMMANDS.txt](EC2-QUICK-COMMANDS.txt) - 快速命令参考

---

**不要再测试了，先部署！** 🚀

修复已经完成并推送到 GitHub，现在只需要在 EC2 上运行最新代码即可。
