# 容器重启导致游戏丢失问题

## 问题现象

容器重启后，所有 API 请求返回 404：
```
POST /api/games/5e8bf7a9/ai-action HTTP/1.1" 404 Not Found
GET /api/games/5e8bf7a9?include_hole_cards=true HTTP/1.1" 404 Not Found
```

## 根本原因

**backend/app/routers/games.py** 第 20 行：
```python
games: Dict[str, PokerGame] = {}
```

游戏状态存储在**内存字典**中，容器重启后会清空。

## 临时解决方案（测试 VARCHAR 修复）

### 方案 1: 清除浏览器缓存并重新开始

1. **清除浏览器缓存**：
   - Chrome: Ctrl+Shift+Delete
   - 或使用无痕模式：Ctrl+Shift+N

2. **刷新页面**：
   - 访问 http://your-server:3000
   - 点击"开始游戏"
   - 这会创建新的游戏 ID

3. **测试 VARCHAR 修复**：
   - 让游戏完成
   - 查看控制台是否还有 500 错误
   - 访问数据分析页面查看动作记录

### 方案 2: 直接访问首页

直接访问首页会自动创建新游戏：
```
http://your-server:3000
```

## 验证修复是否成功

### ✅ 修复成功的标志：

1. **游戏完成后没有 500 错误**
   ```
   [Finish] Calling finish API to save game data...
   ✓ POST /api/games/xxx/finish 200 OK  (不是 500)
   ```

2. **数据分析页面显示动作记录**
   - 访问 http://your-server:3000/analytics
   - 点击最新游戏的"查看详情"
   - 展开任意玩家，查看"动作记录"表格
   - 应该看到：小盲注、大盲注、跟注、加注等

3. **数据库中有完整数据**
   ```bash
   docker exec poker-db psql -U postgres -d poker -c "SELECT COUNT(*) FROM actions WHERE action_type IN ('small_blind', 'big_blind');"
   ```
   应该返回 > 0

### ❌ 仍然失败的标志：

如果还是看到：
```
sqlalchemy.exc.DataError: value too long for type character varying(10)
```

说明数据库迁移未成功，需要手动执行：
```bash
docker exec poker-db psql -U postgres -d poker -c "ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);"
```

## 长期解决方案（未实现）

### 问题：游戏状态只存在内存中

**影响**：
- 容器重启 → 游戏丢失 → 用户断线
- 无法横向扩展（多个后端实例）
- 无法恢复进行中的游戏

### 解决方案：Redis 持久化

需要修改 `backend/app/routers/games.py`：

```python
# 当前实现（内存）
games: Dict[str, PokerGame] = {}

# 改为 Redis
import redis
import pickle

redis_client = redis.Redis(host='redis', port=6379, db=0)

def save_game(game_id: str, game: PokerGame):
    """保存游戏到 Redis"""
    redis_client.set(f"game:{game_id}", pickle.dumps(game), ex=3600)

def load_game(game_id: str) -> PokerGame:
    """从 Redis 加载游戏"""
    data = redis_client.get(f"game:{game_id}")
    if not data:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return pickle.loads(data)
```

**优点**：
- ✓ 容器重启不影响游戏
- ✓ 支持多个后端实例
- ✓ 可以设置过期时间（TTL）

**工作量**：约 2-3 小时

## 当前测试流程

### 步骤 1: 确认后端已更新

```bash
./diagnose.sh
```

检查输出中的：
```
✓ 本地和容器内代码都已更新
```

### 步骤 2: 确认数据库已迁移

```bash
docker exec poker-db psql -U postgres -d poker -c "SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'actions' AND column_name = 'action_type';"
```

预期输出：
```
 column_name  | character_maximum_length
--------------+--------------------------
 action_type  |                       20
```

### 步骤 3: 清除浏览器并重新测试

1. **清除浏览器缓存** 或使用无痕模式
2. **访问首页**: http://your-server:3000
3. **开始新游戏**
4. **让游戏完成**（等待 AI 自动完成）
5. **检查控制台**：
   - 打开 F12 开发者工具
   - 查看 Console 标签
   - finish API 应该返回 200 而不是 500

6. **查看数据分析**:
   - 访问 http://your-server:3000/analytics
   - 点击最新游戏
   - 点击"查看详情"
   - 展开玩家手牌
   - 查看动作记录

### 步骤 4: 验证动作记录

动作记录应该包含：

| 阶段   | 动作     | 金额 | 底池 |
|--------|----------|------|------|
| 翻牌前 | 小盲注   | 1.0  | 1.0  |
| 翻牌前 | 大盲注   | 2.0  | 3.0  |
| 翻牌前 | 跟注     | 2.0  | 5.0  |
| ...    | ...      | ...  | ...  |

## 常见问题

### Q1: 为什么不直接实现 Redis 持久化？

A: Redis 持久化需要：
1. 修改游戏状态读写逻辑
2. 处理序列化/反序列化
3. 实现过期清理机制
4. 测试所有边界情况

当前优先修复 VARCHAR 问题，Redis 持久化可以后续优化。

### Q2: 如果游戏中途容器重启怎么办？

A: 当前会丢失。建议：
1. 避免在游戏进行中重启容器
2. 只在空闲时更新后端
3. 或者实现 Redis 持久化

### Q3: 测试时一直看到 404 怎么办？

A: 说明浏览器仍在访问旧游戏 ID。解决：
1. 清除浏览器缓存
2. 使用无痕模式
3. 或直接访问首页（会自动创建新游戏）

## 总结

**当前状态**：
- ✅ VARCHAR 问题已修复（代码 + 数据库迁移）
- ✅ 容器已重启
- ⚠️ 旧游戏 ID 已失效（内存清空）

**测试要求**：
- 必须清除浏览器缓存或使用无痕模式
- 开始**新游戏**测试 VARCHAR 修复
- 不能继续使用旧游戏 ID

**下一步**：
1. 清除浏览器缓存
2. 重新开始游戏
3. 验证 finish API 返回 200
4. 查看数据分析中的动作记录
