<template>
  <div class="analytics-container">
    <el-card class="header-card">
      <h1>📊 游戏数据分析</h1>
      <p class="subtitle">实时统计和深度分析</p>
    </el-card>

    <!-- 整体统计 -->
    <el-card class="stats-overview">
      <template #header>
        <div class="card-header">
          <span>整体统计</span>
          <el-select v-model="overviewDays" @change="loadOverview" size="small" style="width: 120px">
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
            <el-option label="最近90天" :value="90" />
          </el-select>
        </div>
      </template>
      <el-row :gutter="20" v-if="overview">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总游戏数</div>
            <div class="stat-value">{{ overview.total_games }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">已完成</div>
            <div class="stat-value success">{{ overview.finished_games }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总底池</div>
            <div class="stat-value warning">{{ formatNumber(overview.total_pot) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均时长</div>
            <div class="stat-value info">{{ formatDuration(overview.avg_duration_seconds) }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20">
      <!-- 手牌类型分布 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>手牌类型分布</span>
              <el-button size="small" @click="loadHandTypes">刷新</el-button>
            </div>
          </template>
          <div v-if="handTypes.length > 0" class="hand-types-chart">
            <div v-for="item in handTypes" :key="item.hand_type" class="hand-type-item">
              <div class="hand-type-label">{{ item.hand_type }}</div>
              <div class="hand-type-bar-container">
                <div class="hand-type-bar" :style="{ width: item.percentage + '%' }">
                  <span class="hand-type-count">{{ item.count }}</span>
                </div>
                <span class="hand-type-percentage">{{ item.percentage.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>

      <!-- 位置胜率分析 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>位置胜率分析</span>
              <el-button size="small" @click="loadPositions">刷新</el-button>
            </div>
          </template>
          <div v-if="positions.length > 0" class="positions-chart">
            <div v-for="pos in positions" :key="pos.position" class="position-item">
              <div class="position-name">{{ pos.position_name }}</div>
              <div class="position-stats">
                <div class="position-stat">
                  <span class="label">胜率:</span>
                  <span class="value" :class="getWinRateClass(pos.win_rate)">
                    {{ pos.win_rate.toFixed(1) }}%
                  </span>
                </div>
                <div class="position-stat">
                  <span class="label">场次:</span>
                  <span class="value">{{ pos.total }}</span>
                </div>
                <div class="position-stat">
                  <span class="label">平均盈利:</span>
                  <span class="value" :class="pos.avg_profit >= 0 ? 'profit' : 'loss'">
                    {{ formatNumber(pos.avg_profit) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 游戏历史 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>游戏历史</span>
          <div>
            <el-select v-model="historyStatus" @change="loadHistory" size="small" style="width: 120px; margin-right: 10px">
              <el-option label="全部" :value="null" />
              <el-option label="已完成" value="finished" />
              <el-option label="进行中" value="playing" />
            </el-select>
            <el-button size="small" @click="loadHistory">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="gameHistory" style="width: 100%" v-loading="loading">
        <el-table-column prop="game_uuid" label="游戏ID" width="120" />
        <el-table-column prop="num_players" label="玩家数" width="80" />
        <el-table-column prop="total_pot" label="底池" width="120">
          <template #default="{ row }">
            <span class="pot-value">{{ formatNumber(row.total_pot) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="hands_count" label="手牌数" width="80" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="viewGameDetail(row.id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="totalGames > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalGames"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadHistory"
        @size-change="loadHistory"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <!-- 游戏详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="游戏详情" width="80%" :close-on-click-modal="false">
      <div v-if="gameDetail" class="game-detail">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="游戏ID">{{ gameDetail.game_uuid }}</el-descriptions-item>
          <el-descriptions-item label="玩家数">{{ gameDetail.num_players }}</el-descriptions-item>
          <el-descriptions-item label="总底池">{{ formatNumber(gameDetail.total_pot) }}</el-descriptions-item>
          <el-descriptions-item label="小盲注">{{ gameDetail.small_blind }}</el-descriptions-item>
          <el-descriptions-item label="大盲注">{{ gameDetail.big_blind }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(gameDetail.status)">
              {{ getStatusText(gameDetail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTime(gameDetail.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatTime(gameDetail.ended_at) }}</el-descriptions-item>
          <el-descriptions-item label="获胜者">玩家 {{ gameDetail.winner_id }}</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px">手牌记录</h3>
        <el-table :data="gameDetail.hands" style="width: 100%">
          <el-table-column prop="player_id" label="玩家" width="80">
            <template #default="{ row }">P{{ row.player_id }}</template>
          </el-table-column>
          <el-table-column prop="position" label="位置" width="80" />
          <el-table-column prop="hole_cards" label="底牌" width="100" />
          <el-table-column prop="final_hand" label="最终牌型" width="200" />
          <el-table-column prop="profit_loss" label="盈亏" width="120">
            <template #default="{ row }">
              <span :class="row.profit_loss >= 0 ? 'profit' : 'loss'">
                {{ row.profit_loss >= 0 ? '+' : '' }}{{ formatNumber(row.profit_loss) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="is_winner" label="是否获胜" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_winner" type="success" size="small">获胜</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else v-loading="true" style="height: 200px"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// 整体统计
const overviewDays = ref(30)
const overview = ref(null)

// 手牌类型分布
const handTypes = ref([])

// 位置分析
const positions = ref([])

// 游戏历史
const gameHistory = ref([])
const totalGames = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const historyStatus = ref(null)
const loading = ref(false)

// 游戏详情
const showDetailDialog = ref(false)
const gameDetail = ref(null)

// 加载整体统计
const loadOverview = async () => {
  try {
    const { data } = await api.get(`/analytics/overview?days=${overviewDays.value}`)
    overview.value = data
  } catch (error) {
    console.error('加载整体统计失败:', error)
    ElMessage.error('加载整体统计失败')
  }
}

// 加载手牌类型分布
const loadHandTypes = async () => {
  try {
    const { data } = await api.get('/analytics/hand-types?limit=200')
    handTypes.value = data.distribution
  } catch (error) {
    console.error('加载手牌类型分布失败:', error)
    ElMessage.error('加载手牌类型分布失败')
  }
}

// 加载位置分析
const loadPositions = async () => {
  try {
    const { data } = await api.get('/analytics/positions?limit=200')
    positions.value = data.positions
  } catch (error) {
    console.error('加载位置分析失败:', error)
    ElMessage.error('加载位置分析失败')
  }
}

// 加载游戏历史
const loadHistory = async () => {
  loading.value = true
  try {
    const offset = (currentPage.value - 1) * pageSize.value
    const params = { limit: pageSize.value, offset }
    if (historyStatus.value) {
      params.status = historyStatus.value
    }
    const { data } = await api.get('/analytics/games', { params })
    gameHistory.value = data.games
    totalGames.value = data.total
  } catch (error) {
    console.error('加载游戏历史失败:', error)
    ElMessage.error('加载游戏历史失败')
  } finally {
    loading.value = false
  }
}

// 查看游戏详情
const viewGameDetail = async (gameId) => {
  showDetailDialog.value = true
  gameDetail.value = null
  try {
    const { data } = await api.get(`/analytics/games/${gameId}`)
    gameDetail.value = data
  } catch (error) {
    console.error('加载游戏详情失败:', error)
    ElMessage.error('加载游戏详情失败')
  }
}

// 格式化数字
const formatNumber = (num) => {
  if (num == null) return '-'
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
}

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 格式化时间
const formatTime = (isoString) => {
  if (!isoString) return '-'
  return new Date(isoString).toLocaleString('zh-CN')
}

// 获取状态类型
const getStatusType = (status) => {
  const map = { finished: 'success', playing: 'warning', waiting: 'info' }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const map = { finished: '已完成', playing: '进行中', waiting: '等待中' }
  return map[status] || status
}

// 获取胜率样式类
const getWinRateClass = (rate) => {
  if (rate >= 30) return 'high'
  if (rate >= 20) return 'medium'
  return 'low'
}

// 初始化
onMounted(() => {
  loadOverview()
  loadHandTypes()
  loadPositions()
  loadHistory()
})
</script>

<style scoped>
.analytics-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: 100vh;
}

.header-card {
  margin-bottom: 20px;
  text-align: center;
}

.header-card h1 {
  margin: 0;
  color: #1a1a1a;
  font-size: 32px;
}

.subtitle {
  margin: 10px 0 0;
  color: #666;
  font-size: 16px;
}

.stats-overview {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #1a1a1a;
}

.stat-value.success { color: #67c23a; }
.stat-value.warning { color: #e6a23c; }
.stat-value.info { color: #409eff; }

.hand-types-chart, .positions-chart {
  padding: 10px 0;
}

.hand-type-item {
  margin-bottom: 15px;
}

.hand-type-label {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
  color: #333;
}

.hand-type-bar-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hand-type-bar {
  height: 30px;
  background: linear-gradient(90deg, #409eff, #66b1ff);
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  min-width: 40px;
  transition: width 0.3s ease;
}

.hand-type-count {
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.hand-type-percentage {
  font-size: 14px;
  color: #666;
  min-width: 50px;
}

.position-item {
  margin-bottom: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.position-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.position-stats {
  display: flex;
  gap: 20px;
}

.position-stat {
  display: flex;
  gap: 5px;
  align-items: center;
}

.position-stat .label {
  font-size: 13px;
  color: #666;
}

.position-stat .value {
  font-size: 14px;
  font-weight: 600;
}

.position-stat .value.high { color: #67c23a; }
.position-stat .value.medium { color: #e6a23c; }
.position-stat .value.low { color: #f56c6c; }
.position-stat .value.profit { color: #67c23a; }
.position-stat .value.loss { color: #f56c6c; }

.pot-value {
  font-weight: 600;
  color: #e6a23c;
}

.profit {
  color: #67c23a;
  font-weight: 600;
}

.loss {
  color: #f56c6c;
  font-weight: 600;
}

.game-detail {
  max-height: 600px;
  overflow-y: auto;
}
</style>
