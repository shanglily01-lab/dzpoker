# 部署指南

## 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 内存: 4GB+
- 磁盘: 10GB+

## 方式一: Docker Compose 部署 (推荐)

### 1. 上传代码到服务器

```bash
# 方式A: 使用scp上传
scp -r dzpoker/ user@your-server:/home/user/

# 方式B: 使用git (如果已推送到仓库)
git clone https://your-repo/dzpoker.git
```

### 2. 进入项目目录

```bash
cd dzpoker
```

### 3. 创建环境配置文件

```bash
cp backend/.env.example backend/.env

# 编辑配置 (修改密码等)
vim backend/.env
```

### 4. 启动服务

```bash
# 启动所有服务 (后台运行)
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 访问服务

- 前端: http://服务器IP:3000
- 后端API: http://服务器IP:8000
- API文档: http://服务器IP:8000/docs

---

## 方式二: 手动部署 (不使用Docker)

### 1. 安装依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm postgresql redis-server

# CentOS
sudo yum install -y python311 nodejs npm postgresql-server redis
```

### 2. 配置PostgreSQL

```bash
# 启动PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
```

```sql
CREATE DATABASE poker;
CREATE USER poker_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE poker TO poker_user;
\q
```

### 3. 配置Redis

```bash
sudo systemctl start redis
sudo systemctl enable redis
```

### 4. 部署后端

```bash
cd backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL="postgresql+asyncpg://poker_user:your_password@localhost:5432/poker"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key-here"

# 启动服务 (开发模式)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 或使用gunicorn (生产模式)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 5. 部署前端

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 使用nginx托管 (见下方nginx配置)
```

### 6. 配置Nginx

```bash
sudo apt install -y nginx
sudo vim /etc/nginx/sites-available/poker
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /home/user/dzpoker/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket代理
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/poker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 方式三: 使用Systemd管理服务

### 创建后端服务

```bash
sudo vim /etc/systemd/system/poker-api.service
```

```ini
[Unit]
Description=Poker API Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/dzpoker/backend
Environment="DATABASE_URL=postgresql+asyncpg://poker_user:password@localhost:5432/poker"
Environment="REDIS_URL=redis://localhost:6379/0"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/home/user/dzpoker/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable poker-api
sudo systemctl start poker-api
sudo systemctl status poker-api
```

---

## 常用命令

### Docker Compose

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 重启
docker-compose restart

# 查看日志
docker-compose logs -f api      # 后端日志
docker-compose logs -f frontend # 前端日志
docker-compose logs -f db       # 数据库日志

# 重新构建
docker-compose build --no-cache
docker-compose up -d

# 进入容器
docker-compose exec api bash
docker-compose exec db psql -U postgres -d poker
```

### 数据库操作

```bash
# 进入PostgreSQL
docker-compose exec db psql -U postgres -d poker

# 备份
docker-compose exec db pg_dump -U postgres poker > backup.sql

# 恢复
cat backup.sql | docker-compose exec -T db psql -U postgres -d poker
```

---

## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 3000 | Vue前端 |
| 后端 | 8000 | FastAPI |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |

---

## 防火墙配置

```bash
# Ubuntu UFW
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 3000
sudo ufw allow 8000

# CentOS firewalld
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## 故障排查

### 1. 数据库连接失败

```bash
# 检查PostgreSQL状态
docker-compose logs db

# 确认数据库已创建
docker-compose exec db psql -U postgres -l
```

### 2. Redis连接失败

```bash
# 检查Redis状态
docker-compose exec redis redis-cli ping
# 应返回 PONG
```

### 3. 前端无法访问API

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查nginx配置
nginx -t
```

### 4. 查看详细日志

```bash
# 后端日志
docker-compose logs -f api --tail=100

# 全部日志
docker-compose logs -f
```
