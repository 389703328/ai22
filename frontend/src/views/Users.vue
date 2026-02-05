<template>
  <div class="users-container">
    <div class="page-header">
      <div class="header-content">
        <h1>用户管理</h1>
        <p class="subtitle">管理系统用户及其权限配置</p>
      </div>
      <el-button type="primary" size="large" @click="showCreateDialog">新建用户</el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchParams.keyword"
            placeholder="用户名/邮箱/姓名"
            clearable
            @input="handleSearchInput"
            style="width: 240px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchParams.role" placeholder="全部" clearable @change="handleFilterChange" style="width: 140px">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchParams.status" placeholder="全部" clearable @change="handleFilterChange" style="width: 140px">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
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

    <!-- 用户表格 -->
    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="users" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="username" label="用户名" min-width="150" />
        <el-table-column prop="real_name" label="真实姓名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="phone" label="手机号" min-width="130" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="260">
          <template #default="{ row }">
            <el-button link type="primary" @click="editUser(row)">编辑</el-button>
            <el-button link type="warning" @click="managePermissions(row)">权限</el-button>
            <el-button link type="danger" @click="deleteUser(row)">删除</el-button>
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
        @size-change="fetchUsers"
        @current-change="fetchUsers"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新建用户'"
      width="600px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input
            v-model="form.password"
            type="password"
            maxlength="72"
            show-word-limit
            :placeholder="isEdit ? '留空则不修改密码' : '请输入密码（6-72字符）'"
            show-password
          />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 权限管理对话框 -->
    <el-dialog v-model="permissionDialogVisible" title="权限管理" width="800px">
      <el-tabs v-model="activePermissionTab">
        <el-tab-pane label="专家权限" name="expert">
          <el-checkbox-group v-model="permissions.expert_ids">
            <el-checkbox v-for="expert in availableExperts" :key="expert.id" :label="expert.id">
              {{ expert.name }}
            </el-checkbox>
          </el-checkbox-group>
        </el-tab-pane>
        <el-tab-pane label="MCP工具" name="mcp">
          <el-checkbox-group v-model="permissions.mcp_ids">
            <el-checkbox v-for="mcp in availableMCPs" :key="mcp.id" :label="mcp.id">
              {{ mcp.name }}
            </el-checkbox>
          </el-checkbox-group>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="savePermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import api from '../services/api.js'

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const activePermissionTab = ref('expert')
const currentUser = ref(null)
const searchTimeout = ref(null)

const searchParams = reactive({
  keyword: '',
  role: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  username: '',
  password: '',
  real_name: '',
  email: '',
  phone: '',
  role: 'user',
  status: 'active'
})

const permissions = reactive({
  expert_ids: [],
  subagent_ids: [],
  mcp_ids: [],
  skill_ids: [],
  knowledge_ids: []
})

const availableExperts = ref([])
const availableMCPs = ref([])

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' },
    { max: 72, message: '密码长度不能超过 72 个字符', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/users/', {
      params: {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...searchParams
      }
    })
    users.value = data.items
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearchInput = () => {
  clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    pagination.page = 1
    fetchUsers()
  }, 500)
}

const handleFilterChange = () => {
  pagination.page = 1
  fetchUsers()
}

const handleReset = () => {
  searchParams.keyword = ''
  searchParams.role = ''
  searchParams.status = ''
  pagination.page = 1
  fetchUsers()
}

const handleRefresh = () => {
  fetchUsers()
}

const showCreateDialog = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const editUser = (row) => {
  isEdit.value = true
  currentUser.value = row
  Object.assign(form, {
    username: row.username,
    password: '',
    real_name: row.real_name,
    email: row.email,
    phone: row.phone,
    role: row.role,
    status: row.status
  })
  dialogVisible.value = true
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    username: '',
    password: '',
    real_name: '',
    email: '',
    phone: '',
    role: 'user',
    status: 'active'
  })
  currentUser.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const payload = { ...form }
      if (isEdit.value && !payload.password) {
        delete payload.password
      }

      if (isEdit.value) {
        // 更新时发送 UserUpdate 模型的字段
        const updatePayload = {
          real_name: payload.real_name || null,
          email: payload.email || null,
          phone: payload.phone || null,
          role: payload.role,
          status: payload.status
        }
        if (payload.password) {
          updatePayload.password = payload.password
        }
        await api.put(`/users/${currentUser.value.id}/`, updatePayload)
        ElMessage.success('更新成功')
      } else {
        // 创建时发送 UserCreate 模型的字段
        const createPayload = {
          username: payload.username,
          password: payload.password,
          real_name: payload.real_name || null,
          email: payload.email || null,
          phone: payload.phone || null
        }
        await api.post('/users/', createPayload)
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      fetchUsers()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除用户 "${row.username}" 吗？`, '提示', {
      type: 'warning'
    })

    await api.delete(`/users/${row.id}/`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const managePermissions = async (row) => {
  currentUser.value = row
  try {
    const { data } = await api.get(`/users/${row.id}/permissions/`)
    Object.assign(permissions, data)
    permissionDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取权限失败')
  }
}

const savePermissions = async () => {
  submitting.value = true
  try {
    await api.put(`/users/${currentUser.value.id}/permissions/`, permissions)
    ElMessage.success('权限更新成功')
    permissionDialogVisible.value = false
  } catch (error) {
    ElMessage.error('权限更新失败')
  } finally {
    submitting.value = false
  }
}

const loadAvailableResources = async () => {
  try {
    const [expertsRes, mcpRes] = await Promise.all([
      api.get('/ai/experts/', { params: { page: 1, page_size: 100 } }),
      api.get('/mcp/', { params: { page: 1, page_size: 100 } })
    ])
    availableExperts.value = expertsRes.data.items
    availableMCPs.value = mcpRes.data.items
  } catch (error) {
    console.error('加载资源失败', error)
  }
}

onMounted(() => {
  fetchUsers()
  loadAvailableResources()
})
</script>

<style scoped>
.users-container {
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

:deep(.el-checkbox) {
  display: block;
  margin: 8px 0;
}
</style>
