# 后端部署指南 - 修复 action_type 字段长度问题

## 问题说明

后端在保存玩家动作时出现错误：
```
sqlalchemy.exc.DBAPIError: value too long for type character varying(10)
INSERT INTO actions (..., action_type, ...) VALUES (..., 'small_blind', ...)
```

**原因**: `actions` 表的 `action_type` 字段定义为 `VARCHAR(10)`，但 `'small_blind'` 有 11 个字符。

## 修复方案

需要执行两步操作：
1. **数据库迁移**: 增加字段长度
2. **后端代码更新**: 更新模型定义

---

## 方法一: 自动化部署（推荐）

### 步骤 1: 上传文件到服务器

将以下文件上传到服务器的项目目录：
- `deploy-backend-with-migration.sh`
- `backend/app/models.py` (已修改)

### 步骤 2: 执行部署脚本

```bash
cd /path/to/dzpoker
chmod +x deploy-backend-with-migration.sh
./deploy-backend-with-migration.sh
```

脚本会自动完成：
- 停止后端容器
- 执行数据库迁移
- 重新构建并启动后端

### 步骤 3: 验证部署

访问数据分析页面，开始一局新游戏，查看是否正确保存了动作记录。

---

## 方法二: 手动部署

### 步骤 1: 查找数据库容器名称

```bash
docker ps | grep postgres
```

记录容器名称，例如 `dzpoker-db-1` 或 `dzpoker_db_1`

### 步骤 2: 连接数据库执行迁移

将 `<DB_CONTAINER_NAME>` 替换为实际容器名称：

```bash
docker exec -it <DB_CONTAINER_NAME> psql -U dzpoker_user -d dzpoker_db
```

在 psql 提示符下执行：

```sql
-- 增加字段长度
ALTER TABLE actions ALTER COLUMN street TYPE VARCHAR(20);
ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);

-- 验证修改
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'actions'
AND column_name IN ('street', 'action_type');

-- 退出
\q
```

预期输出：
```
 column_name  | data_type       | character_maximum_length
--------------+-----------------+-------------------------
 street       | character varying | 20
 action_type  | character varying | 20
```

### 步骤 3: 更新后端代码

确保 `backend/app/models.py` 中的 Action 模型已更新：

```python
class Action(Base):
    """玩家动作记录表"""
    __tablename__ = "actions"

    # ...
    street = Column(String(20))  # 改为 20
    action_type = Column(String(20))  # 改为 20
    # ...
```

### 步骤 4: 重新构建后端

```bash
# 检测 Docker Compose 命令
if command -v docker-compose &> /dev/null; then
    DC="docker-compose"
else
    DC="docker compose"
fi

# 停止后端
$DC stop api

# 删除旧容器和镜像
$DC rm -f api
docker rmi dzpoker-api 2>/dev/null || true

# 重新构建
$DC build api

# 启动
$DC up -d api
```

### 步骤 5: 检查日志

```bash
$DC logs -f api
```

查找以下成功标志：
- ✓ 服务器启动成功
- ✓ 数据库连接成功
- ✓ 没有 VARCHAR 长度相关错误

---

## 方法三: 使用 SQL 文件迁移

### 步骤 1: 准备 SQL 文件

将 `backend/migrations/001_increase_action_fields.sql` 上传到服务器

### 步骤 2: 执行迁移

```bash
docker cp backend/migrations/001_increase_action_fields.sql <DB_CONTAINER_NAME>:/tmp/
docker exec -it <DB_CONTAINER_NAME> psql -U dzpoker_user -d dzpoker_db -f /tmp/001_increase_action_fields.sql
```

### 步骤 3: 重新构建后端

参考方法二的步骤 4-5

---

## 常见问题排查

### 问题 1: 找不到数据库容器

**错误**: `Error: No such container: dzpoker-db-1`

**解决**:
```bash
# 查看所有容器
docker ps -a

# 查找包含 postgres 的容器
docker ps -a | grep postgres
```

使用正确的容器名称替换脚本中的 `dzpoker-db-1`

### 问题 2: 数据库密码错误

**错误**: `psql: FATAL: password authentication failed`

**解决**: 检查 `docker-compose.yml` 中的数据库配置：
```yaml
services:
  db:
    environment:
      POSTGRES_USER: dzpoker_user
      POSTGRES_PASSWORD: <查看这里>
      POSTGRES_DB: dzpoker_db
```

使用正确的用户名和密码

### 问题 3: 迁移后仍然报错

**检查步骤**:

1. 验证字段长度已修改：
```bash
docker exec -it <DB_CONTAINER_NAME> psql -U dzpoker_user -d dzpoker_db -c "SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name = 'action_type';"
```

2. 确认后端已重新构建：
```bash
docker images | grep dzpoker-api
```
查看镜像创建时间是否是最新的

3. 检查后端日志：
```bash
docker-compose logs --tail=50 api
```

---

## 验证部署成功

### 测试流程

1. **开始新游戏**
   - 访问 http://localhost:3000
   - 点击"开始游戏"
   - 让游戏自动完成

2. **查看数据分析**
   - 访问 http://localhost:3000/analytics
   - 点击最新的游戏记录
   - 点击"查看详情"

3. **展开玩家手牌**
   - 点击任意玩家行的展开图标
   - 查看"动作记录"表格

4. **验证数据完整性**
   - ✓ 应该看到【小盲注】动作
   - ✓ 应该看到【大盲注】动作
   - ✓ 应该看到【跟注】、【加注】、【弃牌】等动作
   - ✓ 每个动作都有金额和底池大小

### 预期结果

正常的动作记录应该类似：

| 阶段   | 动作     | 金额  | 底池  | 时间              |
|--------|----------|-------|-------|-------------------|
| 翻牌前 | 小盲注   | 1.0   | 1.0   | 2025-01-20 10:30  |
| 翻牌前 | 大盲注   | 2.0   | 3.0   | 2025-01-20 10:30  |
| 翻牌前 | 跟注     | 2.0   | 5.0   | 2025-01-20 10:31  |
| 翻牌前 | 加注     | 4.0   | 9.0   | 2025-01-20 10:31  |

---

## 回滚方案

如果部署后出现问题，可以回滚：

### 回滚数据库迁移

```sql
ALTER TABLE actions ALTER COLUMN street TYPE VARCHAR(10);
ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(10);
```

**警告**: 如果已经有长度超过 10 的数据，回滚会失败！

### 回滚代码

```bash
git checkout HEAD~1 backend/app/models.py
docker-compose build api
docker-compose up -d api
```

---

## 技术细节

### 修改的文件

1. **backend/app/models.py**
   - Line 91: `street = Column(String(20))`  # was 10
   - Line 92: `action_type = Column(String(20))`  # was 10

2. **新增文件**
   - `backend/migrations/001_increase_action_fields.sql` - SQL 迁移脚本
   - `deploy-backend-with-migration.sh` - 自动化部署脚本

### 需要存储的 action_type 值

| action_type   | 长度 | 说明     |
|---------------|------|----------|
| small_blind   | 11   | 小盲注   |
| big_blind     | 9    | 大盲注   |
| fold          | 4    | 弃牌     |
| check         | 5    | 过牌     |
| call          | 4    | 跟注     |
| raise         | 5    | 加注     |
| all_in        | 6    | All-in   |

VARCHAR(20) 提供了足够的余量。

---

## 联系支持

如果遇到问题：

1. 收集以下信息：
   - 后端日志: `docker-compose logs api > backend.log`
   - 数据库日志: `docker logs dzpoker-db-1 > db.log`
   - 错误截图

2. 检查以下配置：
   - Docker 版本: `docker --version`
   - Docker Compose 版本: `docker-compose --version` 或 `docker compose version`
   - 数据库版本: `docker exec dzpoker-db-1 psql --version`

3. 提供完整的错误信息用于诊断
