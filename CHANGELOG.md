# 📝 更新日志 (Changelog)

所有重要的项目更改都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.0.0] - 2026-01-12

### 🎉 第一阶段完成 - 核心功能实现

#### ✨ 新增功能

**游戏核心 (Core Game Logic)**
- ✅ 完整的德州扑克游戏引擎 (`backend/app/core/poker.py`)
  - 支持2-9人桌
  - 完整的游戏状态机（等待/翻牌前/翻牌圈/转牌圈/河牌圈/摊牌/结束）
  - 玩家操作处理（弃牌/过牌/跟注/加注/All-in）
  - 盲注管理和下注轮次控制
  - 奖池分配和结算

- ✅ 牌型评估算法 (`backend/app/core/hand_evaluator.py`)
  - 10种完整牌型判断（皇家同花顺→高牌）
  - 基于组合数学的最优5张牌评估（C(7,5)=21种组合）
  - 支持平局判定
  - 牌型中文描述生成

- ✅ 摊牌功能 (`backend/app/routers/games.py`)
  - 自动计算获胜者
  - 支持多人平局情况
  - 奖池自动分配

**前端界面 (Frontend UI)**
- ✅ 全新游戏桌面UI (`frontend/src/views/GameTable.vue`)
  - 仿真德州扑克椭圆桌面设计
  - 深色主题渐变背景
  - 玩家座位上下分布（支持2-9人）
  - 公共牌区域和底池显示
  - 实时游戏日志系统
  - WebSocket连接状态指示

- ✅ 扑克牌组件 (`frontend/src/components/PlayingCard.vue`)
  - 精美扑克牌显示效果
  - 红黑花色自动区分
  - 翻牌动画效果
  - 3种尺寸支持（small/normal/large）
  - 渐变牌背图案

- ✅ 玩家座位组件 (`frontend/src/components/PlayerSeat.vue`)
  - 圆形玩家头像
  - 位置标识（BTN/SB/BB/UTG/MP/CO）
  - 筹码千分位格式化
  - 当前下注悬浮显示
  - 手牌显示/隐藏切换
  - 状态标签（All-In/弃牌）
  - 当前用户金色高亮

- ✅ 玩家操作面板
  - 大号操作按钮（弃牌/过牌/跟注/加注/All-in）
  - 图标+文字组合设计
  - 智能按钮禁用状态
  - 加注金额滑块
  - 操作提示动画

**AI和分析 (AI & Analytics)**
- ✅ 智能发牌引擎 (`backend/app/ai/smart_dealer.py`)
  - 权重调整系统（活跃度/连续输牌/技能等级）
  - 公平性约束（±15%调整范围）
  - 手牌强度评估
  - 概率性重抽机制

- ✅ 玩家行为分析 (`backend/app/ai/analyzer.py`)
  - VPIP（自愿入池率）计算
  - PFR（翻前加注率）计算
  - AF（激进因子）计算
  - 3-bet率和WTSD（摊牌率）统计

- ✅ 玩家类型分类
  - 紧凶型（TAG）识别
  - 松凶型（LAG）识别
  - 被动型识别
  - 鱼（Fish）识别
  - 常规型识别

- ✅ 技能评分系统（0-100分）
  - VPIP合理性评分（20分）
  - PFR合理性评分（20分）
  - PFR/VPIP比例评分（15分）
  - 激进因子评分（15分）
  - 基础分（30分）

**API端点 (API Endpoints)**
- ✅ 游戏管理API（14个端点）
  - POST `/api/games` - 创建游戏
  - GET `/api/games/{game_id}` - 获取游戏状态
  - POST `/api/games/{game_id}/start` - 开始游戏
  - POST `/api/games/{game_id}/deal` - 发底牌（支持智能模式）
  - POST `/api/games/{game_id}/flop` - 发翻牌
  - POST `/api/games/{game_id}/turn` - 发转牌
  - POST `/api/games/{game_id}/river` - 发河牌
  - POST `/api/games/{game_id}/action/{player_id}` - 玩家操作
  - POST `/api/games/{game_id}/showdown` - 摊牌
  - WebSocket `/api/games/ws/{game_id}` - 实时通信

- ✅ 玩家管理API（8个端点）
  - POST `/api/players/register` - 用户注册
  - POST `/api/players/login` - 用户登录
  - GET `/api/players/{player_id}` - 获取玩家信息
  - GET `/api/players/{player_id}/stats` - 获取玩家统计
  - GET `/api/players/{player_id}/profile` - 获取玩家画像
  - GET `/api/players` - 获取玩家列表

**实时通信 (Real-time Communication)**
- ✅ WebSocket集成
  - 游戏开始通知（game_started）
  - 底牌发放通知（cards_dealt）
  - 公共牌更新通知（community_cards）
  - 玩家动作广播（player_action）
  - 摊牌结果推送（showdown）
  - 心跳机制（ping/pong）
  - 自动重连功能

**部署工具 (Deployment Tools)**
- ✅ Amazon Linux自动部署脚本 (`deploy-amazon-linux.sh`)
  - 自动检测系统版本（AL2/AL2023）
  - Docker和Docker Compose安装
  - 防火墙配置
  - 环境变量生成
  - Systemd服务创建

- ✅ 服务重启工具 (`restart.sh`)
  - 7种重启方式
  - 交互式菜单
  - 自动健康检查
  - 彩色输出提示

- ✅ Docker冲突修复工具 (`fix-docker-conflicts.sh`)
  - 5种修复策略
  - Podman冲突处理

- ✅ Buildx升级脚本 (`fix-buildx.sh`)
  - 自动下载最新版本
  - 用户和root双重安装

- ✅ 健康检查脚本 (`health-check.sh`)
  - 容器状态检查
  - 服务健康验证
  - 资源使用监控

**测试 (Testing)**
- ✅ 完整游戏流程测试 (`test_game_flow.py`)
  - 创建游戏测试
  - 发牌测试
  - 玩家操作测试
  - 公共牌发放测试
  - 摊牌测试
  - 牌型评估器单元测试

**文档 (Documentation)**
- ✅ 项目README (`README.md`) - 完整项目说明
- ✅ 快速部署指南 (`QUICK-START.md`) - 5分钟快速部署
- ✅ 详细部署文档 (`README-DEPLOYMENT.md`) - 完整部署指南
- ✅ 部署检查清单 (`DEPLOYMENT-CHECKLIST.md`) - 逐步验证
- ✅ 系统架构设计 (`系统架构设计.md`) - 架构说明
- ✅ 第一阶段开发总结 (`开发总结-第一阶段.md`) - 工作总结

#### 🐛 修复Bug

**前端Bug修复**
- ✅ 修复手牌显示问题
  - 问题：玩家手牌不显示或显示错误
  - 原因：playerCards索引使用`idx+1`而非实际player_id
  - 修复：使用`gameState.value.players[idx]?.player_id`正确映射
  - 影响文件：`frontend/src/views/GameTable.vue`
  - 提交：ea65ebb

- ✅ 修复handleWsMessage重复定义
  - 问题：WebSocket消息处理函数被重复定义，导致消息处理异常
  - 原因：代码中存在两个handleWsMessage函数定义
  - 修复：合并为单一函数，统一处理所有消息类型
  - 影响文件：`frontend/src/views/GameTable.vue`
  - 提交：e984ad6

- ✅ 添加手牌隐私保护
  - 问题：所有玩家的手牌都显示给所有人
  - 修复：添加条件判断，只显示当前玩家自己的手牌
  - 其他玩家显示牌背图案
  - 提交：ea65ebb

**后端Bug修复**
- ✅ 修复数据库初始化错误
  - 问题：init.sql尝试INSERT到不存在的表
  - 原因：表由SQLAlchemy自动创建，init.sql不应包含INSERT
  - 修复：删除所有INSERT语句，仅保留扩展创建
  - 影响文件：`backend/init.sql`

**部署Bug修复**
- ✅ 修复Docker/Podman冲突
  - 问题：Amazon Linux预装podman与Docker冲突
  - 修复：添加`--allowerasing`标志到yum install命令
  - 影响文件：`deploy-amazon-linux.sh`

- ✅ 修复Docker Buildx版本过旧
  - 问题：compose build报错"requires buildx 0.17 or later"
  - 修复：创建Buildx升级脚本，自动下载v0.30.1
  - 新增文件：`fix-buildx.sh`

- ✅ 移除Docker Compose版本警告
  - 问题：Docker Compose v2不再需要version字段
  - 修复：删除docker-compose.yml中的`version: '3.8'`
  - 影响文件：`docker-compose.yml`, `docker-compose.prod.yml`

**WebSocket优化**
- ✅ 添加自动重连机制
  - 连接断开后3秒自动尝试重连
  - 连接状态实时显示
  - 影响文件：`frontend/src/views/GameTable.vue`
  - 提交：e984ad6

#### 📝 已知问题 (Known Issues)

1. **Dashboard和PlayerStats使用模拟数据**
   - 影响：仪表盘和玩家统计页面无法显示真实数据
   - 优先级：中
   - 计划：Phase 2修复

2. **游戏状态仅存内存**
   - 影响：服务器重启后所有游戏丢失
   - 风险：高
   - 计划：实现Redis持久化

3. **缺少玩家超时机制**
   - 影响：一个玩家不操作会卡住整个游戏
   - 优先级：高
   - 计划：添加30秒超时自动弃牌

4. **边池逻辑未实现**
   - 影响：多人All-in场景无法正确分配底池
   - 优先级：中
   - 计划：实现完整边池算法

5. **API缺少JWT认证**
   - 影响：任何人都可以调用游戏API
   - 风险：高
   - 计划：添加JWT中间件验证

#### ⚠️ 废弃功能 (Deprecated)

- 无

#### 🔒 安全更新 (Security)

- ✅ 密码使用bcrypt加密存储
- ✅ JWT Token 24小时自动过期
- ⚠️ API端点缺少认证（待修复）

#### 🎯 性能优化 (Performance)

- ✅ 使用异步SQLAlchemy提升数据库性能
- ✅ Redis缓存游戏状态
- ✅ WebSocket减少HTTP轮询开销

#### 📊 统计数据 (Statistics)

**代码量**
- 后端Python代码：~5000行
- 前端Vue/JS代码：~3500行
- 测试代码：~500行
- 总计：~9000行

**文件数量**
- 后端文件：25个
- 前端文件：18个
- 配置文件：12个
- 文档文件：8个
- 脚本文件：7个
- 总计：70个

**功能完成度**
- 核心游戏逻辑：90%
- 前端UI：85%
- AI分析：80%
- 部署工具：95%
- 文档：85%
- 测试覆盖：30%
- **总体**：**76%**

---

## [未发布] - 开发中

### 🔮 计划功能 (Planned)

**Phase 2: 数据和稳定性**
- [ ] 连接Dashboard到真实API
- [ ] 连接PlayerStats到真实API
- [ ] 实现游戏状态Redis持久化
- [ ] 添加玩家超时自动弃牌机制
- [ ] 实现完整边池（Side Pot）逻辑
- [ ] 为所有游戏API添加JWT认证

**Phase 3: 高级功能**
- [ ] 游戏回放功能
- [ ] 观战模式
- [ ] 聊天系统
- [ ] 排行榜
- [ ] 成就系统
- [ ] 数据可视化图表

**Phase 4: AI增强**
- [ ] 智能发牌算法验证和优化
- [ ] AI决策模型
- [ ] 对手建模
- [ ] 概率计算器
- [ ] 策略建议系统升级

**Phase 5: 生产环境**
- [ ] 负载均衡
- [ ] 数据库主从复制
- [ ] Redis集群
- [ ] 监控和告警
- [ ] 日志聚合
- [ ] 自动化运维

---

## 版本号说明

- **主版本号 (Major)**: 不兼容的API修改
- **次版本号 (Minor)**: 向下兼容的功能性新增
- **修订号 (Patch)**: 向下兼容的问题修正

---

## 链接

- [项目主页](https://github.com/your-repo/dzpoker)
- [问题反馈](https://github.com/your-repo/dzpoker/issues)
- [提交历史](https://github.com/your-repo/dzpoker/commits/master)

---

**最后更新**: 2026-01-12
