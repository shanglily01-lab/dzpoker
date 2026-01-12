import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ==================== 游戏相关 ====================

export const createGame = (data) => {
  return api.post('/games', data)
}

export const getGame = (gameId) => {
  return api.get(`/games/${gameId}`)
}

export const startGame = (gameId) => {
  return api.post(`/games/${gameId}/start`)
}

export const dealCards = (gameId, smart = false) => {
  return api.post(`/games/${gameId}/deal`, null, {
    params: { smart }
  })
}

export const dealFlop = (gameId) => {
  return api.post(`/games/${gameId}/flop`)
}

export const dealTurn = (gameId) => {
  return api.post(`/games/${gameId}/turn`)
}

export const dealRiver = (gameId) => {
  return api.post(`/games/${gameId}/river`)
}

export const playerAction = (gameId, action) => {
  return api.post(`/games/${gameId}/action`, action)
}

// ==================== 玩家相关 ====================

export const register = (data) => {
  return api.post('/players/register', data)
}

export const login = (data) => {
  return api.post('/players/login', data)
}

export const getPlayer = (playerId) => {
  return api.get(`/players/${playerId}`)
}

export const getPlayerStats = (playerId) => {
  return api.get(`/players/${playerId}/stats`)
}

export const getPlayerProfile = (playerId) => {
  return api.get(`/players/${playerId}/profile`)
}

export const getPlayers = (params) => {
  return api.get('/players', { params })
}

// 游戏统计API
export const getGameStats = () => {
  return api.get('/games/stats')
}

export const listGames = (params) => {
  return api.get('/games/list', { params })
}

// ==================== 模拟相关 ====================

export const autoPlayGame = (gameId, speed = 1.0) => {
  return api.post(`/simulation/${gameId}/auto-play`, null, {
    params: { speed }
  })
}

export const singleAIAction = (gameId) => {
  return api.post(`/simulation/${gameId}/single-action`)
}

export default api
