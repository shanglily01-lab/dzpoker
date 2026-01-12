# ⚡ 快速修复：数据库密码错误

## 问题

```
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "postgres"
```

## 原因

数据库容器保留了旧的密码配置，与当前 docker-compose.yml 中的密码不匹配。

---

## 🚀 快速解决方案

在 EC2 服务器上执行以下命令：

```bash
# 1. 进入项目目录
cd /opt/dzpoker

# 2. 停止所有服务
sudo docker-compose down

# 3. 删除数据库卷（会清空所有数据）
sudo docker volume rm dzpoker_postgres_data

# 4. 重新启动所有服务
sudo docker-compose up -d

# 5. 等待30秒让服务完全启动
sleep 30

# 6. 检查服务状态
sudo docker-compose ps
```

---

## ✅ 验证修复

### 1. 检查容器状态

```bash
sudo docker-compose ps
```

所有容器应该显示 `Up` 状态：

```
NAME             STATUS
poker-api        Up
poker-db         Up (healthy)
poker-redis      Up
poker-frontend   Up
```

### 2. 检查后端日志

```bash
sudo docker-compose logs --tail=50 api
```

应该看到：

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**不应该再看到** `InvalidPasswordError` 错误。

### 3. 测试 API 端点

```bash
# 测试统计端点
curl http://localhost:8000/api/games/stats

# 预期输出:
{
  "total_games": 0,
  "active_games": 0,
  "finished_games": 0,
  "total_players": 0,
  "total_hands": 0,
  "total_pot": 0
}
```

```bash
# 测试列表端点
curl http://localhost:8000/api/games/list

# 预期输出:
[]
```

### 4. 测试前端

访问: http://13.212.252.171:3000

Dashboard 应该能正常显示，不再出现 502 错误。

---

## 📝 使用自动化脚本（可选）

```bash
cd /opt/dzpoker

# 拉取最新代码（包含修复脚本）
sudo git pull origin master

# 运行修复脚本
sudo chmod +x fix-database-password.sh
sudo bash fix-database-password.sh
```

脚本会自动完成所有步骤并验证修复结果。

---

## 🔍 如果仍然失败

### 检查数据库连接

```bash
# 进入数据库容器
sudo docker-compose exec db psql -U postgres -d poker

# 如果成功，应该看到 postgres 提示符:
poker=#

# 退出
\q
```

### 检查环境变量

```bash
# 查看后端容器的环境变量
sudo docker-compose exec api env | grep DATABASE

# 应该输出:
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/poker
```

### 查看完整日志

```bash
# 查看所有服务日志
sudo docker-compose logs

# 只看后端日志
sudo docker-compose logs -f api
```

### 完全重建

如果以上都不行，尝试完全重建：

```bash
cd /opt/dzpoker

# 停止并删除所有容器和卷
sudo docker-compose down -v

# 删除镜像
sudo docker rmi dzpoker-api dzpoker-frontend

# 重新构建和启动
sudo docker-compose build --no-cache
sudo docker-compose up -d

# 等待启动
sleep 30

# 检查状态
sudo docker-compose ps
sudo docker-compose logs api
```

---

## 💡 为什么会出现这个问题？

1. **首次部署**: 数据库使用了不同的密码
2. **更新配置**: docker-compose.yml 中修改了密码，但数据库卷保留旧密码
3. **环境不一致**: 开发环境和生产环境密码不同

## 🛡️ 预防措施

### 1. 生产环境使用强密码

编辑 `docker-compose.yml`:

```yaml
db:
  environment:
    POSTGRES_PASSWORD: your-strong-password-here  # 改成强密码

api:
  environment:
    DATABASE_URL: postgresql+asyncpg://postgres:your-strong-password-here@db:5432/poker
```

### 2. 使用环境变量文件

创建 `.env` 文件:

```bash
POSTGRES_PASSWORD=your-strong-password
DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@db:5432/poker
```

然后在 `docker-compose.yml` 中引用:

```yaml
db:
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

api:
  environment:
    DATABASE_URL: ${DATABASE_URL}
```

### 3. 定期备份数据库

```bash
# 备份
sudo docker-compose exec db pg_dump -U postgres poker > backup-$(date +%Y%m%d).sql

# 恢复
sudo docker-compose exec -T db psql -U postgres poker < backup-20260112.sql
```

---

## 📞 需要更多帮助？

- 完整故障排查指南: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 502 错误修复: [FIX-502-ERROR.md](FIX-502-ERROR.md)
- 快速开始: [QUICK-START.md](QUICK-START.md)

---

**创建时间**: 2026-01-12
**问题**: Database password authentication failed
**解决方案**: Reset database volume
