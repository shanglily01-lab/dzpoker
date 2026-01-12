# 🔧 修复 502 Bad Gateway 错误

## 问题描述

Dashboard 页面访问时出现 502 Bad Gateway 错误：
```
Failed to load resource: the server responded with a status of 502 (Bad Gateway)
```

## 原因分析

后端容器正在运行旧代码，缺少新添加的 API 端点：
- `/api/games/stats` - 游戏统计数据
- `/api/games/list` - 游戏列表

需要重新构建后端容器以包含最新代码。

---

## 🚀 快速修复（推荐）

在 EC2 服务器 (http://13.212.252.171) 上执行：

### 方法1: 使用自动更新脚本

```bash
# 1. SSH 连接到服务器
ssh -i your-key.pem ec2-user@13.212.252.171

# 2. 进入项目目录
cd /opt/dzpoker

# 3. 拉取最新代码（包含更新脚本）
sudo git pull origin master

# 4. 执行自动更新脚本
sudo chmod +x update-backend.sh
sudo bash update-backend.sh
```

脚本会自动完成：
- ✅ 拉取最新代码
- ✅ 停止后端容器
- ✅ 重新构建后端镜像
- ✅ 启动后端容器
- ✅ 测试新端点

---

## 🔍 手动修复（备选）

如果自动脚本失败，可以手动执行：

### 步骤1: 连接服务器

```bash
ssh -i your-key.pem ec2-user@13.212.252.171
```

### 步骤2: 拉取最新代码

```bash
cd /opt/dzpoker
sudo git pull origin master
```

### 步骤3: 重新构建后端

```bash
# 停止后端容器
sudo docker-compose stop api

# 重新构建（不使用缓存）
sudo docker-compose build --no-cache api

# 启动后端容器
sudo docker-compose up -d api
```

### 步骤4: 等待服务启动

```bash
# 等待10秒
sleep 10

# 查看容器状态
sudo docker-compose ps api
```

### 步骤5: 检查日志

```bash
# 查看最近日志
sudo docker-compose logs --tail=50 api
```

### 步骤6: 测试新端点

```bash
# 测试统计端点
curl http://localhost:8000/api/games/stats

# 测试列表端点
curl http://localhost:8000/api/games/list
```

**预期输出:**
```json
# /api/games/stats
{
  "total_games": 0,
  "active_games": 0,
  "finished_games": 0,
  "total_players": 0,
  "total_hands": 0,
  "total_pot": 0
}

# /api/games/list
[]
```

---

## ✅ 验证修复

### 1. 检查后端 API

访问 Swagger 文档：
```
http://13.212.252.171:8000/docs
```

应该能看到新添加的端点：
- `GET /api/games/stats` - 获取游戏统计数据
- `GET /api/games/list` - 获取游戏列表

### 2. 检查前端 Dashboard

访问前端应用：
```
http://13.212.252.171:3000
```

Dashboard 页面应该能正常显示：
- 总游戏数
- 总玩家数
- 进行中游戏
- 总手牌数
- 最近游戏列表

### 3. 浏览器控制台

打开浏览器开发者工具 (F12)，查看 Network 标签：
- `/api/games/stats` 应该返回 200 OK
- `/api/games/list` 应该返回 200 OK

---

## 🐛 如果仍然失败

### 选项1: 完全重启所有服务

```bash
cd /opt/dzpoker
sudo bash restart.sh
# 选择选项 6: 完全重启
```

### 选项2: 查看详细日志

```bash
# 查看所有服务日志
sudo docker-compose logs -f

# 只看后端日志
sudo docker-compose logs -f api

# 只看数据库日志
sudo docker-compose logs -f db
```

### 选项3: 检查数据库连接

```bash
# 测试数据库
sudo docker-compose exec db pg_isready -U postgres

# 连接数据库
sudo docker-compose exec db psql -U postgres -d poker

# 查看表
\dt

# 退出
\q
```

### 选项4: 检查 Redis

```bash
# 测试 Redis
sudo docker-compose exec redis redis-cli ping
```

### 选项5: 检查网络连接

```bash
# 后端能否访问数据库
sudo docker-compose exec api ping db

# 前端能否访问后端
sudo docker-compose exec frontend ping api
```

---

## 📋 完整健康检查

执行完整健康检查脚本：

```bash
cd /opt/dzpoker
sudo docker-compose ps
sudo docker-compose logs --tail=100
```

检查清单：
- [ ] 所有容器状态为 `Up`
- [ ] poker-api 没有错误日志
- [ ] poker-db 状态为 `healthy`
- [ ] poker-redis 正常响应 PING
- [ ] 端点 `/api/games/stats` 返回 JSON
- [ ] 端点 `/api/games/list` 返回数组
- [ ] 前端 Dashboard 正常显示数据

---

## 💡 预防措施

### 每次代码更新后都要重新构建

```bash
# 1. 拉取代码
sudo git pull origin master

# 2. 重新构建
sudo docker-compose build --no-cache

# 3. 重启服务
sudo docker-compose up -d

# 4. 验证
sudo docker-compose ps
```

### 或使用快捷脚本

```bash
# 后端更新
sudo bash update-backend.sh

# 或完全重启
sudo bash restart.sh
# 选择选项 6
```

---

## 📞 获取更多帮助

如果以上方法都无法解决问题：

1. **查看完整故障排查指南**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **检查部署清单**: [DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md)
3. **快速开始指南**: [QUICK-START.md](QUICK-START.md)

---

## 📝 技术细节

### 添加的新端点

**backend/app/routers/games.py**:

```python
@router.get("/stats")
async def get_game_stats():
    """获取游戏统计数据"""
    total_games = len(games)
    active_games = sum(1 for g in games.values()
                      if g.state not in [GameState.WAITING, GameState.FINISHED])
    # ... 更多统计逻辑
    return {
        "total_games": total_games,
        "active_games": active_games,
        "total_players": len(all_players),
        "total_hands": total_hands
    }

@router.get("/list")
async def list_games(limit: int = 10, state: str = None):
    """获取游戏列表"""
    game_list = []
    for game_id, game in games.items():
        if state and game.state.value != state:
            continue
        game_info = {
            "game_id": game_id,
            "num_players": len(game.players),
            "state": game.state.value,
            "pot": game.pot
        }
        game_list.append(game_info)
    return game_list[:limit]
```

### 前端 API 调用

**frontend/src/api/index.js**:

```javascript
export const getGameStats = () => {
  return api.get('/games/stats')
}

export const listGames = (params) => {
  return api.get('/games/list', { params })
}
```

**frontend/src/views/Dashboard.vue**:

```javascript
const loadStats = async () => {
  const data = await getGameStats()
  stats.totalGames = data.total_games
  stats.totalPlayers = data.total_players
  stats.activeGames = data.active_games
  stats.totalHands = data.total_hands
}

const loadRecentGames = async () => {
  const data = await listGames({ limit: 10 })
  recentGames.value = data.map(game => ({
    game_id: game.game_id,
    num_players: game.num_players,
    status: game.state,
    pot: game.pot
  }))
}
```

---

**创建时间**: 2026-01-12
**适用版本**: v1.0.0+
**相关提交**: 0698834, 9a2c1e7
