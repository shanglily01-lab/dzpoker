# 🃏 德州扑克AI测试系统 (DZPoker)

> 基于AI的德州扑克发牌算法测试平台，集成玩家行为分析、智能发牌策略和实时对战功能

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.x-green)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)](https://fastapi.tiangolo.com/)

---

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [核心算法](#核心算法)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [部署文档](#部署文档)
- [更新日志](#更新日志)

---

## ✨ 功能特性

### 🎮 核心游戏功能
- ✅ **完整的德州扑克逻辑** - 支持2-9人桌，包含所有游戏阶段
- ✅ **实时多人对战** - WebSocket实时通信，低延迟游戏体验
- ✅ **精美游戏界面** - 仿真德州扑克桌面，专业扑克牌显示
- ✅ **完整牌型判断** - 10种牌型评估，支持平局判定
- ✅ **摊牌和结算** - 自动计算获胜者和奖池分配

### 🤖 AI智能功能
- ✅ **智能发牌引擎** - 在公平性约束内优化发牌策略（±15%调整范围）
- ✅ **玩家行为分析** - 实时追踪VPIP、PFR、AF等核心指标
- ✅ **玩家类型分类** - 自动识别紧凶型(TAG)、松凶型(LAG)、被动型、鱼
- ✅ **技术水平评估** - 基于多维度指标的技能评分系统(0-100分)
- ✅ **AI建议系统** - 针对不同玩家类型提供策略建议

### 📊 数据和分析
- ✅ **玩家统计追踪** - 完整的游戏历史和统计数据
- ✅ **实时日志系统** - 游戏动作记录和事件追踪
- ✅ **数据持久化** - PostgreSQL存储，支持历史查询
- ⏳ **数据可视化** - 图表展示玩家表现趋势（开发中）

---

## 🛠 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11 | 后端语言 |
| **FastAPI** | Latest | Web框架 |
| **SQLAlchemy** | 2.0 | ORM（异步） |
| **PostgreSQL** | 15 | 主数据库 |
| **Redis** | 7 | 缓存和会话 |
| **WebSocket** | - | 实时通信 |
| **Pydantic** | 2.x | 数据验证 |
| **Alembic** | Latest | 数据库迁移 |

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue** | 3.x | 前端框架 |
| **Vite** | Latest | 构建工具 |
| **Element Plus** | Latest | UI组件库 |
| **Pinia** | Latest | 状态管理 |
| **Axios** | Latest | HTTP客户端 |
| **Vue Router** | 4.x | 路由管理 |

### DevOps
| 技术 | 用途 |
|------|------|
| **Docker** | 容器化 |
| **Docker Compose** | 容器编排 |
| **Nginx** | 反向代理（可选） |
| **Git** | 版本控制 |

---

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/dzpoker.git
cd dzpoker

# 2. 配置环境变量（可选）
cp backend/.env.example backend/.env

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

**服务访问地址：**
- 🎮 前端界面: http://localhost:3000
- 🔧 后端API: http://localhost:8000
- 📖 API文档: http://localhost:8000/docs
- 🗄️ PostgreSQL: localhost:5432
- 🔴 Redis: localhost:6379

### 方式二：快速重启

```bash
# 使用重启脚本
chmod +x restart.sh
bash restart.sh

# 选择重启方式：
# 1) 重启所有服务
# 2) 仅重启后端 API
# 3) 仅重启前端
# ... 等7种方式
```

### 方式三：本地开发

**后端开发：**
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动PostgreSQL和Redis（需提前安装）
# 或使用Docker: docker-compose up -d db redis

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

**前端开发：**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

---

## 📁 项目结构

```
dzpoker/
├── 📂 backend/                   # 后端服务
│   ├── 📂 app/
│   │   ├── 📂 core/              # 核心模块
│   │   │   ├── config.py         # 配置管理
│   │   │   ├── database.py       # 数据库连接
│   │   │   ├── redis.py          # Redis连接
│   │   │   ├── poker.py          # 🎮 德州扑克核心逻辑
│   │   │   └── hand_evaluator.py # 🃏 牌型评估算法
│   │   ├── 📂 routers/           # API路由
│   │   │   ├── games.py          # 游戏API（14个端点）
│   │   │   └── players.py        # 玩家API（8个端点）
│   │   ├── 📂 ai/                # AI模块
│   │   │   ├── analyzer.py       # 🤖 玩家行为分析
│   │   │   └── smart_dealer.py   # 🎲 智能发牌引擎
│   │   ├── 📂 models/            # 数据库模型
│   │   │   └── models.py         # SQLAlchemy模型（5张表）
│   │   ├── schemas.py            # Pydantic数据验证
│   │   └── main.py               # FastAPI入口
│   ├── requirements.txt          # Python依赖（30个包）
│   ├── Dockerfile                # 后端容器镜像
│   └── init.sql                  # 数据库初始化脚本
│
├── 📂 frontend/                  # 前端服务
│   ├── 📂 src/
│   │   ├── 📂 views/             # 页面组件
│   │   │   ├── Home.vue          # 首页
│   │   │   ├── GameTable.vue     # 🎮 游戏桌面（主要游戏界面）
│   │   │   ├── Dashboard.vue     # 数据仪表盘
│   │   │   └── PlayerStats.vue   # 玩家统计
│   │   ├── 📂 components/        # 可复用组件
│   │   │   ├── PlayingCard.vue   # 🃏 扑克牌组件
│   │   │   └── PlayerSeat.vue    # 👤 玩家座位组件
│   │   ├── 📂 stores/            # Pinia状态管理
│   │   │   └── game.js           # 游戏状态
│   │   ├── 📂 api/               # API封装
│   │   │   └── index.js          # Axios实例和18个API方法
│   │   ├── 📂 router/            # Vue Router
│   │   │   └── index.js          # 路由配置
│   │   ├── App.vue               # 根组件
│   │   └── main.js               # 入口文件
│   ├── package.json              # NPM依赖
│   ├── vite.config.js            # Vite配置
│   └── Dockerfile                # 前端容器镜像
│
├── 📂 docs/                      # 文档目录
│   ├── README-DEPLOYMENT.md      # 📖 详细部署文档
│   ├── DEPLOYMENT-CHECKLIST.md   # ✅ 部署检查清单
│   ├── QUICK-START.md            # ⚡ 快速部署指南
│   └── 系统架构设计.md            # 🏗️ 架构设计文档
│
├── 📂 scripts/                   # 脚本工具
│   ├── deploy-amazon-linux.sh   # Amazon Linux自动部署
│   ├── quick-deploy.sh           # 快速部署脚本
│   ├── restart.sh                # 🔄 服务重启工具（7种方式）
│   ├── fix-docker-conflicts.sh  # Docker冲突修复
│   ├── fix-buildx.sh             # Buildx升级脚本
│   ├── simple-deploy.sh          # 简化部署脚本
│   └── health-check.sh           # 健康检查脚本
│
├── 📂 tests/                     # 测试代码
│   └── test_game_flow.py         # 完整游戏流程测试
│
├── docker-compose.yml            # 开发环境编排
├── docker-compose.prod.yml       # 生产环境编排
├── .gitignore                    # Git忽略规则
├── README.md                     # 📖 项目说明（本文件）
└── LICENSE                       # MIT许可证
```

---

## 🧮 核心算法

### 1. 牌型评估算法

**支持的10种牌型（从高到低）：**

| 牌型 | 英文 | 示例 | 评分 |
|-----|------|------|------|
| 皇家同花顺 | Royal Flush | A♠ K♠ Q♠ J♠ 10♠ | 10 |
| 同花顺 | Straight Flush | 9♥ 8♥ 7♥ 6♥ 5♥ | 9 |
| 四条 | Four of a Kind | K♦ K♠ K♥ K♣ 3♠ | 8 |
| 葫芦 | Full House | Q♣ Q♦ Q♠ 5♥ 5♦ | 7 |
| 同花 | Flush | A♦ J♦ 9♦ 6♦ 3♦ | 6 |
| 顺子 | Straight | 10♠ 9♣ 8♦ 7♥ 6♠ | 5 |
| 三条 | Three of a Kind | 7♥ 7♦ 7♠ K♣ 2♦ | 4 |
| 两对 | Two Pair | J♠ J♦ 8♥ 8♣ A♠ | 3 |
| 一对 | One Pair | 9♣ 9♦ K♠ 7♥ 4♦ | 2 |
| 高牌 | High Card | A♠ K♦ 10♥ 7♣ 3♠ | 1 |

**算法实现：**
```python
def evaluate_hand(hole_cards, community_cards):
    """
    从7张牌（2张手牌+5张公共牌）中找出最强的5张牌组合

    算法：
    1. 使用itertools.combinations生成C(7,5)=21种组合
    2. 评估每种组合，计算牌型等级和决定性点数
    3. 返回最强牌型

    时间复杂度：O(21 × k)，其中k是单次评估复杂度
    """
    from itertools import combinations

    all_cards = hole_cards + community_cards
    best_rank = HandRank.HIGH_CARD
    best_values = []

    for five_cards in combinations(all_cards, 5):
        rank, values = _evaluate_five_cards(list(five_cards))
        if rank > best_rank or (rank == best_rank and values > best_values):
            best_rank = rank
            best_values = values

    return best_rank, best_values
```

### 2. 智能发牌策略

**权重调整算法：**
```python
# 基础权重
weight = 1.0

# 规则1: 不活跃玩家提升（活跃度 < 30%）
if activity_score < 0.3:
    weight *= 1.1  # 提升10%

# 规则2: 连续输牌补偿（连续输5手以上）
if loss_streak >= 5:
    weight *= (1 + loss_streak * 0.02)  # 每手增加2%

# 规则3: 技能等级调整
if skill_level < 30:  # 新手玩家
    weight *= 1.05  # 提升5%

# 公平性约束：最大调整幅度±15%
weight = clamp(weight, 0.85, 1.15)
```

**发牌流程：**
1. 计算每个玩家的权重
2. 根据权重调整抽牌概率
3. 发放手牌，评估手牌强度（0-1分）
4. 对权重高的玩家，有30%概率重抽以获得更强牌

### 3. 玩家类型分类

**分类规则：**
```python
def classify_player(vpip, pfr, af):
    """
    基于核心指标分类玩家类型

    指标说明：
    - VPIP (Voluntarily Put $ In Pot): 自愿入池率
    - PFR (Pre-Flop Raise): 翻前加注率
    - AF (Aggression Factor): 激进因子 = (加注+下注) / 跟注
    """
    if vpip < 25 and pfr > 15 and af > 1.5:
        return "紧凶型 (TAG)"  # Tight-Aggressive
    elif vpip > 25 and pfr > 20 and af > 2.0:
        return "松凶型 (LAG)"  # Loose-Aggressive
    elif pfr < 10 and af < 1.0:
        return "被动型"        # Passive
    elif vpip > 35 and pfr < 15:
        return "鱼 (Fish)"     # Recreational player
    else:
        return "常规型"        # Regular
```

**玩家类型特征：**

| 类型 | VPIP | PFR | AF | 特点 | 建议策略 |
|------|------|-----|-------|------|----------|
| 🎯 **紧凶型 (TAG)** | < 25% | > 15% | > 1.5 | 只玩强牌，下注激进 | 尊重其加注，避免硬碰硬 |
| 🌟 **松凶型 (LAG)** | > 25% | > 20% | > 2.0 | 玩牌范围广，极具攻击性 | 等待强牌，诱其上钩 |
| 😴 **被动型** | 任意 | < 10% | < 1.0 | 跟注为主，很少加注 | 多偷盲，控制底池 |
| 🐟 **鱼 (Fish)** | > 35% | < 15% | 任意 | 入池过多，缺乏策略 | 价值下注，不要诈唬 |
| 📊 **常规型** | 18-35% | 12-20% | 1.0-2.0 | 平衡打法 | 根据具体情况调整 |

### 4. 技术水平评估 (0-100分)

**评分维度：**
```python
def evaluate_skill(vpip, pfr, af, vpip_pfr_ratio):
    score = 30  # 基础分

    # 维度1: VPIP合理性 (20分)
    # 理想范围：18-25%
    if 18 <= vpip <= 25:
        score += 20
    elif 15 <= vpip < 18 or 25 < vpip <= 30:
        score += 15
    elif vpip < 15 or vpip > 30:
        score += 5

    # 维度2: PFR合理性 (20分)
    # 理想范围：12-18%
    if 12 <= pfr <= 18:
        score += 20
    elif 10 <= pfr < 12 or 18 < pfr <= 22:
        score += 15

    # 维度3: PFR/VPIP比例 (15分)
    # 理想：> 0.65（表示玩牌时主动性强）
    if vpip_pfr_ratio >= 0.65:
        score += 15
    elif vpip_pfr_ratio >= 0.50:
        score += 10

    # 维度4: 激进因子 (15分)
    # 理想范围：1.5-3.0
    if 1.5 <= af <= 3.0:
        score += 15
    elif 1.0 <= af < 1.5 or 3.0 < af <= 4.0:
        score += 10

    return min(100, score)
```

**等级划分：**
- 🏆 **专家 (80-100分)**: 理解深刻，策略灵活
- 💎 **高级 (60-79分)**: 技术扎实，偶有失误
- ⭐ **中级 (40-59分)**: 基础良好，需要提升
- 🌱 **初级 (20-39分)**: 正在学习，进步空间大
- 🆕 **新手 (0-19分)**: 刚接触游戏，需要指导

---

## 📡 API文档

### 游戏管理 API

#### 创建游戏
```http
POST /api/games
Content-Type: application/json

{
  "num_players": 6,
  "small_blind": 10,
  "big_blind": 20
}

Response:
{
  "game_id": "uuid-string",
  "state": "waiting",
  "players": []
}
```

#### 开始游戏
```http
POST /api/games/{game_id}/start

Response:
{
  "message": "游戏已开始",
  "state": "preflop"
}
```

#### 发底牌 (支持智能发牌)
```http
POST /api/games/{game_id}/deal?smart=true

Response:
{
  "hole_cards": [
    [{"rank": 12, "suit": 0}, {"rank": 11, "suit": 0}],  # 玩家1: A♠ K♠
    [{"rank": 10, "suit": 1}, {"rank": 9, "suit": 1}]    # 玩家2: Q♥ J♥
  ],
  "deck_remaining": 48
}
```

#### 发公共牌
```http
# 发翻牌 (Flop - 3张)
POST /api/games/{game_id}/flop

# 发转牌 (Turn - 1张)
POST /api/games/{game_id}/turn

# 发河牌 (River - 1张)
POST /api/games/{game_id}/river
```

#### 玩家操作
```http
POST /api/games/{game_id}/action/{player_id}
Content-Type: application/json

{
  "action": "raise",  # fold | check | call | raise | all_in
  "amount": 50
}
```

#### 摊牌
```http
POST /api/games/{game_id}/showdown

Response:
{
  "winners": [
    {
      "player_id": 1,
      "hand_description": "同花顺 (K高)",
      "winnings": 200
    }
  ],
  "pot": 200
}
```

### 玩家管理 API

#### 注册
```http
POST /api/players/register
Content-Type: application/json

{
  "username": "player1",
  "password": "password123",
  "initial_chips": 1000
}
```

#### 登录
```http
POST /api/players/login
Content-Type: application/x-www-form-urlencoded

username=player1&password=password123

Response:
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

#### 获取玩家画像
```http
GET /api/players/{player_id}/profile
Authorization: Bearer {token}

Response:
{
  "player_id": 1,
  "username": "player1",
  "stats": {
    "vpip": 22.5,
    "pfr": 16.3,
    "af": 2.1,
    "win_rate": 54.2
  },
  "player_type": "紧凶型 (TAG)",
  "skill_level": 75,
  "recommendations": ["继续保持紧凶打法", "可以适当增加诈唬频率"]
}
```

### WebSocket API

```javascript
// 连接游戏WebSocket
const ws = new WebSocket('ws://localhost:8000/api/games/ws/{game_id}')

// 接收消息类型
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)

  switch(data.type) {
    case 'game_started':      // 游戏开始
    case 'cards_dealt':       // 底牌已发放
    case 'community_cards':   // 公共牌更新
    case 'player_action':     // 玩家动作
    case 'showdown':          // 摊牌结果
  }
}
```

---

## 💻 开发指南

### 数据库迁移

```bash
# 生成迁移文件
cd backend
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 测试

```bash
# 运行完整游戏流程测试
python test_game_flow.py

# 预期输出：
# ✅ 测试创建游戏
# ✅ 测试开始游戏
# ✅ 测试发底牌
# ✅ 测试玩家操作
# ✅ 测试发翻牌/转牌/河牌
# ✅ 测试摊牌
# ✅ 测试牌型评估器
```

### 代码风格

**Python (后端):**
```bash
# 使用black格式化
black backend/app

# 使用flake8检查
flake8 backend/app --max-line-length=100
```

**JavaScript (前端):**
```bash
# 使用ESLint
npm run lint

# 自动修复
npm run lint:fix
```

---

## 📚 部署文档

### Amazon Linux部署

详细文档请参阅：
- 📖 [README-DEPLOYMENT.md](README-DEPLOYMENT.md) - 完整部署指南
- ⚡ [QUICK-START.md](QUICK-START.md) - 快速部署指南
- ✅ [DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md) - 部署检查清单

**一键部署命令：**
```bash
chmod +x deploy-amazon-linux.sh
sudo bash deploy-amazon-linux.sh
```

### 服务管理

```bash
# 使用重启脚本（推荐）
bash restart.sh

# 手动管理
docker-compose start      # 启动
docker-compose stop       # 停止
docker-compose restart    # 重启
docker-compose logs -f    # 查看日志
```

---

## 📝 更新日志

### v1.0.0 (2026-01-12) - 第一阶段完成

#### ✅ 已完成功能

**核心游戏逻辑 (90%)**
- ✅ 完整的德州扑克引擎 (poker.py)
- ✅ 牌型评估算法 (hand_evaluator.py) - 10种牌型
- ✅ 摊牌和奖池分配
- ✅ 玩家操作处理（弃牌/过牌/跟注/加注/All-in）
- ⏳ 边池逻辑（开发中）

**前端游戏界面 (85%)**
- ✅ 精美游戏桌面UI重构
- ✅ 扑克牌组件 (PlayingCard.vue)
- ✅ 玩家座位组件 (PlayerSeat.vue)
- ✅ 实时游戏日志
- ✅ 玩家操作面板
- ✅ WebSocket实时通信
- ⏳ Dashboard真实数据连接（开发中）

**AI和分析 (80%)**
- ✅ 智能发牌引擎
- ✅ 玩家行为分析
- ✅ 玩家类型分类
- ✅ 技术水平评估

**部署和运维 (95%)**
- ✅ Docker容器化
- ✅ Amazon Linux部署脚本
- ✅ 7种重启方式工具
- ✅ 健康检查脚本
- ✅ 完整文档

#### 🐛 已修复Bug
- ✅ 手牌显示问题 - playerCards索引错误
- ✅ handleWsMessage重复定义
- ✅ 数据库初始化错误
- ✅ Docker Buildx版本问题
- ✅ WebSocket连接稳定性

#### 📝 已知问题
1. Dashboard和PlayerStats使用模拟数据（需连接真实API）
2. 游戏状态仅存内存（需Redis持久化）
3. 缺少玩家超时机制
4. 边池逻辑未实现
5. API缺少JWT认证

#### 🔮 下一步计划
- [ ] 连接Dashboard到真实API
- [ ] 实现游戏状态Redis持久化
- [ ] 添加玩家超时自动弃牌
- [ ] 实现完整边池逻辑
- [ ] 添加API JWT认证保护

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📧 联系方式

- 项目主页: https://github.com/your-repo/dzpoker
- 问题反馈: https://github.com/your-repo/dzpoker/issues
- 邮箱: your-email@example.com

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库
- [PostgreSQL](https://www.postgresql.org/) - 强大的开源数据库
- [Redis](https://redis.io/) - 高性能缓存系统

---

**🎮 祝您游戏愉快！**
