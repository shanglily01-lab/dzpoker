import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/game/:id',
    name: 'Game',
    component: () => import('@/views/GameTable.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/PlayerStats.vue')
  },
  {
    path: '/simulation',
    name: 'Simulation',
    component: () => import('@/views/GameSimulation.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
