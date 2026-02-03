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
        text-color="#606266"
        active-text-color="#409EFC"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>系统首页</span>
        </el-menu-item>
        
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-menu-item index="/ai">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 智能对话</span>
        </el-menu-item>
        
        <el-menu-item index="/ai-experts">
          <el-icon><Collection /></el-icon>
          <span>专家模型库</span>
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
import { House, User, ChatDotRound, Collection } from '@element-plus/icons-vue'

const route = useRoute()
const activePath = computed(() => route.path)

const currentRouteName = computed(() => {
  switch (route.path) {
    case '/': return '系统首页';
    case '/users': return '用户管理';
    case '/ai': return 'AI 智能对话';
    case '/ai-experts': return '专家模型管理';
    default: return '当前页面';
  }
})
</script>

<style>
:root {
  --el-color-primary: #409EFC;
  --header-height: 60px;
  --aside-width: 240px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  background-color: #f0f2f5;
  color: #303133;
}

.layout-container {
  height: 100vh;
  display: flex;
}

/* Sidebar Styles */
.aside-menu {
  background-color: #ffffff;
  border-right: 1px solid #dcdfe6;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px 0 rgba(29, 35, 41, 0.05);
  z-index: 10;
  transition: width 0.3s;
}

.logo-container {
  height: var(--header-height);
  display: flex;
  align-items: center;
  padding-left: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.logo-icon {
  font-size: 28px;
  margin-right: 12px;
}

.logo-text {
  font-weight: 600;
  font-size: 18px;
  color: #303133;
  letter-spacing: 0.5px;
}

.el-menu-vertical {
  border-right: none !important;
  flex: 1;
  padding-top: 10px;
}

.el-menu-item {
  margin: 4px 8px;
  border-radius: 4px;
  height: 50px;
  line-height: 50px;
}

.el-menu-item.is-active {
  background-color: #ecf5ff;
  font-weight: 600;
}

.el-menu-item:hover {
  background-color: #f5f7fa;
}

.menu-footer {
  padding: 20px;
  text-align: center;
  border-top: 1px solid #f0f0f0;
}

.version-text {
  font-size: 12px;
  color: #909399;
}

/* Header Styles */
.main-header {
  background-color: #ffffff;
  border-bottom: 1px solid #dcdfe6;
  height: var(--header-height) !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08);
  position: relative;
  z-index: 9;
}

.header-right .user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.3s;
}

.header-right .user-info:hover {
  background: #f5f7fa;
}

.user-avatar {
  background-color: #409EFC;
  color: white;
  margin-right: 8px;
  font-size: 12px;
}

.admin-name {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

/* Main Content Styles */
.main-body {
  background-color: #f0f2f5;
  padding: 0 !important;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.main-content-wrapper {
  flex: 1;
  padding: 24px;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
}

.main-footer {
  text-align: center;
  color: #909399;
  font-size: 12px;
  padding: 20px 0;
  height: auto !important;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>