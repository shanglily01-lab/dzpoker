<template>
  <div class="dashboard">
    <h2>控制台</h2>

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
import { createGame as apiCreateGame } from '@/api'

const router = useRouter()

const stats = reactive({
  totalGames: 0,
  totalPlayers: 0,
  activeGames: 0,
  totalHands: 0
})

const recentGames = ref([])
const showCreateGame = ref(false)

const gameForm = reactive({
  numPlayers: 6,
  smallBlind: 1,
  bigBlind: 2
})

const getStatusType = (status) => {
  if (status === 'waiting') return 'info'
  if (status === 'playing') return 'warning'
  if (status === 'finished') return 'success'
  return 'info'
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
    router.push(`/game/${res.game_id}`)
  } catch (err) {
    ElMessage.error('创建失败')
  }
}

const runSimulation = () => {
  ElMessage.info('模拟测试功能开发中...')
}

const exportData = () => {
  ElMessage.info('数据导出功能开发中...')
}

onMounted(() => {
  // 模拟数据
  stats.totalGames = 128
  stats.totalPlayers = 45
  stats.activeGames = 3
  stats.totalHands = 2456
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard h2 {
  margin-bottom: 20px;
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
