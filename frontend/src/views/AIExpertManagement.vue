<template>
  <div class="ai-expert-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>AI专家管理</h1>
      <button class="btn btn-primary" @click="handleCreateNew">+ 新建专家</button>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="search-filter-box">
      <div class="search-group">
        <input
          v-model="localFilters.keyword"
          type="text"
          placeholder="搜索专家名称或编码..."
          class="search-input"
          @input="handleSearchInput"
        />
        
        <select v-model="localFilters.status" class="filter-select" @change="handleFilterChange">
          <option value="">全部状态</option>
          <option value="active">激活</option>
          <option value="inactive">停用</option>
          <option value="draft">草稿</option>
        </select>

        <input
          v-model="localFilters.category"
          list="categoryOptions"
          type="text"
          placeholder="全部分类"
          class="filter-select"
          @input="handleFilterChange"
        />
        <datalist id="categoryOptions">
          <option v-for="item in categories" :key="item" :value="item" />
        </datalist>

        <button class="btn btn-secondary" @click="handleReset">重置</button>
        <button class="btn btn-secondary" @click="handleRefresh" :disabled="loading">
          {{ loading ? '加载中...' : '刷新' }}
        </button>
      </div>
    </div>

    <!-- 加载中状态 -->
    <div v-if="loading" class="loading-box">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-box">
      <p>❌ {{ error }}</p>
      <button class="btn btn-secondary" @click="error = ''">关闭</button>
    </div>

    <!-- 空数据提示 -->
    <div v-if="!loading && experts.length === 0 && !error" class="empty-box">
      <p>暂无数据</p>
    </div>

    <!-- 数据表格 -->
    <div v-if="!loading && experts.length > 0" class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>编码</th>
            <th>名称</th>
            <th>分类</th>
            <th>状态</th>
            <th>版本</th>
            <th>使用次数</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="expert in experts" :key="expert.id" class="data-row">
            <td>{{ expert.id }}</td>
            <td class="code-cell">{{ expert.code }}</td>
            <td>{{ expert.name }}</td>
            <td><span v-if="expert.category" class="tag">{{ expert.category }}</span></td>
            <td>
              <select :value="expert.status" class="status-select" @change="handleStatusChange(expert.id, $event)">
                <option value="active">激活</option>
                <option value="inactive">停用</option>
                <option value="draft">草稿</option>
              </select>
            </td>
            <td>{{ expert.version }}</td>
            <td>{{ expert.usage_count }}</td>
            <td class="time-cell">{{ formatDate(expert.created_time) }}</td>
            <td class="action-cell">
              <button class="btn btn-sm btn-secondary" @click="handleManage(expert.id)">管理</button>
              <button class="btn btn-sm btn-info" @click="handleEdit(expert)">编辑</button>
              <button class="btn btn-sm btn-danger" @click="handleDelete(expert.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="pagination-box">
        <span>共 {{ total }} 条 | 第 {{ page }}/{{ totalPages }} 页</span>
        <div class="pagination-controls">
          <button :disabled="page === 1" class="btn btn-secondary" @click="page > 1 && store.setPage(page - 1)">上一页</button>
          <button :disabled="page === totalPages" class="btn btn-secondary" @click="page < totalPages && store.setPage(page + 1)">下一页</button>
          <select @change="store.setPageSize(parseInt($event.target.value))">
            <option value="10">10条/页</option>
            <option value="20">20条/页</option>
            <option value="50">50条/页</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <div v-if="showDialog" class="dialog-overlay" @click="showDialog = false">
      <div class="dialog-box" @click.stop>
        <div class="dialog-header">
          <h2>{{ isEditMode ? '编辑专家' : '新建专家' }}</h2>
          <button class="close-btn" @click="showDialog = false">&times;</button>
        </div>
        <form @submit.prevent="handleSaveForm" class="dialog-form">
          <div class="form-group">
            <label>编码 *</label>
            <input v-model="formData.code" type="text" required />
          </div>
          <div class="form-group">
            <label>名称 *</label>
            <input v-model="formData.name" type="text" required />
          </div>
          <div class="form-group">
            <label>核心提示词 *</label>
            <textarea v-model="formData.prompt" required rows="5"></textarea>
          </div>
          <div class="form-group">
            <label>分类</label>
            <input v-model="formData.category" list="formCategoryOptions" type="text" placeholder="可自定义" />
            <datalist id="formCategoryOptions">
              <option v-for="item in categories" :key="item" :value="item" />
            </datalist>
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="formData.status">
              <option value="draft">草稿</option>
              <option value="active">激活</option>
              <option value="inactive">停用</option>
            </select>
          </div>
          <div class="form-group" v-if="!isEditMode">
            <label>创建人 *</label>
            <input v-model="formData.created_by" type="text" required />
          </div>
          <div class="dialog-footer">
            <button type="button" class="btn btn-secondary" @click="showDialog = false">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAIExpertStore } from '../stores/aiExpert'

const store = useAIExpertStore()
const router = useRouter()

const loading = ref(false)
const error = ref('')
const showDialog = ref(false)
const isEditMode = ref(false)
const searchTimeout = ref(null)
const localFilters = ref({ keyword: '', status: '', category: '' })
const formData = ref({
  code: '',
  name: '',
  prompt: '',
  status: 'draft',
  created_by: 'admin'
})

const page = computed(() => store.page)
const pageSize = computed(() => store.pageSize)
const experts = computed(() => store.experts)
const total = computed(() => store.total)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)
const categories = computed(() => store.availableCategories)

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr
  }
}

const handleSearchInput = () => {
  clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    store.setFilters(localFilters.value)
  }, 500)
}

const handleFilterChange = () => {
  store.setFilters(localFilters.value)
}

const handleReset = () => {
  localFilters.value = { keyword: '', status: '', category: '' }
  store.resetFilters()
}

const handleRefresh = async () => {
  loading.value = true
  try {
    await store.fetchExperts()
  } catch (err) {
    error.value = '刷新失败: ' + (err.message || '未知错误')
  } finally {
    loading.value = false
  }
}

const handleCreateNew = () => {
  isEditMode.value = false
  formData.value = {
    code: '',
    name: '',
    prompt: '',
    category: '',
    status: 'draft',
    created_by: 'admin'
  }
  showDialog.value = true
}

const handleEdit = (expert) => {
  isEditMode.value = true
  formData.value = { ...expert }
  showDialog.value = true
}

const handleManage = (id) => {
  router.push(`/ai-experts/${id}`)
}

const handleDelete = async (id) => {
  if (!confirm('确定要删除该专家吗？')) return
  try {
    await store.deleteExpert(id)
    error.value = ''
  } catch (err) {
    error.value = '删除失败: ' + (err.message || '未知错误')
  }
}

const handleStatusChange = async (id, event) => {
  try {
    await store.updateExpertStatus(id, event.target.value)
    error.value = ''
  } catch (err) {
    error.value = '状态更新失败: ' + (err.message || '未知错误')
  }
}

const handleSaveForm = async () => {
  try {
    if (isEditMode.value) {
      const { id, ...data } = formData.value
      await store.updateExpert(id, data)
    } else {
      await store.createExpert(formData.value)
    }
    showDialog.value = false
    error.value = ''
  } catch (err) {
    error.value = '保存失败: ' + (err.message || '未知错误')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    console.log('Mounting AIExpertManagement, fetching data...')
    await store.fetchCategories()
    await store.fetchExperts()
    console.log('Data fetched:', store.experts)
    error.value = ''
  } catch (err) {
    console.error('Error fetching data:', err)
    error.value = '加载数据失败: ' + (err.message || '请检查后端服务是否正常运行')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.ai-expert-management {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(30, 60, 114, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(30, 60, 114, 0.6);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-secondary {
  background: #f0f2f5;
  color: #333;
  border: 1px solid #e0e0e0;
}

.btn-secondary:hover {
  background: #e8e8e8;
  transform: translateY(-1px);
}

.btn-info {
  background: #3498db;
  color: white;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* 搜索和筛选 */
.search-filter-box {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
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

.search-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input,
.filter-select {
  padding: 10px 14px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.3s ease;
}

.search-input {
  min-width: 200px;
  flex: 1;
}

.search-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #1E3C72;
  box-shadow: 0 0 0 3px rgba(30, 60, 114, 0.1);
}

.filter-select {
  min-width: 120px;
  background: white;
  cursor: pointer;
}

/* 加载和错误 */
.loading-box,
.error-box,
.empty-box {
  background: white;
  padding: 60px 40px;
  border-radius: 12px;
  margin-bottom: 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f0f0f0;
  border-top: 4px solid #1E3C72;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-box p,
.empty-box p {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.error-box {
  background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
  color: #c53030;
  border: 1.5px solid #fc8181;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
}

.error-box p {
  margin: 0;
  font-size: 14px;
}

/* 表格 */
.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  animation: slideUp 0.5s ease-out 0.2s both;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table thead {
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f0f5 100%);
  border-bottom: 2px solid #e8e8f0;
}

.data-table th {
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.data-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
}

.data-row {
  transition: all 0.3s ease;
}

.data-row:hover {
  background: #f8f9ff;
  box-shadow: inset 0 0 0 1px #f0f0ff;
}

.code-cell {
  font-family: 'Monaco', 'Courier', monospace;
  color: #1E3C72;
  font-weight: 500;
}

.time-cell {
  color: #999;
  font-size: 12px;
}

.tag {
  display: inline-block;
  background: linear-gradient(135deg, #cce5ff 0%, #e0d5ff 100%);
  color: #0c5aa0;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status-select {
  padding: 6px 10px;
  border: 1.5px solid #e0e0e0;
  border-radius: 6px;
  font-size: 12px;
  font-family: inherit;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.status-select:focus {
  outline: none;
  border-color: #1E3C72;
}

.action-cell {
  display: flex;
  gap: 8px;
}

/* 分页 */
.pagination-box {
  background: white;
  padding: 20px 24px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  animation: slideUp 0.5s ease-out 0.3s both;
}

.pagination-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.pagination-controls select {
  padding: 8px 12px;
  border: 1.5px solid #e0e0e0;
  border-radius: 6px;
  font-size: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.dialog-box {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: scaleIn 0.3s ease-out;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f0f5 100%);
}

.dialog-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  color: #999;
  transition: all 0.3s ease;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #333;
}

.dialog-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.3s ease;
  background: white;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #1E3C72;
  box-shadow: 0 0 0 3px rgba(30, 60, 114, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式 */
@media (max-width: 768px) {
  .ai-expert-management {
    padding: 0;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 24px;
  }

  .page-header h1 {
    font-size: 24px;
    width: 100%;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .search-filter-box {
    padding: 16px;
  }

  .search-group {
    flex-direction: column;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }

  .data-table {
    font-size: 12px;
  }

  .data-table th,
  .data-table td {
    padding: 10px 8px;
  }

  .pagination-box {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .pagination-controls {
    width: 100%;
    flex-direction: column;
  }

  .pagination-controls button,
  .pagination-controls select {
    width: 100%;
  }

  .dialog-box {
    width: 95%;
  }

  .action-cell {
    flex-direction: column;
  }

  .action-cell .btn {
    width: 100%;
    padding: 8px 12px;
    font-size: 12px;
  }
}
</style>
