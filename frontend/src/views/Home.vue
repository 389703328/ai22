<template>
  <div class="home-container">
    <div class="hero-section">
      <h1>AI22 Project</h1>
      <p class="subtitle">Full-stack AI Agent Management Platform</p>
    </div>
    
    <el-row :gutter="24">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>Frontend Stack</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Framework">Vue 3 (Composition API)</el-descriptions-item>
            <el-descriptions-item label="UI Library">Element Plus</el-descriptions-item>
            <el-descriptions-item label="State Management">Pinia</el-descriptions-item>
            <el-descriptions-item label="Build Tool">Vite</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="feature-card">
           <template #header>
            <div class="card-header">
              <el-icon><Platform /></el-icon>
              <span>Backend Stack</span>
            </div>
          </template>
           <el-descriptions :column="1" border>
            <el-descriptions-item label="Framework">FastAPI</el-descriptions-item>
            <el-descriptions-item label="Language">Python 3.10+</el-descriptions-item>
            <el-descriptions-item label="Database">PostgreSQL</el-descriptions-item>
            <el-descriptions-item label="ORM">SQLAlchemy (Async)</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { Monitor, Platform } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.hero-section {
  text-align: center;
  margin-bottom: 60px;
  padding: 60px 0;
  background: linear-gradient(135deg, var(--el-color-primary-light-9) 0%, var(--el-color-primary-light-8) 100%);
  border-radius: 16px;
}

h1 {
  font-size: 3rem;
  font-weight: 700;
  color: var(--el-color-primary);
  margin: 0 0 16px 0;
  letter-spacing: -1px;
}

.subtitle {
  font-size: 1.25rem;
  color: var(--el-text-color-regular);
  margin: 0;
}

.feature-card {
  height: 100%;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--el-text-color-primary);
}
</style>
