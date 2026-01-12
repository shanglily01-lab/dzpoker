<template>
  <div class="simulation-container">
    <div class="simulation-header">
      <h2>🎮 自动游戏模拟</h2>
      <el-button @click="goBack" type="info" plain>
        <el-icon><Back /></el-icon>
        返回
      </el-button>
    </div>

    <!-- 创建游戏表单 -->
    <el-card v-if="!currentGameId" class="create-card">
      <template #header>创建模拟游戏</template>
      <el-form :model="gameForm" label-width="100px">
        <el-form-item label="玩家数量">
          <el-input-number v-model="gameForm.numPlayers" :min="2" :max="9" />
        </el-form-item>
        <el-form-item label="小盲注">
          <el-input-number v-model="gameForm.smallBlind" :min="1" />
        </el-form-item>
        <el-form-item label="大盲注">
          <el-input-number v-model="gameForm.bigBlind" :min="2" />
        </el-form-item>
        <el-form-item label="模拟速度">
          <el-slider v-model="simulationSpeed" :min="0.5" :max="5" :step="0.5" show-stops />
          <span class="speed-label">{{ simulationSpeed }}x</span>
        </el-form-item>
        <el-form-item>
          <el-button @click="createAndSimulate" type="primary" size="large" :loading="creating">
            创建并开始模拟
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 模拟进度 -->
    <el-card v-if="simulating" class="progress-card">
      <template #header>
        <div class="card-header">
          <span>模拟进行中...</span>
          <el-tag type="warning" effect="dark">
            <el-icon class="is-loading"><Loading /></el-icon>
            进行中
          </el-tag>
        </div>
      </template>
      <el-progress :percentage="progress" status="success" :stroke-width="20" />
      <div class="current-action">{{ currentAction }}</div>
    </el-card>

    <!-- 游戏记录 -->
    <el-card v-if="gameLog" class="log-card">
      <template #header>
        <div class="card-header">
          <span>游戏记录</span>
          <el-button @click="clearLog" size="small" text>清空</el-button>
        </div>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="(action, index) in gameLog.actions"
          :key="index"
          :timestamp="formatTimestamp(index)"
          :color="getActionColor(action.type)"
        >
          {{ formatAction(action) }}
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 获胜者信息 -->
    <el-card v-if="gameLog && gameLog.winners && gameLog.winners.length > 0" class="winner-card">
      <template #header>
        <div class="card-header">
          <el-icon><Trophy /></el-icon>
          <span>获胜者</span>
        </div>
      </template>
      <div class="winners">
        <div v-for="winner in gameLog.winners" :key="winner.player_id" class="winner-item">
          <div class="winner-avatar">🏆</div>
          <div class="winner-info">
            <div class="winner-name">玩家 P{{ winner.player_id }}</div>
            <div class="winner-hand">{{ winner.hand_description }}</div>
            <div class="winner-chips">赢得 {{ formatChips(winner.winnings) }} 筹码</div>
          </div>
        </div>
      </div>
      <el-divider />
      <el-button @click="simulateAnother" type="primary" size="large">
        再来一局
      </el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, Loading, Trophy } from '@element-plus/icons-vue'
import { createGame, autoPlayGame } from '@/api'

const router = useRouter()

const gameForm = reactive({
  numPlayers: 6,
  smallBlind: 10,
  bigBlind: 20
})

const simulationSpeed = ref(2.0)
const currentGameId = ref(null)
const simulating = ref(false)
const creating = ref(false)
const progress = ref(0)
const currentAction = ref('')
const gameLog = ref(null)

const formatChips = (amount) => {
  if (!amount) return '0'
  return amount.toLocaleString()
}

const goBack = () => {
  router.push('/')
}

const createAndSimulate = async () => {
  creating.value = true
  try {
    // 创建游戏
    const game = await createGame({
      num_players: gameForm.numPlayers,
      small_blind: gameForm.smallBlind,
      big_blind: gameForm.bigBlind
    })

    currentGameId.value = game.game_id
    ElMessage.success('游戏创建成功，开始模拟...')

    // 延迟一下让用户看到消息
    await new Promise(resolve => setTimeout(resolve, 500))

    // 开始模拟
    await runSimulation(game.game_id)

  } catch (err) {
    ElMessage.error('创建失败: ' + (err.message || '未知错误'))
  } finally {
    creating.value = false
  }
}

const runSimulation = async (gameId) => {
  simulating.value = true
  progress.value = 0
  currentAction.value = '初始化游戏...'

  try {
    // 模拟进度动画
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 5
      }
    }, 200)

    // 运行自动模拟
    const result = await autoPlayGame(gameId, simulationSpeed.value)

    clearInterval(progressInterval)
    progress.value = 100
    currentAction.value = '模拟完成！'

    gameLog.value = result.game_log

    ElMessage.success({
      message: '游戏模拟完成！',
      duration: 3000
    })

  } catch (err) {
    ElMessage.error('模拟失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
  } finally {
    simulating.value = false
  }
}

const formatTimestamp = (index) => {
  return `步骤 ${index + 1}`
}

const getActionColor = (type) => {
  const colorMap = {
    'game_started': '#67C23A',
    'hole_cards_dealt': '#409EFF',
    'flop_dealt': '#E6A23C',
    'turn_dealt': '#E6A23C',
    'river_dealt': '#E6A23C',
    'player_action': '#909399',
    'showdown': '#F56C6C',
    'early_win': '#67C23A'
  }
  return colorMap[type] || '#909399'
}

const formatAction = (action) => {
  const typeMap = {
    'player_type_assigned': (a) => `玩家 P${a.player_id} 类型: ${a.player_type}`,
    'game_started': () => '🎮 游戏开始',
    'hole_cards_dealt': () => '🃏 底牌已发放',
    'flop_dealt': (a) => `🎴 翻牌: ${a.cards.map(c => `${c.rank}${c.suit}`).join(' ')}`,
    'turn_dealt': (a) => `🎴 转牌: ${a.card.rank}${a.card.suit}`,
    'river_dealt': (a) => `🎴 河牌: ${a.card.rank}${a.card.suit}`,
    'player_action': (a) => {
      const actionText = {
        'fold': '弃牌',
        'check': '过牌',
        'call': '跟注',
        'raise': '加注',
        'all_in': 'All-in'
      }[a.action] || a.action

      let text = `👤 玩家 P${a.player_id} (${a.player_type}): ${actionText}`
      if (a.amount > 0) {
        text += ` ${formatChips(a.amount)}`
      }
      text += ` | 剩余: ${formatChips(a.chips_remaining)} | 底池: ${formatChips(a.pot)}`
      return text
    },
    'showdown': (a) => {
      const winners = a.result.winners.map(w => `P${w.player_id}`).join(', ')
      return `🏆 摊牌结束 - 获胜者: ${winners}`
    },
    'early_win': (a) => `🏆 玩家 P${a.winner_id} 获胜（其他玩家弃牌） - 赢得 ${formatChips(a.pot)}`,
    'invalid_action': (a) => `⚠️ 玩家 P${a.player_id} 尝试无效动作: ${a.attempted_action}`
  }

  const formatter = typeMap[action.type]
  return formatter ? formatter(action) : JSON.stringify(action)
}

const clearLog = () => {
  gameLog.value = null
  currentGameId.value = null
  progress.value = 0
  currentAction.value = ''
}

const simulateAnother = () => {
  clearLog()
  ElMessage.info('准备开始新的模拟...')
}
</script>

<style scoped>
.simulation-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.simulation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.simulation-header h2 {
  margin: 0;
  color: #e94560;
}

.create-card,
.progress-card,
.log-card,
.winner-card {
  margin-bottom: 20px;
  background-color: #16213e;
  border: 1px solid #0f3460;
  color: #eee;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.speed-label {
  margin-left: 10px;
  color: #4ecca3;
  font-weight: bold;
}

.current-action {
  margin-top: 20px;
  text-align: center;
  font-size: 18px;
  color: #4ecca3;
}

.winners {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.winner-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #1a2744 0%, #0f3460 100%);
  border-radius: 10px;
  border: 2px solid #4ecca3;
}

.winner-avatar {
  font-size: 48px;
  margin-right: 20px;
}

.winner-info {
  flex: 1;
}

.winner-name {
  font-size: 24px;
  font-weight: bold;
  color: #4ecca3;
  margin-bottom: 5px;
}

.winner-hand {
  font-size: 18px;
  color: #e94560;
  margin-bottom: 5px;
}

.winner-chips {
  font-size: 16px;
  color: #ffd700;
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
}

:deep(.el-timeline-item__content) {
  color: #eee;
}

:deep(.el-progress__text) {
  color: #4ecca3 !important;
}

:deep(.el-form-item__label) {
  color: #eee;
}
</style>
