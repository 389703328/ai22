/**
 * User store for state management
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { userApi } from '@/api';
import type { User, UserCreate, UserUpdate, UserLogin, Token, PaginatedResponse } from '@/types/user';

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref<User[]>([]);
  const currentUser = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const loading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref({
    total: 0,
    page: 1,
    limit: 20,
    offset: 0
  });

  // Getters
  const isAuthenticated = computed(() => !!token.value);
  const userCount = computed(() => users.value.length);
  const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.limit));

  // Actions
  const setToken = (newToken: string | null) => {
    token.value = newToken;
    if (newToken) {
      localStorage.setItem('access_token', newToken);
    } else {
      localStorage.removeItem('access_token');
    }
  };

  const login = async (credentials: UserLogin): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await userApi.login(credentials);
      setToken(response.access_token);
      ElMessage.success('登录成功');
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败';
      ElMessage.error(error.value);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    try {
      await userApi.logout();
    } catch (err) {
      // Ignore logout errors
    } finally {
      setToken(null);
      currentUser.value = null;
      users.value = [];
      ElMessage.success('已退出登录');
    }
  };

  const fetchCurrentUser = async (): Promise<boolean> => {
    if (!isAuthenticated.value) return false;
    
    loading.value = true;
    error.value = null;
    
    try {
      const user = await userApi.getCurrentUser();
      currentUser.value = user;
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取用户信息失败';
      if (err.response?.status === 401) {
        setToken(null);
      }
      return false;
    } finally {
      loading.value = false;
    }
  };

  const fetchUsers = async (page = 1, limit = 20): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await userApi.getUsers(page, limit);
      users.value = response.items;
      pagination.value = {
        total: response.total,
        page,
        limit,
        offset: response.offset
      };
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取用户列表失败';
      ElMessage.error(error.value);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const createUser = async (userData: UserCreate): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      const newUser = await userApi.createUser(userData);
      users.value.push(newUser);
      pagination.value.total += 1;
      ElMessage.success('用户创建成功');
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建用户失败';
      ElMessage.error(error.value);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const updateUser = async (id: number, userData: UserUpdate): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      const updatedUser = await userApi.updateUser(id, userData);
      const index = users.value.findIndex(user => user.id === id);
      if (index !== -1) {
        users.value[index] = updatedUser;
      }
      if (currentUser.value?.id === id) {
        currentUser.value = updatedUser;
      }
      ElMessage.success('用户更新成功');
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新用户失败';
      ElMessage.error(error.value);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const deleteUser = async (id: number): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      await userApi.deleteUser(id);
      users.value = users.value.filter(user => user.id !== id);
      pagination.value.total -= 1;
      ElMessage.success('用户删除成功');
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除用户失败';
      ElMessage.error(error.value);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  return {
    // State
    users,
    currentUser,
    token,
    loading,
    error,
    pagination,
    
    // Getters
    isAuthenticated,
    userCount,
    totalPages,
    
    // Actions
    setToken,
    login,
    logout,
    fetchCurrentUser,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    clearError
  };
});