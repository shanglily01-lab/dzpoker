# DZPoker 部署检查清单

## 📋 部署前检查

### ✅ AWS 准备工作

- [ ] 创建 EC2 实例
  - [ ] 实例类型: t3.medium 或更高 (2核4GB)
  - [ ] 操作系统: Amazon Linux 2 或 Amazon Linux 2023
  - [ ] 磁盘空间: 至少 20GB
  - [ ] 分配弹性IP (可选，用于固定IP)

- [ ] 配置安全组规则
  - [ ] SSH (22) - 仅允许您的IP访问
  - [ ] HTTP (80) - 0.0.0.0/0
  - [ ] HTTPS (443) - 0.0.0.0/0
  - [ ] 前端 (3000) - 0.0.0.0/0
  - [ ] API (8000) - 0.0.0.0/0

- [ ] 下载并保存 SSH 密钥 (.pem文件)

### ✅ 本地准备工作

- [ ] 准备项目代码
  - [ ] 确保代码完整无误
  - [ ] 检查 docker-compose.yml 配置
  - [ ] 检查 Dockerfile 配置

- [ ] 准备部署脚本
  - [ ] deploy-amazon-linux.sh
  - [ ] quick-deploy.sh
  - [ ] docker-compose.prod.yml

---

## 🚀 部署步骤

### 第一步: 连接服务器

```bash
# 设置密钥权限
chmod 400 your-key.pem

# SSH连接
ssh -i your-key.pem ec2-user@YOUR_SERVER_IP
```

- [ ] 成功连接到服务器
- [ ] 切换到root用户: `sudo su -`

---

### 第二步: 上传部署文件

**方式A: 上传整个项目**

```bash
# 在本地执行
scp -i your-key.pem -r dzpoker/ ec2-user@YOUR_SERVER_IP:/home/ec2-user/
```

**方式B: 只上传部署脚本**

```bash
# 在本地执行
scp -i your-key.pem deploy-amazon-linux.sh ec2-user@YOUR_SERVER_IP:/home/ec2-user/
```

**方式C: 使用Git**

```bash
# 在服务器执行
cd /opt
git clone https://your-repo/dzpoker.git
```

- [ ] 代码已成功上传到服务器

---

### 第三步: 执行部署脚本

**如果使用自动化部署脚本:**

```bash
chmod +x deploy-amazon-linux.sh
sudo bash deploy-amazon-linux.sh
```

脚本会询问以下问题，请做好准备:

1. **是否继续?** - 如果系统不是Amazon Linux会询问
2. **项目部署目录** - 默认 `/opt/dzpoker`，可自定义
3. **代码获取方式** - Git克隆/手动上传/跳过
4. **Git仓库地址** - 如果选择Git方式
5. **是否安装Nginx** - 推荐选择 `y`
6. **是否创建系统服务** - 推荐选择 `y`

- [ ] 脚本执行完成，无错误
- [ ] 记录生成的数据库密码

---

**如果使用快速部署脚本:**

```bash
cd /opt/dzpoker
chmod +x quick-deploy.sh
bash quick-deploy.sh
```

- [ ] 脚本执行完成，无错误

---

### 第四步: 验证部署

#### 检查服务状态

```bash
cd /opt/dzpoker
docker-compose ps
```

预期输出: 所有服务状态为 `Up`

- [ ] poker-api: Up
- [ ] poker-frontend: Up
- [ ] poker-db: Up (healthy)
- [ ] poker-redis: Up

#### 检查服务健康

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

- [ ] API响应正常 (返回HTML)
- [ ] 前端响应正常 (返回HTML)
- [ ] 数据库返回 "accepting connections"
- [ ] Redis返回 "PONG"

#### 浏览器访问测试

- [ ] 访问前端: `http://YOUR_SERVER_IP:3000` - 页面加载正常
- [ ] 访问API文档: `http://YOUR_SERVER_IP:8000/docs` - Swagger页面显示
- [ ] 测试WebSocket连接 - 实时功能正常

---

### 第五步: 配置优化 (可选)

#### 配置Nginx反向代理

如果安装了Nginx:

```bash
# 检查Nginx配置
sudo nginx -t

# 启动Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 查看状态
sudo systemctl status nginx
```

- [ ] Nginx配置正确
- [ ] Nginx运行正常
- [ ] 通过80端口访问成功

#### 配置域名 (可选)

1. 在域名DNS管理中添加A记录指向服务器IP
2. 修改Nginx配置文件中的 `server_name`
3. 重启Nginx

- [ ] 域名解析生效
- [ ] 通过域名访问成功

#### 配置SSL证书 (推荐)

```bash
# 安装certbot
sudo yum install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 测试自动续期
sudo certbot renew --dry-run
```

- [ ] SSL证书安装成功
- [ ] HTTPS访问正常
- [ ] 自动续期配置成功

---

### 第六步: 安全加固

#### 修改默认密码

```bash
# 1. 修改数据库密码
docker-compose exec db psql -U postgres -c "ALTER USER postgres PASSWORD 'NEW_STRONG_PASSWORD';"

# 2. 更新 backend/.env 中的 DATABASE_URL
vim backend/.env

# 3. 重启服务
docker-compose restart api
```

- [ ] 数据库密码已修改
- [ ] .env文件已更新
- [ ] 服务重启成功

#### 更新JWT密钥

```bash
# 生成新密钥
openssl rand -hex 32

# 更新 backend/.env
vim backend/.env
# 修改 SECRET_KEY=新生成的密钥

# 重启API服务
docker-compose restart api
```

- [ ] JWT密钥已更新
- [ ] API服务正常

#### 限制端口访问 (使用Nginx后)

```bash
# 关闭3000和8000端口的外部访问
sudo firewall-cmd --permanent --remove-port=3000/tcp
sudo firewall-cmd --permanent --remove-port=8000/tcp
sudo firewall-cmd --reload
```

- [ ] 只通过80/443端口访问
- [ ] 直接端口访问已禁用

#### 配置防火墙

```bash
# 检查firewalld状态
sudo systemctl status firewalld

# 如果未启动
sudo systemctl start firewalld
sudo systemctl enable firewalld
```

- [ ] 防火墙已启用
- [ ] 规则配置正确

---

### 第七步: 备份配置

#### 备份重要文件

```bash
# 创建备份目录
mkdir -p ~/backups

# 备份环境配置
cp backend/.env ~/backups/.env.backup

# 备份docker-compose配置
cp docker-compose.yml ~/backups/docker-compose.yml.backup

# 备份nginx配置
sudo cp /etc/nginx/nginx.conf ~/backups/nginx.conf.backup
```

- [ ] 配置文件已备份
- [ ] 备份文件安全保存

#### 创建数据库备份脚本

```bash
# 创建备份脚本
cat > ~/backup-db.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cd /opt/dzpoker
docker-compose exec -T db pg_dump -U postgres poker > $BACKUP_DIR/poker_backup_$DATE.sql
echo "Backup completed: poker_backup_$DATE.sql"
# 删除7天前的备份
find $BACKUP_DIR -name "poker_backup_*.sql" -mtime +7 -delete
EOF

chmod +x ~/backup-db.sh

# 添加到crontab (每天凌晨2点备份)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-db.sh") | crontab -
```

- [ ] 备份脚本已创建
- [ ] 定时任务已配置
- [ ] 手动执行测试成功

---

### 第八步: 监控配置 (可选)

#### 配置日志轮转

```bash
# 创建日志轮转配置
sudo cat > /etc/logrotate.d/dzpoker <<'EOF'
/opt/dzpoker/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
```

- [ ] 日志轮转已配置

#### 设置资源监控告警

```bash
# 安装监控工具
sudo yum install -y htop iotop

# 查看资源使用
htop
docker stats
```

- [ ] 监控工具已安装
- [ ] 资源使用正常

---

## ✅ 部署后验证清单

### 功能测试

- [ ] 用户注册功能正常
- [ ] 用户登录功能正常
- [ ] 创建游戏功能正常
- [ ] 发牌功能正常
- [ ] WebSocket实时通信正常
- [ ] 玩家统计数据正常显示

### 性能测试

- [ ] 页面加载时间 < 3秒
- [ ] API响应时间 < 500ms
- [ ] WebSocket连接稳定
- [ ] 多用户并发测试通过

### 安全测试

- [ ] SQL注入防护测试
- [ ] XSS攻击防护测试
- [ ] CSRF防护测试
- [ ] JWT令牌验证测试

---

## 📝 重要信息记录

### 服务器信息

```
公网IP: ____________________
内网IP: ____________________
域名: ______________________
SSH端口: __________________
```

### 密码记录 (请安全保管)

```
数据库密码: ________________
JWT密钥: ___________________
Redis密码: _________________
SSL证书路径: ______________
```

### 访问地址

```
前端: http://YOUR_IP:3000
API: http://YOUR_IP:8000
文档: http://YOUR_IP:8000/docs
```

### 关键文件路径

```
项目目录: /opt/dzpoker
配置文件: /opt/dzpoker/backend/.env
Nginx配置: /etc/nginx/nginx.conf
日志目录: /opt/dzpoker/logs
备份目录: /opt/backups
```

---

## 🔧 常见问题

### Q1: 容器启动失败怎么办?

```bash
# 查看日志
docker-compose logs api
docker-compose logs frontend

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### Q2: 数据库连接失败?

```bash
# 检查数据库状态
docker-compose exec db pg_isready -U postgres

# 检查密码是否一致
cat backend/.env | grep DATABASE_URL
docker-compose logs db
```

### Q3: 端口无法访问?

```bash
# 检查防火墙
sudo firewall-cmd --list-all

# 检查AWS安全组
# 在AWS控制台检查安全组规则

# 检查服务是否监听
sudo netstat -tlnp | grep 8000
```

### Q4: 内存不足?

```bash
# 查看内存使用
free -h
docker stats

# 清理Docker资源
docker system prune -a
```

---

## 📞 获取帮助

如遇到问题:

1. 查看日志: `docker-compose logs -f`
2. 查看系统日志: `journalctl -xe`
3. 检查容器状态: `docker-compose ps`
4. 检查资源使用: `htop`, `docker stats`

---

**部署成功后，请妥善保管此清单！** ✅
