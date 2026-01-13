# 🃏 德州扑克 AI 系统 (DZPoker)

基于 AI 的德州扑克发牌算法测试平台，集成 AI 决策引擎、实时游戏和自动模拟功能。

**生产环境**: http://13.212.252.171:3000

---

## 🚀 快速开始

### 本地运行

```bash
docker-compose up -d

# 访问
前端: http://localhost:3000
后端: http://localhost:8000
API文档: http://localhost:8000/docs
```

### EC2 部署

有三种部署方式：

#### 1. 快速部署（推荐，2-3分钟）

重新构建前端，后端使用现有镜像：

```bash
ssh ubuntu@13.212.252.171
cd dzpoker
bash restart.sh
```

**说明**: 前端是编译型的，JavaScript 改动必须重新构建。后端 Python 代码可以直接加载。

#### 2. 智能部署（2-7分钟）

自动检测变化，只重新构建修改的服务：

```bash
ssh ubuntu@13.212.252.171
cd dzpoker
bash deploy.sh
```

#### 3. 完全重新构建（5-7分钟）

适用于依赖变化（如 requirements.txt, package.json）：

```bash
ssh ubuntu@13.212.252.171
cd dzpoker

git fetch origin && \
git reset --hard origin/master && \
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
docker-compose down && \
docker-compose build --no-cache api frontend && \
docker-compose up -d
```

---

## ✅ 验证部署

### 1. 检查服务

```bash
docker-compose ps        # 所有容器应显示 Up
docker logs api --tail 50  # 无错误信息
```

### 2. 测试 API

```bash
# 创建游戏
curl -X POST http://localhost:8000/api/games \
  -H "Content-Type: application/json" \
  -d '{"num_players": 4, "small_blind": 10, "big_blind": 20}'

# 复制返回的 game_id，然后：
GAME_ID="YOUR_GAME_ID"
curl -X POST http://localhost:8000/api/games/$GAME_ID/start
curl -X POST http://localhost:8000/api/games/$GAME_ID/ai-action
```

**成功标志**: 返回 `{"success": true, "action": ...}`

### 3. 浏览器测试

访问 http://13.212.252.171:3000，创建游戏 → 开始游戏 → 点击"自动游戏"

**应该看到**:
- ✅ 游戏自动进行（preflop → flop → turn → river → showdown）
- ✅ 无任何错误
- ✅ 正常显示获胜者

---

## 🏗️ 技术栈

**后端**: FastAPI + PostgreSQL + Redis + WebSocket
**前端**: Vue 3 + Vite + Element Plus
**AI**: 5 种玩家类型（TAG, LAG, PASSIVE, FISH, REGULAR）

---

## 📁 项目结构

```
dzpoker/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── poker.py              # 游戏引擎
│   │   │   ├── hand_evaluator.py     # 手牌评估
│   │   │   └── config.py             # 配置
│   │   ├── ai/
│   │   │   └── decision_maker.py     # AI 决策引擎
│   │   ├── routers/
│   │   │   ├── games.py              # 游戏 API
│   │   │   ├── players.py            # 玩家 API
│   │   │   └── simulation.py         # 模拟 API
│   │   └── main.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue         # 仪表盘
│   │   │   ├── GameTable.vue         # 游戏桌
│   │   │   └── PlayerStats.vue       # 统计
│   │   ├── components/               # UI 组件
│   │   ├── api/                      # API 封装
│   │   └── router/                   # 路由
│   ├── nginx.conf
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🎮 核心功能

### 完整游戏流程
- 创建游戏（2-10 人）
- 自动发牌和盲注
- Preflop → Flop → Turn → River → Showdown
- 手牌评估和获胜者判定

### AI 自动游戏
- 5 种 AI 玩家风格
- 基于手牌强度、位置、筹码的智能决策
- 完全自动化游戏模拟

### 实时更新
- WebSocket 实时通信
- 游戏状态自动同步

---

## 🔧 开发

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### 测试

```bash
# 后端
cd backend
pytest

# 前端
cd frontend
npm run test
```

---

## 🐛 故障排查

### Git 冲突

```bash
git fetch origin
git reset --hard origin/master
```

### 容器问题

```bash
# 查看日志
docker logs api --tail 100

# 重启
docker-compose down
docker-compose up -d --build
```

### Python 缓存

```bash
find backend -type d -name __pycache__ -exec rm -rf {} +
find backend -type f -name "*.pyc" -delete
```

---

## 📊 API 文档

### 游戏 API

- `POST /api/games` - 创建游戏
- `GET /api/games/{id}` - 获取状态
- `POST /api/games/{id}/start` - 开始游戏
- `POST /api/games/{id}/action` - 玩家动作
- `POST /api/games/{id}/ai-action` - AI 动作
- `POST /api/games/{id}/showdown` - 摊牌

### WebSocket

- `ws://{host}:8000/api/games/ws/{game_id}` - 实时更新

**完整文档**: http://localhost:8000/docs

---

## 📝 最近更新

**2026-01-12** - 修复所有错误
- ✅ 500 错误：添加 `get_current_player()` 方法
- ✅ 400 错误：移除重复发牌调用
- ✅ CORS 错误：统一 API 调用方式

**提交历史**:
```
5199d1e - 添加最终修复总结文档
d015f40 - 修复 400 错误：移除 runAutoGame 中的重复发牌调用
92566d4 - 修复 CORS 错误：统一使用 API 封装调用 showdown
917efce - 修复 500 错误：添加 get_current_player() 方法
```

---

## 🗺️ 后续计划

- [ ] 游戏状态持久化到 Redis
- [ ] 玩家超时自动弃牌
- [ ] 边池（Side Pot）逻辑
- [ ] JWT 认证
- [ ] 玩家统计和排行榜

---

## 📄 许可证

MIT License

---

生成时间: 2026-01-12
