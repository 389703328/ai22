<template>
  <div class="users">
    <h1>User Management</h1>
    
    <div v-if="loading" class="loading">Loading users...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div class="user-list">
      <div v-for="user in users" :key="user.id" class="user-card">
        <h3>{{ user.username }}</h3>
        <p>{{ user.email }}</p>
        <small>ID: {{ user.id }}</small>
      </div>
    </div>
    
    <button @click="fetchUsers" class="btn">Refresh Users</button>
  </div>
</template>

<script>
import { useUserStore } from '../stores/user.js'
import { storeToRefs } from 'pinia'

export default {
  name: 'Users',
  setup() {
    const userStore = useUserStore()
    const { users, loading, error } = storeToRefs(userStore)
    
    const fetchUsers = () => {
      userStore.fetchUsers()
    }
    
    // Fetch users on component mount
    fetchUsers()
    
    return {
      users,
      loading,
      error,
      fetchUsers
    }
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.users {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 32px 0;
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.loading,
.error {
  background: white;
  padding: 60px 40px;
  border-radius: 12px;
  text-align: center;
  font-size: 18px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  animation: slideUp 0.5s ease-out both;
}

.error {
  background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
  color: #c53030;
  border: 1.5px solid #fc8181;
}

.loading {
  color: #666;
}

.user-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin: 32px 0;
  animation: slideUp 0.5s ease-out 0.1s both;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
  position: relative;
  overflow: hidden;
}

.user-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #1E3C72 0%, #2A5298 100%);
}

.user-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(30, 60, 114, 0.15);
  border-color: #1E3C72;
}

.user-card h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.user-card p {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
  word-break: break-all;
}

.user-card small {
  display: block;
  color: #999;
  font-size: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.btn {
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(30, 60, 114, 0.4);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(30, 60, 114, 0.6);
}

.btn:active {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

@media (max-width: 768px) {
  .users {
    padding: 24px 16px;
  }

  h1 {
    font-size: 24px;
    margin-bottom: 24px;
  }

  .user-list {
    grid-template-columns: 1fr;
    gap: 16px;
    margin: 24px 0;
  }

  .user-card {
    padding: 20px;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>