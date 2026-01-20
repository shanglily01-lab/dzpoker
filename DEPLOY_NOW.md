# 🚀 立即部署（3条命令）

## 修复内容
- ✅ **VARCHAR 长度限制** - 修复 small_blind/big_blind 保存错误
- ✅ **Redis 游戏持久化** - 容器重启后游戏不丢失
- ✅ **导入错误修复** - 修复 simulation.py 导入问题

---

## Linux 服务器执行

```bash
# 1. 拉取代码
cd /path/to/dzpoker && git pull

# 2. 快速部署（10秒）
chmod +x quick-update.sh && ./quick-update.sh

# 3. 验证部署（可选）
chmod +x verify-backend.sh && ./verify-backend.sh
```

---

## 预期结果

### ✅ 成功标志

```
✅ Redis 游戏存储初始化成功: redis://redis:6379/0
✅ 数据库初始化完成
✅ Redis连接成功
INFO:     Application startup complete.
```

### ✅ API 测试成功

```
✅ API 正常响应 (HTTP 200)
   创建的游戏 ID: a1b2c3d4
```

---

## 测试步骤

### 1. 清除浏览器缓存
**重要！** 旧游戏 ID 已失效

- Chrome: Ctrl+Shift+Delete
- 或使用无痕模式：Ctrl+Shift+N

### 2. 访问首页
```
http://your-server:3000
```

### 3. 开始新游戏
- 点击"开始游戏"
- 等待游戏完成
- 不应该有 404 或 500 错误

### 4. 测试容器重启（验证 Redis 持久化）
```bash
# 重启后端
docker-compose restart api

# 刷新浏览器
# 游戏应该继续，不会 404
```

### 5. 查看数据分析
```
http://your-server:3000/analytics
```

- 点击游戏详情
- 展开玩家手牌
- 查看动作记录（应包含小盲注、大盲注等）

---

## 如果遇到问题

### 问题：ImportError
```bash
# 解决：拉取最新代码
git pull
docker-compose restart api
```

### 问题：Redis 连接失败
```bash
# 检查 Redis 容器
docker-compose ps redis

# 启动 Redis
docker-compose up -d redis
docker-compose restart api
```

### 问题：仍然 404
**原因**：浏览器缓存了旧游戏 ID

**解决**：清除浏览器缓存或无痕模式

### 问题：仍然 500（finish API）
**原因**：数据库迁移未成功

**解决**：
```bash
# 手动执行迁移
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);"
docker-compose restart api
```

---

## 完整日志查看

```bash
# 后端日志
docker-compose logs -f api

# 数据库日志
docker logs poker-db

# Redis 日志
docker logs poker-redis
```

---

## 文件说明

| 文件 | 用途 |
|------|------|
| [quick-update.sh](quick-update.sh) | 快速部署（10秒） |
| [verify-backend.sh](verify-backend.sh) | 验证部署 |
| [diagnose.sh](diagnose.sh) | 诊断问题 |
| [force-restart.sh](force-restart.sh) | 强制重启 |
| [FINAL_DEPLOYMENT.md](FINAL_DEPLOYMENT.md) | 完整文档 |

---

## 一键部署

```bash
cd /path/to/dzpoker && git pull && chmod +x quick-update.sh && ./quick-update.sh && chmod +x verify-backend.sh && ./verify-backend.sh
```

**完成！** 🎉
