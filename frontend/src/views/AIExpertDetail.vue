<template>
  <div class="ai-expert-detail">
    <div class="page-header">
      <div class="header-left">
        <button class="btn btn-secondary" @click="handleBack">返回</button>
        <div class="title-box">
          <h1>专家详情</h1>
          <p class="subtitle">{{ expert?.name || '未命名专家' }}（{{ expert?.code || '-' }}）</p>
        </div>
      </div>
      <div class="header-right">
        <span class="status-tag" :class="expert?.status">{{ statusText }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading-box">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-if="error" class="error-box">
      <p>❌ {{ error }}</p>
      <button class="btn btn-secondary" @click="error = ''">关闭</button>
    </div>

    <div v-if="!loading" class="tabs">
      <button class="tab" :class="{ active: activeTab === 'knowledge' }" @click="activeTab = 'knowledge'">
        知识库
      </button>
      <button class="tab" :class="{ active: activeTab === 'skills' }" @click="activeTab = 'skills'">
        Skills库
      </button>
      <button class="tab" :class="{ active: activeTab === 'subAgents' }" @click="activeTab = 'subAgents'">
        子智能体
      </button>
    </div>

    <!-- 知识库管理 -->
    <section v-if="activeTab === 'knowledge'" class="tab-panel">
      <div class="panel-header">
        <h2>知识条目</h2>
        <button class="btn btn-primary" @click="resetKnowledgeForm">新建条目</button>
      </div>

      <div class="form-card">
        <div class="form-row">
          <label>标题 *</label>
          <input v-model="knowledgeForm.title" type="text" placeholder="请输入标题" />
        </div>
        <div class="form-row">
          <label>内容 *</label>
          <textarea v-model="knowledgeForm.content" rows="4" placeholder="请输入内容"></textarea>
        </div>
        <div class="form-row">
          <label>元数据(JSON)</label>
          <textarea v-model="knowledgeForm.metadata" rows="3" placeholder='如：{"source":"manual"}'></textarea>
        </div>
        <div class="form-row">
          <label>启用</label>
          <select v-model="knowledgeForm.enabled">
            <option :value="true">启用</option>
            <option :value="false">停用</option>
          </select>
        </div>
        <div class="form-actions">
          <button class="btn btn-secondary" @click="resetKnowledgeForm">清空</button>
          <button class="btn btn-primary" @click="saveKnowledgeItem">保存</button>
        </div>
      </div>

      <div class="list-card" v-if="knowledgeItems.length">
        <div class="list-item" v-for="item in knowledgeItems" :key="item.id">
          <div class="list-info">
            <h3>{{ item.title }}</h3>
            <p class="muted">{{ item.content }}</p>
          </div>
          <div class="list-actions">
            <button class="btn btn-sm btn-info" @click="editKnowledgeItem(item)">编辑</button>
            <button class="btn btn-sm btn-danger" @click="deleteKnowledgeItem(item.id)">删除</button>
          </div>
        </div>
      </div>
      <div v-else class="empty-box">暂无知识条目</div>
    </section>

    <!-- Skills 管理 -->
    <section v-if="activeTab === 'skills'" class="tab-panel">
      <div class="panel-header">
        <h2>技能条目</h2>
        <button class="btn btn-primary" @click="resetSkillForm">新建技能</button>
      </div>

      <div class="form-card">
        <div class="form-row">
          <label>名称 *</label>
          <input v-model="skillForm.name" type="text" placeholder="请输入技能名称" />
        </div>
        <div class="form-row">
          <label>描述</label>
          <input v-model="skillForm.description" type="text" placeholder="请输入描述" />
        </div>
        <div class="form-row">
          <label>内容 *</label>
          <textarea v-model="skillForm.content" rows="4" placeholder="请输入技能内容"></textarea>
        </div>
        <div class="form-row">
          <label>分类</label>
          <input v-model="skillForm.category" type="text" placeholder="可选" />
        </div>
        <div class="form-row">
          <label>标签</label>
          <input v-model="skillForm.tags" type="text" placeholder="用英文逗号分隔" />
        </div>
        <div class="form-row">
          <label>启用</label>
          <select v-model="skillForm.enabled">
            <option :value="true">启用</option>
            <option :value="false">停用</option>
          </select>
        </div>
        <div class="form-actions">
          <button class="btn btn-secondary" @click="resetSkillForm">清空</button>
          <button class="btn btn-primary" @click="saveSkillItem">保存</button>
        </div>
      </div>

      <div class="list-card" v-if="skillItems.length">
        <div class="list-item" v-for="item in skillItems" :key="item.id">
          <div class="list-info">
            <h3>{{ item.name }}</h3>
            <p class="muted">{{ item.description || item.content }}</p>
          </div>
          <div class="list-actions">
            <button class="btn btn-sm btn-info" @click="editSkillItem(item)">编辑</button>
            <button class="btn btn-sm btn-danger" @click="deleteSkillItem(item.id)">删除</button>
          </div>
        </div>
      </div>
      <div v-else class="empty-box">暂无技能条目</div>
    </section>

    <!-- 子智能体管理 -->
    <section v-if="activeTab === 'subAgents'" class="tab-panel">
      <div class="panel-header">
        <h2>子智能体</h2>
        <button class="btn btn-primary" @click="resetSubAgentForm">新建子智能体</button>
      </div>

      <div class="form-card">
        <div class="form-row">
          <label>名称 *</label>
          <input v-model="subAgentForm.name" type="text" placeholder="请输入子智能体名称" />
        </div>
        <div class="form-row">
          <label>描述</label>
          <input v-model="subAgentForm.description" type="text" placeholder="请输入描述" />
        </div>
        <div class="form-row">
          <label>提示词 *</label>
          <textarea v-model="subAgentForm.prompt" rows="4" placeholder="请输入提示词"></textarea>
        </div>
        <div class="form-row">
          <label>状态</label>
          <select v-model="subAgentForm.status">
            <option value="draft">草稿</option>
            <option value="active">激活</option>
            <option value="inactive">停用</option>
          </select>
        </div>
        <div class="form-actions">
          <button class="btn btn-secondary" @click="resetSubAgentForm">清空</button>
          <button class="btn btn-primary" @click="saveSubAgent">保存</button>
        </div>
      </div>

      <div class="list-card" v-if="subAgents.length">
        <div class="list-item" v-for="item in subAgents" :key="item.id">
          <div class="list-info">
            <h3>{{ item.name }}</h3>
            <p class="muted">{{ item.description || item.prompt }}</p>
          </div>
          <div class="list-actions">
            <button class="btn btn-sm btn-info" @click="editSubAgent(item)">编辑</button>
            <button class="btn btn-sm btn-danger" @click="deleteSubAgent(item.id)">删除</button>
          </div>
        </div>
      </div>
      <div v-else class="empty-box">暂无子智能体</div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const expertId = computed(() => Number(route.params.id))

const loading = ref(false)
const error = ref('')
const activeTab = ref('knowledge')

const expert = ref(null)
const knowledgeItems = ref([])
const skillItems = ref([])
const subAgents = ref([])

const knowledgeEditingId = ref(null)
const skillEditingId = ref(null)
const subAgentEditingId = ref(null)

const knowledgeForm = ref({
  title: '',
  content: '',
  metadata: '',
  enabled: true
})

const skillForm = ref({
  name: '',
  description: '',
  content: '',
  category: '',
  tags: '',
  enabled: true
})

const subAgentForm = ref({
  name: '',
  description: '',
  prompt: '',
  status: 'draft'
})

const statusText = computed(() => {
  if (!expert.value) return '未知'
  const map = { active: '激活', inactive: '停用', draft: '草稿' }
  return map[expert.value.status] || expert.value.status
})

const handleBack = () => {
  router.push('/ai-experts')
}

const parseMetadata = (text) => {
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    throw new Error('元数据必须是合法的 JSON')
  }
}

const toTagArray = (text) => {
  if (!text) return []
  return text.split(',').map((item) => item.trim()).filter(Boolean)
}

const getSuccessData = (response) => response?.data?.data ?? response?.data

const fetchExpert = async () => {
  const response = await api.get(`/ai/experts/${expertId.value}`)
  expert.value = response.data
}

const fetchKnowledge = async () => {
  const response = await api.get(`/experts/${expertId.value}/knowledge/items`)
  knowledgeItems.value = getSuccessData(response) || []
}

const fetchSkills = async () => {
  const response = await api.get(`/experts/${expertId.value}/skills`)
  skillItems.value = getSuccessData(response) || []
}

const fetchSubAgents = async () => {
  const response = await api.get(`/ai/experts/${expertId.value}/sub-agents`)
  subAgents.value = response.data.items || []
}

const resetKnowledgeForm = () => {
  knowledgeEditingId.value = null
  knowledgeForm.value = { title: '', content: '', metadata: '', enabled: true }
}

const resetSkillForm = () => {
  skillEditingId.value = null
  skillForm.value = { name: '', description: '', content: '', category: '', tags: '', enabled: true }
}

const resetSubAgentForm = () => {
  subAgentEditingId.value = null
  subAgentForm.value = { name: '', description: '', prompt: '', status: 'draft' }
}

const editKnowledgeItem = (item) => {
  knowledgeEditingId.value = item.id
  knowledgeForm.value = {
    title: item.title,
    content: item.content,
    metadata: item.metadata ? JSON.stringify(item.metadata, null, 2) : '',
    enabled: item.enabled
  }
}

const editSkillItem = (item) => {
  skillEditingId.value = item.id
  skillForm.value = {
    name: item.name,
    description: item.description || '',
    content: item.content,
    category: item.category || '',
    tags: (item.tags || []).join(','),
    enabled: item.enabled
  }
}

const editSubAgent = (item) => {
  subAgentEditingId.value = item.id
  subAgentForm.value = {
    name: item.name,
    description: item.description || '',
    prompt: item.prompt,
    status: item.status
  }
}

const saveKnowledgeItem = async () => {
  try {
    const payload = {
      title: knowledgeForm.value.title,
      content: knowledgeForm.value.content,
      metadata: parseMetadata(knowledgeForm.value.metadata),
      enabled: knowledgeForm.value.enabled
    }
    if (knowledgeEditingId.value) {
      await api.put(`/experts/${expertId.value}/knowledge/items/${knowledgeEditingId.value}`, payload)
    } else {
      await api.post(`/experts/${expertId.value}/knowledge/items`, payload)
    }
    await fetchKnowledge()
    resetKnowledgeForm()
  } catch (err) {
    error.value = err.message || '保存失败'
  }
}

const saveSkillItem = async () => {
  try {
    const payload = {
      name: skillForm.value.name,
      description: skillForm.value.description || null,
      content: skillForm.value.content,
      category: skillForm.value.category || null,
      tags: toTagArray(skillForm.value.tags),
      enabled: skillForm.value.enabled
    }
    if (skillEditingId.value) {
      await api.put(`/experts/${expertId.value}/skills/${skillEditingId.value}`, payload)
    } else {
      await api.post(`/experts/${expertId.value}/skills`, payload)
    }
    await fetchSkills()
    resetSkillForm()
  } catch (err) {
    error.value = err.message || '保存失败'
  }
}

const saveSubAgent = async () => {
  try {
    const payload = { ...subAgentForm.value }
    if (subAgentEditingId.value) {
      await api.put(`/ai/experts/${expertId.value}/sub-agents/${subAgentEditingId.value}`, payload)
    } else {
      await api.post(`/ai/experts/${expertId.value}/sub-agents`, payload)
    }
    await fetchSubAgents()
    resetSubAgentForm()
  } catch (err) {
    error.value = err.message || '保存失败'
  }
}

const deleteKnowledgeItem = async (id) => {
  if (!confirm('确定要删除该条目吗？')) return
  try {
    await api.delete(`/experts/${expertId.value}/knowledge/items/${id}`)
    await fetchKnowledge()
  } catch (err) {
    error.value = err.message || '删除失败'
  }
}

const deleteSkillItem = async (id) => {
  if (!confirm('确定要删除该技能吗？')) return
  try {
    await api.delete(`/experts/${expertId.value}/skills/${id}`)
    await fetchSkills()
  } catch (err) {
    error.value = err.message || '删除失败'
  }
}

const deleteSubAgent = async (id) => {
  if (!confirm('确定要删除该子智能体吗？')) return
  try {
    await api.delete(`/ai/experts/${expertId.value}/sub-agents/${id}`)
    await fetchSubAgents()
  } catch (err) {
    error.value = err.message || '删除失败'
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([fetchExpert(), fetchKnowledge(), fetchSkills(), fetchSubAgents()])
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.ai-expert-detail {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-box h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
}

.subtitle {
  margin: 4px 0 0;
  color: #666;
  font-size: 14px;
}

.status-tag {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.status-tag.active { background: #16a34a; }
.status-tag.inactive { background: #6b7280; }
.status-tag.draft { background: #f59e0b; }

.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.tab {
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  background: #f2f4f7;
  cursor: pointer;
}

.tab.active {
  background: #1E3C72;
  color: #fff;
}

.tab-panel {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.form-card {
  background: #f9fafb;
  padding: 16px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 12px;
  align-items: start;
  margin-bottom: 12px;
}

.form-row input,
.form-row textarea,
.form-row select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.list-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #f0f0f0;
  border-radius: 10px;
}

.list-info h3 {
  margin: 0 0 6px;
  font-size: 16px;
}

.muted {
  color: #666;
  margin: 0;
  font-size: 13px;
}

.list-actions {
  display: flex;
  gap: 8px;
}

.loading-box,
.error-box,
.empty-box {
  background: #fff;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f0f0f0;
  border-top: 4px solid #1E3C72;
  border-radius: 50%;
  margin: 0 auto 12px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.btn-primary {
  background: #1E3C72;
  color: #fff;
}

.btn-secondary {
  background: #e5e7eb;
  color: #333;
}

.btn-info {
  background: #3498db;
  color: #fff;
}

.btn-danger {
  background: #e74c3c;
  color: #fff;
}

.btn-sm {
  padding: 6px 10px;
  font-size: 12px;
}
</style>
