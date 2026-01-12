# 🎯 500 错误已修复 - 请立即部署

## 问题

您的 AI 操作端点 `/api/games/{id}/ai-action` 一直返回 500 错误。

## 原因

代码中调用了不存在的 `game.get_current_player()` 方法。

## 解决

✅ 已在 `backend/app/core/poker.py` 中添加该方法
✅ 已更新所有辅助脚本使用正确容器名
✅ 已推送到 GitHub

---

## 🚀 在 EC2 上部署（必须！）

### 方法 1: 复制粘贴快速命令

打开 [EC2-QUICK-COMMANDS.txt](EC2-QUICK-COMMANDS.txt)，复制命令执行。

### 方法 2: 一键脚本

```bash
ssh user@13.212.252.171
cd dzpoker
git pull origin master && \
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
docker-compose down && \
docker-compose build --no-cache api && \
docker-compose up -d
```

### 方法 3: 查看详细指南

阅读 [DEPLOY-FIX-500.md](DEPLOY-FIX-500.md) 了解完整步骤和排查方法。

---

## ✅ 验证修复

部署后，测试 AI 端点：

```bash
# 在 EC2 服务器上执行
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 4, "small_blind": 10, "big_blind": 20}'

# 复制返回的 game_id，然后：
GAME_ID="YOUR_GAME_ID"
curl -X POST http://localhost:8000/api/games/$GAME_ID/start
curl -X POST http://localhost:8000/api/games/$GAME_ID/ai-action
```

**成功标志**: 返回 JSON 包含 `{"success": true, "player_id": ..., "action": ...}`

**失败标志**: 返回 `Internal Server Error` 或其他错误

---

## 📄 相关文档

- **[FIX-SUMMARY.md](FIX-SUMMARY.md)** - 修复总结和技术细节
- **[DEPLOY-FIX-500.md](DEPLOY-FIX-500.md)** - 详细部署指南（含常见问题）
- **[EC2-QUICK-COMMANDS.txt](EC2-QUICK-COMMANDS.txt)** - 快速命令参考

---

## ⏱️ 预计时间

整个部署过程约 **4-5 分钟**。

---

## 📊 提交历史

- `917efce` - 修复 500 错误：添加 get_current_player() 方法
- `a789895` - 添加 500 错误修复部署指南和更新脚本
- `fa4268e` - 添加 EC2 快速修复命令参考文件
- `1ce23c6` - 添加 500 错误修复总结文档
- `3e56197` - 添加 500 错误修复快速指南
- `93703b8` - 添加 EC2 Git 冲突解决指南
- `0ddbdf8` - 修复 400 错误：移除前端重复发牌调用

---

**现在就去 EC2 部署吧！** 🚀
