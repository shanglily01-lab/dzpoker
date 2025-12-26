<template>
  <div class="home">
    <div class="hero">
      <h1>德州扑克AI测试系统</h1>
      <p>智能发牌算法 · 玩家行为分析 · AI策略优化</p>

      <div class="actions">
        <el-button type="primary" size="large" @click="createGame">
          创建游戏
        </el-button>
        <el-button size="large" @click="goToDashboard">
          进入控制台
        </el-button>
      </div>
    </div>

    <!-- 功能介绍 -->
    <div class="features">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <span class="feature-icon">🎴</span>
              <span>智能发牌</span>
            </template>
            <p>基于AI的智能发牌策略,在公平性约束内提升游戏娱乐性</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <span class="feature-icon">📊</span>
              <span>玩家分析</span>
            </template>
            <p>实时追踪玩家行为,自动分类玩家类型,评估技战术水平</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <span class="feature-icon">🤖</span>
              <span>AI优化</span>
            </template>
            <p>持续学习优化发牌算法,提升拟人性和游戏体验</p>
          </el-card>
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createGame as apiCreateGame } from '@/api'

const router = useRouter()
const showCreateDialog = ref(false)
const creating = ref(false)

const gameForm = reactive({
  numPlayers: 6,
  smallBlind: 1,
  bigBlind: 2,
  smartDealing: true
})

const createGame = () => {
  showCreateDialog.value = true
}

const goToDashboard = () => {
  router.push('/dashboard')
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
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 80px 20px;
}

.hero h1 {
  font-size: 48px;
  color: #e94560;
  margin-bottom: 20px;
}

.hero p {
  font-size: 18px;
  color: #aaa;
  margin-bottom: 40px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.features {
  margin-top: 60px;
}

.feature-card {
  background-color: #16213e;
  border: 1px solid #0f3460;
  color: #eee;
  height: 200px;
}

.feature-card :deep(.el-card__header) {
  background-color: #0f3460;
  padding: 15px 20px;
}

.feature-icon {
  font-size: 24px;
  margin-right: 10px;
}

.feature-card p {
  color: #aaa;
  line-height: 1.8;
}
</style>
