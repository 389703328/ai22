<template>
  <div class="ai-expert-detail">
    <!-- 头部导航 -->
    <el-page-header @back="handleBack" class="page-header">
      <template #content>
        <div class="flex items-center gap-4">
          <span class="text-xl font-bold">{{ expert?.name || '专家详情' }}</span>
          <el-tag v-if="expert?.code" type="info" size="small">{{ expert.code }}</el-tag>
        </div>
      </template>
      <template #extra>
        <span class="status-tag" :class="expert?.status">
          <el-tag :type="getTagType(expert?.status)">{{ statusText }}</el-tag>
        </span>
      </template>
    </el-page-header>

    <!-- 加载/错误状态 -->
    <div v-loading="loading" class="min-h-[200px]">
      <el-alert v-if="error" :title="error" type="error" show-icon class="mb-4" @close="error = ''" />

      <!-- 主要内容区 -->
      <div v-if="!loading && expert" class="content-container mt-6">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 知识库 TAB -->
          <el-tab-pane label="知识库" name="knowledge">
            <template #label>
              <span class="custom-tabs-label">
                <el-icon><Document /></el-icon>
                <span>知识库</span>
              </span>
            </template>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-base font-medium">知识库列表 ({{ knowledgeItems.length }})</h3>
              <el-button type="primary" :icon="Plus" @click="openKnowledgeModal()">新建条目</el-button>
            </div>

            <el-empty v-if="knowledgeItems.length === 0" description="暂无知识条目" />
            
            <div v-else class="flex flex-col gap-4">
              <el-card v-for="item in knowledgeItems" :key="item.id" shadow="hover">
                <div class="flex justify-between items-start">
                  <div class="w-full mr-4">
                    <div class="flex items-center gap-2 mb-2">
                      <h4 class="m-0 text-base">{{ item.title }}</h4>
                      <el-tag :type="item.enabled ? 'success' : 'info'" size="small" effect="plain">
                        {{ item.enabled ? '已启用' : '已禁用' }}
                      </el-tag>
                    </div>
                    <p class="text-gray-500 text-sm line-clamp-2 my-0">{{ item.content }}</p>
                  </div>
                  <div class="flex flex-col gap-2 shrink-0">
                    <el-button size="small" :icon="Edit" @click="openKnowledgeModal(item)">编辑</el-button>
                    <el-button size="small" type="danger" plain :icon="Delete" @click="deleteKnowledgeItem(item.id)">删除</el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </el-tab-pane>

          <!-- Skills TAB -->
          <el-tab-pane label="Skills库" name="skills">
            <template #label>
              <span class="custom-tabs-label">
                <el-icon><Tools /></el-icon>
                <span>Skills库</span>
              </span>
            </template>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-base font-medium">Skills列表 ({{ skillItems.length }})</h3>
              <el-button type="primary" :icon="Plus" @click="openSkillModal()">新建技能</el-button>
            </div>
            
            <el-empty v-if="skillItems.length === 0" description="暂无技能数据" />

            <div v-else class="flex flex-col gap-4">
              <el-card v-for="item in skillItems" :key="item.id" shadow="hover">
                <div class="flex justify-between items-start">
                  <div class="w-full mr-4">
                    <div class="flex items-center gap-2 mb-2">
                      <h4 class="m-0 text-base">{{ item.name }}</h4>
                      <el-tag v-if="item.category" size="small" effect="light">{{ item.category }}</el-tag>
                      <div class="w-2 h-2 rounded-full" :class="item.enabled ? 'bg-green-500' : 'bg-gray-300'"></div>
                    </div>
                    <p class="text-gray-500 text-sm line-clamp-2 mb-3 mt-0">{{ item.description || item.content }}</p>
                    <div class="flex gap-2 flex-wrap" v-if="item.tags && item.tags.length">
                      <el-tag v-for="tag in item.tags" :key="tag" size="small" round type="info">
                        {{ tag }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="flex flex-col gap-2 shrink-0">
                    <el-button size="small" :icon="Edit" @click="openSkillModal(item)">编辑</el-button>
                    <el-button size="small" type="danger" plain :icon="Delete" @click="deleteSkillItem(item.id)">删除</el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </el-tab-pane>

          <!-- 知识图谱 TAB -->
          <el-tab-pane label="知识图谱" name="knowledgeGraph">
            <template #label>
              <span class="custom-tabs-label">
                <el-icon><Share /></el-icon>
                <span>知识图谱</span>
              </span>
            </template>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-base font-medium">知识图谱列表 ({{ knowledgeGraphs.length }})</h3>
              <el-button type="primary" :icon="Plus" @click="openGraphModal()">新建图谱</el-button>
            </div>

            <el-empty v-if="knowledgeGraphs.length === 0" description="暂无知识图谱" />

            <div v-else class="flex flex-col gap-4">
              <el-card v-for="item in knowledgeGraphs" :key="item.id" shadow="hover">
                <div class="flex justify-between items-start">
                  <div class="w-full mr-4">
                    <div class="flex items-center gap-2 mb-2">
                      <h4 class="m-0 text-base">{{ item.name }}</h4>
                      <el-tag type="primary" size="small">{{ item.graph_type }}</el-tag>
                    </div>
                    <p class="text-gray-500 text-sm my-2">{{ item.description }}</p>
                    <div class="flex gap-4 text-sm text-gray-600">
                      <span>存储: {{ item.storage }}</span>
                      <span>节点: {{ item.node_count }}</span>
                      <span>边: {{ item.edge_count }}</span>
                    </div>
                  </div>
                  <div class="flex flex-col gap-2 shrink-0">
                    <el-button size="small" :icon="Edit" @click="openGraphModal(item)">编辑</el-button>
                    <el-button size="small" type="danger" plain :icon="Delete" @click="deleteGraph(item.id)">删除</el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </el-tab-pane>

          <!-- 子智能体 TAB -->
          <el-tab-pane label="子智能体" name="subAgents">
            <template #label>
              <span class="custom-tabs-label">
                <el-icon><User /></el-icon>
                <span>子智能体</span>
              </span>
            </template>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-base font-medium">子智能体列表 ({{ subAgents.length }})</h3>
              <el-button type="primary" :icon="Plus" @click="openSubAgentModal()">新建智能体</el-button>
            </div>

            <el-empty v-if="subAgents.length === 0" description="暂无子智能体" />

            <div v-else class="flex flex-col gap-4">
              <el-card v-for="item in subAgents" :key="item.id" shadow="hover">
                <div class="flex justify-between items-start">
                  <div class="w-full mr-4">
                    <div class="flex items-center gap-2 mb-2">
                      <h4 class="m-0 text-base">{{ item.name }}</h4>
                      <el-tag :type="getTagType(item.status)" size="small">
                        {{ getStatusLabel(item.status) }}
                      </el-tag>
                    </div>
                    <p class="text-gray-500 text-sm line-clamp-2 my-0">{{ item.description }}</p>
                  </div>
                  <div class="flex flex-col gap-2 shrink-0">
                    <el-button size="small" :icon="Edit" @click="openSubAgentModal(item)">编辑</el-button>
                    <el-button size="small" type="danger" plain :icon="Delete" @click="deleteSubAgent(item.id)">删除</el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- MODALS / DIALOGS -->

    <!-- Knowledge Modal -->
    <el-dialog
      v-model="showKnowledgeModal"
      :title="knowledgeEditingId ? '编辑知识条目' : '新建知识条目'"
      width="600px"
    >
      <el-form :model="knowledgeForm" label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model="knowledgeForm.title" placeholder="输入标题" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="knowledgeForm.content" type="textarea" :rows="5" placeholder="输入详细内容" />
        </el-form-item>
        <el-form-item label="文件上传">
          <el-upload
            :auto-upload="false"
            :on-change="handleKnowledgeFileChange"
            :limit="1"
            :file-list="knowledgeFileList"
          >
            <el-button :icon="Upload">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持txt, md, pdf等文件</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="元数据 (JSON)">
          <el-input v-model="knowledgeForm.metadata" type="textarea" :rows="3" placeholder='例如: {"source": "manual"}' />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="knowledgeForm.enabled">启用该条目</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showKnowledgeModal = false">取消</el-button>
          <el-button type="primary" @click="saveKnowledgeItem">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Skill Modal -->
    <el-dialog
      v-model="showSkillModal"
      :title="skillEditingId ? '编辑技能' : '新建技能'"
      width="600px"
    >
      <el-form :model="skillForm" label-position="top">
        <el-form-item label="技能名称" required>
          <el-input v-model="skillForm.name" placeholder="输入技能名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="skillForm.description" placeholder="简短描述" />
        </el-form-item>
        <el-form-item label="技能内容/代码" required>
          <el-input v-model="skillForm.content" type="textarea" :rows="5" placeholder="输入技能具体的 Prompt 或代码" />
        </el-form-item>
        <el-form-item label="文件上传">
          <el-upload
            :auto-upload="false"
            :on-change="handleSkillFileChange"
            :limit="1"
            :file-list="skillFileList"
          >
            <el-button :icon="Upload">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持py, js, md等文件</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-input v-model="skillForm.category" placeholder="例如: data_processing" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标签 (逗号分隔)">
              <el-input v-model="skillForm.tags" placeholder="python, analysis" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-checkbox v-model="skillForm.enabled">启用该技能</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSkillModal = false">取消</el-button>
          <el-button type="primary" @click="saveSkillItem">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- SubAgent Modal -->
    <el-dialog
      v-model="showSubAgentModal"
      :title="subAgentEditingId ? '编辑子智能体' : '新建子智能体'"
      width="600px"
    >
      <el-form :model="subAgentForm" label-position="top">
        <el-form-item label="智能体名称" required>
          <el-input v-model="subAgentForm.name" placeholder="输入名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="subAgentForm.description" placeholder="简短的功能描述" />
        </el-form-item>
        <el-form-item label="系统提示词 (Prompt)" required>
          <el-input v-model="subAgentForm.prompt" type="textarea" :rows="6" placeholder="定义该智能体的行为和角色..." />
        </el-form-item>
        <el-form-item label="API Key（可选）">
          <el-input v-model="subAgentForm.api_key" type="password" placeholder="输入API Key" show-password />
          <template #extra>
            <span class="text-gray-500 text-sm">为该子智能体配置独立的API Key</span>
          </template>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="subAgentForm.status" placeholder="选择状态" class="w-full">
            <el-option label="草稿" value="draft" />
            <el-option label="激活" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSubAgentModal = false">取消</el-button>
          <el-button type="primary" @click="saveSubAgent">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Knowledge Graph Modal -->
    <el-dialog
      v-model="showGraphModal"
      :title="graphEditingId ? '编辑知识图谱' : '新建知识图谱'"
      width="600px"
    >
      <el-form :model="graphForm" label-position="top">
        <el-form-item label="图谱名称" required>
          <el-input v-model="graphForm.name" placeholder="输入图谱名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="graphForm.description" type="textarea" :rows="2" placeholder="图谱用途说明" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="图谱类型">
              <el-select v-model="graphForm.graph_type" placeholder="选择类型" class="w-full">
                <el-option label="通用" value="general" />
                <el-option label="领域" value="domain" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="存储方式">
              <el-select v-model="graphForm.storage" placeholder="选择存储" class="w-full">
                <el-option label="Neo4j" value="neo4j" />
                <el-option label="内存" value="memory" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="文件上传">
          <el-upload
            :auto-upload="false"
            :on-change="handleGraphFileChange"
            :limit="1"
            :file-list="graphFileList"
          >
            <el-button :icon="Upload">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持json, graphml等图谱文件</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="配置 (JSON)">
          <el-input v-model="graphForm.config" type="textarea" :rows="4" placeholder='例如: {"uri": "bolt://localhost:7687"}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showGraphModal = false">取消</el-button>
          <el-button type="primary" @click="saveGraph">保存</el-button>
        </span>
      </template>
    </el-dialog>


  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Edit, Delete, Document, Tools, User, Share, Upload } from '@element-plus/icons-vue'
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
const knowledgeGraphs = ref([])

// Modal States
const showKnowledgeModal = ref(false)
const showSkillModal = ref(false)
const showSubAgentModal = ref(false)
const showGraphModal = ref(false)

const knowledgeEditingId = ref(null)
const skillEditingId = ref(null)
const subAgentEditingId = ref(null)
const graphEditingId = ref(null)

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
  api_key: '',
  status: 'draft'
})

const graphForm = ref({
  name: '',
  description: '',
  graph_type: 'general',
  storage: 'neo4j',
  config: ''
})

// 文件上传相关状态
const knowledgeFileList = ref([])
const skillFileList = ref([])
const graphFileList = ref([])
const knowledgeUploadFile = ref(null)
const skillUploadFile = ref(null)
const graphUploadFile = ref(null)

// 文件上传处理函数
const handleKnowledgeFileChange = (file) => {
  knowledgeUploadFile.value = file.raw
  knowledgeFileList.value = [file]
}

const handleSkillFileChange = (file) => {
  skillUploadFile.value = file.raw
  skillFileList.value = [file]
}

const handleGraphFileChange = (file) => {
  graphUploadFile.value = file.raw
  graphFileList.value = [file]
}

// 上传文件到服务器
const uploadFile = async (file, uploadType) => {
  if (!file) return null
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('expert_id', expertId.value)
  
  const response = await api.post(`/upload/${uploadType}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  
  return response.data.data
}

const statusText = computed(() => {
  if (!expert.value) return '未知'
  const map = { active: '激活', inactive: '停用', draft: '草稿' }
  return map[expert.value.status] || expert.value.status
})

const getStatusLabel = (status) => {
  const map = { active: '激活', inactive: '停用', draft: '草稿' }
  return map[status] || status
}

const getTagType = (status) => {
  const map = { active: 'success', inactive: 'danger', draft: 'warning' }
  return map[status] || 'info'
}

const handleBack = () => {
  router.push('/ai-experts')
}

const closeModals = () => {
  showKnowledgeModal.value = false
  showSkillModal.value = false
  showSubAgentModal.value = false
  showGraphModal.value = false
  error.value = ''
}

const parseMetadata = (text) => {
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    throw new Error('元数据必须是合法的 JSON (例如 {"key": "value"})')
  }
}

const toTagArray = (text) => {
  if (!text) return []
  return text.split(',').map((item) => item.trim()).filter(Boolean)
}

const getSuccessData = (response) => response?.data?.data ?? response?.data

const fetchExpert = async () => {
  const response = await api.get(`/ai/experts/${expertId.value}/`)
  expert.value = response.data
}

const fetchKnowledge = async () => {
  const response = await api.get(`/experts/${expertId.value}/knowledge/items/`)
  knowledgeItems.value = getSuccessData(response) || []
}

const fetchSkills = async () => {
  const response = await api.get(`/experts/${expertId.value}/skills/`)
  skillItems.value = getSuccessData(response) || []
}

const fetchSubAgents = async () => {
  const response = await api.get(`/ai/experts/${expertId.value}/sub-agents/`)
  subAgents.value = response.data.items || []
}

const fetchKnowledgeGraphs = async () => {
  const response = await api.get(`/experts/${expertId.value}/knowledge-graphs/`)
  knowledgeGraphs.value = response.data.items || []
}

// Knowledge Handlers
const openKnowledgeModal = (item = null) => {
  knowledgeFileList.value = []
  knowledgeUploadFile.value = null
  
  if (item) {
    knowledgeEditingId.value = item.id
    knowledgeForm.value = {
      title: item.title,
      content: item.content,
      metadata: item.metadata ? JSON.stringify(item.metadata, null, 2) : '',
      enabled: item.enabled
    }
    // 如果有文件，显示文件名
    if (item.file_name) {
      knowledgeFileList.value = [{ name: item.file_name, url: item.file_path }]
    }
  } else {
    knowledgeEditingId.value = null
    knowledgeForm.value = { title: '', content: '', metadata: '', enabled: true }
  }
  showKnowledgeModal.value = true
}

const saveKnowledgeItem = async () => {
  try {
    // 如果有文件上传，先上传文件
    let fileData = null
    if (knowledgeUploadFile.value) {
      fileData = await uploadFile(knowledgeUploadFile.value, 'knowledge')
    }
    
    const payload = {
      title: knowledgeForm.value.title,
      content: knowledgeForm.value.content,
      file_path: fileData?.file_path || null,
      file_name: fileData?.file_name || null,
      metadata: parseMetadata(knowledgeForm.value.metadata),
      enabled: knowledgeForm.value.enabled
    }
    if (knowledgeEditingId.value) {
      await api.put(`/experts/${expertId.value}/knowledge/items/${knowledgeEditingId.value}`, payload)
    } else {
      await api.post(`/experts/${expertId.value}/knowledge/items`, payload)
    }
    await fetchKnowledge()
    closeModals()
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

const deleteKnowledgeItem = async (id) => {
  if (!confirm('确定要删除该条目吗？')) return
  try {
    await api.delete(`/experts/${expertId.value}/knowledge/items/${id}/`)
    await fetchKnowledge()
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}

// Skills Handlers
const openSkillModal = (item = null) => {
  skillFileList.value = []
  skillUploadFile.value = null
  
  if (item) {
    skillEditingId.value = item.id
    skillForm.value = {
      name: item.name,
      description: item.description || '',
      content: item.content,
      category: item.category || '',
      tags: (item.tags || []).join(', '),
      enabled: item.enabled
    }
    if (item.file_name) {
      skillFileList.value = [{ name: item.file_name, url: item.file_path }]
    }
  } else {
    skillEditingId.value = null
    skillForm.value = { name: '', description: '', content: '', category: '', tags: '', enabled: true }
  }
  showSkillModal.value = true
}

const saveSkillItem = async () => {
  try {
    // 如果有文件上传，先上传文件
    let fileData = null
    if (skillUploadFile.value) {
      fileData = await uploadFile(skillUploadFile.value, 'skill')
    }
    
    const payload = {
      name: skillForm.value.name,
      description: skillForm.value.description || null,
      content: skillForm.value.content,
      file_path: fileData?.file_path || null,
      file_name: fileData?.file_name || null,
      category: skillForm.value.category || null,
      tags: toTagArray(skillForm.value.tags),
      enabled: skillForm.value.enabled
    }
    if (skillEditingId.value) {
      await api.put(`/experts/${expertId.value}/skills/${skillEditingId.value}/`, payload)
    } else {
      await api.post(`/experts/${expertId.value}/skills/`, payload)
    }
    await fetchSkills()
    closeModals()
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

const deleteSkillItem = async (id) => {
  if (!confirm('确定要删除该技能吗？')) return
  try {
    await api.delete(`/experts/${expertId.value}/skills/${id}/`)
    await fetchSkills()
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}

// SubAgents Handlers
const openSubAgentModal = (item = null) => {
  if (item) {
    subAgentEditingId.value = item.id
    subAgentForm.value = {
      name: item.name,
      description: item.description || '',
      prompt: item.prompt,
      api_key: item.api_key || '',
      status: item.status
    }
  } else {
    subAgentEditingId.value = null
    subAgentForm.value = { name: '', description: '', prompt: '', api_key: '', status: 'draft' }
  }
  showSubAgentModal.value = true
}

const saveSubAgent = async () => {
  try {
    const payload = { ...subAgentForm.value }
    if (subAgentEditingId.value) {
      await api.put(`/ai/experts/${expertId.value}/sub-agents/${subAgentEditingId.value}/`, payload)
    } else {
      await api.post(`/ai/experts/${expertId.value}/sub-agents/`, payload)
    }
    await fetchSubAgents()
    closeModals()
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

const deleteSubAgent = async (id) => {
  if (!confirm('确定要删除该子智能体吗？')) return
  try {
    await api.delete(`/ai/experts/${expertId.value}/sub-agents/${id}/`)
    await fetchSubAgents()
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}

// Knowledge Graph Handlers
const openGraphModal = (item = null) => {
  graphFileList.value = []
  graphUploadFile.value = null
  
  if (item) {
    graphEditingId.value = item.id
    graphForm.value = {
      name: item.name,
      description: item.description,
      graph_type: item.graph_type,
      storage: item.storage,
      config: item.config ? JSON.stringify(item.config, null, 2) : ''
    }
    if (item.file_name) {
      graphFileList.value = [{ name: item.file_name, url: item.file_path }]
    }
  } else {
    graphEditingId.value = null
    graphForm.value = {
      name: '',
      description: '',
      graph_type: 'general',
      storage: 'neo4j',
      config: ''
    }
  }
  showGraphModal.value = true
}

const saveGraph = async () => {
  try {
    // 如果有文件上传，先上传文件
    let fileData = null
    if (graphUploadFile.value) {
      fileData = await uploadFile(graphUploadFile.value, 'knowledge-graph')
    }
    
    const payload = {
      name: graphForm.value.name,
      description: graphForm.value.description,
      graph_type: graphForm.value.graph_type,
      storage: graphForm.value.storage,
      file_path: fileData?.file_path || null,
      file_name: fileData?.file_name || null,
      config: parseMetadata(graphForm.value.config),
      expert_id: expertId.value
    }
    if (graphEditingId.value) {
      await api.put(`/experts/${expertId.value}/knowledge-graphs/${graphEditingId.value}/`, payload)
    } else {
      await api.post(`/experts/${expertId.value}/knowledge-graphs/`, payload)
    }
    await fetchKnowledgeGraphs()
    closeModals()
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

const deleteGraph = async (id) => {
  if (!confirm('确定要删除该知识图谱吗？')) return
  try {
    await api.delete(`/experts/${expertId.value}/knowledge-graphs/${id}/`)
    await fetchKnowledgeGraphs()
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([fetchExpert(), fetchKnowledge(), fetchSkills(), fetchSubAgents(), fetchKnowledgeGraphs()])
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.ai-expert-detail {
  width: 100%;
  animation: fadeIn 0.3s ease-out;
}

.page-header {
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

.custom-tabs-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Utilities for this component since we don't have full Tailwind */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.gap-2 { gap: 8px; }
.gap-4 { gap: 16px; }
.mb-2 { margin-bottom: 8px; }
.mb-3 { margin-bottom: 12px; }
.mb-4 { margin-bottom: 16px; }
.mt-0 { margin-top: 0; }
.mt-6 { margin-top: 24px; }
.mr-4 { margin-right: 16px; }
.m-0 { margin: 0; }
.w-full { width: 100%; }
.shrink-0 { flex-shrink: 0; }
.flex-wrap { flex-wrap: wrap; }
.min-h-\[200px\] { min-height: 200px; }

.text-xl { font-size: var(--text-xl); }
.text-base { font-size: var(--text-base); }
.text-sm { font-size: var(--text-sm); }
.font-bold { font-weight: var(--font-bold); }
.font-medium { font-weight: var(--font-medium); }
.text-gray-500 { color: var(--text-secondary); }

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
