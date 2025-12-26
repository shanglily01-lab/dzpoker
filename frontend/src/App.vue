<template>
  <el-config-provider :locale="zhCn">
    <el-container class="app-container">
      <!-- 头部导航 -->
      <el-header class="app-header">
        <div class="logo">
          <span class="logo-icon">🎰</span>
          <span class="logo-text">德州扑克AI系统</span>
        </div>
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          :ellipsis="false"
          router
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/dashboard">控制台</el-menu-item>
          <el-menu-item index="/stats">玩家统计</el-menu-item>
        </el-menu>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer class="app-footer">
        德州扑克AI测试系统 v1.0.0
      </el-footer>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background-color: #1a1a2e;
  color: #eee;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  background-color: #16213e;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  margin-right: 40px;
}

.logo-icon {
  font-size: 28px;
  margin-right: 10px;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  color: #e94560;
}

.el-menu {
  background-color: transparent;
  border: none;
}

.el-menu-item {
  color: #aaa !important;
}

.el-menu-item:hover,
.el-menu-item.is-active {
  color: #e94560 !important;
  background-color: transparent !important;
}

.app-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.app-footer {
  text-align: center;
  color: #666;
  font-size: 12px;
  background-color: #16213e;
}
</style>
