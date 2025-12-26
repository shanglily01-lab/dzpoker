<template>
  <div class="game-table">
    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <span>游戏ID: {{ gameId }}</span>
          <el-tag :type="statusType">{{ gameState.state || '等待中' }}</el-tag>
        </div>
      </template>

      <!-- 牌桌 -->
      <div class="poker-table">
        <!-- 公共牌 -->
        <div class="community-cards">
          <div
            v-for="(card, index) in gameState.community_cards"
            :key="index"
            class="card"
            :class="getSuitClass(card.suit)"
          >
            {{ getCardDisplay(card) }}
          </div>
          <div
            v-for="i in (5 - (gameState.community_cards?.length || 0))"
            :key="'empty-' + i"
            class="card card-back"
          >
            🂠
          </div>
        </div>

        <!-- 底池 -->
        <div class="pot">
          底池: {{ gameState.pot || 0 }}
        </div>

        <!-- 玩家座位 -->
        <div class="players-circle">
          <div
            v-for="player in gameState.players"
            :key="player.player_id"
            class="player-seat"
            :class="{
              'is-active': player.is_active,
              'is-current': player.position === gameState.current_player
            }"
          >
            <div class="player-avatar">P{{ player.player_id }}</div>
            <div class="player-chips">{{ player.chips }}</div>
            <div class="player-bet" v-if="player.current_bet > 0">
              下注: {{ player.current_bet }}
            </div>
            <!-- 玩家手牌 -->
            <div class="player-cards" v-if="playerCards[player.player_id]">
              <span
                v-for="(card, idx) in playerCards[player.player_id]"
                :key="idx"
                class="mini-card"
                :class="getSuitClass(card.suit)"
              >
                {{ getCardDisplay(card) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button @click="startGame" :disabled="gameState.state !== 'waiting'">
          开始游戏
        </el-button>
        <el-button @click="dealCards" :disabled="gameState.state !== 'waiting'">
          发牌
        </el-button>
        <el-button @click="dealFlop" :disabled="gameState.state !== 'preflop'">
          发翻牌
        </el-button>
        <el-button @click="dealTurn" :disabled="gameState.state !== 'flop'">
          发转牌
        </el-button>
        <el-button @click="dealRiver" :disabled="gameState.state !== 'turn'">
          发河牌
        </el-button>
      </div>
    </el-card>

    <!-- 游戏日志 -->
    <el-card class="log-card">
      <template #header>游戏日志</template>
      <div class="log-content">
        <p v-for="(log, index) in logs" :key="index">{{ log }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getGame,
  startGame as apiStartGame,
  dealCards as apiDealCards,
  dealFlop as apiDealFlop,
  dealTurn as apiDealTurn,
  dealRiver as apiDealRiver
} from '@/api'

const route = useRoute()
const gameId = route.params.id

const gameState = ref({
  state: 'waiting',
  pot: 0,
  current_player: 0,
  community_cards: [],
  players: []
})

const playerCards = ref({})
const logs = ref([])
let ws = null

const statusType = computed(() => {
  const state = gameState.value.state
  if (state === 'waiting') return 'info'
  if (state === 'finished') return 'success'
  return 'warning'
})

const SUITS = ['♠', '♥', '♦', '♣']
const RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

const getCardDisplay = (card) => {
  return RANKS[card.rank] + SUITS[card.suit]
}

const getSuitClass = (suit) => {
  return suit === 1 || suit === 2 ? 'red' : 'black'
}

const addLog = (msg) => {
  logs.value.unshift(`[${new Date().toLocaleTimeString()}] ${msg}`)
  if (logs.value.length > 50) logs.value.pop()
}

const loadGame = async () => {
  try {
    const data = await getGame(gameId)
    gameState.value = data
    addLog('游戏状态已加载')
  } catch (err) {
    ElMessage.error('加载游戏失败')
  }
}

const connectWebSocket = () => {
  const wsUrl = `ws://${window.location.hostname}:8000/api/games/ws/${gameId}`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    addLog('WebSocket已连接')
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    handleWsMessage(data)
  }

  ws.onclose = () => {
    addLog('WebSocket已断开')
  }
}

const handleWsMessage = (data) => {
  if (data.type === 'game_started') {
    gameState.value = data.state
    addLog('游戏已开始')
  } else if (data.type === 'cards_dealt') {
    // 保存玩家手牌
    data.data.hole_cards.forEach((cards, idx) => {
      playerCards.value[idx + 1] = cards
    })
    addLog('底牌已发放')
  } else if (data.type === 'community_cards') {
    gameState.value.community_cards = data.data.cards || [
      ...gameState.value.community_cards,
      data.data.card
    ]
    addLog(`${data.data.street}已发放`)
  } else if (data.type === 'player_action') {
    gameState.value = data.data.game_state
    addLog(`玩家${data.data.player_id} ${data.data.action}`)
  }
}

const startGame = async () => {
  try {
    await apiStartGame(gameId)
    ElMessage.success('游戏已开始')
    loadGame()
  } catch (err) {
    ElMessage.error('开始失败')
  }
}

const dealCards = async () => {
  try {
    const data = await apiDealCards(gameId, true)
    data.hole_cards.forEach((cards, idx) => {
      playerCards.value[idx + 1] = cards
    })
    gameState.value.state = 'preflop'
    addLog('底牌已发放')
  } catch (err) {
    ElMessage.error('发牌失败')
  }
}

const dealFlop = async () => {
  try {
    const data = await apiDealFlop(gameId)
    gameState.value.community_cards = data.cards
    gameState.value.state = 'flop'
    addLog('翻牌已发放')
  } catch (err) {
    ElMessage.error('发翻牌失败')
  }
}

const dealTurn = async () => {
  try {
    const data = await apiDealTurn(gameId)
    gameState.value.community_cards.push(data.card)
    gameState.value.state = 'turn'
    addLog('转牌已发放')
  } catch (err) {
    ElMessage.error('发转牌失败')
  }
}

const dealRiver = async () => {
  try {
    const data = await apiDealRiver(gameId)
    gameState.value.community_cards.push(data.card)
    gameState.value.state = 'river'
    addLog('河牌已发放')
  } catch (err) {
    ElMessage.error('发河牌失败')
  }
}

onMounted(() => {
  loadGame()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) ws.close()
})
</script>

<style scoped>
.game-table {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.table-card, .log-card {
  background-color: #16213e;
  border: 1px solid #0f3460;
  color: #eee;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.poker-table {
  background: radial-gradient(ellipse at center, #1a472a 0%, #0d2818 100%);
  border-radius: 150px;
  padding: 40px;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.community-cards {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.card {
  width: 50px;
  height: 70px;
  background: white;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.card.black { color: #000; }
.card.red { color: #e94560; }
.card.card-back {
  background: #1a472a;
  border: 2px solid #2d5a3d;
  color: #4a7c59;
}

.pot {
  background: rgba(0, 0, 0, 0.5);
  padding: 10px 30px;
  border-radius: 20px;
  color: gold;
  font-size: 18px;
  margin-bottom: 30px;
}

.players-circle {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
}

.player-seat {
  background: rgba(0, 0, 0, 0.6);
  padding: 10px 15px;
  border-radius: 10px;
  text-align: center;
  min-width: 80px;
  border: 2px solid transparent;
}

.player-seat.is-current {
  border-color: gold;
}

.player-seat:not(.is-active) {
  opacity: 0.5;
}

.player-avatar {
  width: 40px;
  height: 40px;
  background: #0f3460;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 5px;
  font-weight: bold;
}

.player-chips {
  color: #4ecca3;
  font-size: 14px;
}

.player-bet {
  color: gold;
  font-size: 12px;
  margin-top: 3px;
}

.player-cards {
  display: flex;
  gap: 3px;
  justify-content: center;
  margin-top: 5px;
}

.mini-card {
  background: white;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 12px;
}

.mini-card.red { color: #e94560; }
.mini-card.black { color: #000; }

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.log-card {
  max-height: 500px;
}

.log-content {
  height: 400px;
  overflow-y: auto;
  font-size: 12px;
  color: #aaa;
}

.log-content p {
  margin: 5px 0;
  padding: 5px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
}
</style>
