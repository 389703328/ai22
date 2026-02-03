<template>
  <div class="model-management">
    <div class="page-header">
      <div class="header-content">
        <h1>模型管理</h1>
        <p class="subtitle">管理AI模型配置与提供商集成</p>
      </div>
      <el-button type="primary" size="large" @click="showCreateDialog">新建模型</el-button>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input v-model="searchParams.keyword" placeholder="模型名称" clearable @clear="fetchModels" />
        </el-form-item>
        <el-form-item label="提供商">
          <el-select v-model="searchParams.provider" placeholder="全部" clearable @change="fetchModels">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Ollama" value="ollama" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchParams.enabled" placeholder="全部" clearable @change="fetchModels">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchModels">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 模型表格 -->
    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="models" border stripe>
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column label="提供商" width="120">
          <template #default="{ row }">
            <el-tag>{{ providerMap[row.provider] || row.provider }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="模型" width="200" />
        <el-table-column prop="base_url" label="Base URL" min-width="200" show-overflow-tooltip />
        <el-table-column label="温度" width="100">
          <template #default="{ row }">
            {{ (row.temperature / 100).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="max_tokens" label="最大Token" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button link type="primary" @click="editModel(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteModel(row)">删除</el-button>
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
        @size-change="fetchModels"
        @current-change="fetchModels"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模型' : '新建模型'"
      width="700px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="form.provider" placeholder="请选择提供商">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Ollama" value="ollama" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="form.model_name" placeholder="如: gpt-4, claude-3-opus" />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="form.api_key" type="password" placeholder="请输入API Key" show-password />
        </el-form-item>
        <el-form-item label="Base URL" prop="base_url">
          <el-input v-model="form.base_url" placeholder="如: https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="温度" prop="temperature">
          <el-slider v-model="form.temperature" :min="0" :max="100" :step="1" show-input />
          <span style="font-size: 12px; color: #909399">实际值: {{ (form.temperature / 100).toFixed(2) }}</span>
        </el-form-item>
        <el-form-item label="最大Token" prop="max_tokens">
          <el-input-number v-model="form.max_tokens" :min="1" :max="128000" :step="100" />
        </el-form-item>
        <el-form-item label="其他配置" prop="config">
          <el-input v-model="configJson" type="textarea" :rows="5" placeholder='JSON配置，例如: {"top_p": 1.0}' />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../services/api.js'

const loading = ref(false)
const submitting = ref(false)
const models = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentModel = ref(null)

const providerMap = {
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  ollama: 'Ollama',
  custom: '自定义'
}

const searchParams = reactive({
  keyword: '',
  provider: '',
  enabled: null
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  name: '',
  provider: 'openai',
  model_name: '',
  api_key: '',
  base_url: '',
  temperature: 70,
  max_tokens: 4096,
  config: null,
  enabled: true
})

const configJson = ref('')

const rules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }]
}

const fetchModels = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/models/', {
      params: {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...searchParams
      }
    })
    models.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const editModel = (row) => {
  isEdit.value = true
  currentModel.value = row
  Object.assign(form, {
    name: row.name,
    provider: row.provider,
    model_name: row.model_name,
    api_key: row.api_key,
    base_url: row.base_url,
    temperature: row.temperature,
    max_tokens: row.max_tokens,
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
    provider: 'openai',
    model_name: '',
    api_key: '',
    base_url: '',
    temperature: 70,
    max_tokens: 4096,
    config: null,
    enabled: true
  })
  configJson.value = ''
  currentModel.value = null
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
        await api.put(`/models/${currentModel.value.id}/`, payload)
        ElMessage.success('更新成功')
      } else {
        await api.post('/models/', payload)
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      fetchModels()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const deleteModel = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除模型 "${row.name}" 吗？`, '提示', {
      type: 'warning'
    })

    await api.delete(`/models/${row.id}/`)
    ElMessage.success('删除成功')
    fetchModels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchModels()
})
</script>

<style scoped>
.model-management {
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

.search-card {
  margin-bottom: 20px;
}

.table-card {
  min-height: 400px;
}
</style>
