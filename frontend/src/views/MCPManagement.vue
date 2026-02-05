<template>
  <div class="mcp-management">
    <div class="page-header">
      <div class="header-content">
        <h1>MCP工具管理</h1>
        <p class="subtitle">管理模型上下文协议（MCP）工具与集成</p>
      </div>
      <el-button type="primary" size="large" @click="showCreateDialog">新建工具</el-button>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyword"
            placeholder="工具名称/描述"
            clearable
            @input="handleSearchInput"
            style="width: 240px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchParams.tool_type" placeholder="全部" clearable @change="handleFilterChange" style="width: 140px">
            <el-option label="函数" value="function" />
            <el-option label="API" value="api" />
            <el-option label="集成" value="integration" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchParams.enabled" placeholder="全部" clearable @change="handleFilterChange" style="width: 140px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <el-button @click="handleReset">重置</el-button>
          <el-button type="primary" plain @click="handleRefresh" :loading="loading">
            <el-icon class="el-icon--left"><Refresh /></el-icon>刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- MCP表格 -->
    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="mcps" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column label="图标" width="80">
          <template #default="{ row }">
            <el-avatar v-if="row.icon" :src="row.icon" :size="40" />
            <el-avatar v-else :size="40">{{ row.name[0] }}</el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column label="类型" min-width="120">
          <template #default="{ row }">
            <el-tag>{{ typeMap[row.tool_type] || row.tool_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="method" label="方法" width="100" />
        <el-table-column prop="endpoint" label="端点" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button link type="primary" @click="editMCP(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteMCP(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchMCPs"
        @current-change="fetchMCPs"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑工具' : '新建工具'"
      width="700px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入工具名称" />
        </el-form-item>
        <el-form-item label="图标URL" prop="icon">
          <el-input v-model="form.icon" placeholder="请输入图标URL" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="类型" prop="tool_type">
          <el-select v-model="form.tool_type" placeholder="请选择类型">
            <el-option label="函数" value="function" />
            <el-option label="API" value="api" />
            <el-option label="集成" value="integration" />
          </el-select>
        </el-form-item>
        <el-form-item label="方法" prop="method">
          <el-select v-model="form.method" placeholder="请选择HTTP方法">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="端点" prop="endpoint">
          <el-input v-model="form.endpoint" placeholder="请输入API端点" />
        </el-form-item>
        <el-form-item label="配置" prop="config">
          <el-input v-model="configJson" type="textarea" :rows="5" placeholder='JSON配置，例如: {"key": "value"}' />
        </el-form-item>
        <el-form-item label="状态" prop="enabled">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import api from '../services/api.js'

const loading = ref(false)
const submitting = ref(false)
const mcps = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentMCP = ref(null)
const searchTimeout = ref(null)

const typeMap = {
  function: '函数',
  api: 'API',
  integration: '集成'
}

const searchParams = reactive({
  keyword: '',
  tool_type: '',
  enabled: null
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  name: '',
  icon: '',
  description: '',
  tool_type: 'function',
  method: 'GET',
  endpoint: '',
  config: null,
  enabled: true
})

const configJson = ref('')

const rules = {
  name: [{ required: true, message: '请输入工具名称', trigger: 'blur' }],
  tool_type: [{ required: true, message: '请选择工具类型', trigger: 'change' }]
}

const fetchMCPs = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/mcp/', {
      params: {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...searchParams
      }
    })
    mcps.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取MCP工具列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearchInput = () => {
  clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    pagination.page = 1
    fetchMCPs()
  }, 500)
}

const handleFilterChange = () => {
  pagination.page = 1
  fetchMCPs()
}

const handleReset = () => {
  searchParams.keyword = ''
  searchParams.tool_type = ''
  searchParams.enabled = null
  pagination.page = 1
  fetchMCPs()
}

const handleRefresh = () => {
  fetchMCPs()
}

const showCreateDialog = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const editMCP = (row) => {
  isEdit.value = true
  currentMCP.value = row
  Object.assign(form, {
    name: row.name,
    icon: row.icon,
    description: row.description,
    tool_type: row.tool_type,
    method: row.method,
    endpoint: row.endpoint,
    config: row.config,
    enabled: row.enabled
  })
  configJson.value = row.config ? JSON.stringify(row.config, null, 2) : ''
  dialogVisible.value = true
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    name: '',
    icon: '',
    description: '',
    tool_type: 'function',
    method: 'GET',
    endpoint: '',
    config: null,
    enabled: true
  })
  configJson.value = ''
  currentMCP.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const payload = { ...form }
      if (configJson.value) {
        try {
          payload.config = JSON.parse(configJson.value)
        } catch {
          ElMessage.error('配置JSON格式错误')
          submitting.value = false
          return
        }
      }

      if (isEdit.value) {
        await api.put(`/mcp/${currentMCP.value.id}/`, payload)
        ElMessage.success('更新成功')
      } else {
        await api.post('/mcp/', payload)
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      fetchMCPs()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const deleteMCP = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除工具 "${row.name}" 吗？`, '提示', {
      type: 'warning'
    })

    await api.delete(`/mcp/${row.id}/`)
    ElMessage.success('删除成功')
    fetchMCPs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchMCPs()
})
</script>

<style scoped>
.mcp-management {
  padding: 0;
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
  min-height: 400px;
}
</style>
