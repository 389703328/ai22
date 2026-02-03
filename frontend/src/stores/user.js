import { defineStore } from 'pinia'
import api from '../services/api.js'

export const useUserStore = defineStore('user', {
  state: () => ({
    users: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchUsers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get('/users')
        this.users = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    async createUser(userData) {
      try {
        const response = await api.post('/users', userData)
        this.users.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      }
    }
  }
})