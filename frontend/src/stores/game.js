import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGameStore = defineStore('game', () => {
  // 状态
  const currentGame = ref(null)
  const playerCards = ref({})
  const isConnected = ref(false)
  const logs = ref([])

  // 计算属性
  const gameId = computed(() => currentGame.value?.game_id || null)
  const gameState = computed(() => currentGame.value?.state || 'waiting')
  const pot = computed(() => currentGame.value?.pot || 0)
  const communityCards = computed(() => currentGame.value?.community_cards || [])
  const players = computed(() => currentGame.value?.players || [])

  // 方法
  const setGame = (game) => {
    currentGame.value = game
  }

  const updateGameState = (state) => {
    if (currentGame.value) {
      currentGame.value = { ...currentGame.value, ...state }
    }
  }

  const setPlayerCards = (playerId, cards) => {
    playerCards.value[playerId] = cards
  }

  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString()
    logs.value.unshift(`[${timestamp}] ${message}`)
    if (logs.value.length > 100) {
      logs.value.pop()
    }
  }

  const clearGame = () => {
    currentGame.value = null
    playerCards.value = {}
    logs.value = []
  }

  const setConnected = (status) => {
    isConnected.value = status
  }

  return {
    // 状态
    currentGame,
    playerCards,
    isConnected,
    logs,

    // 计算属性
    gameId,
    gameState,
    pot,
    communityCards,
    players,

    // 方法
    setGame,
    updateGameState,
    setPlayerCards,
    addLog,
    clearGame,
    setConnected
  }
})
