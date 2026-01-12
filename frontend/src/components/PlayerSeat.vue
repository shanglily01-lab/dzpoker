<template>
  <div class="player-seat-component" :class="playerStateClasses">
    <!-- 玩家头像 -->
    <div class="player-avatar">
      <div class="avatar-circle">
        P{{ player.player_id }}
      </div>
      <div v-if="player.position !== undefined" class="position-badge">
        {{ positionName }}
      </div>
    </div>

    <!-- 玩家信息 -->
    <div class="player-info">
      <div class="player-name">玩家 {{ player.player_id }}</div>
      <div class="player-chips">
        <span class="chips-icon">🪙</span>
        {{ formatChips(player.chips) }}
      </div>
    </div>

    <!-- 当前下注 -->
    <div v-if="player.current_bet > 0" class="current-bet">
      <div class="bet-chips">
        💰 {{ formatChips(player.current_bet) }}
      </div>
    </div>

    <!-- 手牌 -->
    <div class="player-cards">
      <template v-if="showCards && cards.length > 0">
        <PlayingCard
          v-for="(card, idx) in cards"
          :key="idx"
          :card="card"
          :show-card="true"
          size="small"
        />
      </template>
      <template v-else-if="!showCards && cards.length > 0">
        <div class="card-back-mini"></div>
        <div class="card-back-mini"></div>
      </template>
    </div>

    <!-- 状态指示器 -->
    <div class="player-status">
      <el-tag v-if="player.is_all_in" type="danger" size="small">All-In</el-tag>
      <el-tag v-else-if="!player.is_active" type="info" size="small">弃牌</el-tag>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PlayingCard from './PlayingCard.vue'

const props = defineProps({
  player: {
    type: Object,
    required: true
  },
  cards: {
    type: Array,
    default: () => []
  },
  showCards: {
    type: Boolean,
    default: false
  },
  isCurrentUser: {
    type: Boolean,
    default: false
  }
})

const playerStateClasses = computed(() => {
  return {
    'is-active': props.player.is_active,
    'is-all-in': props.player.is_all_in,
    'is-folded': !props.player.is_active && !props.player.is_all_in,
    'is-current-user': props.isCurrentUser
  }
})

const positionName = computed(() => {
  const positions = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO']
  return positions[props.player.position] || `P${props.player.position + 1}`
})

const formatChips = (amount) => {
  if (!amount) return '0'
  return amount.toLocaleString()
}
</script>

<style scoped>
.player-seat-component {
  background: rgba(0, 0, 0, 0.7);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 15px;
  min-width: 140px;
  transition: all 0.3s ease;
  position: relative;
}

.player-seat-component:hover {
  border-color: rgba(255, 255, 255, 0.4);
  transform: scale(1.05);
}

.player-seat-component.is-current-user {
  border-color: #ffd700;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
}

.player-seat-component.is-folded {
  opacity: 0.5;
  filter: grayscale(60%);
}

.player-seat-component.is-all-in {
  border-color: #e74c3c;
  animation: pulse 2s infinite;
}

/* 头像区域 */
.player-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  position: relative;
}

.avatar-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.position-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ffd700;
  color: #000;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: bold;
}

/* 玩家信息 */
.player-info {
  text-align: center;
  margin-bottom: 10px;
}

.player-name {
  color: #fff;
  font-size: 14px;
  margin-bottom: 5px;
  font-weight: 500;
}

.player-chips {
  color: #4ecca3;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.chips-icon {
  font-size: 14px;
}

/* 当前下注 */
.current-bet {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.bet-chips {
  background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
  color: #ffd700;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: bold;
  border: 2px solid #ffd700;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  white-space: nowrap;
}

/* 手牌 */
.player-cards {
  display: flex;
  gap: 5px;
  justify-content: center;
  margin-bottom: 10px;
  min-height: 70px;
  align-items: center;
}

.card-back-mini {
  width: 50px;
  height: 70px;
  background: repeating-linear-gradient(
    45deg,
    #667eea,
    #667eea 10px,
    #764ba2 10px,
    #764ba2 20px
  );
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* 状态指示器 */
.player-status {
  display: flex;
  justify-content: center;
  min-height: 24px;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 20px rgba(231, 76, 60, 0.5);
  }
  50% {
    box-shadow: 0 0 40px rgba(231, 76, 60, 0.8);
  }
}
</style>
