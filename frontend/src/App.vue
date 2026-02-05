<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="aside-menu">
      <div class="logo-container">
        <span class="logo-icon">🤖</span>
        <span class="logo-text">AI 专家管理平台</span>
      </div>
      
      <el-menu
        :default-active="activePath"
        class="el-menu-vertical"
        router
        :collapse="false"
        background-color="#ffffff"
        text-color="#475569"
        active-text-color="#2563eb"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>系统首页</span>
        </el-menu-item>
        
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-menu-item index="/ai-experts">
          <el-icon><Collection /></el-icon>
          <span>专家管理</span>
        </el-menu-item>

        <el-menu-item index="/mcp">
          <el-icon><Tools /></el-icon>
          <span>MCP管理</span>
        </el-menu-item>

        <el-menu-item index="/models">
          <el-icon><Setting /></el-icon>
          <span>模型管理</span>
        </el-menu-item>
        
        <el-menu-item index="/ai">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 对话</span>
        </el-menu-item>
      </el-menu>

      <div class="menu-footer">
        <span class="version-text">v1.2.0</span>
      </div>
    </el-aside>
    
    <el-container class="is-vertical">
      <el-header class="main-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.path !== '/'">{{ currentRouteName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <div class="user-info">
            <el-avatar :size="32" class="user-avatar">AD</el-avatar>
            <span class="admin-name">管理员</span>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-body">
        <div class="main-content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
        <el-footer class="main-footer">
          © 2026 AI Expert Manager System. All rights reserved.
        </el-footer>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { House, User, ChatDotRound, Collection, Tools, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const activePath = computed(() => route.path)

const currentRouteName = computed(() => {
  switch (route.path) {
    case '/': return '系统首页';
    case '/users': return '用户管理';
    case '/ai': return 'AI 智能对话';
    case '/ai-experts': return '专家管理';
    case '/mcp': return 'MCP工具管理';
    case '/models': return '模型配置';
    default: 
      if (route.path.startsWith('/ai-experts/')) return '专家详情';
      return '当前页面';
  }
})
</script>

<style>
:root {
  --el-color-primary: var(--primary);
  --el-color-primary-light-3: var(--primary-light);
  --header-height: 56px;
  --aside-width: 240px;
}

.layout-container {
  height: 100vh;
  display: flex;
}

.aside-menu {
  background: var(--bg-card);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
  z-index: 10;
  transition: width var(--transition);
}

.logo-container {
  height: var(--header-height);
  display: flex;
  align-items: center;
  padding-left: var(--space-6);
  border-bottom: 1px solid var(--border-light);
}

.logo-icon {
  font-size: 24px;
  margin-right: var(--space-3);
}

.logo-text {
  font-weight: var(--font-semibold);
  font-size: var(--text-lg);
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.el-menu-vertical {
  border-right: none !important;
  flex: 1;
  padding-top: var(--space-2);
}

.el-menu-item {
  margin: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  height: 44px;
  line-height: 44px;
  font-size: var(--text-sm);
}

.el-menu-item.is-active {
  background: var(--primary-light);
  color: var(--primary);
  font-weight: var(--font-semibold);
}

.el-menu-item:hover {
  background: var(--bg-hover);
}

.menu-footer {
  padding: var(--space-5);
  text-align: center;
  border-top: 1px solid var(--border-light);
}

.version-text {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.main-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  height: var(--header-height) !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  box-shadow: var(--shadow-sm);
  position: relative;
  z-index: 9;
}

.header-right .user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  transition: background var(--transition);
}

.header-right .user-info:hover {
  background: var(--bg-hover);
}

.user-avatar {
  background: var(--primary);
  color: white;
  margin-right: var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.admin-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.main-body {
  background: var(--bg-page);
  padding: 0 !important;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.main-content-wrapper {
  flex: 1;
  padding: var(--space-6);
  width: 96%;
  margin: 0 auto;
}

.main-footer {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--text-xs);
  padding: var(--space-5) 0;
  height: auto !important;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>