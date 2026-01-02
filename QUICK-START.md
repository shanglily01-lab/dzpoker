# 🚀 DZPoker - Amazon Linux 快速部署指南

> 5分钟完成部署！

---

## 📦 部署文件说明

本项目提供了以下部署文件：

| 文件名 | 用途 | 适用场景 |
|--------|------|----------|
| `deploy-amazon-linux.sh` | 全自动部署脚本 | 首次部署，自动安装所有依赖 |
| `quick-deploy.sh` | 快速部署脚本 | Docker已安装，快速启动应用 |
| `docker-compose.yml` | 开发环境配置 | 本地开发和测试 |
| `docker-compose.prod.yml` | 生产环境配置 | 生产环境部署 |
| `README-DEPLOYMENT.md` | 详细部署文档 | 完整部署指南和故障排查 |
| `DEPLOYMENT-CHECKLIST.md` | 部署检查清单 | 逐步检查部署流程 |

---

## ⚡ 三种部署方式

### 方式一: 一键自动部署 (推荐新手)

**适用场景**: 全新服务器，什么都没装

```bash
# 1. 上传部署脚本
scp -i your-key.pem deploy-amazon-linux.sh ec2-user@YOUR_IP:/home/ec2-user/

# 2. 连接服务器
ssh -i your-key.pem ec2-user@YOUR_IP

# 3. 执行部署
chmod +x deploy-amazon-linux.sh
sudo bash deploy-amazon-linux.sh
```

**脚本会自动完成:**
- ✅ 检测系统版本
- ✅ 安装Docker和Docker Compose
- ✅ 配置防火墙
- ✅ 下载/上传代码
- ✅ 配置环境变量
- ✅ 启动所有服务
- ✅ 健康检查

**部署时间**: 约10-15分钟

---

### 方式二: 快速部署 (推荐老手)

**适用场景**: Docker已安装，代码已上传

```bash
# 1. 上传代码
scp -i your-key.pem -r dzpoker/ ec2-user@YOUR_IP:/opt/

# 2. 连接服务器
ssh -i your-key.pem ec2-user@YOUR_IP

# 3. 快速部署
cd /opt/dzpoker
chmod +x quick-deploy.sh
bash quick-deploy.sh
```

**部署时间**: 约3-5分钟

---

### 方式三: 手动部署 (推荐专家)

**适用场景**: 需要自定义配置

```bash
# 1. 安装Docker (如未安装)
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# 2. 安装Docker Compose (如未安装)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 上传代码
cd /opt
git clone https://your-repo/dzpoker.git
cd dzpoker

# 4. 配置环境
cp backend/.env.example backend/.env
vim backend/.env  # 修改配置

# 5. 启动服务
docker-compose up -d

# 6. 查看状态
docker-compose ps
docker-compose logs -f
```

**部署时间**: 约5-10分钟

---

## 🔑 部署前准备

### 1. AWS EC2 实例

- **实例类型**: t3.medium 或更高 (2核4GB)
- **系统**: Amazon Linux 2 或 Amazon Linux 2023
- **磁盘**: 20GB+
- **网络**: 弹性IP (可选)

### 2. 安全组规则

在AWS控制台配置安全组，开放端口:

```
SSH:      22   (仅你的IP)
HTTP:     80   (0.0.0.0/0)
HTTPS:    443  (0.0.0.0/0)
Frontend: 3000 (0.0.0.0/0)
API:      8000 (0.0.0.0/0)
```

### 3. SSH密钥

下载并保存 `.pem` 密钥文件，设置权限:

```bash
chmod 400 your-key.pem
```

---

## 📋 部署流程

### Step 1: 连接服务器

```bash
ssh -i your-key.pem ec2-user@YOUR_SERVER_IP
```

### Step 2: 选择部署方式

根据实际情况选择上述三种方式之一

### Step 3: 验证部署

```bash
# 查看服务状态
cd /opt/dzpoker
docker-compose ps

# 应该看到4个服务都是 Up 状态:
# poker-api        Up (healthy)
# poker-frontend   Up
# poker-db         Up (healthy)
# poker-redis      Up
```

### Step 4: 访问应用

在浏览器中访问:

```
前端: http://YOUR_SERVER_IP:3000
API:  http://YOUR_SERVER_IP:8000/docs
```

---

## ✅ 验证清单

部署完成后，检查以下内容:

- [ ] 所有Docker容器运行正常
- [ ] 前端页面可以正常访问
- [ ] API文档可以正常访问
- [ ] 用户注册功能正常
- [ ] 用户登录功能正常
- [ ] 创建游戏功能正常

---

## 🔧 常用命令

### 🔄 快速重启 (推荐)

使用重启脚本，提供7种重启方式：

```bash
cd /opt/dzpoker
chmod +x restart.sh
bash restart.sh
```

**重启选项:**
1. 重启所有服务 (推荐) - 快速重启所有容器
2. 仅重启后端 API - 后端代码更新后使用
3. 仅重启前端 - 前端代码更新后使用
4. 仅重启数据库 - 数据库配置修改后使用
5. 仅重启Redis - Redis配置修改后使用
6. 完全重启 - 停止→删除→重建 (解决复杂问题)
7. 快速重启 - 不重新构建镜像

### 📋 基础命令

```bash
# 进入项目目录
cd /opt/dzpoker

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose logs -f redis

# 手动重启服务
docker-compose restart              # 重启所有
docker-compose restart api          # 重启后端
docker-compose restart frontend     # 重启前端

# 停止服务
docker-compose stop                 # 停止所有
docker-compose down                 # 停止并删除容器

# 启动服务
docker-compose start                # 启动所有
docker-compose up -d                # 创建并启动

# 重新构建
docker-compose build --no-cache
docker-compose up -d

# 备份数据库
docker-compose exec db pg_dump -U postgres poker > backup.sql

# 进入容器
docker-compose exec api bash
docker-compose exec db psql -U postgres -d poker
```

---

## 🐛 故障排查

### 问题1: 端口无法访问

**检查AWS安全组:**
1. 登录AWS控制台
2. EC2 → 安全组
3. 确认已开放 80, 443, 3000, 8000 端口

**检查防火墙:**
```bash
sudo firewall-cmd --list-all
```

### 问题2: 容器启动失败

**查看日志:**
```bash
docker-compose logs api
docker-compose logs frontend
docker-compose logs db
```

**重新启动:**
```bash
docker-compose down
docker-compose up -d
```

### 问题3: 数据库连接失败

**检查数据库:**
```bash
docker-compose exec db pg_isready -U postgres
```

**检查配置:**
```bash
cat backend/.env | grep DATABASE_URL
```

### 问题4: 磁盘空间不足

**清理Docker:**
```bash
docker system prune -a
docker volume prune
```

---

## 🔒 安全建议

### 1. 修改默认密码

```bash
# 生成强密码
openssl rand -base64 16

# 修改数据库密码
docker-compose exec db psql -U postgres -c "ALTER USER postgres PASSWORD 'NEW_PASSWORD';"

# 更新 backend/.env
vim backend/.env
# 修改 DATABASE_URL 中的密码

# 重启
docker-compose restart api
```

### 2. 配置HTTPS

```bash
# 安装certbot
sudo yum install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com
```

### 3. 限制SSH访问

在AWS安全组中，将SSH端口(22)限制为仅你的IP可访问

---

## 📊 性能优化

### 1. 调整Worker数量

编辑 `docker-compose.yml`:

```yaml
command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

根据CPU核心数调整 `-w` 参数 (建议: CPU核心数 × 2 + 1)

### 2. 配置数据库连接池

编辑 `backend/.env`:

```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

### 3. 启用Redis持久化

Redis默认已启用AOF持久化

---

## 🔄 更新部署

### 不停机更新

```bash
cd /opt/dzpoker
git pull
docker-compose build api frontend
docker-compose up -d --no-deps --build api
docker-compose up -d --no-deps --build frontend
```

### 完全重启更新

```bash
cd /opt/dzpoker
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 获取帮助

### 查看日志

```bash
# 应用日志
docker-compose logs -f

# 系统日志
journalctl -xe

# Nginx日志
sudo tail -f /var/log/nginx/error.log
```

### 健康检查

```bash
# API健康检查
curl http://localhost:8000/health

# 数据库检查
docker-compose exec db pg_isready -U postgres

# Redis检查
docker-compose exec redis redis-cli ping
```

---

## 🎉 部署成功！

访问地址:
- **前端**: http://YOUR_IP:3000
- **API**: http://YOUR_IP:8000
- **文档**: http://YOUR_IP:8000/docs

---

## 📚 更多文档

- [详细部署文档](README-DEPLOYMENT.md) - 完整的部署指南
- [部署检查清单](DEPLOYMENT-CHECKLIST.md) - 逐步检查清单
- [系统架构设计](系统架构设计.md) - 架构说明
- [原始部署文档](DEPLOY.md) - 通用部署指南

---

**祝您部署顺利！** 🚀
