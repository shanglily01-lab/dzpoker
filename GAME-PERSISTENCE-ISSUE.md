# 游戏持久化问题说明
# Game Persistence Issue

## 🔴 当前问题

### 症状
```
开始游戏失败: Request failed with status code 404
发牌失败: Request failed with status code 404
```

### 错误详情
```javascript
:3000/api/games/ca424408/start:1  Failed to load resource: the server responded with a status of 404 (Not Found)
:3000/api/games/ca424408/deal?smart=true:1  Failed to load resource: the server responded with a status of 404 (Not Found)
```

### 根本原因

**游戏状态只存储在内存中，服务器重启后丢失**

当前代码：
```python
# backend/app/routers/games.py
games: Dict[str, PokerGame] = {}  # ⚠️ 只在内存中！
```

当发生以下情况时，所有游戏数据丢失：
1. 服务器重启
2. Docker 容器重启
3. 代码更新后 restart
4. 应用崩溃

---

## ✅ API 端点验证

经过测试，API 端点本身工作正常：

```bash
# 创建游戏
curl -X POST http://13.212.252.171:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 4, "small_blind": 10, "big_blind": 20}'
# ✅ 返回: {"game_id":"703b237a",...}

# 开始游戏
curl -X POST http://13.212.252.171:8000/api/games/703b237a/start
# ✅ 返回: {"message":"游戏开始","state":"preflop","pot":30.0}

# 尝试旧的游戏 ID
curl -X POST http://13.212.252.171:8000/api/games/ca424408/start
# ❌ 返回: {"detail":"游戏不存在"}
```

---

## 🔧 解决方案

### 短期解决方案（临时）

**用户每次需要创建新游戏**

前端修改建议：
1. 页面加载时检查游戏是否存在
2. 如果返回 404，自动创建新游戏
3. 提示用户"游戏已过期，已创建新游戏"

```javascript
// GameTable.vue
const loadGame = async () => {
  try {
    const data = await getGame(gameId)
    gameState.value = data
  } catch (err) {
    if (err.response?.status === 404) {
      // 游戏不存在，提示用户
      ElMessage.warning('游戏不存在或已过期，请返回首页创建新游戏')
      setTimeout(() => {
        router.push('/')
      }, 2000)
    }
  }
}
```

### 长期解决方案（推荐）

**实现 Redis 游戏状态持久化**

#### 步骤1: 创建 Redis 存储层

```python
# backend/app/core/game_store.py
import json
from typing import Optional, Dict
from redis import Redis
from ..core.poker import PokerGame

class GameStore:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.prefix = "game:"

    def save(self, game_id: str, game: PokerGame):
        """保存游戏状态到 Redis"""
        key = f"{self.prefix}{game_id}"
        # 序列化游戏状态
        game_data = game.to_dict()
        self.redis.setex(
            key,
            3600 * 24,  # 24小时过期
            json.dumps(game_data)
        )

    def load(self, game_id: str) -> Optional[PokerGame]:
        """从 Redis 加载游戏状态"""
        key = f"{self.prefix}{game_id}"
        data = self.redis.get(key)
        if data:
            game_data = json.loads(data)
            return PokerGame.from_dict(game_data)
        return None

    def delete(self, game_id: str):
        """删除游戏"""
        key = f"{self.prefix}{game_id}"
        self.redis.delete(key)

    def exists(self, game_id: str) -> bool:
        """检查游戏是否存在"""
        key = f"{self.prefix}{game_id}"
        return self.redis.exists(key) > 0
```

#### 步骤2: 实现序列化方法

```python
# backend/app/core/poker.py
class PokerGame:
    # ... 现有代码 ...

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "game_id": self.game_id,
            "state": self.state.value,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "small_blind": self.small_blind,
            "big_blind": self.big_blind,
            "players": [p.to_dict() for p in self.players],
            "community_cards": [c.to_dict() for c in self.community_cards],
            "deck": [c.to_dict() for c in self.deck],
            "dealer_position": self.dealer_position,
            "current_player_index": self.current_player_index
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PokerGame':
        """从字典反序列化"""
        game = cls(
            num_players=len(data["players"]),
            small_blind=data["small_blind"],
            big_blind=data["big_blind"]
        )
        game.game_id = data["game_id"]
        game.state = GameState(data["state"])
        game.pot = data["pot"]
        game.current_bet = data["current_bet"]
        # ... 恢复其他状态 ...
        return game
```

#### 步骤3: 修改路由使用 Redis

```python
# backend/app/routers/games.py
from ..core.game_store import GameStore
from ..core.redis import redis_client

game_store = GameStore(redis_client)

@router.post("")
async def create_game(request: CreateGameRequest):
    """创建游戏"""
    game_id = str(uuid.uuid4())[:8]
    game = PokerGame(
        num_players=request.num_players,
        small_blind=request.small_blind,
        big_blind=request.big_blind
    )

    # 保存到 Redis
    game_store.save(game_id, game)

    return GameResponse(...)

@router.get("/{game_id}")
async def get_game(game_id: str):
    """获取游戏状态"""
    game = game_store.load(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    return game.get_state()
```

---

## 📊 优先级和工作量

### 当前待办事项优先级

| 优先级 | 任务 | 工作量 | 影响 |
|-------|------|--------|------|
| 🔴 高 | 在 EC2 更新代码 | 5分钟 | AI功能可用 |
| 🔴 高 | Redis 游戏持久化 | 2-3小时 | 解决404问题 |
| 🟡 中 | PlayerStats 真实API | 1-2小时 | 统计功能 |
| 🟡 中 | 玩家超时机制 | 1小时 | 用户体验 |
| 🟢 低 | 边池逻辑 | 2-3小时 | All-in场景 |
| 🟢 低 | JWT 认证 | 2小时 | 安全性 |

### 建议执行顺序

1. **立即执行**：更新 EC2 服务器代码
   ```bash
   ssh user@13.212.252.171 "cd dzpoker && git pull && docker-compose restart"
   ```

2. **短期临时方案**：前端增加游戏不存在的处理
   - 检测 404 错误
   - 提示用户返回首页创建新游戏

3. **中期根本解决**：实现 Redis 持久化
   - 游戏状态保存到 Redis
   - 支持服务器重启后恢复游戏
   - 设置合理的过期时间（24小时）

---

## 🎯 用户体验改进

### 前端改进建议

#### 1. 自动检测游戏状态

```javascript
// GameTable.vue - onMounted
onMounted(async () => {
  try {
    await loadGame()
    connectWebSocket()
    addLog('欢迎来到德州扑克！')

    // ... 自动游戏逻辑 ...
  } catch (err) {
    if (err.response?.status === 404) {
      ElMessageBox.confirm(
        '游戏不存在或已过期，是否返回首页创建新游戏？',
        '提示',
        {
          confirmButtonText: '返回首页',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        router.push('/')
      })
    }
  }
})
```

#### 2. Dashboard 显示游戏状态

```javascript
// Dashboard.vue
const checkGameStatus = async (gameId) => {
  try {
    await getGame(gameId)
    return 'active'
  } catch {
    return 'expired'
  }
}
```

#### 3. 游戏列表显示过期状态

在游戏列表中标记哪些游戏仍然有效，哪些已过期。

---

## 📝 总结

### 当前状况
- ✅ API 端点正常工作
- ❌ 游戏状态只在内存中
- ❌ 服务器重启后游戏丢失
- ❌ 用户会遇到 404 错误

### 立即需要做的
1. 更新 EC2 服务器代码（修复 AI 500 错误）
2. 前端添加 404 错误处理（临时方案）

### 后续需要做的
1. 实现 Redis 游戏持久化（根本解决）
2. 添加游戏过期机制
3. 改进用户体验

---

生成时间: 2026-01-12
