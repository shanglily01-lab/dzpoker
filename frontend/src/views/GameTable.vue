<template>
  <div class="game-container">
    <!-- 获胜动画弹窗 -->
    <el-dialog
      v-model="showWinnerDialog"
      :show-close="false"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      width="380px"
      top="10vh"
      class="winner-dialog"
    >
      <div class="winner-animation">
        <!-- 粒子背景 -->
        <div class="particles">
          <div v-for="i in 15" :key="i" class="particle" :style="getParticleStyle(i)"></div>
        </div>

        <!-- 光环效果 -->
        <div class="glow-ring"></div>

        <!-- 奖杯 -->
        <div class="winner-trophy">
          <div class="trophy-shine"></div>
          🏆
        </div>

        <!-- 标题 -->
        <div class="winner-title">
          <span class="title-text">WINNER</span>
          <div class="title-underline"></div>
        </div>

        <!-- 获胜者信息 -->
        <div class="winner-players">
          <div v-for="winner in currentWinners" :key="winner.player_id" class="winner-item">
            <div class="winner-badge">
              <span class="badge-star">⭐</span>
            </div>
            <div class="winner-name">玩家 P{{ winner.player_id }}</div>
            <div class="winner-hand">
              <span class="hand-icon">🎴</span>
              {{ winner.hand_description }}
            </div>
            <div class="winner-chips">
              <span class="chips-plus">+</span>
              <span class="chips-amount">{{ formatChips(winner.winnings) }}</span>
              <span class="chips-icon">💎</span>
            </div>
          </div>
        </div>

        <!-- 倒计时 -->
        <div class="winner-countdown">
          <div class="countdown-ring">
            <span class="countdown-number">{{ winnerCountdown }}</span>
          </div>
          <div class="countdown-text">秒后开始下一局</div>
        </div>
      </div>
    </el-dialog>

    <!-- 顶部信息栏 -->
    <div class="top-bar">
      <div class="game-info">
        <h2>德州扑克 - {{ gameId }}</h2>
        <el-tag :type="statusTagType" size="large">
          {{ stateDisplayName }}
        </el-tag>
      </div>
      <div class="connection-status">
        <el-icon v-if="wsConnected" color="#67C23A"><SuccessFilled /></el-icon>
        <el-icon v-else color="#F56C6C"><CircleCloseFilled /></el-icon>
        {{ wsConnected ? '已连接' : '未连接' }}
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧：牌桌 -->
      <div class="table-section">
        <el-card class="table-card" :body-style="{ padding: 0 }">
          <div class="poker-table">
            <!-- 顶部玩家位置 (2-3人) -->
            <div class="top-players">
              <div
                v-for="player in topPlayers"
                :key="player.player_id"
                class="player-seat"
                :class="getPlayerClasses(player)"
              >
                <PlayerSeat :player="player" :is-current-user="player.player_id === currentPlayer"
                  :cards="getPlayerCards(player)" :show-cards="shouldShowCards(player)" />
              </div>
            </div>

            <!-- 中央区域：公共牌和底池 -->
            <div class="center-area">
              <div class="community-section">
                <h3>公共牌</h3>
                <div class="community-cards">
                  <PlayingCard
                    v-for="(card, index) in gameState.community_cards"
                    :key="index"
                    :card="card"
                    :index="index"
                  />
                  <div
                    v-for="i in (5 - (gameState.community_cards?.length || 0))"
                    :key="'empty-' + i"
                    class="card card-placeholder"
                  >
                    <div class="card-back"></div>
                  </div>
                </div>
              </div>

              <div class="pot-display">
                <div class="pot-icon">💰</div>
                <div class="pot-amount">{{ formatChips(gameState.pot || 0) }}</div>
                <div class="pot-label">底池</div>
              </div>
            </div>

            <!-- 底部玩家位置 (2-3人) -->
            <div class="bottom-players">
              <div
                v-for="player in bottomPlayers"
                :key="player.player_id"
                class="player-seat"
                :class="getPlayerClasses(player)"
              >
                <PlayerSeat :player="player" :is-current-user="player.player_id === currentPlayer"
                  :cards="getPlayerCards(player)" :show-cards="shouldShowCards(player)" />
              </div>
            </div>
          </div>

          <!-- 玩家操作区域 -->
          <div v-if="canCurrentPlayerAct" class="action-panel">
            <div class="action-prompt">
              <el-icon class="prompt-icon"><Timer /></el-icon>
              轮到你操作 · 当前下注: <span class="highlight">{{ gameState.current_bet }}</span>
            </div>
            <div class="action-buttons">
              <el-button @click="playerAction('fold')" type="danger" size="large">
                <el-icon><CloseBold /></el-icon>
                弃牌
              </el-button>
              <el-button @click="playerAction('check')" :disabled="!canCheck" type="info" size="large">
                <el-icon><Check /></el-icon>
                过牌
              </el-button>
              <el-button @click="playerAction('call')" :disabled="!canCall" type="primary" size="large">
                <el-icon><CircleCheckFilled /></el-icon>
                跟注 {{ formatChips(callAmount) }}
              </el-button>
              <div class="raise-control">
                <el-input-number
                  v-model="raiseAmount"
                  :min="Math.min(minRaise, currentPlayerChips)"
                  :max="currentPlayerChips"
                  :step="gameState.blind || 10"
                  size="large"
                  controls-position="right"
                />
                <el-button @click="playerAction('raise', raiseAmount)" :disabled="!canRaise"
                  type="warning" size="large">
                  <el-icon><Top /></el-icon>
                  加注
                </el-button>
              </div>
              <el-button @click="playerAction('all_in')" :disabled="currentPlayerChips <= 0"
                type="danger" size="large" plain>
                <el-icon><Lightning /></el-icon>
                All-In {{ formatChips(currentPlayerChips) }}
              </el-button>
            </div>
          </div>

          <!-- 游戏管理控制台（仅调试/管理员） -->
          <div v-if="showAdminControls" class="admin-controls">
            <el-divider>游戏控制台</el-divider>

            <!-- 显示所有手牌开关 -->
            <div class="admin-option" style="margin-bottom: 15px;">
              <el-switch
                v-model="showAllCards"
                active-text="显示所有手牌"
                inactive-text="隐藏其他玩家手牌"
                style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
              />
            </div>

            <!-- AI自动模式 -->
            <div class="ai-mode-section">
              <el-switch
                v-model="aiAutoMode"
                active-text="AI自动模式"
                inactive-text="手动模式"
                @change="toggleAIMode"
              />
              <el-button
                v-if="!aiAutoMode"
                @click="executeAISingleAction"
                :disabled="!canExecuteAIAction"
                type="warning"
                size="small"
              >
                <el-icon><Lightning /></el-icon>
                AI执行一步
              </el-button>
              <el-button
                @click="toggleAutoGame"
                :type="autoGameRunning ? 'danger' : 'success'"
                size="small"
                :loading="autoGameRunning"
              >
                {{ autoGameRunning ? '停止自动游戏' : '开始自动游戏' }}
              </el-button>
            </div>

            <el-divider />

            <div class="control-buttons">
              <el-button @click="startGame" :disabled="gameState.state !== 'waiting'"
                type="primary" size="small">
                开始游戏
              </el-button>
              <el-button @click="dealCards" :disabled="gameState.state !== 'waiting'" size="small">
                发底牌
              </el-button>
              <el-button @click="dealFlop" :disabled="gameState.state !== 'preflop'" size="small">
                发翻牌 (Flop)
              </el-button>
              <el-button @click="dealTurn" :disabled="gameState.state !== 'flop'" size="small">
                发转牌 (Turn)
              </el-button>
              <el-button @click="dealRiver" :disabled="gameState.state !== 'turn'" size="small">
                发河牌 (River)
              </el-button>
              <el-button @click="executeShowdown" :disabled="!canShowdown"
                type="success" size="small">
                摊牌 (Showdown)
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：游戏日志和信息 -->
      <div class="info-section">
        <!-- 当前玩家信息卡片 -->
        <el-card class="player-info-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>我的信息</span>
            </div>
          </template>
          <div class="my-info">
            <div class="info-row">
              <span class="label">玩家ID:</span>
              <el-tag>P{{ currentPlayer }}</el-tag>
            </div>
            <div class="info-row">
              <span class="label">筹码:</span>
              <span class="chips-value">{{ formatChips(currentPlayerChips) }}</span>
            </div>
            <div v-if="currentPlayerState" class="info-row">
              <span class="label">当前下注:</span>
              <span class="bet-value">{{ formatChips(currentPlayerState.current_bet) }}</span>
            </div>
            <div v-if="playerCards[currentPlayer]" class="info-row">
              <span class="label">手牌:</span>
              <div class="my-cards">
                <PlayingCard
                  v-for="(card, idx) in playerCards[currentPlayer]"
                  :key="idx"
                  :card="card"
                  size="small"
                />
              </div>
            </div>
          </div>
        </el-card>

        <!-- 游戏日志 -->
        <el-card class="log-card">
          <template #header>
            <div class="card-header">
              <el-icon><DocumentCopy /></el-icon>
              <span>游戏日志</span>
              <el-button @click="clearLogs" size="small" text>清空</el-button>
            </div>
          </template>
          <div class="log-content" ref="logContainer">
            <div v-for="(log, index) in logs" :key="index" class="log-entry">
              {{ log }}
            </div>
            <div v-if="logs.length === 0" class="log-empty">
              暂无日志
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  SuccessFilled, CircleCloseFilled, Timer, CloseBold, Check,
  CircleCheckFilled, Top, Lightning, User, DocumentCopy
} from '@element-plus/icons-vue'
import {
  getGame,
  startGame as apiStartGame,
  dealCards as apiDealCards,
  dealFlop as apiDealFlop,
  dealTurn as apiDealTurn,
  dealRiver as apiDealRiver,
  showdown as apiShowdown,
  playerAction as apiPlayerAction,
  singleAIAction
} from '@/api'

// 子组件
import PlayingCard from '@/components/PlayingCard.vue'
import PlayerSeat from '@/components/PlayerSeat.vue'

const route = useRoute()
const gameId = route.params.id

// 状态
const gameState = ref({
  state: 'waiting',
  pot: 0,
  current_player: 0,
  current_bet: 0,
  blind: 10,
  community_cards: [],
  players: []
})

const playerCards = ref({})
const logs = ref([])
const wsConnected = ref(false)
const logContainer = ref(null)
let ws = null

// 当前玩家ID（实际应从登录状态获取）
const currentPlayer = ref(1)

// 是否显示管理控制台
const showAdminControls = ref(true) // 开发时为true，生产环境应为false

// 是否显示所有玩家手牌
const showAllCards = ref(true) // 默认显示所有手牌

// AI自动模式
const aiAutoMode = ref(false)
const autoGameRunning = ref(false)
let autoGameInterval = null
let isProcessingShowdown = false

// 获胜动画
const showWinnerDialog = ref(false)
const currentWinners = ref([])
const winnerCountdown = ref(3)

// 计算属性
const stateDisplayName = computed(() => {
  const stateMap = {
    'waiting': '等待中',
    'preflop': '翻牌前',
    'flop': '翻牌圈',
    'turn': '转牌圈',
    'river': '河牌圈',
    'showdown': '摊牌',
    'finished': '已结束'
  }
  return stateMap[gameState.value.state] || gameState.value.state
})

const statusTagType = computed(() => {
  const state = gameState.value.state
  if (state === 'waiting') return 'info'
  if (state === 'finished') return 'success'
  if (state === 'showdown') return 'warning'
  return 'primary'
})

const topPlayers = computed(() => {
  const players = gameState.value.players || []
  const half = Math.ceil(players.length / 2)
  return players.slice(0, half)
})

const bottomPlayers = computed(() => {
  const players = gameState.value.players || []
  const half = Math.ceil(players.length / 2)
  return players.slice(half)
})

const currentPlayerState = computed(() => {
  return gameState.value.players?.find(p => p.player_id === currentPlayer.value)
})

const currentPlayerChips = computed(() => {
  return currentPlayerState.value?.chips || 0
})

const canCurrentPlayerAct = computed(() => {
  if (!gameState.value.players || gameState.value.players.length === 0) return false
  const player = gameState.value.players.find(p => p.position === gameState.value.current_player)
  return player && player.player_id === currentPlayer.value &&
         ['preflop', 'flop', 'turn', 'river'].includes(gameState.value.state)
})

const callAmount = computed(() => {
  const player = currentPlayerState.value
  if (!player) return 0
  return Math.max(0, gameState.value.current_bet - player.current_bet)
})

const canCheck = computed(() => callAmount.value === 0)
const canCall = computed(() => callAmount.value > 0 && callAmount.value <= currentPlayerChips.value)
const minRaise = computed(() => gameState.value.current_bet + (gameState.value.blind || 10))
const canRaise = computed(() => currentPlayerChips.value > callAmount.value)
const canShowdown = computed(() => {
  return gameState.value.state === 'river' || gameState.value.state === 'showdown'
})

const canExecuteAIAction = computed(() => {
  return ['preflop', 'flop', 'turn', 'river'].includes(gameState.value.state) &&
         gameState.value.current_player != null
})

const raiseAmount = ref(minRaise.value)

// 监听 minRaise 变化，自动更新 raiseAmount
watch(minRaise, (newVal) => {
  if (raiseAmount.value < newVal) {
    raiseAmount.value = newVal
  }
})

// 监听 showAllCards 变化，重新加载游戏状态
watch(showAllCards, async () => {
  await loadGame()
})

// 方法
const formatChips = (amount) => {
  if (!amount) return '0'
  return amount.toLocaleString()
}

const getParticleStyle = (index) => {
  const size = Math.random() * 8 + 4
  const left = Math.random() * 100
  const animationDelay = Math.random() * 3
  const animationDuration = Math.random() * 2 + 2

  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    bottom: '-10px',
    animationDelay: `${animationDelay}s`,
    animationDuration: `${animationDuration}s`
  }
}

const getPlayerClasses = (player) => {
  return {
    'is-active': player.is_active,
    'is-current': player.position === gameState.value.current_player,
    'is-all-in': player.is_all_in,
    'is-me': player.player_id === currentPlayer.value
  }
}

const getPlayerCards = (player) => {
  return playerCards.value[player.player_id] || []
}

const shouldShowCards = (player) => {
  // 如果开启了显示所有手牌，始终显示
  if (showAllCards.value) return true

  // 只显示当前玩家自己的牌，或者在showdown/finished状态显示所有牌
  return player.player_id === currentPlayer.value ||
         ['showdown', 'finished'].includes(gameState.value.state)
}

const addLog = (msg) => {
  const timestamp = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  logs.value.unshift(`[${timestamp}] ${msg}`)
  if (logs.value.length > 100) logs.value.pop()

  // 滚动到顶部
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = 0
    }
  })
}

const clearLogs = () => {
  logs.value = []
  addLog('日志已清空')
}

const loadGame = async () => {
  try {
    const data = await getGame(gameId, showAllCards.value)
    gameState.value = data

    // 如果返回了底牌数据，更新 playerCards
    if (data.players) {
      data.players.forEach(player => {
        if (player.hole_cards) {
          playerCards.value[player.player_id] = player.hole_cards
        }
      })
    }

    addLog('✓ 游戏状态已刷新')
  } catch (err) {
    if (err.response?.status === 404) {
      ElMessageBox.confirm(
        '游戏不存在或已过期（服务器重启后游戏数据会丢失）',
        '游戏不存在',
        {
          confirmButtonText: '返回首页',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        router.push('/')
      }).catch(() => {
        // 用户点击取消
      })
    } else {
      ElMessage.error('加载游戏失败: ' + err.message)
    }
  }
}

const connectWebSocket = () => {
  const wsUrl = `ws://${window.location.hostname}:8000/api/games/ws/${gameId}`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    wsConnected.value = true
    addLog('✓ WebSocket 已连接')
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    handleWsMessage(data)
  }

  ws.onclose = () => {
    wsConnected.value = false
    addLog('✗ WebSocket 已断开')
    // 尝试重连
    setTimeout(() => {
      if (!wsConnected.value) {
        addLog('尝试重新连接...')
        connectWebSocket()
      }
    }, 3000)
  }

  ws.onerror = () => {
    addLog('✗ WebSocket 连接错误')
  }
}

const handleWsMessage = (data) => {
  if (data.type === 'game_started') {
    gameState.value = data.state
    addLog('🎮 游戏已开始！')
  } else if (data.type === 'cards_dealt') {
    // 保存玩家手牌
    data.data.hole_cards.forEach((cards, idx) => {
      const playerId = gameState.value.players[idx]?.player_id
      if (playerId) {
        playerCards.value[playerId] = cards
      }
    })
    addLog('🃏 底牌已发放')
  } else if (data.type === 'community_cards') {
    gameState.value.community_cards = data.data.cards || [
      ...gameState.value.community_cards,
      data.data.card
    ]
    addLog(`🎴 ${data.data.street} 已发放`)
  } else if (data.type === 'player_action') {
    gameState.value = data.data.game_state
    const actionText = {
      'fold': '弃牌',
      'check': '过牌',
      'call': '跟注',
      'raise': '加注',
      'all_in': 'All-in'
    }[data.data.action] || data.data.action
    addLog(`👤 玩家 P${data.data.player_id} ${actionText}`)
  } else if (data.type === 'showdown') {
    data.data.winners.forEach(winner => {
      addLog(`🏆 玩家 P${winner.player_id} 获胜！${winner.hand_description} - 赢得 ${formatChips(winner.winnings)}`)
    })
    gameState.value.state = 'finished'
    ElMessage.success({
      message: '游戏结束！',
      duration: 3000
    })
  }
}

// API 调用
const startGame = async () => {
  try {
    await apiStartGame(gameId)
    ElMessage.success('游戏已开始')
    await loadGame()
  } catch (err) {
    ElMessage.error('开始游戏失败: ' + err.message)
  }
}

const dealCards = async () => {
  try {
    const data = await apiDealCards(gameId, true)
    data.hole_cards.forEach((cards, idx) => {
      const playerId = gameState.value.players[idx]?.player_id
      if (playerId) {
        playerCards.value[playerId] = cards
      }
    })
    gameState.value.state = 'preflop'
    addLog('🃏 底牌已发放')
    ElMessage.success('底牌已发放')
  } catch (err) {
    ElMessage.error('发牌失败: ' + err.message)
  }
}

const dealFlop = async () => {
  try {
    ElMessage.warning('注意：后端会在下注轮结束时自动发翻牌，通常不需要手动点击')
    const data = await apiDealFlop(gameId)
    gameState.value.community_cards = data.cards
    gameState.value.state = 'flop'
    addLog('🎴 翻牌已发放（手动）')
    ElMessage.success('翻牌已发放')
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.warning('翻牌已自动发放，无需手动操作')
      await loadGame() // 刷新游戏状态
    } else {
      ElMessage.error('发翻牌失败: ' + err.message)
    }
  }
}

const dealTurn = async () => {
  try {
    ElMessage.warning('注意：后端会在下注轮结束时自动发转牌，通常不需要手动点击')
    const data = await apiDealTurn(gameId)
    gameState.value.community_cards.push(data.card)
    gameState.value.state = 'turn'
    addLog('🎴 转牌已发放（手动）')
    ElMessage.success('转牌已发放')
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.warning('转牌已自动发放，无需手动操作')
      await loadGame() // 刷新游戏状态
    } else {
      ElMessage.error('发转牌失败: ' + err.message)
    }
  }
}

const dealRiver = async () => {
  try {
    ElMessage.warning('注意：后端会在下注轮结束时自动发河牌，通常不需要手动点击')
    const data = await apiDealRiver(gameId)
    gameState.value.community_cards.push(data.card)
    gameState.value.state = 'river'
    addLog('🎴 河牌已发放（手动）')
    ElMessage.success('河牌已发放')
  } catch (err) {
    if (err.response?.status === 400) {
      ElMessage.warning('河牌已自动发放，无需手动操作')
      await loadGame() // 刷新游戏状态
    } else {
      ElMessage.error('发河牌失败: ' + err.message)
    }
  }
}

const executeShowdown = async () => {
  try {
    console.log(`[Showdown] Called, current state: ${gameState.value.state}, current_player: ${gameState.value.current_player}`)

    // 先刷新状态，确保是最新的
    await loadGame()

    console.log(`[Showdown] After refresh - state: ${gameState.value.state}, current_player: ${gameState.value.current_player}`)

    // 再次检查状态
    if (gameState.value.state !== 'showdown') {
      addLog(`⚠️ 游戏状态已变为 ${gameState.value.state}，跳过摊牌`)
      return
    }

    console.log('[Showdown] Calling API...')
    const data = await apiShowdown(gameId)

    data.winners.forEach(winner => {
      addLog(`🏆 玩家 P${winner.player_id} 获胜！${winner.hand_description} - 赢得 ${formatChips(winner.winnings)}`)
    })

    gameState.value.state = 'finished'
    await loadGame()

    // 显示获胜动画
    if (autoGameRunning.value) {
      await showWinnerAnimation(data.winners)
    } else {
      ElMessage.success('游戏结束！')
    }
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.message
    addLog(`❌ 摊牌失败: ${errorMsg}`)
    if (err.response?.status !== 400) {
      ElMessage.error('摊牌失败: ' + errorMsg)
    }
  }
}

// 显示获胜动画
const showWinnerAnimation = async (winners) => {
  return new Promise((resolve) => {
    currentWinners.value = winners
    showWinnerDialog.value = true
    winnerCountdown.value = 3

    const countdownInterval = setInterval(() => {
      winnerCountdown.value--
      if (winnerCountdown.value <= 0) {
        clearInterval(countdownInterval)
        showWinnerDialog.value = false
        resolve()
      }
    }, 1000)
  })
}

const playerAction = async (action, amount = 0) => {
  try {
    const actionData = {
      player_id: currentPlayer.value,
      action: action,
      amount: amount || undefined
    }

    const result = await apiPlayerAction(gameId, actionData)

    const actionText = {
      'fold': '弃牌',
      'check': '过牌',
      'call': '跟注',
      'raise': '加注',
      'all_in': 'All-in'
    }[action] || action

    addLog(`✓ 你执行了 ${actionText}${amount > 0 ? ` (${formatChips(amount)})` : ''}`)

    // 更新游戏状态
    if (result.game_state) {
      gameState.value = result.game_state
    } else {
      await loadGame()
    }

    ElMessage.success(`${actionText}成功`)
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.message || '操作失败'
    ElMessage.error(`操作失败: ${errorMsg}`)
    console.error('Player action error:', err)
  }
}

// AI相关方法
const executeAISingleAction = async () => {
  try {
    const result = await singleAIAction(gameId)

    const actionText = {
      'fold': '弃牌',
      'check': '过牌',
      'call': '跟注',
      'raise': '加注',
      'all_in': 'All-in'
    }[result.action] || result.action

    addLog(`🤖 AI玩家 P${result.player_id} (${result.player_type}): ${actionText}${result.amount > 0 ? ` ${formatChips(result.amount)}` : ''}`)

    if (result.game_state) {
      gameState.value = result.game_state
    } else {
      await loadGame()
    }
  } catch (err) {
    // 只在非 400 错误时显示消息（400 表示没有当前玩家，是正常情况）
    if (err.response?.status !== 400) {
      ElMessage.error('AI执行失败: ' + (err.response?.data?.detail || err.message || '未知错误'))
    }
    // 重新抛出错误，让外层 catch 处理
    throw err
  }
}

const toggleAIMode = (enabled) => {
  if (enabled) {
    addLog('✅ AI自动模式已启用')
    ElMessage.success('AI将自动执行非当前玩家的动作')
  } else {
    addLog('⏸️ AI自动模式已禁用')
  }
}

const toggleAutoGame = async () => {
  if (autoGameRunning.value) {
    // 停止自动游戏
    autoGameRunning.value = false
    if (autoGameInterval) {
      clearInterval(autoGameInterval)
      autoGameInterval = null
    }
    addLog('⏹️ 自动游戏已停止')
    ElMessage.info('自动游戏已停止')
  } else {
    // 开始自动游戏
    autoGameRunning.value = true
    addLog('▶️ 自动游戏已开始')
    ElMessage.success('自动游戏进行中...')

    // 自动执行游戏流程
    await runAutoGame()
  }
}

const runAutoGame = async () => {
  try {
    // 如果游戏还在等待状态，先开始游戏
    if (gameState.value.state === 'waiting') {
      await startGame()
      // startGame 已经发牌，不需要再调用 dealCards()
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    // 自动执行AI动作
    autoGameInterval = setInterval(async () => {
      if (!autoGameRunning.value) {
        clearInterval(autoGameInterval)
        return
      }

      const currentState = gameState.value.state

      // 如果在下注阶段，执行AI动作
      if (['preflop', 'flop', 'turn', 'river'].includes(currentState)) {
        // 只有当有当前玩家且不是用户玩家时才执行AI动作
        console.log(`[Auto] State: ${currentState}, current_player: ${gameState.value.current_player}, user player: ${currentPlayer.value}`)

        const currentGamePlayer = gameState.value.current_player

        if (currentGamePlayer != null && currentGamePlayer !== -1) {
          // 检查是否是用户玩家，如果是用户则跳过AI执行
          if (currentGamePlayer === currentPlayer.value) {
            console.log('[Auto] Current player is user, skipping AI action')
            await new Promise(resolve => setTimeout(resolve, 500))
            await loadGame()
          } else {
            // 是AI玩家，执行AI动作
            try {
              await executeAISingleAction()
              await new Promise(resolve => setTimeout(resolve, 800))
            } catch (err) {
              // 如果AI动作失败，刷新游戏状态
              console.log('[Auto] AI action failed, refreshing game state:', err.response?.data?.detail || err.message)
              await loadGame()
              console.log(`[Auto] After refresh - State: ${gameState.value.state}, current_player: ${gameState.value.current_player}`)
            }
          }
        } else {
          // 没有当前玩家，可能是下注轮结束了，等待状态更新
          console.log('[Auto] No current player, waiting...')
          await new Promise(resolve => setTimeout(resolve, 500))
          await loadGame()
        }
      }

      // 检查是否需要摊牌（后端已自动处理状态推进和发牌）
      if (currentState === 'showdown' && !isProcessingShowdown) {
        const activePlayers = gameState.value.players?.filter(p => p.is_active || p.is_all_in) || []
        // current_player 为 null, undefined, 或 -1 都表示没有当前玩家
        console.log(`[Auto] Showdown check - activePlayers: ${activePlayers.length}, current_player: ${gameState.value.current_player}`)

        if (activePlayers.length > 1 && (gameState.value.current_player == null || gameState.value.current_player === -1)) {
          isProcessingShowdown = true
          console.log('[Auto] Calling showdown...')
          await new Promise(resolve => setTimeout(resolve, 1000))
          await executeShowdown()
          addLog('🏆 自动摊牌')
          isProcessingShowdown = false

          // executeShowdown 中已经显示动画并等待

          // 检查是否还有多个玩家有筹码，如果有则开始下一局
          await loadGame()
          const playersWithChips = gameState.value.players?.filter(p => p.chips > 0) || []

          if (playersWithChips.length > 1) {
            addLog('💫 开始下一局...')
            await startGame()
            await new Promise(resolve => setTimeout(resolve, 1000))
          } else {
            // 只剩一个玩家有筹码，游戏彻底结束
            const winner = playersWithChips[0]
            if (winner) {
              addLog(`🎊 玩家 P${winner.player_id} 赢得所有筹码！游戏结束！`)
              ElMessage.success(`玩家 P${winner.player_id} 获得最终胜利！`)
            }
            autoGameRunning.value = false
            clearInterval(autoGameInterval)
          }
        }
      } else if (currentState === 'finished') {
        // 检查是否有获胜者信息需要显示
        if (gameState.value.last_winners && gameState.value.last_winners.length > 0 && !showWinnerDialog.value) {
          // 显示获胜者动画
          console.log('[Auto] Showing winner animation from last_winners')
          currentWinners.value = gameState.value.last_winners
          showWinnerDialog.value = true

          // 等待动画播放完成（3秒倒计时）
          await new Promise(resolve => setTimeout(resolve, 3000))
          showWinnerDialog.value = false
          currentWinners.value = []
        }

        // 检查是否应该继续下一局
        const playersWithChips = gameState.value.players?.filter(p => p.chips > 0) || []

        if (playersWithChips.length > 1 && autoGameRunning.value) {
          // 还有多个玩家，继续下一局
          await new Promise(resolve => setTimeout(resolve, 1000))
          addLog('💫 开始下一局...')
          await startGame()
        } else {
          // 游戏彻底结束
          const winner = playersWithChips[0]
          if (winner) {
            addLog(`🎊 玩家 P${winner.player_id} 赢得所有筹码！游戏结束！`)
            ElMessage.success(`玩家 P${winner.player_id} 获得最终胜利！`)
          }
          autoGameRunning.value = false
          clearInterval(autoGameInterval)
        }
      }
    }, 1000)
  } catch (err) {
    autoGameRunning.value = false
    if (autoGameInterval) {
      clearInterval(autoGameInterval)
    }
    ElMessage.error('自动游戏失败: ' + (err.message || '未知错误'))
  }
}

// 生命周期
onMounted(async () => {
  await loadGame()
  connectWebSocket()
  addLog('欢迎来到德州扑克！')

  // 检查URL参数，如果有auto=true则自动开始游戏
  const urlParams = new URLSearchParams(window.location.search)
  if (urlParams.get('auto') === 'true') {
    addLog('🤖 检测到自动模式，3秒后开始自动游戏...')
    await new Promise(resolve => setTimeout(resolve, 3000))
    await toggleAutoGame()
  }
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
  if (autoGameInterval) {
    clearInterval(autoGameInterval)
  }
})
</script>

<style scoped>
.game-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
  padding: 20px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 30px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.game-info h2 {
  margin: 0 0 10px 0;
  color: #fff;
  font-size: 24px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 14px;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

/* 牌桌区域 */
.table-section {
  min-height: 600px;
}

.table-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  overflow: hidden;
}

.poker-table {
  background: radial-gradient(ellipse at center, #1a5c2e 0%, #0d3318 100%);
  border: 8px solid #8b6914;
  border-radius: 200px / 120px;
  padding: 40px 60px;
  min-height: 550px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.5);
}

.top-players, .bottom-players {
  display: flex;
  justify-content: space-around;
  gap: 20px;
  flex-wrap: wrap;
}

.center-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px 0;
}

.community-section h3 {
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  margin: 0 0 15px 0;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.community-cards {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.card {
  width: 70px;
  height: 98px;
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.card-placeholder {
  background: rgba(0, 0, 0, 0.3);
  border: 2px dashed rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-back {
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    #2d5a3d,
    #2d5a3d 10px,
    #1a4728 10px,
    #1a4728 20px
  );
  border-radius: 6px;
}

.pot-display {
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  padding: 20px 40px;
  border-radius: 50px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  text-align: center;
  border: 2px solid #ffd700;
}

.pot-icon {
  font-size: 32px;
  margin-bottom: 5px;
}

.pot-amount {
  font-size: 28px;
  font-weight: bold;
  color: #ffd700;
  margin-bottom: 5px;
}

.pot-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 玩家座位 */
.player-seat {
  transition: all 0.3s ease;
}

.player-seat.is-current {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.player-seat.is-me {
  position: relative;
}

.player-seat.is-me::after {
  content: 'YOU';
  position: absolute;
  top: -10px;
  right: -10px;
  background: #ffd700;
  color: #000;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: bold;
}

/* 操作面板 */
.action-panel {
  background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
  padding: 25px 30px;
  border-top: 3px solid #4a90e2;
}

.action-prompt {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  margin-bottom: 20px;
  font-weight: 500;
}

.prompt-icon {
  font-size: 24px;
  color: #ffd700;
}

.highlight {
  color: #ffd700;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 120px;
}

.raise-control {
  display: flex;
  gap: 10px;
  align-items: center;
  flex: 2;
}

.raise-control .el-input-number {
  flex: 1;
}

/* 管理控制台 */
.admin-controls {
  padding: 20px 30px;
  background: rgba(0, 0, 0, 0.2);
}

.control-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 右侧信息区 */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.player-info-card, .log-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-weight: 500;
}

.my-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.chips-value {
  color: #4ecca3;
  font-size: 20px;
  font-weight: bold;
}

.bet-value {
  color: #ffd700;
  font-size: 18px;
  font-weight: bold;
}

.my-cards {
  display: flex;
  gap: 8px;
}

/* 日志区域 */
.log-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}

.log-entry {
  padding: 8px 12px;
  margin-bottom: 6px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  line-height: 1.5;
  font-family: 'Consolas', 'Monaco', monospace;
}

.log-empty {
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  padding: 40px 20px;
  font-size: 14px;
}

/* 滚动条样式 */
.log-content::-webkit-scrollbar {
  width: 8px;
}

.log-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.log-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* AI控制样式 */
.ai-mode-section {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  margin-bottom: 15px;
}

.ai-mode-section :deep(.el-switch__label) {
  color: #fff;
}

.ai-mode-section :deep(.el-switch__label.is-active) {
  color: #67C23A;
}

/* 获胜动画样式 */
.winner-dialog :deep(.el-dialog) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border: 2px solid rgba(255, 215, 0, 0.3);
  border-radius: 30px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.8),
              0 0 50px rgba(255, 215, 0, 0.2);
  overflow: visible;
}

.winner-dialog :deep(.el-dialog__body) {
  padding: 25px 20px;
  position: relative;
  overflow: hidden;
}

.winner-animation {
  text-align: center;
  color: white;
  position: relative;
  z-index: 2;
}

/* 粒子效果 */
.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.particle {
  position: absolute;
  background: radial-gradient(circle, #ffd700 0%, transparent 70%);
  border-radius: 50%;
  animation: float-particle 3s infinite ease-in-out;
}

@keyframes float-particle {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) scale(0);
    opacity: 0;
  }
}

/* 光环效果 */
.glow-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle,
    rgba(255, 215, 0, 0.1) 0%,
    rgba(255, 215, 0, 0.05) 50%,
    transparent 70%);
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.5;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 1;
  }
}

/* 奖杯 */
.winner-trophy {
  position: relative;
  font-size: 60px;
  animation: trophy-bounce 1s ease-in-out, trophy-rotate 3s ease-in-out infinite 1s;
  margin-bottom: 15px;
  filter: drop-shadow(0 5px 15px rgba(255, 215, 0, 0.6));
  display: inline-block;
}

.trophy-shine {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg,
    transparent 0%,
    rgba(255, 255, 255, 0.8) 50%,
    transparent 100%);
  animation: shine-sweep 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes trophy-bounce {
  0% {
    transform: translateY(0) scale(0);
    opacity: 0;
  }
  50% {
    transform: translateY(-30px) scale(1.2);
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

@keyframes trophy-rotate {
  0%, 100% {
    transform: rotateY(0deg);
  }
  50% {
    transform: rotateY(15deg);
  }
}

@keyframes shine-sweep {
  0% {
    transform: translateX(-100%) skewX(-15deg);
  }
  100% {
    transform: translateX(200%) skewX(-15deg);
  }
}

/* 标题 */
.winner-title {
  margin-bottom: 20px;
  position: relative;
}

.title-text {
  font-size: 32px;
  font-weight: 900;
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #ffd700 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
  letter-spacing: 5px;
  animation: title-glow 2s ease-in-out infinite;
  display: inline-block;
}

@keyframes title-glow {
  0%, 100% {
    filter: brightness(1) drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));
  }
  50% {
    filter: brightness(1.3) drop-shadow(0 0 20px rgba(255, 215, 0, 0.8));
  }
}

.title-underline {
  height: 3px;
  width: 120px;
  margin: 10px auto 0;
  background: linear-gradient(90deg,
    transparent 0%,
    #ffd700 50%,
    transparent 100%);
  border-radius: 2px;
  animation: underline-expand 1s ease-out;
}

@keyframes underline-expand {
  from {
    width: 0;
    opacity: 0;
  }
  to {
    width: 200px;
    opacity: 1;
  }
}

/* 获胜者信息 */
.winner-players {
  margin-bottom: 20px;
}

.winner-item {
  background: linear-gradient(135deg,
    rgba(255, 215, 0, 0.1) 0%,
    rgba(255, 215, 0, 0.05) 100%);
  border: 2px solid rgba(255, 215, 0, 0.3);
  border-radius: 15px;
  padding: 15px 20px;
  margin-bottom: 15px;
  backdrop-filter: blur(10px);
  animation: slide-in 0.6s ease-out;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3),
              inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.winner-item::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg,
    transparent 30%,
    rgba(255, 215, 0, 0.1) 50%,
    transparent 70%);
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.winner-badge {
  margin-bottom: 8px;
}

.badge-star {
  font-size: 28px;
  display: inline-block;
  animation: star-spin 2s linear infinite;
  filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.8));
}

@keyframes star-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.winner-name {
  font-size: 22px;
  font-weight: 900;
  margin-bottom: 8px;
  color: #ffd700;
  text-shadow: 0 0 20px rgba(255, 215, 0, 0.5),
               2px 2px 4px rgba(0, 0, 0, 0.5);
  letter-spacing: 2px;
}

.winner-hand {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 12px;
  padding: 8px 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  display: inline-block;
}

.hand-icon {
  font-size: 24px;
  margin-right: 10px;
  display: inline-block;
  animation: card-flip 2s ease-in-out infinite;
}

@keyframes card-flip {
  0%, 100% {
    transform: rotateY(0deg);
  }
  50% {
    transform: rotateY(180deg);
  }
}

.winner-chips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 28px;
  font-weight: 900;
  margin-top: 20px;
  position: relative;
}

.chips-plus {
  color: #4ade80;
  font-size: 24px;
  animation: plus-bounce 0.8s ease-out;
}

@keyframes plus-bounce {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.3);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.chips-amount {
  color: #ffd700;
  text-shadow: 0 0 20px rgba(255, 215, 0, 0.8),
               0 0 40px rgba(255, 215, 0, 0.4),
               3px 3px 6px rgba(0, 0, 0, 0.5);
  animation: chips-count 0.8s ease-out, chips-glow 2s ease-in-out infinite 0.8s;
}

@keyframes chips-count {
  from {
    transform: scale(0.5);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes chips-glow {
  0%, 100% {
    filter: brightness(1);
  }
  50% {
    filter: brightness(1.3);
  }
}

.chips-icon {
  font-size: 40px;
  animation: gem-sparkle 1.5s ease-in-out infinite;
  filter: drop-shadow(0 0 15px rgba(255, 215, 0, 0.6));
}

@keyframes gem-sparkle {
  0%, 100% {
    transform: scale(1) rotate(0deg);
  }
  25% {
    transform: scale(1.1) rotate(-5deg);
  }
  75% {
    transform: scale(1.1) rotate(5deg);
  }
}

.chips-icon {
  font-size: 36px;
  animation: rotate-coin 2s linear infinite;
}

@keyframes rotate-coin {
  0% {
    transform: rotateY(0deg);
  }
  100% {
    transform: rotateY(360deg);
  }
}

.chips-amount {
  font-family: 'Arial', sans-serif;
}

.winner-countdown {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.countdown-ring {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg,
    rgba(255, 215, 0, 0.2) 0%,
    rgba(255, 215, 0, 0.1) 100%);
  border: 3px solid rgba(255, 215, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 30px rgba(255, 215, 0, 0.3),
              inset 0 0 20px rgba(255, 215, 0, 0.1);
  animation: ring-pulse 1s ease-in-out infinite;
}

@keyframes ring-pulse {
  0%, 100% {
    transform: scale(1);
    border-color: rgba(255, 215, 0, 0.5);
  }
  50% {
    transform: scale(1.05);
    border-color: rgba(255, 215, 0, 0.8);
  }
}

.countdown-number {
  font-size: 28px;
  font-weight: 900;
  color: #ffd700;
  text-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
  animation: number-tick 1s ease-in-out infinite;
}

@keyframes number-tick {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.countdown-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}
</style>
