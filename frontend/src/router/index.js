import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Users from '../views/Users.vue'
import AIChat from '../views/AIChat.vue'
import AIExpertManagement from '../views/AIExpertManagement.vue'
import AIExpertDetail from '../views/AIExpertDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/users',
    name: 'Users',
    component: Users
  },
  {
    path: '/ai',
    name: 'AIChat',
    component: AIChat
  },
  {
    path: '/ai-experts',
    name: 'AIExpertManagement',
    component: AIExpertManagement
  },
  {
    path: '/ai-experts/:id',
    name: 'AIExpertDetail',
    component: AIExpertDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router