# 3秒快速修复指南

## 原因
后端代码已经通过 `docker-compose.yml` 的 volume 映射自动同步到容器内，**无需重新构建**！

你的配置：
```yaml
volumes:
  - ./backend:/app  # 本地代码直接映射到容器
command: uvicorn app.main:app --reload  # 自动重载
```

---

## 方法一：只需一条命令（3秒）

### Windows PowerShell:
```powershell
.\quick-update.ps1
```

### Linux/Mac:
```bash
chmod +x quick-update.sh
./quick-update.sh
```

---

## 方法二：手动执行（分步骤理解）

### 步骤 1: 数据库迁移（一次性，2秒）

```bash
# 增加字段长度
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN street TYPE VARCHAR(20);"
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);"
```

### 步骤 2: 重启后端（1秒）

```bash
docker-compose restart api
```

**就这么简单！** 因为：
- ✓ 你的 `backend/app/models.py` 已经修改（VARCHAR 20）
- ✓ Volume 映射会自动同步代码到容器
- ✓ `--reload` 参数会自动重载代码
- ✓ 无需重新构建镜像

---

## 为什么之前要重新构建？

**误解**：以为必须 `docker-compose build` 才能更新代码

**真相**：
- 有 volume 映射 = 代码自动同步 ✓
- 有 `--reload` = 自动重载 ✓
- **只有依赖变更（requirements.txt）才需要 rebuild**

---

## 验证更新

```bash
# 查看后端日志
docker-compose logs -f api

# 应该看到：
# INFO:     Application startup complete.
# 没有 VARCHAR 错误
```

---

## 以后更新代码的正确流程

### 只改代码（99%的情况）:
```bash
# 1. 拉取代码
git pull

# 2. 重启容器（如果不是热重载）
docker-compose restart api
```

### 改了依赖（很少）:
```bash
# 1. 拉取代码
git pull

# 2. 重新构建
docker-compose build api

# 3. 重启
docker-compose up -d api
```

---

## 前端更新也可以优化

如果前端也配置了 volume 映射，可以：

```yaml
# 在 docker-compose.yml 中添加
frontend:
  build: ./frontend
  volumes:
    - ./frontend/src:/app/src  # 源码映射
    - ./frontend/public:/app/public  # 静态资源
```

但前端通常需要重新构建（因为有编译步骤），除非使用开发模式。

---

## 当前状态

✓ **models.py** - 已修改 VARCHAR(10) → VARCHAR(20)
✓ **Volume 映射** - 代码已自动同步
⏳ **数据库迁移** - 需要执行一次
⏳ **容器重启** - 需要重启一次

**执行**: `./quick-update.ps1` 或 `./quick-update.sh`

**时间**: 10秒（包括等待启动）

---

## 疑难解答

### Q: 重启后还是报错？
A: 检查 volume 映射是否生效：
```bash
docker exec poker-api ls -la /app/app/models.py
docker exec poker-api cat /app/app/models.py | grep "String(20)"
```

### Q: 数据库迁移失败？
A: 检查容器名称：
```bash
docker ps | grep postgres
# 如果不是 poker-db，修改命令中的容器名
```

### Q: 想回到完整重建？
A: 可以，但很慢（3-5分钟）：
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 总结

**过去的错误做法**（5分钟）:
```bash
docker-compose build api  # 不必要！
docker-compose up -d api
```

**正确的快速做法**（3秒）:
```bash
docker-compose restart api  # 就这么简单！
```

**完整修复**（10秒，只需一次）:
```bash
./quick-update.ps1  # 包括数据库迁移 + 重启
```
