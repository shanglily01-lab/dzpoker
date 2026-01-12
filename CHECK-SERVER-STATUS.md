# 检查服务器状态
# Check Server Status

## 🔴 紧急：500 错误持续出现

错误日志显示 `/api/games/{id}/ai-action` 返回 500 Internal Server Error。

这**100%确认服务器还在运行旧代码**。

---

## ✅ 立即执行以下命令

### SSH 登录服务器
```bash
ssh user@13.212.252.171
```

### 检查当前代码版本
```bash
cd dzpoker
git log -1 --oneline
```

**预期看到**：`b28f6cc 添加 API 测试工具和最终更新总结`

**如果不是**：说明代码还没更新！

### 查看后端日志（查看 500 错误原因）
```bash
docker logs backend --tail 100 | grep -i error
```

**可能看到的错误**：
- `ModuleNotFoundError: No module named 'app.ai.decision_maker'`
- `ImportError: cannot import name 'ai_decision_maker'`
- `AttributeError: 'PokerGame' object has no attribute 'get_current_player'`

### 检查文件是否存在
```bash
# 检查 AI 决策器
ls -la backend/app/ai/decision_maker.py

# 检查 games.py 是否有最新代码
grep -n "ai_decision_maker" backend/app/routers/games.py

# 检查 games.py 是否有 ai-action 端点
grep -n "ai-action" backend/app/routers/games.py
```

### 更新代码
```bash
git pull origin master
```

**应该看到**：
```
Updating xxxxx..b28f6cc
Fast-forward
 backend/app/routers/games.py          | XX ++++
 backend/app/ai/decision_maker.py      | NEW FILE
 frontend/nginx.conf                   | XX ++--
 ...
```

### 重新构建并启动
```bash
docker-compose down
docker-compose up -d --build
```

**等待 3-5 分钟构建完成**

### 验证更新成功
```bash
# 1. 检查服务状态
docker-compose ps
# 所有服务应该 Up

# 2. 查看后端日志
docker logs backend --tail 50
# 应该看到正常启动，无错误

# 3. 测试 AI 端点
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 4, "small_blind": 10, "big_blind": 20}'

# 获取返回的 game_id，然后：
GAME_ID="替换为上面的game_id"
curl -X POST http://localhost:8000/api/games/$GAME_ID/start
curl -X POST http://localhost:8000/api/games/$GAME_ID/ai-action

# 如果返回 JSON 而不是错误，说明成功！
```

---

## 📊 预期结果

### 更新前（当前状态）：
```bash
$ git log -1 --oneline
xxxxx 旧的提交信息

$ curl -X POST http://localhost:8000/api/games/xxx/ai-action
Internal Server Error  # 500 错误

$ docker logs backend --tail 20
ModuleNotFoundError: No module named 'app.ai.decision_maker'
```

### 更新后（预期状态）：
```bash
$ git log -1 --oneline
b28f6cc 添加 API 测试工具和最终更新总结

$ curl -X POST http://localhost:8000/api/games/xxx/ai-action
{"success":true,"player_id":1,"action":"raise",...}  # 返回 JSON

$ docker logs backend --tail 20
INFO: 127.0.0.1 - "POST /api/games/xxx/ai-action HTTP/1.1" 200 OK
```

---

## 🐛 常见问题

### Q1: git pull 说 "Already up to date"

**可能原因**：您在错误的目录或分支

**解决**：
```bash
# 确认当前目录
pwd
# 应该在 /home/user/dzpoker 或类似路径

# 确认当前分支
git branch
# 应该在 master 或 main

# 查看远程更新
git fetch origin
git log HEAD..origin/master --oneline
# 应该看到新的提交
```

### Q2: docker-compose up 失败

**查看错误**：
```bash
docker-compose logs
```

**常见错误**：
- 端口占用：`docker-compose down` 再试
- 磁盘空间不足：`docker system prune -f`
- 权限问题：`sudo docker-compose up -d`

### Q3: 构建很慢

**正常**！因为需要：
- 重新构建 frontend（npm install + build）
- 重新构建 backend（安装依赖）
- 第一次构建可能需要 5-10 分钟

**加速方法**：
```bash
# 如果只改了 Python 代码，可以只重启 backend
docker-compose restart backend

# 如果改了 nginx 配置，必须重新构建 frontend
docker-compose up -d --build frontend
```

---

## 📞 紧急联系信息

如果上述步骤都执行了但还是 500 错误：

1. **复制完整的后端日志**
   ```bash
   docker logs backend > backend.log
   cat backend.log
   ```

2. **检查代码完整性**
   ```bash
   # 检查所有关键文件
   ls -la backend/app/ai/
   ls -la backend/app/routers/
   cat backend/app/routers/games.py | grep -A 10 "ai-action"
   ```

3. **尝试手动导入测试**
   ```bash
   docker exec -it backend python -c "
   from app.ai.decision_maker import ai_decision_maker
   print('AI decision maker loaded successfully')
   "
   ```

---

## ⏰ 预计时间

- **检查状态**: 1 分钟
- **更新代码**: 30 秒
- **重新构建**: 3-5 分钟
- **验证**: 1 分钟

**总计**: 约 5-7 分钟

---

生成时间: 2026-01-12
紧急程度: 🔴🔴🔴 最高
