# 历史数据查询和分析API使用指南

## 概述

系统提供完整的历史数据查询和深度分析API，可以查看所有游戏记录、玩家统计、手牌分布等详细数据。

## API端点

### 1. 游戏历史查询

#### 获取游戏列表
```bash
GET /api/analytics/games?limit=50&offset=0&status=finished
```

参数：
- `limit`: 返回数量 (1-200，默认50)
- `offset`: 偏移量 (默认0)
- `status`: 状态筛选 (finished/playing/waiting，可选)

返回示例：
```json
{
  "games": [
    {
      "id": 1,
      "game_uuid": "5bd7643c",
      "num_players": 6,
      "small_blind": 1.0,
      "big_blind": 2.0,
      "total_pot": 1250.0,
      "winner_id": 3,
      "status": "finished",
      "started_at": "2026-01-13T10:30:00Z",
      "ended_at": "2026-01-13T10:35:00Z",
      "duration": 300.0,
      "hands_count": 6
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

#### 获取游戏详情
```bash
GET /api/analytics/games/{game_id}
```

返回完整游戏信息，包括：
- 游戏基本信息
- 每个玩家的手牌（底牌、最终牌型、盈亏）
- 每手牌的所有动作记录

返回示例：
```json
{
  "id": 1,
  "game_uuid": "5bd7643c",
  "num_players": 6,
  "total_pot": 1250.0,
  "winner_id": 3,
  "hands": [
    {
      "id": 1,
      "player_id": 1,
      "position": 0,
      "hole_cards": "AhKd",
      "final_hand": "一对K",
      "profit_loss": -100.0,
      "is_winner": false,
      "actions": [
        {
          "street": "preflop",
          "action_type": "raise",
          "amount": 10.0,
          "pot_size": 20.0,
          "created_at": "2026-01-13T10:30:05Z"
        },
        {
          "street": "flop",
          "action_type": "call",
          "amount": 20.0,
          "pot_size": 100.0,
          "created_at": "2026-01-13T10:30:15Z"
        }
      ]
    }
  ]
}
```

### 2. 玩家统计分析

#### 获取玩家统计
```bash
GET /api/analytics/players/{player_id}/stats
```

返回示例：
```json
{
  "player_id": 1,
  "total_games": 50,
  "total_hands": 300,
  "wins": 75,
  "win_rate": 25.0,
  "total_profit": 5000.0,
  "vpip": 28.5,
  "pfr": 18.3,
  "af": 2.1,
  "updated_at": "2026-01-13T10:30:00Z",
  "recent_hands": [
    {
      "game_id": 10,
      "position": 2,
      "hole_cards": "AsKs",
      "final_hand": "同花顺 (A高)",
      "profit_loss": 500.0,
      "is_winner": true,
      "created_at": "2026-01-13T10:25:00Z"
    }
  ]
}
```

统计指标说明：
- `win_rate`: 胜率 (%)
- `total_profit`: 总盈利
- `vpip`: 入池率 (Voluntarily Put money In Pot)
- `pfr`: 翻前加注率 (Pre-Flop Raise)
- `af`: 激进因子 (Aggression Factor)

### 3. 整体统计

#### 获取整体统计数据
```bash
GET /api/analytics/overview?days=30
```

参数：
- `days`: 统计最近多少天 (1-365，默认30)

返回示例：
```json
{
  "period_days": 30,
  "total_games": 150,
  "finished_games": 140,
  "total_pot": 185000.0,
  "avg_duration_seconds": 420.5,
  "total_hands": 900,
  "max_pot_game": {
    "game_uuid": "abc123",
    "total_pot": 5000.0,
    "started_at": "2026-01-12T15:30:00Z"
  }
}
```

### 4. 深度分析

#### 手牌类型分布
```bash
GET /api/analytics/hand-types?limit=100
```

参数：
- `limit`: 统计最近多少局 (10-1000，默认100)

返回示例：
```json
{
  "total_hands": 100,
  "distribution": [
    {
      "hand_type": "一对",
      "count": 42,
      "percentage": 42.0
    },
    {
      "hand_type": "两对",
      "count": 18,
      "percentage": 18.0
    },
    {
      "hand_type": "高牌",
      "count": 25,
      "percentage": 25.0
    }
  ]
}
```

#### 位置胜率分析
```bash
GET /api/analytics/positions?limit=100
```

参数：
- `limit`: 统计最近多少局 (10-1000，默认100)

返回示例：
```json
{
  "total_hands": 100,
  "positions": [
    {
      "position": 0,
      "position_name": "BTN",
      "total": 20,
      "wins": 8,
      "win_rate": 40.0,
      "avg_profit": 150.5
    },
    {
      "position": 1,
      "position_name": "SB",
      "total": 20,
      "wins": 3,
      "win_rate": 15.0,
      "avg_profit": -50.2
    }
  ]
}
```

位置说明：
- BTN: Button (庄家位置，最后行动)
- SB: Small Blind (小盲注)
- BB: Big Blind (大盲注)
- UTG: Under The Gun (枪口位置，第一个行动)
- MP: Middle Position (中间位置)
- CO: Cut Off (庄家右边)

## 使用示例

### Python示例
```python
import requests

# 获取最近50局游戏
response = requests.get('http://localhost:8000/api/analytics/games?limit=50&status=finished')
games = response.json()

# 获取某个游戏的详细信息
game_id = games['games'][0]['id']
detail = requests.get(f'http://localhost:8000/api/analytics/games/{game_id}')
print(detail.json())

# 获取玩家统计
stats = requests.get('http://localhost:8000/api/analytics/players/1/stats')
print(f"胜率: {stats.json()['win_rate']}%")

# 获取手牌类型分布
hand_types = requests.get('http://localhost:8000/api/analytics/hand-types?limit=200')
for item in hand_types.json()['distribution']:
    print(f"{item['hand_type']}: {item['percentage']:.1f}%")
```

### JavaScript示例
```javascript
// 获取游戏历史
fetch('/api/analytics/games?limit=50')
  .then(res => res.json())
  .then(data => console.log(data))

// 获取整体统计
fetch('/api/analytics/overview?days=7')
  .then(res => res.json())
  .then(data => {
    console.log(`7天内完成了 ${data.finished_games} 局游戏`)
    console.log(`总底池: ${data.total_pot}`)
    console.log(`平均时长: ${data.avg_duration_seconds}秒`)
  })
```

### cURL示例
```bash
# 获取游戏历史
curl "http://localhost:8000/api/analytics/games?limit=10"

# 获取玩家统计
curl "http://localhost:8000/api/analytics/players/1/stats"

# 获取位置分析
curl "http://localhost:8000/api/analytics/positions?limit=200"
```

## 数据分析建议

### 1. 玩家表现分析
- 查看玩家的胜率和盈利趋势
- 分析VPIP和PFR判断玩家风格（紧/松，凶/弱）
- 比较不同位置的表现

### 2. 手牌分析
- 统计哪些手牌赢得最多
- 分析不同起手牌的盈利能力
- 研究特定牌型的出现频率

### 3. 位置优势
- 比较不同位置的胜率
- 分析位置对盈利的影响
- 优化各位置的策略

### 4. 游戏趋势
- 追踪长期盈利趋势
- 识别峰值和低谷期
- 调整策略以适应对手

## 注意事项

1. **数据量**: 查询大量数据时建议使用分页
2. **性能**: 深度分析查询可能需要几秒钟
3. **实时性**: 数据在游戏结束时保存，正在进行的游戏不会立即显示
4. **隐私**: 生产环境建议添加身份验证

## API文档

访问 `http://localhost:8000/docs` 查看完整的交互式API文档（Swagger UI）
