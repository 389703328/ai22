<template>
  <div class="ai-expert-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1>AI专家管理</h1>
        <p class="subtitle">管理和配置您的AI专家智能体，定义其行为与核心提示词</p>
      </div>
      <el-button type="primary" size="large" @click="handleCreateNew">
        <el-icon class="el-icon--left"><Plus /></el-icon>新建专家
      </el-button>
    </div>

    <!-- 搜索和筛选区域 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :inline="true" :model="localFilters" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="localFilters.keyword"
            placeholder="搜索专家名称或编码..."
            clearable
            @input="handleSearchInput"
            style="width: 240px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="localFilters.status" placeholder="全部状态" clearable @change="handleFilterChange" style="width: 140px">
            <el-option label="激活" value="active" />
            <el-option label="停用" value="inactive" />
            <el-option label="草稿" value="draft" />
          </el-select>
        </el-form-item>

        <el-form-item label="分类">
          <el-autocomplete
            v-model="localFilters.category"
            :fetch-suggestions="queryCategorySearch"
            placeholder="全部分类"
            clearable
            @select="handleFilterChange"
            @input="handleFilterChange"
            style="width: 180px"
          />
        </el-form-item>

        <el-form-item class="filter-actions">
          <el-button @click="handleReset">重置</el-button>
          <el-button type="primary" plain @click="handleRefresh" :loading="loading">
            <el-icon class="el-icon--left"><Refresh /></el-icon>刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" show-icon @close="error = ''" style="margin-bottom: 20px" />

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="experts" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="code" label="编码" min-width="150">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" min-width="120">
          <template #default="{ row }">
            <el-tag v-if="row.category" effect="plain" size="small">{{ row.category }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="row.status === 'active' ? 'success' : row.status === 'inactive' ? 'info' : 'warning'"
            >
              {{ row.status === 'active' ? '激活' : row.status === 'inactive' ? '停用' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" min-width="100" />
        <el-table-column prop="usage_count" label="使用次数" min-width="120" sortable />
        <el-table-column prop="created_by" label="创建人" min-width="120" />
        <el-table-column prop="created_time" label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="260">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleManage(row.id)">管理</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="store.page"
        v-model:page-size="store.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="store.setPageSize"
        @current-change="store.setPage"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="isEditMode ? '编辑专家' : '新建专家'"
      width="600px"
      align-center
    >
      <el-form :model="formData" label-position="top" label-width="100px" class="dialog-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="专家编码" required>
              <el-input 
                v-model="formData.code" 
                placeholder="唯一标识码 (例如: code_assistant)" 
                :disabled="isEditMode" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专家名称" required>
              <el-input v-model="formData.name" placeholder="显示名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="分类">
          <el-autocomplete
            v-model="formData.category"
            :fetch-suggestions="queryCategorySearch"
            placeholder="选择或输入分类 (例如: 编程, 写作)"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="核心提示词 (System Prompt)" required>
          <el-input 
            v-model="formData.prompt" 
            type="textarea" 
            :rows="6" 
            placeholder="定义专家的核心人设、行为准则和回复风格..."
          />
        </el-form-item>
        
        <el-form-item label="初始状态">
          <el-radio-group v-model="formData.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="active">激活</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveForm">
            {{ isEditMode ? '保存修改' : '立即创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Plus, Refresh, Setting, Edit, Delete } from '@element-plus/icons-vue'
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

const queryCategorySearch = (queryString, cb) => {
  const results = categories.value.map(cat => ({ value: cat }))
  cb(queryString ? results.filter(i => i.value.toLowerCase().includes(queryString.toLowerCase())) : results)
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

const handleStatusChange = async (id, val) => {
  try {
    await store.updateExpertStatus(id, val)
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
    await store.fetchCategories()
    await store.fetchExperts()
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
.ai-expert-management {
  max-width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content h1 {
  font-size: 30px !important;
  font-weight: 700 !important;
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.subtitle {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin: 0;
}

.filter-card {
  margin-bottom: 24px;
}

.filter-actions {
  margin-left: auto;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.table-card {
  margin-bottom: 24px;
  min-height: 400px;
}

.table-card :deep(.table-header-cell) {
  background-color: var(--el-fill-color-light) !important;
  color: var(--el-color-primary);
}

/* 状态颜色 */
.status-select-active :deep(.el-input__inner) {
  color: var(--el-color-success);
}

.status-select-inactive :deep(.el-input__inner) {
  color: var(--el-color-info);
}

.status-select-draft :deep(.el-input__inner) {
  color: var(--el-color-warning);
}
</style>
