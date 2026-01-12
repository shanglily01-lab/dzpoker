# 🔧 故障排查指南 (Troubleshooting Guide)

> 遇到问题？这里有完整的排查步骤和解决方案

---

## 📋 目录

- [快速诊断](#快速诊断)
- [常见错误](#常见错误)
- [服务状态检查](#服务状态检查)
- [网络问题](#网络问题)
- [数据库问题](#数据库问题)
- [前端问题](#前端问题)
- [性能问题](#性能问题)

---

## 🚀 快速诊断

### 1. 检查所有服务状态

```bash
cd /opt/dzpoker  # 或你的项目目录
docker-compose ps
```

**预期输出**：所有服务应该显示 `Up` 状态

```
NAME                COMMAND                  SERVICE             STATUS
poker-api           "uvicorn app.main:ap…"   api                 Up (healthy)
poker-frontend      "docker-entrypoint.s…"   frontend            Up
poker-db            "docker-entrypoint.s…"   db                  Up (healthy)
poker-redis         "docker-entrypoint.s…"   redis               Up
```

### 2. 快速健康检查

```bash
# 检查后端API
curl http://localhost:8000/docs

# 检查前端
curl http://localhost:3000

# 检查数据库
docker-compose exec db pg_isready -U postgres

# 检查Redis
docker-compose exec redis redis-cli ping
```

### 3. 查看最近的错误日志

```bash
# 所有服务日志（最近100行）
docker-compose logs --tail=100

# 后端API日志
docker-compose logs --tail=50 api

# 前端日志
docker-compose logs --tail=50 frontend
```

---

## ❌ 常见错误

### 错误1: 502 Bad Gateway

**症状**：
- 前端显示 "Failed to load resource: 502 Bad Gateway"
- 无法访问 http://localhost:8000/docs
- API请求全部失败

**可能原因**：
1. 后端容器未启动
2. 后端容器启动失败
3. 后端进程崩溃
4. 数据库连接失败

**排查步骤**：

```bash
# 1. 检查后端容器状态
docker-compose ps api

# 2. 查看后端日志
docker-compose logs api

# 3. 检查数据库连接
docker-compose exec db pg_isready -U postgres

# 4. 检查网络连接
docker-compose exec api ping db
```

**解决方案**：

#### 方案A: 重启后端服务
```bash
cd /opt/dzpoker
docker-compose restart api

# 等待10秒
sleep 10

# 检查状态
docker-compose ps api
curl http://localhost:8000/docs
```

#### 方案B: 重建后端容器
```bash
cd /opt/dzpoker
docker-compose stop api
docker-compose rm -f api
docker-compose up -d api

# 查看启动日志
docker-compose logs -f api
```

#### 方案C: 完全重启
```bash
cd /opt/dzpoker
docker-compose down
docker-compose up -d

# 等待所有服务启动
sleep 15
docker-compose ps
```

#### 方案D: 检查环境变量
```bash
# 查看后端环境变量
docker-compose exec api env | grep DATABASE

# 如果DATABASE_URL不正确，修改backend/.env
vim backend/.env

# 然后重启
docker-compose restart api
```

#### 方案E: 代码更新后重新构建
```bash
# 如果刚更新了代码，需要重新构建后端
cd /opt/dzpoker

# 拉取最新代码
git pull origin master

# 使用更新脚本（推荐）
chmod +x update-backend.sh
bash update-backend.sh

# 或手动执行
docker-compose stop api
docker-compose build --no-cache api
docker-compose up -d api

# 等待启动
sleep 10

# 测试新端点
curl http://localhost:8000/api/games/stats
curl http://localhost:8000/api/games/list
```

---

### 错误2: 数据库连接失败

**症状**：
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**排查步骤**：

```bash
# 1. 检查数据库容器
docker-compose ps db

# 2. 检查数据库是否ready
docker-compose exec db pg_isready -U postgres

# 3. 查看数据库日志
docker-compose logs db

# 4. 尝试连接数据库
docker-compose exec db psql -U postgres -d poker
```

**解决方案**：

```bash
# 重启数据库
docker-compose restart db

# 等待数据库启动
sleep 10

# 验证
docker-compose exec db pg_isready -U postgres

# 重启后端以重新连接
docker-compose restart api
```

---

### 错误3: 端口被占用

**症状**：
```
ERROR: for api  Cannot start service api: Ports are not available
```

**排查步骤**：

```bash
# Linux/Mac
sudo lsof -i :8000
sudo lsof -i :3000

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

**解决方案**：

```bash
# 方案A: 停止占用端口的进程
# Linux/Mac
sudo kill -9 <PID>

# Windows
taskkill /PID <PID> /F

# 方案B: 修改docker-compose.yml中的端口映射
# 将 "8000:8000" 改为 "8001:8000"
# 将 "3000:3000" 改为 "3001:3000"
```

---

### 错误4: 前端无法连接后端

**症状**：
- 前端页面打开正常
- 但所有API请求失败
- 浏览器控制台显示CORS错误或连接超时

**排查步骤**：

```bash
# 1. 检查后端是否运行
curl http://localhost:8000/docs

# 2. 检查前端配置
cat frontend/vite.config.js | grep proxy

# 3. 检查网络
docker-compose exec frontend ping api
```

**解决方案**：

```bash
# 1. 确保后端正常运行
docker-compose restart api

# 2. 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete

# 3. 重启前端
docker-compose restart frontend

# 4. 检查防火墙
# Linux
sudo iptables -L | grep 8000

# Windows
netsh advfirewall firewall show rule name=all | findstr 8000
```

---

### 错误5: Redis连接失败

**症状**：
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**解决方案**：

```bash
# 检查Redis
docker-compose ps redis
docker-compose exec redis redis-cli ping

# 重启Redis
docker-compose restart redis

# 重启依赖Redis的服务
docker-compose restart api
```

---

## 🔍 服务状态检查

### 完整健康检查脚本

创建文件 `check-health.sh`:

```bash
#!/bin/bash

echo "=== DZPoker 健康检查 ==="
echo ""

# 1. Docker服务
echo "[1/8] 检查Docker服务..."
if docker ps > /dev/null 2>&1; then
    echo "✅ Docker运行正常"
else
    echo "❌ Docker未运行"
    exit 1
fi

# 2. 容器状态
echo ""
echo "[2/8] 检查容器状态..."
docker-compose ps

# 3. 后端API
echo ""
echo "[3/8] 检查后端API..."
if curl -sf http://localhost:8000/docs > /dev/null; then
    echo "✅ 后端API正常"
else
    echo "❌ 后端API异常"
fi

# 4. 前端
echo ""
echo "[4/8] 检查前端..."
if curl -sf http://localhost:3000 > /dev/null; then
    echo "✅ 前端正常"
else
    echo "❌ 前端异常"
fi

# 5. 数据库
echo ""
echo "[5/8] 检查数据库..."
if docker-compose exec -T db pg_isready -U postgres 2>/dev/null | grep -q "accepting connections"; then
    echo "✅ 数据库正常"
else
    echo "❌ 数据库异常"
fi

# 6. Redis
echo ""
echo "[6/8] 检查Redis..."
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis正常"
else
    echo "❌ Redis异常"
fi

# 7. 磁盘空间
echo ""
echo "[7/8] 检查磁盘空间..."
df -h | grep -E "Filesystem|/$"

# 8. 内存使用
echo ""
echo "[8/8] 检查内存使用..."
free -h

echo ""
echo "=== 健康检查完成 ==="
```

使用方法：
```bash
chmod +x check-health.sh
./check-health.sh
```

---

## 🌐 网络问题

### 容器间网络不通

**检查容器网络**：

```bash
# 查看网络
docker network ls

# 查看容器IP
docker-compose exec api hostname -i
docker-compose exec db hostname -i

# 测试连通性
docker-compose exec api ping db
docker-compose exec frontend ping api
```

**重建网络**：

```bash
docker-compose down
docker network prune
docker-compose up -d
```

---

## 🗄️ 数据库问题

### 重置数据库

⚠️ **警告：会删除所有数据！**

```bash
# 1. 停止服务
docker-compose stop api

# 2. 删除数据库数据
docker-compose down -v  # 删除所有卷

# 3. 重新启动
docker-compose up -d

# 4. 等待初始化
sleep 15

# 5. 检查
docker-compose exec db psql -U postgres -d poker -c "\dt"
```

### 手动运行数据库迁移

```bash
# 进入后端容器
docker-compose exec api bash

# 运行迁移
alembic upgrade head

# 退出
exit
```

### 查看数据库表

```bash
# 连接数据库
docker-compose exec db psql -U postgres -d poker

# 查看表
\dt

# 查看表结构
\d players
\d games

# 查询数据
SELECT * FROM players LIMIT 10;

# 退出
\q
```

---

## 🎨 前端问题

### 前端无法加载

**清除缓存并重建**：

```bash
# 停止前端
docker-compose stop frontend

# 删除前端容器
docker-compose rm -f frontend

# 重建前端
docker-compose build --no-cache frontend

# 启动前端
docker-compose up -d frontend

# 查看日志
docker-compose logs -f frontend
```

### 前端构建失败

**检查Node版本和依赖**：

```bash
# 进入前端容器
docker-compose exec frontend sh

# 检查Node版本
node --version
npm --version

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 退出
exit
```

---

## ⚡ 性能问题

### 容器占用资源过高

**查看资源使用**：

```bash
# 实时监控
docker stats

# 查看单个容器
docker stats poker-api
```

**优化方案**：

1. **限制容器资源**（编辑 docker-compose.yml）:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

2. **清理无用资源**:
```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理未使用的网络
docker network prune

# 一键清理所有
docker system prune -a --volumes
```

---

## 📞 获取帮助

### 收集诊断信息

如果问题无法解决，请收集以下信息并提交Issue：

```bash
# 1. 系统信息
uname -a
docker --version
docker-compose --version

# 2. 容器状态
docker-compose ps > diagnostic.txt

# 3. 所有日志
docker-compose logs > logs.txt

# 4. 网络信息
docker network inspect dzpoker_default > network.txt

# 5. 打包
tar -czf diagnostic.tar.gz diagnostic.txt logs.txt network.txt
```

### 联系方式

- GitHub Issues: https://github.com/your-repo/dzpoker/issues
- 邮件: your-email@example.com

---

## 🔄 常用修复命令速查

```bash
# 快速重启所有服务
docker-compose restart

# 重建并重启所有服务
docker-compose down && docker-compose up -d

# 仅重启后端
docker-compose restart api

# 仅重启前端
docker-compose restart frontend

# 查看实时日志
docker-compose logs -f

# 查看最近100行日志
docker-compose logs --tail=100

# 进入后端容器
docker-compose exec api bash

# 进入数据库
docker-compose exec db psql -U postgres -d poker

# 清理所有并重新开始
docker-compose down -v
docker system prune -a
docker-compose up -d
```

---

**最后更新**: 2026-01-12
**维护者**: DZPoker开发团队
