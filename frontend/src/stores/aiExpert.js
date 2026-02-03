import { defineStore } from 'pinia'
import api from '../services/api'

export const useAIExpertStore = defineStore('aiExpert', {
  state: () => ({
    // 列表数据
    experts: [],
    total: 0,
    page: 1,
    pageSize: 10,
    
    // 加载状态
    loading: false,
    error: null,
    
    // 筛选条件
    filters: {
      keyword: '',
      status: '',
      category: ''
    },

    // 分类列表
    categories: [],
    
    // 表单数据
    formData: null,
    formDialogVisible: false,
    isEdit: false
  }),

  getters: {
    // 获取所有可用的分类
    availableCategories: (state) => state.categories,
    
    // 获取所有可用的状态
    availableStatuses: () => [
      { label: '激活', value: 'active' },
      { label: '停用', value: 'inactive' },
      { label: '草稿', value: 'draft' }
    ]
  },

  actions: {
    // ============ 数据获取 ============
    
    /**
     * 获取专家列表
     */
    async fetchExperts() {
      this.loading = true
      this.error = null
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
          ...(this.filters.keyword && { keyword: this.filters.keyword }),
          ...(this.filters.status && { status: this.filters.status }),
          ...(this.filters.category && { category: this.filters.category })
        }
        
        const response = await api.get('/ai/experts/', { params })
        this.experts = response.data.items || []
        this.total = response.data.total || 0
        this.page = response.data.page || 1
        this.pageSize = response.data.page_size || 10
      } catch (err) {
        this.error = err.response?.data?.detail || err.message || '获取专家列表失败'
        console.error('获取专家列表失败:', err)
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取专家分类列表
     */
    async fetchCategories() {
      try {
        const response = await api.get('/ai/experts/categories/')
        this.categories = response.data.items || []
      } catch (err) {
        console.error('获取分类失败:', err)
      }
    },

    /**
     * 获取单个专家详情
     */
    async fetchExpertById(id) {
      try {
        const response = await api.get(`/ai/experts/${id}/`)
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || '获取专家详情失败'
        throw err
      }
    },

    // ============ CRUD 操作 ============

    /**
     * 创建专家
     */
    async createExpert(expertData) {
      try {
        const response = await api.post('/ai/experts/', expertData)
        await this.fetchExperts()
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || '创建专家失败'
        throw err
      }
    },

    /**
     * 更新专家
     */
    async updateExpert(id, expertData) {
      try {
        const response = await api.put(`/ai/experts/${id}/`, expertData)
        await this.fetchExperts()
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || '更新专家失败'
        throw err
      }
    },

    /**
     * 删除专家
     */
    async deleteExpert(id) {
      try {
        await api.delete(`/ai/experts/${id}/`)
        await this.fetchExperts()
        return { success: true }
      } catch (err) {
        this.error = err.response?.data?.detail || '删除专家失败'
        throw err
      }
    },

    /**
     * 切换专家状态
     */
    async updateExpertStatus(id, status) {
      try {
        await api.patch(`/ai/experts/${id}/status?status=${status}`)
        await this.fetchExperts()
      } catch (err) {
        this.error = err.response?.data?.detail || '状态更新失败'
        throw err
      }
    },

    // ============ 分页和筛选 ============

    /**
     * 设置当前页码
     */
    setPage(page) {
      this.page = page
      this.fetchExperts()
    },

    /**
     * 设置每页数量
     */
    setPageSize(pageSize) {
      this.pageSize = pageSize
      this.page = 1 // 重置到第一页
      this.fetchExperts()
    },

    /**
     * 设置筛选条件
     */
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.page = 1 // 重置到第一页
      this.fetchExperts()
    },

    /**
     * 重置筛选条件
     */
    resetFilters() {
      this.filters = { keyword: '', status: '', category: '' }
      this.page = 1
      this.fetchExperts()
    },

    /**
     * 搜索专家
     */
    searchExperts(keyword) {
      this.setFilters({ keyword })
    },

    /**
     * 按状态筛选
     */
    filterByStatus(status) {
      this.setFilters({ status })
    },

    /**
     * 按分类筛选
     */
    filterByCategory(category) {
      this.setFilters({ category })
    },

    // ============ 表单对话框 ============

    /**
     * 打开创建表单
     */
    openCreateForm() {
      this.isEdit = false
      this.formData = {
        code: '',
        name: '',
        avatar: '',
        welcome_message: '欢迎咨询！',
        introduction: '',
        capabilities: '',
        prompt: '',
        status: 'draft',
        version: '1.0.0',
        category: '',
        tags: [],
        sort_order: 999,
        created_by: 'admin'
      }
      this.formDialogVisible = true
    },

    /**
     * 打开编辑表单
     */
    openEditForm(expert) {
      this.isEdit = true
      this.formData = {
        ...expert,
        tags: expert.tags || []
      }
      this.formDialogVisible = true
    },

    /**
     * 关闭表单对话框
     */
    closeForm() {
      this.formDialogVisible = false
      this.formData = null
    },

    /**
     * 清空错误信息
     */
    clearError() {
      this.error = null
    }
  }
})
