<template>
  <div class="dashboard" v-loading="loading">
    <div class="dashboard-header">
      <h2>控制台</h2>
      <el-button @click="refreshData" :loading="loading" type="primary" plain>
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.totalGames }}</div>
          <div class="stat-label">总游戏数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.totalPlayers }}</div>
          <div class="stat-label">总玩家数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.activeGames }}</div>
          <div class="stat-label">进行中游戏</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.totalHands }}</div>
          <div class="stat-label">总手牌数</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-card class="section-card">
      <template #header>快速操作</template>
      <div class="quick-actions">
        <el-button type="primary" @click="showCreateGame = true">
          创建新游戏
        </el-button>
        <el-button @click="runSimulation">
          运行模拟测试
        </el-button>
        <el-button @click="exportData">
          导出数据
        </el-button>
      </div>
    </el-card>

    <!-- 最近游戏 -->
    <el-card class="section-card">
      <template #header>最近游戏</template>
      <el-table :data="recentGames" stripe>
        <el-table-column prop="game_id" label="游戏ID" width="120" />
        <el-table-column prop="num_players" label="玩家数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pot" label="底池" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="enterGame(row.game_id)">
              进入
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建游戏弹窗 -->
    <el-dialog v-model="showCreateGame" title="创建新游戏" width="400px">
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
      </el-form>
      <template #footer>
        <el-button @click="showCreateGame = false">取消</el-button>
        <el-button type="primary" @click="createGame">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { createGame as apiCreateGame, getGameStats, listGames } from '@/api'

const router = useRouter()

const stats = reactive({
  totalGames: 0,
  totalPlayers: 0,
  activeGames: 0,
  totalHands: 0
})

const recentGames = ref([])
const showCreateGame = ref(false)
const loading = ref(false)

const gameForm = reactive({
  numPlayers: 6,
  smallBlind: 1,
  bigBlind: 2
})

const getStatusType = (status) => {
  const stateMap = {
    'waiting': 'info',
    'preflop': 'warning',
    'flop': 'warning',
    'turn': 'warning',
    'river': 'warning',
    'showdown': 'warning',
    'finished': 'success'
  }
  return stateMap[status] || 'info'
}

const enterGame = (gameId) => {
  router.push(`/game/${gameId}`)
}

const createGame = async () => {
  try {
    const res = await apiCreateGame({
      num_players: gameForm.numPlayers,
      small_blind: gameForm.smallBlind,
      big_blind: gameForm.bigBlind
    })

    ElMessage.success('游戏创建成功')
    showCreateGame.value = false

    // 刷新数据
    await refreshData()

    router.push(`/game/${res.game_id}`)
  } catch (err) {
    ElMessage.error('创建失败: ' + (err.message || '未知错误'))
  }
}

const loadStats = async () => {
  try {
    const data = await getGameStats()
    stats.totalGames = data.total_games
    stats.totalPlayers = data.total_players
    stats.activeGames = data.active_games
    stats.totalHands = data.total_hands
  } catch (err) {
    console.error('加载统计数据失败:', err)
  }
}

const loadRecentGames = async () => {
  try {
    const data = await listGames({ limit: 10 })
    recentGames.value = data.map(game => ({
      game_id: game.game_id,
      num_players: game.num_players,
      status: game.state,
      pot: game.pot
    }))
  } catch (err) {
    console.error('加载游戏列表失败:', err)
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadStats(),
      loadRecentGames()
    ])
  } catch (err) {
    console.error('刷新数据失败:', err)
  } finally {
    loading.value = false
  }
}

const runSimulation = () => {
  router.push('/simulation')
}

const exportData = () => {
  ElMessage.info('数据导出功能开发中...')
}

onMounted(async () => {
  await refreshData()

  // 每30秒自动刷新一次
  setInterval(() => {
    loadStats()
    loadRecentGames()
  }, 30000)
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-header h2 {
  margin: 0;
  color: #e94560;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  background-color: #16213e;
  border: 1px solid #0f3460;
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #4ecca3;
}

.stat-label {
  color: #aaa;
  margin-top: 10px;
}

.section-card {
  background-color: #16213e;
  border: 1px solid #0f3460;
  color: #eee;
  margin-bottom: 20px;
}

.quick-actions {
  display: flex;
  gap: 15px;
}

:deep(.el-table) {
  background-color: transparent;
  color: #eee;
}

:deep(.el-table th) {
  background-color: #0f3460 !important;
  color: #eee;
}

:deep(.el-table tr) {
  background-color: #16213e;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #1a2744;
}
</style>
