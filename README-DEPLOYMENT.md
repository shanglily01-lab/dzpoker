# DZPoker - Amazon Linux 部署指南

## 📋 部署前准备

### 1. 服务器要求
- **操作系统**: Amazon Linux 2 或 Amazon Linux 2023
- **配置要求**:
  - CPU: 2核心以上
  - 内存: 4GB以上
  - 磁盘: 20GB以上可用空间
- **网络**: 公网IP，开放必要端口

### 2. AWS 安全组配置

在AWS控制台配置安全组，开放以下端口:

| 端口 | 协议 | 用途 | 来源 |
|------|------|------|------|
| 22 | TCP | SSH | 您的IP |
| 80 | TCP | HTTP | 0.0.0.0/0 |
| 443 | TCP | HTTPS | 0.0.0.0/0 |
| 3000 | TCP | 前端服务 | 0.0.0.0/0 |
| 8000 | TCP | 后端API | 0.0.0.0/0 |

### 3. SSH连接服务器

```bash
# 使用密钥连接
ssh -i your-key.pem ec2-user@your-server-ip

# 切换到root用户
sudo su -
```

---

## 🚀 部署方式

### 方式一: 自动化部署 (推荐)

**适用场景**: 首次部署，自动安装所有依赖

#### 步骤:

1. **上传部署脚本到服务器**

```bash
# 在本地执行
scp -i your-key.pem deploy-amazon-linux.sh ec2-user@your-server-ip:/home/ec2-user/
```

2. **连接服务器并执行部署**

```bash
# SSH连接服务器
ssh -i your-key.pem ec2-user@your-server-ip

# 赋予执行权限
chmod +x deploy-amazon-linux.sh

# 执行部署脚本 (需要root权限)
sudo bash deploy-amazon-linux.sh
```

3. **按照提示操作**

脚本会自动完成以下任务:
- ✅ 检测系统版本
- ✅ 更新系统软件包
- ✅ 安装Docker和Docker Compose
- ✅ 配置防火墙规则
- ✅ 创建项目目录
- ✅ 配置环境变量
- ✅ 安装Nginx (可选)
- ✅ 启动应用服务
- ✅ 执行健康检查

4. **部署完成后访问**

```
前端: http://YOUR_SERVER_IP:3000
API:  http://YOUR_SERVER_IP:8000/docs
```

---

### 方式二: 快速部署

**适用场景**: 代码已上传，Docker已安装，需要快速启动

#### 步骤:

1. **上传项目代码**

```bash
# 方式A: 使用scp
scp -i your-key.pem -r dzpoker/ ec2-user@your-server-ip:/opt/

# 方式B: 使用Git
ssh -i your-key.pem ec2-user@your-server-ip
cd /opt
git clone https://your-repo/dzpoker.git
```

2. **执行快速部署脚本**

```bash
cd /opt/dzpoker
chmod +x quick-deploy.sh
bash quick-deploy.sh
```

---

### 方式三: Docker Compose 手动部署

**适用场景**: 已熟悉Docker，需要自定义配置

#### 步骤:

1. **安装Docker和Docker Compose**

```bash
# Amazon Linux 2023
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **上传并配置项目**

```bash
cd /opt/dzpoker

# 配置环境变量
cp backend/.env.example backend/.env
vim backend/.env  # 修改配置
```

3. **启动服务**

```bash
# 开发模式
docker-compose up -d

# 生产模式
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔧 配置说明

### 环境变量配置 (backend/.env)

```env
# 应用配置
APP_NAME=德州扑克AI系统
APP_VERSION=1.0.0
DEBUG=false  # 生产环境设置为false

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@db:5432/poker

# Redis配置
REDIS_URL=redis://redis:6379/0

# JWT配置
SECRET_KEY=YOUR_SECRET_KEY  # 使用: openssl rand -hex 32 生成
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 生成安全密钥

```bash
# 生成SECRET_KEY
openssl rand -hex 32

# 生成数据库密码
openssl rand -base64 16
```

---

## 📊 常用管理命令

### Docker Compose 命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f db

# 重启服务
docker-compose restart

# 重启特定服务
docker-compose restart api

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重新构建并启动
docker-compose build --no-cache
docker-compose up -d
```

### 数据库管理

```bash
# 进入数据库
docker-compose exec db psql -U postgres -d poker

# 备份数据库
docker-compose exec db pg_dump -U postgres poker > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
cat backup.sql | docker-compose exec -T db psql -U postgres poker

# 查看数据库大小
docker-compose exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('poker'));"
```

### Redis 管理

```bash
# 连接Redis
docker-compose exec redis redis-cli

# 查看Redis信息
docker-compose exec redis redis-cli info

# 清空Redis缓存
docker-compose exec redis redis-cli FLUSHALL
```

### 系统监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看Docker磁盘使用
docker system df

# 清理未使用的镜像和容器
docker system prune -a
```

---

## 🔒 安全建议

### 1. 修改默认密码

```bash
# 修改数据库密码
docker-compose exec db psql -U postgres -c "ALTER USER postgres PASSWORD 'new_password';"

# 更新.env中的DATABASE_URL
vim backend/.env
```

### 2. 配置防火墙

```bash
# 如果使用Nginx反向代理，关闭直接端口访问
sudo firewall-cmd --permanent --remove-port=3000/tcp
sudo firewall-cmd --permanent --remove-port=8000/tcp
sudo firewall-cmd --reload
```

### 3. 启用HTTPS (使用Let's Encrypt)

```bash
# 安装certbot
sudo yum install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 0 * * * certbot renew --quiet
```

### 4. 限制SSH访问

```bash
# 编辑SSH配置
sudo vim /etc/ssh/sshd_config

# 修改以下配置
PermitRootLogin no
PasswordAuthentication no
Port 2222  # 修改默认端口

# 重启SSH服务
sudo systemctl restart sshd
```

---

## 🐛 故障排查

### 问题0: Docker安装时依赖冲突 ⚠️ 常见问题

**错误信息:**
```
Error:
 Problem: package docker-xyz conflicts with podman-xyz
 - cannot install both
(try to add '--allowerasing' to command line to replace conflicting packages)
```

**原因:** Amazon Linux 系统预装的 podman 与 Docker 有包冲突

**解决方案1: 使用修复脚本 (推荐)**

```bash
# 下载并运行修复脚本
chmod +x fix-docker-conflicts.sh
sudo bash fix-docker-conflicts.sh
```

修复脚本会自动尝试5种方案：
1. 使用 `--allowerasing` 替换冲突包
2. 使用 `--skip-broken` 跳过冲突包
3. 清理缓存后重试
4. 使用Docker官方仓库
5. 全部依次尝试直到成功

**解决方案2: 手动修复**

```bash
# 方法A: 允许删除冲突包 (推荐)
sudo yum install -y docker --allowerasing

# 方法B: 跳过冲突包
sudo yum install -y docker --skip-broken

# 方法C: 先卸载冲突包
sudo yum remove -y podman buildah
sudo yum install -y docker

# 方法D: 使用Docker官方仓库
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
```

**验证安装:**

```bash
docker --version
sudo systemctl start docker
sudo docker run --rm hello-world
```

---

### 问题1: Docker服务无法启动

```bash
# 检查Docker状态
sudo systemctl status docker

# 启动Docker
sudo systemctl start docker

# 查看Docker日志
sudo journalctl -u docker -n 50
```

### 问题2: 容器启动失败

```bash
# 查看容器日志
docker-compose logs api

# 查看容器详情
docker inspect poker-api

# 进入容器排查
docker-compose exec api bash
```

### 问题3: 数据库连接失败

```bash
# 检查数据库是否就绪
docker-compose exec db pg_isready -U postgres

# 检查数据库日志
docker-compose logs db

# 检查网络连接
docker-compose exec api ping db
```

### 问题4: 端口被占用

```bash
# 查看端口占用
sudo netstat -tlnp | grep 8000

# 杀死占用进程
sudo kill -9 PID
```

### 问题5: 磁盘空间不足

```bash
# 清理Docker资源
docker system prune -a --volumes

# 清理日志文件
sudo find /var/log -type f -name "*.log" -mtime +7 -delete
```

---

## 📈 性能优化

### 1. 调整Docker资源限制

修改 `docker-compose.prod.yml`:

```yaml
api:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

### 2. 配置PostgreSQL性能参数

```bash
# 进入数据库
docker-compose exec db psql -U postgres

# 调整配置
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

# 重启数据库
docker-compose restart db
```

### 3. 启用Gunicorn多进程

修改启动命令:

```bash
# 根据CPU核心数调整worker数量
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 🔄 更新部署

### 方式一: 不停机更新 (推荐)

```bash
# 拉取最新代码
cd /opt/dzpoker
git pull

# 重新构建
docker-compose build api frontend

# 滚动更新
docker-compose up -d --no-deps --build api
docker-compose up -d --no-deps --build frontend
```

### 方式二: 完全重启

```bash
cd /opt/dzpoker
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 技术支持

如遇到问题，请检查:
1. 系统日志: `journalctl -xe`
2. Docker日志: `docker-compose logs -f`
3. 应用日志: 查看容器内日志文件

---

**祝您部署顺利！** 🎉
