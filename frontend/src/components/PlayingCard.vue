<template>
  <div class="playing-card" :class="[suitColor, sizeClass, { 'is-revealed': showCard }]">
    <div v-if="showCard" class="card-face">
      <div class="card-rank">{{ rankSymbol }}</div>
      <div class="card-suit">{{ suitSymbol }}</div>
    </div>
    <div v-else class="card-back">
      <div class="back-pattern"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  card: {
    type: Object,
    required: false,
    default: null
  },
  showCard: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'normal', // 'small', 'normal', 'large'
    validator: (value) => ['small', 'normal', 'large'].includes(value)
  },
  index: {
    type: Number,
    default: 0
  }
})

const SUITS = ['♠', '♥', '♦', '♣']
const RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

const rankSymbol = computed(() => {
  if (!props.card) return ''
  return RANKS[props.card.rank] || ''
})

const suitSymbol = computed(() => {
  if (!props.card) return ''
  return SUITS[props.card.suit] || ''
})

const suitColor = computed(() => {
  if (!props.card) return ''
  // Hearts (1) and Diamonds (2) are red
  return (props.card.suit === 1 || props.card.suit === 2) ? 'red-suit' : 'black-suit'
})

const sizeClass = computed(() => {
  return `size-${props.size}`
})
</script>

<style scoped>
.playing-card {
  position: relative;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  display: inline-block;
  overflow: hidden;
}

/* 尺寸变体 */
.playing-card.size-small {
  width: 50px;
  height: 70px;
  border-radius: 5px;
}

.playing-card.size-small .card-rank {
  font-size: 18px;
}

.playing-card.size-small .card-suit {
  font-size: 20px;
}

.playing-card.size-normal {
  width: 70px;
  height: 98px;
}

.playing-card.size-large {
  width: 90px;
  height: 126px;
}

.playing-card.size-large .card-rank {
  font-size: 32px;
}

.playing-card.size-large .card-suit {
  font-size: 48px;
}

.playing-card.is-revealed {
  animation: flipIn 0.6s ease;
}

@keyframes flipIn {
  0% {
    transform: rotateY(90deg);
    opacity: 0;
  }
  100% {
    transform: rotateY(0);
    opacity: 1;
  }
}

.playing-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

/* 牌面 */
.card-face {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px;
  position: relative;
}

.card-rank {
  position: absolute;
  top: 5px;
  left: 5px;
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
}

.card-suit {
  font-size: 36px;
  line-height: 1;
}

.playing-card.red-suit .card-rank,
.playing-card.red-suit .card-suit {
  color: #e74c3c;
}

.playing-card.black-suit .card-rank,
.playing-card.black-suit .card-suit {
  color: #2c3e50;
}

/* 牌背 */
.card-back {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.back-pattern {
  width: 100%;
  height: 100%;
  background-image:
    repeating-linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.1) 0px,
      rgba(255, 255, 255, 0.1) 10px,
      transparent 10px,
      transparent 20px
    ),
    repeating-linear-gradient(
      -45deg,
      rgba(255, 255, 255, 0.1) 0px,
      rgba(255, 255, 255, 0.1) 10px,
      transparent 10px,
      transparent 20px
    );
}
</style>
