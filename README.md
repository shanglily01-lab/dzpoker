# 德州扑克发牌算法AI测试系统

一个基于AI的德州扑克发牌算法测试平台,用于提升游戏娱乐性、分析玩家行为和优化发牌策略。

## 功能特性

- **智能发牌引擎**: 在公平性约束内优化发牌策略
- **玩家行为分析**: 实时追踪玩家行为,自动分类玩家类型
- **技术水平评估**: 基于VPIP/PFR等指标评估玩家技术水平
- **实时游戏**: WebSocket支持的实时多人游戏

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11 + FastAPI |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 前端 | Vue 3 + Element Plus |
| 部署 | Docker Compose |

## 项目结构

```
dzpoker/
├── backend/                  # 后端服务
│   ├── app/
│   │   ├── core/            # 核心模块
│   │   │   ├── config.py    # 配置
│   │   │   ├── database.py  # 数据库
│   │   │   ├── redis.py     # Redis
│   │   │   └── poker.py     # 扑克核心逻辑
│   │   ├── routers/         # API路由
│   │   │   ├── games.py     # 游戏API
│   │   │   └── players.py   # 玩家API
│   │   ├── ai/              # AI模块
│   │   │   ├── analyzer.py  # 玩家分析
│   │   │   └── smart_dealer.py  # 智能发牌
│   │   ├── models.py        # 数据模型
│   │   ├── schemas.py       # Pydantic模型
│   │   └── main.py          # 入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # 前端服务
│   ├── src/
│   │   ├── views/           # 页面
│   │   ├── components/      # 组件
│   │   ├── stores/          # Pinia状态
│   │   ├── api/             # API请求
│   │   └── router/          # 路由
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 快速开始

### 使用Docker Compose (推荐)

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

服务启动后:
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 本地开发

**后端:**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

**前端:**

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## API接口

### 游戏管理

```bash
# 创建游戏
POST /api/games
{
  "num_players": 6,
  "small_blind": 1,
  "big_blind": 2
}

# 获取游戏状态
GET /api/games/{game_id}

# 开始游戏
POST /api/games/{game_id}/start

# 发牌 (smart=true 启用智能发牌)
POST /api/games/{game_id}/deal?smart=true

# 发翻牌/转牌/河牌
POST /api/games/{game_id}/flop
POST /api/games/{game_id}/turn
POST /api/games/{game_id}/river
```

### 玩家管理

```bash
# 注册
POST /api/players/register

# 登录
POST /api/players/login

# 获取玩家画像分析
GET /api/players/{player_id}/profile
```

## 核心算法

### 智能发牌策略

```python
# 发牌权重计算
weight = 1.0

# 不活跃玩家提升
if activity_score < 0.3:
    weight *= 1.1

# 连续输牌补偿
if loss_streak >= 5:
    weight *= (1 + loss_streak * 0.02)

# 公平性约束: 最大调整±15%
weight = clamp(weight, 0.85, 1.15)
```

### 玩家类型分类

| 类型 | VPIP | PFR | 特点 |
|------|------|-----|------|
| 紧凶型 (TAG) | < 25% | > 15% | 只玩强牌,下注激进 |
| 松凶型 (LAG) | > 25% | > 20% | 玩牌范围广,下注激进 |
| 被动型 | - | < 10% | 跟注为主,很少加注 |
| 鱼 | > 35% | < 15% | 入池过多,缺乏策略 |

### 技术水平评估 (0-100分)

- VPIP合理性: 20分 (理想范围18-25%)
- PFR合理性: 20分 (理想范围12-18%)
- PFR/VPIP比例: 15分 (理想 > 0.65)
- 激进因子: 15分 (理想范围1.5-3.0)
- 基础分: 30分

## 环境变量

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/poker
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=true
```

## 开发计划

- [x] 基础发牌引擎
- [x] 玩家行为分析
- [x] 智能发牌策略
- [x] WebSocket实时通信
- [ ] 牌型评估算法
- [ ] 模拟测试系统
- [ ] A/B测试框架

## License

MIT
