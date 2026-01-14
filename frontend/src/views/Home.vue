<template>
  <div class="home">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="poker-card card-1">♠</div>
      <div class="poker-card card-2">♥</div>
      <div class="poker-card card-3">♣</div>
      <div class="poker-card card-4">♦</div>
    </div>

    <!-- 主标题区域 -->
    <div class="hero">
      <div class="logo-section">
        <div class="logo">🎰</div>
        <h1 class="title">德州扑克 AI 系统</h1>
        <p class="subtitle">智能发牌算法 · 数据分析 · AI策略优化</p>
      </div>

      <div class="quick-actions">
        <el-button
          type="primary"
          size="large"
          @click="createGame"
          class="main-action-btn"
        >
          <el-icon><Trophy /></el-icon>
          <span>开始游戏</span>
        </el-button>
        <el-button
          size="large"
          @click="goToAnalytics"
          class="secondary-action-btn"
        >
          <el-icon><DataAnalysis /></el-icon>
          <span>数据分析</span>
        </el-button>
      </div>
    </div>

    <!-- 功能导航卡片 -->
    <div class="navigation-cards">
      <el-row :gutter="24">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="nav-card" @click="createGame">
            <div class="nav-card-icon game-icon">🎮</div>
            <h3>创建游戏</h3>
            <p>快速创建新游戏房间</p>
            <div class="nav-card-footer">
              <span>点击进入</span>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="nav-card" @click="goToAnalytics">
            <div class="nav-card-icon analytics-icon">📊</div>
            <h3>数据分析</h3>
            <p>查看历史数据和统计</p>
            <div class="nav-card-footer">
              <span>点击进入</span>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="nav-card" @click="goToStats">
            <div class="nav-card-icon stats-icon">👤</div>
            <h3>玩家统计</h3>
            <p>个人数据和战绩</p>
            <div class="nav-card-footer">
              <span>点击进入</span>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="nav-card" @click="goToSimulation">
            <div class="nav-card-icon sim-icon">⚙️</div>
            <h3>游戏模拟</h3>
            <p>AI策略测试和优化</p>
            <div class="nav-card-footer">
              <span>点击进入</span>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 系统特性 -->
    <div class="features-section">
      <h2 class="section-title">核心特性</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <div class="feature-item">
            <div class="feature-icon">🎴</div>
            <h3>智能发牌系统</h3>
            <p>基于AI的智能发牌策略，在公平性约束内提升游戏娱乐性和策略深度</p>
            <ul class="feature-list">
              <li>公平随机算法</li>
              <li>多种发牌模式</li>
              <li>实时策略调整</li>
            </ul>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="8">
          <div class="feature-item">
            <div class="feature-icon">📈</div>
            <h3>数据分析平台</h3>
            <p>完整的游戏数据记录和深度分析，帮助了解玩家行为和游戏趋势</p>
            <ul class="feature-list">
              <li>游戏历史记录</li>
              <li>手牌类型分布</li>
              <li>位置胜率分析</li>
            </ul>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="8">
          <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <h3>AI 策略引擎</h3>
            <p>多种AI玩家类型，真实模拟不同风格的人类玩家行为模式</p>
            <ul class="feature-list">
              <li>5种玩家类型</li>
              <li>自适应决策</li>
              <li>策略优化学习</li>
            </ul>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 统计数据展示 -->
    <div class="stats-overview" v-if="systemStats">
      <h2 class="section-title">系统概览</h2>
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6">
          <div class="stat-box">
            <div class="stat-value">{{ systemStats.total_games || 0 }}</div>
            <div class="stat-label">总游戏数</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-box">
            <div class="stat-value">{{ systemStats.finished_games || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-box">
            <div class="stat-value">{{ formatLargeNumber(systemStats.total_pot) }}</div>
            <div class="stat-label">总底池</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-box">
            <div class="stat-value">{{ formatDuration(systemStats.avg_duration_seconds) }}</div>
            <div class="stat-label">平均时长</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 创建游戏弹窗 -->
    <el-dialog v-model="showCreateDialog" title="创建新游戏" width="400px">
      <el-form :model="gameForm" label-width="100px">
        <el-form-item label="玩家数量">
          <el-input-number v-model="gameForm.numPlayers" :min="2" :max="10" />
        </el-form-item>
        <el-form-item label="小盲注">
          <el-input-number v-model="gameForm.smallBlind" :min="1" />
        </el-form-item>
        <el-form-item label="大盲注">
          <el-input-number v-model="gameForm.bigBlind" :min="2" />
        </el-form-item>
        <el-form-item label="智能发牌">
          <el-switch v-model="gameForm.smartDealing" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Trophy, DataAnalysis, ArrowRight } from '@element-plus/icons-vue'
import { createGame as apiCreateGame } from '@/api'
import axios from 'axios'

const router = useRouter()
const showCreateDialog = ref(false)
const creating = ref(false)
const systemStats = ref(null)

const gameForm = reactive({
  numPlayers: 6,
  smallBlind: 1,
  bigBlind: 2,
  smartDealing: true
})

// 加载系统统计数据
const loadSystemStats = async () => {
  try {
    const { data } = await axios.get('/api/analytics/overview?days=30')
    systemStats.value = data
  } catch (err) {
    console.error('Failed to load system stats:', err)
  }
}

const createGame = () => {
  showCreateDialog.value = true
}

const goToDashboard = () => {
  router.push('/dashboard')
}

const goToAnalytics = () => {
  router.push('/analytics')
}

const goToStats = () => {
  router.push('/stats')
}

const goToSimulation = () => {
  router.push('/simulation')
}

const confirmCreate = async () => {
  creating.value = true
  try {
    const res = await apiCreateGame({
      num_players: gameForm.numPlayers,
      small_blind: gameForm.smallBlind,
      big_blind: gameForm.bigBlind
    })

    ElMessage.success('游戏创建成功!')
    showCreateDialog.value = false
    router.push(`/game/${res.game_id}`)
  } catch (err) {
    ElMessage.error('创建失败: ' + (err.message || '未知错误'))
  } finally {
    creating.value = false
  }
}

const formatLargeNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toLocaleString()
}

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

onMounted(() => {
  loadSystemStats()
})
</script>

<style scoped>
.home {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
  min-height: 100vh;
}

/* 背景装饰 */
.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.poker-card {
  position: absolute;
  font-size: 120px;
  opacity: 0.03;
  color: #409eff;
  animation: float 20s infinite ease-in-out;
}

.card-1 {
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.card-2 {
  top: 60%;
  right: 15%;
  animation-delay: 5s;
  color: #e94560;
}

.card-3 {
  bottom: 20%;
  left: 20%;
  animation-delay: 10s;
}

.card-4 {
  top: 30%;
  right: 25%;
  animation-delay: 15s;
  color: #f39c12;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(10deg);
  }
}

/* 主标题区域 */
.hero {
  text-align: center;
  padding: 60px 20px 80px;
  position: relative;
  z-index: 1;
}

.logo-section {
  margin-bottom: 40px;
}

.logo {
  font-size: 80px;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.title {
  font-size: 56px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
  letter-spacing: 2px;
}

.subtitle {
  font-size: 20px;
  color: #909399;
  margin-bottom: 0;
}

.quick-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.main-action-btn,
.secondary-action-btn {
  min-width: 180px;
  height: 50px;
  font-size: 16px;
  border-radius: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.main-action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.main-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.secondary-action-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.secondary-action-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

/* 功能导航卡片 */
.navigation-cards {
  margin: 40px 0;
  position: relative;
  z-index: 1;
}

.nav-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 30px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  backdrop-filter: blur(10px);
}

.nav-card:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
}

.nav-card-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: inline-block;
  transition: transform 0.3s ease;
}

.nav-card:hover .nav-card-icon {
  transform: scale(1.2) rotate(5deg);
}

.nav-card h3 {
  font-size: 20px;
  color: #ffffff;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.nav-card p {
  font-size: 14px;
  color: #909399;
  margin: 0;
  line-height: 1.6;
}

.nav-card-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  color: #667eea;
  font-size: 14px;
  font-weight: 500;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.nav-card:hover .nav-card-footer {
  opacity: 1;
}

/* 系统特性 */
.features-section {
  margin: 80px 0;
  position: relative;
  z-index: 1;
}

.section-title {
  text-align: center;
  font-size: 36px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 50px;
  position: relative;
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

.feature-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 32px 24px;
  height: 100%;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.feature-item .feature-icon {
  font-size: 56px;
  margin-bottom: 20px;
  display: block;
}

.feature-item h3 {
  font-size: 22px;
  color: #ffffff;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.feature-item > p {
  color: #909399;
  line-height: 1.8;
  margin-bottom: 20px;
  font-size: 14px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  color: #606266;
  padding: 8px 0;
  font-size: 14px;
  position: relative;
  padding-left: 20px;
}

.feature-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #67c23a;
  font-weight: bold;
}

/* 统计数据展示 */
.stats-overview {
  margin: 60px 0;
  padding: 40px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 20px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  position: relative;
  z-index: 1;
}

.stat-box {
  text-align: center;
  padding: 24px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-box:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-4px);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .title {
    font-size: 36px;
  }

  .subtitle {
    font-size: 16px;
  }

  .logo {
    font-size: 60px;
  }

  .nav-card {
    margin-bottom: 16px;
  }

  .section-title {
    font-size: 28px;
  }

  .quick-actions {
    flex-direction: column;
    align-items: center;
  }

  .main-action-btn,
  .secondary-action-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>
