<template>
  <el-config-provider :locale="zhCn">
    <el-container class="app-container">
      <!-- 头部导航 -->
      <el-header class="app-header">
        <div class="logo" @click="goHome">
          <span class="logo-icon">🎰</span>
          <span class="logo-text">德州扑克AI系统</span>
        </div>
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          :ellipsis="false"
          router
          class="nav-menu"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>控制台</span>
          </el-menu-item>
          <el-menu-item index="/analytics">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
          <el-menu-item index="/stats">
            <el-icon><User /></el-icon>
            <span>玩家统计</span>
          </el-menu-item>
          <el-menu-item index="/simulation">
            <el-icon><Setting /></el-icon>
            <span>游戏模拟</span>
          </el-menu-item>
        </el-menu>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <div class="footer-left">
            <span class="footer-title">德州扑克 AI 系统</span>
            <span class="footer-version">v1.0.0</span>
          </div>
          <div class="footer-links">
            <a href="https://github.com/shanglily01-lab/dzpoker" target="_blank" class="footer-link">
              <el-icon><Link /></el-icon>
              <span>GitHub</span>
            </a>
            <a href="http://localhost:8000/docs" target="_blank" class="footer-link">
              <el-icon><Document /></el-icon>
              <span>API 文档</span>
            </a>
          </div>
        </div>
      </el-footer>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled, Monitor, DataAnalysis, User, Setting, Link, Document } from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const router = useRouter()
const activeMenu = computed(() => route.path)

const goHome = () => {
  router.push('/')
}
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
  background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
  padding: 0 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo {
  display: flex;
  align-items: center;
  margin-right: 50px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 32px;
  margin-right: 12px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
}

.nav-menu {
  background-color: transparent !important;
  border: none !important;
  flex: 1;
}

.el-menu--horizontal {
  border-bottom: none !important;
}

.el-menu-item {
  color: #aaa !important;
  font-size: 15px;
  font-weight: 500;
  border-bottom: 3px solid transparent !important;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.el-menu-item .el-icon {
  font-size: 18px;
}

.el-menu-item:hover {
  color: #667eea !important;
  background-color: rgba(102, 126, 234, 0.1) !important;
  border-bottom-color: #667eea !important;
}

.el-menu-item.is-active {
  color: #667eea !important;
  background-color: rgba(102, 126, 234, 0.15) !important;
  border-bottom-color: #667eea !important;
}

.app-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.app-footer {
  background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
  padding: 20px 30px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.3);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-title {
  font-size: 14px;
  font-weight: 600;
  color: #909399;
}

.footer-version {
  font-size: 12px;
  color: #606266;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  text-decoration: none;
  font-size: 13px;
  transition: all 0.3s ease;
  padding: 6px 12px;
  border-radius: 6px;
}

.footer-link:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.footer-link .el-icon {
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 15px;
  }

  .logo {
    margin-right: 20px;
  }

  .logo-icon {
    font-size: 24px;
  }

  .logo-text {
    font-size: 16px;
  }

  .el-menu-item {
    padding: 0 10px;
    font-size: 14px;
  }

  .el-menu-item span {
    display: none;
  }

  .el-menu-item .el-icon {
    margin: 0;
  }

  .footer-content {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .footer-links {
    justify-content: center;
  }
}
</style>
