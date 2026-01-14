# 数据分析前端使用指南

## 概述

数据分析页面提供了可视化的游戏数据分析界面，包括整体统计、手牌分布、位置分析和游戏历史记录。

## 访问方式

### 方式1：通过游戏页面导航
1. 进入游戏页面 `http://localhost:3000/game/{game_id}`
2. 点击顶部的 "数据分析" 按钮（蓝色按钮，带数据图标）
3. 自动跳转到数据分析页面

### 方式2：直接访问
直接访问 `http://localhost:3000/analytics`

## 功能说明

### 1. 整体统计（顶部卡片）

显示最近N天的游戏统计数据：
- **总游戏数**: 所有游戏数量
- **已完成**: 已结束的游戏数量
- **总底池**: 所有已完成游戏的总底池金额
- **平均时长**: 平均每局游戏的时长（秒）
- **最大底池游戏**: 单局最高底池的游戏信息

**操作**:
- 使用下拉框选择统计时间范围（7天/30天/90天）
- 点击刷新按钮重新加载数据

### 2. 手牌类型分布

以横向条形图展示各种手牌类型的出现频率：
- 显示每种牌型的数量和百分比
- 统计最近200局（可配置）
- 牌型包括：一对、两对、三条、顺子、同花、葫芦、四条、同花顺等

**颜色说明**:
- 蓝色渐变条形图显示相对频率
- 条形图上显示具体数量

### 3. 位置胜率分析

表格形式展示不同位置的统计数据：

| 列名 | 说明 |
|------|------|
| 位置 | 按钮位置（BTN/SB/BB/UTG/MP/CO） |
| 总手数 | 该位置玩了多少手牌 |
| 胜利次数 | 赢牌次数 |
| 胜率 | 胜利次数 / 总手数 × 100% |
| 平均盈利 | 该位置的平均盈亏 |

**颜色说明**:
- 绿色数字：正盈利
- 红色数字：负盈利
- 进度条：直观显示胜率

**位置说明**:
- BTN (Button): 庄家位置，最后行动，位置最好
- SB (Small Blind): 小盲注
- BB (Big Blind): 大盲注
- UTG (Under The Gun): 枪口位置，第一个行动
- MP (Middle Position): 中间位置
- CO (Cut Off): 庄家右边

### 4. 游戏历史记录

分页表格显示所有游戏记录：

**列说明**:
- **游戏ID**: 游戏的唯一标识符
- **玩家数**: 参与游戏的玩家数量
- **盲注**: 小盲/大盲金额
- **底池**: 游戏总底池
- **状态**: waiting/playing/finished
- **开始时间**: 游戏开始的时间
- **时长**: 游戏持续时间（秒）

**操作**:
1. 使用状态筛选器过滤游戏（全部/已完成/进行中/等待中）
2. 点击"查看详情"按钮查看完整游戏信息
3. 使用分页控件浏览历史记录

### 5. 游戏详情弹窗

点击"查看详情"后显示完整游戏信息：

**基本信息**:
- 游戏UUID、玩家数量
- 盲注级别、总底池
- 开始/结束时间、状态

**玩家手牌信息** (展开式表格):
- 玩家ID和位置
- 底牌（hole cards）
- 最终牌型
- 盈亏金额
- 是否获胜

**玩家动作详情** (二级展开):
展开每个玩家可查看其所有动作：
- 动作阶段（preflop/flop/turn/river）
- 动作类型（fold/check/call/raise/all_in）
- 下注金额
- 当时底池大小
- 动作时间

## 数据刷新

所有数据卡片都有独立的刷新按钮，点击即可重新加载最新数据。

## 技术说明

### API端点
页面调用以下后端API：
- `GET /api/analytics/overview` - 整体统计
- `GET /api/analytics/hand-types` - 手牌分布
- `GET /api/analytics/positions` - 位置分析
- `GET /api/analytics/games` - 游戏历史
- `GET /api/analytics/games/{id}` - 游戏详情

详细API文档见: [analytics_api_usage.md](./analytics_api_usage.md)

### 前端技术栈
- Vue 3 Composition API
- Element Plus UI组件库
- Axios HTTP客户端
- 响应式数据绑定

## 部署说明

### 重新部署前端（使新页面生效）

如果数据分析页面无法访问，需要重新构建前端：

**方法1：使用PowerShell脚本（推荐）**
```powershell
cd d:\dzpoker
.\restart-local.ps1
```

**方法2：手动执行Docker命令**
```bash
# 停止服务
docker compose down

# 重新构建前端
docker compose build --no-cache frontend

# 启动服务
docker compose up -d

# 检查状态
docker compose ps
```

**方法3：在服务器上使用部署脚本**
```bash
cd /path/to/dzpoker
bash deploy.sh  # 自动检测变化并构建
```

### 验证部署

1. 访问 `http://localhost:3000/analytics`
2. 应该看到数据分析页面（即使数据为空）
3. 检查浏览器开发者工具的Console，确保没有404错误

## 常见问题

### Q: 点击"数据分析"按钮没反应
A: 检查浏览器控制台是否有路由错误，可能需要重新构建前端

### Q: 页面显示但没有数据
A: 需要先玩几局游戏生成数据，数据在每局结束时自动保存

### Q: 数据加载很慢
A: 减少统计的游戏数量（如手牌分布从200改为100）

### Q: 整体统计显示空数据
A: 确保数据库中有已完成的游戏记录（status='finished'）

## 开发说明

### 文件位置
- 前端页面: `frontend/src/views/Analytics.vue`
- 路由配置: `frontend/src/router/index.js`
- 游戏页面: `frontend/src/views/GameTable.vue` (添加了导航按钮)

### 修改和扩展

如需修改页面样式或添加新功能：
1. 编辑 `Analytics.vue` 文件
2. 运行 `npm run build` 构建
3. 重新部署前端容器

如需添加新的分析API：
1. 在 `backend/app/services/analytics_service.py` 添加方法
2. 在 `backend/app/routers/analytics.py` 添加路由
3. 在 `Analytics.vue` 中调用新API并展示数据
