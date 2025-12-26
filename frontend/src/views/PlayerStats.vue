<template>
  <div class="player-stats">
    <h2>玩家统计分析</h2>

    <!-- 玩家列表 -->
    <el-card class="section-card">
      <template #header>
        <div class="header-with-search">
          <span>玩家列表</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索玩家"
            style="width: 200px"
            clearable
          />
        </div>
      </template>

      <el-table :data="filteredPlayers" stripe @row-click="selectPlayer">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="chips" label="筹码" width="120">
          <template #default="{ row }">
            <span class="chips">{{ row.chips.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级" width="80" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.playerType)">
              {{ row.playerType || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="skillLevel" label="技术评分" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.skillLevel || 0"
              :color="getSkillColor(row.skillLevel)"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 玩家详情 -->
    <el-card v-if="selectedPlayer" class="section-card">
      <template #header>
        玩家详情 - {{ selectedPlayer.nickname }}
      </template>

      <el-row :gutter="20">
        <!-- 基础统计 -->
        <el-col :span="12">
          <h4>核心指标</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-name">VPIP (入池率)</div>
              <div class="stat-value">{{ selectedPlayer.vpip || 0 }}%</div>
              <div class="stat-bar">
                <div
                  class="stat-bar-fill"
                  :style="{ width: (selectedPlayer.vpip || 0) + '%' }"
                ></div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-name">PFR (翻前加注)</div>
              <div class="stat-value">{{ selectedPlayer.pfr || 0 }}%</div>
              <div class="stat-bar">
                <div
                  class="stat-bar-fill pfr"
                  :style="{ width: (selectedPlayer.pfr || 0) + '%' }"
                ></div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-name">AF (激进因子)</div>
              <div class="stat-value">{{ selectedPlayer.af || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-name">总手牌</div>
              <div class="stat-value">{{ selectedPlayer.totalHands || 0 }}</div>
            </div>
          </div>
        </el-col>

        <!-- AI分析 -->
        <el-col :span="12">
          <h4>AI分析建议</h4>
          <div class="recommendations">
            <el-alert
              v-for="(rec, index) in selectedPlayer.recommendations || []"
              :key="index"
              :title="rec"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 10px"
            />
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const searchQuery = ref('')
const selectedPlayer = ref(null)

// 模拟数据
const players = ref([
  {
    id: 1,
    nickname: '玩家1',
    chips: 12500,
    level: 3,
    playerType: '紧凶型',
    skillLevel: 75,
    vpip: 22,
    pfr: 16,
    af: 2.5,
    totalHands: 520,
    recommendations: [
      '数据良好,继续保持!',
      'VPIP和PFR比例合理'
    ]
  },
  {
    id: 2,
    nickname: '玩家2',
    chips: 8200,
    level: 2,
    playerType: '松凶型',
    skillLevel: 62,
    vpip: 35,
    pfr: 22,
    af: 3.2,
    totalHands: 380,
    recommendations: [
      '建议收紧起手牌范围,减少入池率',
      '打法过于激进,建议适当控制'
    ]
  },
  {
    id: 3,
    nickname: '玩家3',
    chips: 5800,
    level: 1,
    playerType: '被动型',
    skillLevel: 38,
    vpip: 18,
    pfr: 6,
    af: 0.8,
    totalHands: 210,
    recommendations: [
      '建议增加翻前加注频率,打法更激进',
      '跟注过多,建议要么加注要么弃牌',
      '打法过于被动,建议增加下注和加注'
    ]
  }
])

const filteredPlayers = computed(() => {
  if (!searchQuery.value) return players.value
  return players.value.filter(p =>
    p.nickname.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const selectPlayer = (row) => {
  selectedPlayer.value = row
}

const getTypeColor = (type) => {
  const colors = {
    '紧凶型': 'success',
    '松凶型': 'warning',
    '被动型': 'info',
    '鱼': 'danger'
  }
  return colors[type] || 'info'
}

const getSkillColor = (level) => {
  if (level >= 70) return '#67c23a'
  if (level >= 50) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  if (players.value.length > 0) {
    selectedPlayer.value = players.value[0]
  }
})
</script>

<style scoped>
.player-stats {
  max-width: 1200px;
  margin: 0 auto;
}

.player-stats h2 {
  margin-bottom: 20px;
  color: #e94560;
}

.section-card {
  background-color: #16213e;
  border: 1px solid #0f3460;
  color: #eee;
  margin-bottom: 20px;
}

.header-with-search {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chips {
  color: #4ecca3;
  font-weight: bold;
}

:deep(.el-table) {
  background-color: transparent;
  color: #eee;
  cursor: pointer;
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

:deep(.el-table tr:hover > td) {
  background-color: #1e3a5f !important;
}

h4 {
  color: #e94560;
  margin-bottom: 15px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stat-item {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
}

.stat-name {
  color: #aaa;
  font-size: 12px;
  margin-bottom: 5px;
}

.stat-value {
  color: #4ecca3;
  font-size: 24px;
  font-weight: bold;
}

.stat-bar {
  height: 6px;
  background: #333;
  border-radius: 3px;
  margin-top: 10px;
  overflow: hidden;
}

.stat-bar-fill {
  height: 100%;
  background: #4ecca3;
  border-radius: 3px;
  transition: width 0.3s;
}

.stat-bar-fill.pfr {
  background: #e94560;
}

.recommendations {
  max-height: 200px;
  overflow-y: auto;
}
</style>
