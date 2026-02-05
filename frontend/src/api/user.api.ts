/**
 * User API module
 */
import http from './http';
import type { User, UserCreate, UserUpdate, UserLogin, Token, PaginatedResponse } from '@/types/user';

export const userApi = {
  // Authentication
  login: async (credentials: UserLogin): Promise<Token> => {
    const { data } = await http.post('/api/v1/auth/login', credentials);
    return data;
  },

  logout: async (): Promise<void> => {
    await http.post('/api/v1/auth/logout');
  },

  getCurrentUser: async (): Promise<User> => {
    const { data } = await http.get('/api/v1/auth/me');
    return data;
  },

  // User CRUD operations
  getUsers: async (page = 1, limit = 20): Promise<PaginatedResponse<User>> => {
    const offset = (page - 1) * limit;
    const { data } = await http.get('/api/v1/users', {
      params: { offset, limit }
    });
    return data;
  },

  getUserById: async (id: number): Promise<User> => {
    const { data } = await http.get(`/api/v1/users/${id}`);
    return data;
  },

  createUser: async (userData: UserCreate): Promise<User> => {
    const { data } = await http.post('/api/v1/users', userData);
    return data;
  },

  updateUser: async (id: number, userData: UserUpdate): Promise<User> => {
    const { data } = await http.put(`/api/v1/users/${id}`, userData);
    return data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await http.delete(`/api/v1/users/${id}`);
  }
};