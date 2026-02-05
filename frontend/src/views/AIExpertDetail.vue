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
            <div class="knowledge-layout">
              <div class="knowledge-sidebar">
                <div class="sidebar-title">目录</div>
                <el-menu
                  :default-active="knowledgeDirectoryKey"
                  :default-openeds="defaultOpeneds"
                  class="knowledge-menu"
                  @select="handleKnowledgeDirectorySelect"
                >
                  <el-sub-menu index="expert-group">
                    <template #title>
                      <span @click.stop="handleKnowledgeDirectorySelect('expert-all')" style="cursor: pointer; display: flex; align-items: center; flex: 1;">
                        <el-icon><Document /></el-icon>
                        <span style="margin-left: 5px;">专家知识库</span>
                      </span>
                    </template>
                    <el-menu-item v-if="expertKnowledgeItems.length === 0 && subAgents.length === 0" index="expert-empty" disabled>
                      暂无文件
                    </el-menu-item>
                    <el-menu-item
                      v-for="item in expertKnowledgeItems"
                      :key="`file-${item.id}`"
                      :index="`file-${item.id}`"
                    >
                      {{ item.name || item.title }}
                    </el-menu-item>
                    <el-sub-menu
                      v-for="agent in subAgents"
                      :key="`subagent-group-${agent.id}`"
                      :index="`subagent-group-${agent.id}`"
                    >
                      <template #title>
                        <span @click.stop="handleKnowledgeDirectorySelect(`subagent-${agent.id}`)" style="cursor: pointer; display: flex; align-items: center; flex: 1;">
                          <el-icon><User /></el-icon>
                          <span style="margin-left: 5px;">{{ agent.name }}</span>
                        </span>
                      </template>
                      <el-menu-item
                        v-if="(subAgentKnowledgeMap[agent.id] || []).length === 0"
                        :index="`subagent-empty-${agent.id}`"
                        disabled
                      >
                        暂无文件
                      </el-menu-item>
                      <el-menu-item
                        v-for="item in subAgentKnowledgeMap[agent.id] || []"
                        :key="`file-${item.id}`"
                        :index="`file-${item.id}`"
                      >
                        {{ item.name || item.title }}
                      </el-menu-item>
                    </el-sub-menu>
                  </el-sub-menu>
                </el-menu>
              </div>
              <div class="knowledge-content">
                <div class="flex justify-between items-center mb-4">
                  <h3 class="text-base font-medium">{{ knowledgeTitle }} ({{ filteredKnowledgeItems.length }})</h3>
                  <el-button type="primary" :icon="Plus" @click="openKnowledgeModal()">新建条目</el-button>
                </div>

                <el-empty v-if="filteredKnowledgeItems.length === 0" description="暂无知识条目" />
                
                <div v-else class="flex flex-col gap-4">
                  <el-card v-for="item in filteredKnowledgeItems" :key="item.id" shadow="hover">
                    <div class="flex justify-between items-start">
                      <div class="w-full mr-4">
                        <div class="flex items-center gap-2 mb-2">
                          <h4 class="m-0 text-base">{{ item.name || item.title }}</h4>
                          <el-tag size="small" effect="plain" type="info">
                            {{ getKnowledgeOwnerLabel(item) }}
                          </el-tag>
                          <el-tag :type="item.enabled ? 'success' : 'info'" size="small" effect="plain">
                            {{ item.enabled ? '已启用' : '已禁用' }}
                          </el-tag>
                        </div>
                        <p class="text-gray-500 text-sm line-clamp-2 my-0">{{ item.text || item.content }}</p>
                      </div>
                      <div class="action-row shrink-0">
                        <el-button size="small" class="action-btn" :icon="Edit" @click="openKnowledgeModal(item)">编辑</el-button>
                        <el-button size="small" class="action-btn" type="danger" plain :icon="Delete" @click="deleteKnowledgeItem(item.id)">删除</el-button>
                      </div>
                    </div>
                  </el-card>
                </div>
              </div>
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
                  <div class="action-row shrink-0">
                    <el-button size="small" class="action-btn" :icon="Edit" @click="openSkillModal(item)">编辑</el-button>
                    <el-button size="small" class="action-btn" type="danger" plain :icon="Delete" @click="deleteSkillItem(item.id)">删除</el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </el-tab-pane>

          <!-- 问题库 TAB -->
          <el-tab-pane label="问题库" name="questions">
            <template #label>
              <span class="custom-tabs-label">
                <el-icon><Edit /></el-icon>
                <span>问题库</span>
              </span>
            </template>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-base font-medium">问题列表 ({{ questionItems.length }})</h3>
              <el-button type="primary" :icon="Plus" @click="openQuestionModal()">新建问题</el-button>
            </div>

            <el-empty v-if="questionItems.length === 0" description="暂无问题数据" />

            <div v-else class="flex flex-col gap-4">
              <el-card v-for="item in questionItems" :key="item.id" shadow="hover">
                <div class="flex justify-between items-start">
                  <div class="w-full mr-4">
                    <div class="flex items-center gap-2 mb-2">
                      <h4 class="m-0 text-base">{{ item.question }}</h4>
                      <el-tag v-if="item.category" size="small" effect="light">{{ item.category }}</el-tag>
                      <el-tag v-if="item.difficulty" size="small" type="warning" effect="plain">难度 {{ item.difficulty }}</el-tag>
                      <el-tag :type="item.enabled ? 'success' : 'info'" size="small" effect="plain">
                        {{ item.enabled ? '已启用' : '已禁用' }}
                      </el-tag>
                    </div>
                    <p class="text-gray-500 text-sm line-clamp-2 mb-3 mt-0">{{ item.answer || '暂无答案' }}</p>
                    <div class="flex gap-2 flex-wrap" v-if="item.tags && item.tags.length">
                      <el-tag v-for="tag in item.tags" :key="tag" size="small" round type="info">
                        {{ tag }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="action-row shrink-0">
                    <el-button size="small" class="action-btn" :icon="Edit" @click="openQuestionModal(item)">编辑</el-button>
                    <el-button size="small" class="action-btn" type="danger" plain :icon="Delete" @click="deleteQuestionItem(item.id)">删除</el-button>
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
                  <div class="action-row shrink-0">
                    <el-button size="small" class="action-btn" :icon="Edit" @click="openGraphModal(item)">编辑</el-button>
                    <el-button size="small" class="action-btn" type="danger" plain :icon="Delete" @click="deleteGraph(item.id)">删除</el-button>
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
                  <div class="action-row shrink-0">
                    <el-button size="small" class="action-btn" type="primary" plain @click="openSubAgentKnowledge(item)">知识库</el-button>
                    <el-button size="small" class="action-btn" type="primary" plain @click="openSubAgentSessions(item)">会话库</el-button>
                    <el-button size="small" class="action-btn" :icon="Edit" @click="openSubAgentModal(item)">编辑</el-button>
                    <el-button size="small" class="action-btn" type="danger" plain :icon="Delete" @click="deleteSubAgent(item.id)">删除</el-button>
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
          <el-form-item label="归属目录" required>
            <el-select v-model="knowledgeOwnerKey" placeholder="选择归属目录" class="w-full">
              <el-option label="专家知识库" value="expert" />
              <el-option
                v-for="agent in subAgents"
                :key="`owner-${agent.id}`"
                :label="agent.name"
                :value="`subagent-${agent.id}`"
              />
            </el-select>
          </el-form-item>
        <el-form-item label="文档名称" required>
          <el-input v-model="knowledgeForm.name" placeholder="输入文档名称" />
        </el-form-item>
        <el-form-item label="文档内容">
          <el-input v-model="knowledgeForm.text" type="textarea" :rows="5" placeholder="输入完整文本内容（可选）" />
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
              <div class="el-upload__tip">上传文件后可不填写文本内容</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="索引技术">
              <el-select v-model="knowledgeForm.indexing_technique" placeholder="选择索引技术" class="w-full">
                <el-option label="高质量" value="high_quality" />
                <el-option label="经济" value="economy" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="索引格式">
              <el-select v-model="knowledgeForm.doc_form" placeholder="选择内容格式" class="w-full">
                <el-option label="Text Model" value="text_model" />
                <el-option label="Hierarchical Model" value="hierarchical_model" />
                <el-option label="Q&A Model" value="qa_model" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="文档语言">
          <el-input v-model="knowledgeForm.doc_language" placeholder="例如：中文" />
        </el-form-item>
        <el-form-item label="处理规则">
          <el-input v-model="knowledgeForm.process_rule_text" type="textarea" :rows="3" placeholder="填写处理规则说明（可选）" />
        </el-form-item>
        <el-divider content-position="left">检索配置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="检索方法">
              <el-select v-model="knowledgeForm.retrieval_model.search_method" placeholder="选择检索方法" class="w-full">
                <el-option label="Hybrid Search" value="hybrid_search" />
                <el-option label="Semantic Search" value="semantic_search" />
                <el-option label="Full Text Search" value="full_text_search" />
                <el-option label="Keyword Search" value="keyword_search" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Top K">
              <el-input-number v-model="knowledgeForm.retrieval_model.top_k" :min="1" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用重排">
              <el-switch v-model="knowledgeForm.retrieval_model.reranking_enable" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="重排模式">
              <el-select v-model="knowledgeForm.retrieval_model.reranking_mode" placeholder="选择重排模式" class="w-full">
                <el-option label="Reranking Model" value="reranking_model" />
                <el-option label="Weighted Score" value="weighted_score" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="重排提供商">
              <el-input v-model="knowledgeForm.retrieval_model.reranking_model.reranking_provider_name" placeholder="提供商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="重排模型名称">
              <el-input v-model="knowledgeForm.retrieval_model.reranking_model.reranking_model_name" placeholder="模型名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用分数阈值">
              <el-switch v-model="knowledgeForm.retrieval_model.score_threshold_enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分数阈值">
              <el-input-number v-model="knowledgeForm.retrieval_model.score_threshold" :min="0" :max="1" :step="0.01" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="语义权重">
          <el-input-number v-model="knowledgeForm.retrieval_model.weights" :min="0" :max="1" :step="0.01" class="w-full" />
        </el-form-item>
        <el-divider content-position="left">Embedding</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Embedding 模型">
              <el-input v-model="knowledgeForm.embedding_model" placeholder="模型名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Embedding 提供商">
              <el-input v-model="knowledgeForm.embedding_model_provider" placeholder="提供商" />
            </el-form-item>
          </el-col>
        </el-row>
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

    <!-- Question Modal -->
    <el-dialog
      v-model="showQuestionModal"
      :title="questionEditingId ? '编辑问题' : '新建问题'"
      width="600px"
    >
      <el-form :model="questionForm" label-position="top">
        <el-form-item label="问题" required>
          <el-input v-model="questionForm.question" type="textarea" :rows="3" placeholder="输入问题内容" />
        </el-form-item>
        <el-form-item label="答案">
          <el-input v-model="questionForm.answer" type="textarea" :rows="4" placeholder="输入问题答案（可选）" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-input v-model="questionForm.category" placeholder="例如：流程类" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度 (1-5)">
              <el-input-number v-model="questionForm.difficulty" :min="1" :max="5" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标签 (逗号分隔)">
          <el-input v-model="questionForm.tags" placeholder="基础, 高频" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="questionForm.enabled">启用该问题</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showQuestionModal = false">取消</el-button>
          <el-button type="primary" @click="saveQuestionItem">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Session Library Modal -->
    <el-dialog
      v-model="showSessionModal"
      :title="sessionDialogTitle"
      width="860px"
    >
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-base font-medium">会话列表 ({{ sessionItems.length }})</h3>
      </div>

      <el-empty v-if="sessionItems.length === 0" description="暂无会话数据" />

      <el-table v-else :data="sessionItems" border style="width: 100%">
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="title" label="会话标题" min-width="160" />
        <el-table-column prop="session_id" label="会话ID" min-width="140" />
        <el-table-column label="反馈" width="100">
          <template #default="scope">
            <el-tag :type="getFeedbackTagType(scope.row.feedback_type)" size="small">
              {{ getFeedbackLabel(scope.row.feedback_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="comment" label="评论" min-width="200" />
        <el-table-column label="操作" width="160">
          <template #default="scope">
            <el-button size="small" class="action-btn" :icon="Edit" @click="openSessionEditModal(scope.row)">编辑</el-button>
            <el-button size="small" class="action-btn" type="danger" plain :icon="Delete" @click="deleteSessionItem(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSessionModal = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Session Edit Modal -->
    <el-dialog
      v-model="showSessionEditModal"
      :title="sessionEditingId ? '编辑会话' : '新建会话'"
      width="600px"
    >
      <el-form :model="sessionForm" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户ID" required>
              <el-input v-model.number="sessionForm.user_id" placeholder="请输入用户ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="会话ID">
              <el-input v-model="sessionForm.session_id" placeholder="外部会话ID（可选）" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="会话标题">
          <el-input v-model="sessionForm.title" placeholder="输入会话标题" />
        </el-form-item>
        <el-form-item label="会话内容">
          <el-input v-model="sessionForm.content" type="textarea" :rows="4" placeholder="会话内容摘要（可选）" />
        </el-form-item>
        <el-form-item label="反馈类型">
          <el-radio-group v-model="sessionForm.feedback_type">
            <el-radio label="none">无</el-radio>
            <el-radio label="like">点赞</el-radio>
            <el-radio label="dislike">踩</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="用户评论">
          <el-input v-model="sessionForm.comment" type="textarea" :rows="3" placeholder="输入评论内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSessionEditModal = false">取消</el-button>
          <el-button type="primary" @click="saveSessionItem">保存</el-button>
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
const questionItems = ref([])
const subAgents = ref([])
const knowledgeGraphs = ref([])

const knowledgeDirectoryKey = ref('expert-all')
const knowledgeOwnerKey = ref('expert')

// Modal States
const showKnowledgeModal = ref(false)
const showSkillModal = ref(false)
const showQuestionModal = ref(false)
const showSubAgentModal = ref(false)
const showGraphModal = ref(false)
const showSessionModal = ref(false)
const showSessionEditModal = ref(false)

const knowledgeEditingId = ref(null)
const skillEditingId = ref(null)
const questionEditingId = ref(null)
const subAgentEditingId = ref(null)
const graphEditingId = ref(null)
const sessionEditingId = ref(null)

const sessionTargetSubAgent = ref(null)
const sessionItems = ref([])

const knowledgeForm = ref({
  name: '',
  text: '',
  indexing_technique: '',
  doc_form: '',
  doc_language: '中文',
  process_rule_text: '',
  retrieval_model: {
    search_method: 'hybrid_search',
    reranking_enable: false,
    reranking_mode: 'reranking_model',
    reranking_model: {
      reranking_provider_name: '',
      reranking_model_name: ''
    },
    top_k: 5,
    score_threshold_enabled: false,
    score_threshold: null,
    weights: null
  },
  embedding_model: '',
  embedding_model_provider: '',
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

const questionForm = ref({
  question: '',
  answer: '',
  category: '',
  tags: '',
  difficulty: null,
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
  storage: 'neo4j'
})

const sessionForm = ref({
  user_id: null,
  session_id: '',
  title: '',
  content: '',
  feedback_type: 'none',
  comment: ''
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

const sessionDialogTitle = computed(() => {
  if (!sessionTargetSubAgent.value) return '会话库'
  return `${sessionTargetSubAgent.value.name} 会话库`
})

const subAgentNameMap = computed(() => {
  return subAgents.value.reduce((acc, item) => {
    acc[item.id] = item.name
    return acc
  }, {})
})

const defaultOpeneds = computed(() => {
  const openeds = ['expert-group']
  subAgents.value.forEach((agent) => {
    openeds.push(`subagent-group-${agent.id}`)
  })
  return openeds
})

const selectedSubAgentId = computed(() => {
  if (!knowledgeDirectoryKey.value.startsWith('subagent-')) return null
  return Number(knowledgeDirectoryKey.value.replace('subagent-', ''))
})

const selectedFileId = computed(() => {
  if (!knowledgeDirectoryKey.value.startsWith('file-')) return null
  return Number(knowledgeDirectoryKey.value.replace('file-', ''))
})

const knowledgeItemMap = computed(() => {
  return knowledgeItems.value.reduce((acc, item) => {
    acc[item.id] = item
    return acc
  }, {})
})

const expertKnowledgeItems = computed(() => {
  return knowledgeItems.value.filter((item) => item.sub_agent_id == null)
})

const subAgentKnowledgeMap = computed(() => {
  return subAgents.value.reduce((acc, agent) => {
    acc[agent.id] = knowledgeItems.value.filter((item) => item.sub_agent_id === agent.id)
    return acc
  }, {})
})

const knowledgeTitle = computed(() => {
  if (knowledgeDirectoryKey.value === 'expert-all') {
    return '专家知识库（全部）'
  }
  if (selectedFileId.value) {
    const item = knowledgeItemMap.value[selectedFileId.value]
    return item?.name || item?.title || '知识条目'
  }
  if (selectedSubAgentId.value) {
    return `${subAgentNameMap.value[selectedSubAgentId.value] || '子智能体'}知识库`
  }
  return '专家知识库'
})

const filteredKnowledgeItems = computed(() => {
  if (knowledgeDirectoryKey.value === 'expert-all') {
    return knowledgeItems.value
  }
  if (selectedFileId.value) {
    const item = knowledgeItemMap.value[selectedFileId.value]
    return item ? [item] : []
  }
  const subAgentId = selectedSubAgentId.value
  if (subAgentId) {
    return knowledgeItems.value.filter((item) => item.sub_agent_id === subAgentId)
  }
  return knowledgeItems.value.filter((item) => item.sub_agent_id == null)
})

const getStatusLabel = (status) => {
  const map = { active: '激活', inactive: '停用', draft: '草稿' }
  return map[status] || status
}

const getTagType = (status) => {
  const map = { active: 'success', inactive: 'danger', draft: 'warning' }
  return map[status] || 'info'
}

const getFeedbackLabel = (type) => {
  const map = { none: '无', like: '点赞', dislike: '踩' }
  return map[type] || '无'
}

const getFeedbackTagType = (type) => {
  const map = { none: 'info', like: 'success', dislike: 'danger' }
  return map[type] || 'info'
}

const handleBack = () => {
  router.push('/ai-experts')
}

const handleKnowledgeDirectorySelect = (key) => {
  knowledgeDirectoryKey.value = key
}

const openSubAgentKnowledge = (item) => {
  activeTab.value = 'knowledge'
  knowledgeDirectoryKey.value = `subagent-${item.id}`
}

const openSubAgentSessions = async (item) => {
  sessionTargetSubAgent.value = item
  await fetchSessions()
  showSessionModal.value = true
}

const closeModals = () => {
  showKnowledgeModal.value = false
  showSkillModal.value = false
  showQuestionModal.value = false
  showSubAgentModal.value = false
  showGraphModal.value = false
  error.value = ''
}

const buildProcessRule = (text) => {
  if (!text) return null
  return { rule: text }
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
  if (knowledgeDirectoryKey.value.startsWith('file-')) {
    const fileId = Number(knowledgeDirectoryKey.value.replace('file-', ''))
    const exists = knowledgeItems.value.some((item) => item.id === fileId)
    if (!exists) {
      knowledgeDirectoryKey.value = 'expert'
    }
  }
}

const fetchSkills = async () => {
  const response = await api.get(`/experts/${expertId.value}/skills/`)
  skillItems.value = getSuccessData(response) || []
}

const fetchQuestions = async () => {
  const response = await api.get(`/experts/${expertId.value}/questions`)
  questionItems.value = getSuccessData(response) || []
}

const fetchSubAgents = async () => {
  const response = await api.get(`/ai/experts/${expertId.value}/sub-agents/`)
  subAgents.value = response.data.items || []
  if (knowledgeDirectoryKey.value.startsWith('subagent-')) {
    const subAgentId = Number(knowledgeDirectoryKey.value.replace('subagent-', ''))
    const exists = subAgents.value.some((item) => item.id === subAgentId)
    if (!exists) {
      knowledgeDirectoryKey.value = 'expert'
    }
  }
}

const fetchKnowledgeGraphs = async () => {
  const response = await api.get(`/experts/${expertId.value}/knowledge-graphs/`)
  knowledgeGraphs.value = response.data.items || []
}

const fetchSessions = async () => {
  if (!sessionTargetSubAgent.value) return
  const response = await api.get(`/sub-agents/${sessionTargetSubAgent.value.id}/sessions`)
  const data = getSuccessData(response)
  sessionItems.value = data?.items || []
}

// Knowledge Handlers
const resolveDefaultOwnerKey = () => {
  if (knowledgeDirectoryKey.value.startsWith('subagent-')) return knowledgeDirectoryKey.value
  if (knowledgeDirectoryKey.value === 'expert') return 'expert'
  if (knowledgeDirectoryKey.value.startsWith('file-')) {
    const selected = knowledgeItemMap.value[selectedFileId.value]
    return selected?.sub_agent_id ? `subagent-${selected.sub_agent_id}` : 'expert'
  }
  return 'expert'
}

const openKnowledgeModal = (item = null) => {
  knowledgeFileList.value = []
  knowledgeUploadFile.value = null
  knowledgeOwnerKey.value = resolveDefaultOwnerKey()
  
  if (item) {
    knowledgeEditingId.value = item.id
    knowledgeOwnerKey.value = item.sub_agent_id ? `subagent-${item.sub_agent_id}` : 'expert'
    knowledgeForm.value = {
      name: item.name || item.title,
      text: item.text || item.content,
      indexing_technique: item.indexing_technique || '',
      doc_form: item.doc_form || '',
      doc_language: item.doc_language || '中文',
      process_rule_text: item.process_rule?.rule || '',
      retrieval_model: {
        search_method: item.retrieval_model?.search_method || 'hybrid_search',
        reranking_enable: item.retrieval_model?.reranking_enable ?? false,
        reranking_mode: item.retrieval_model?.reranking_mode || 'reranking_model',
        reranking_model: {
          reranking_provider_name: item.retrieval_model?.reranking_model?.reranking_provider_name || '',
          reranking_model_name: item.retrieval_model?.reranking_model?.reranking_model_name || ''
        },
        top_k: item.retrieval_model?.top_k || 5,
        score_threshold_enabled: item.retrieval_model?.score_threshold_enabled ?? false,
        score_threshold: item.retrieval_model?.score_threshold ?? null,
        weights: item.retrieval_model?.weights ?? null
      },
      embedding_model: item.embedding_model || '',
      embedding_model_provider: item.embedding_model_provider || '',
      enabled: item.enabled
    }
    // 如果有文件，显示文件名
    if (item.file_name) {
      knowledgeFileList.value = [{ name: item.file_name, url: item.file_path }]
    }
  } else {
    knowledgeEditingId.value = null
    knowledgeForm.value = {
      name: '',
      text: '',
      indexing_technique: '',
      doc_form: '',
      doc_language: '中文',
      process_rule_text: '',
      retrieval_model: {
        search_method: 'hybrid_search',
        reranking_enable: false,
        reranking_mode: 'reranking_model',
        reranking_model: {
          reranking_provider_name: '',
          reranking_model_name: ''
        },
        top_k: 5,
        score_threshold_enabled: false,
        score_threshold: null,
        weights: null
      },
      embedding_model: '',
      embedding_model_provider: '',
      enabled: true
    }
  }
  showKnowledgeModal.value = true
}

const resolveKnowledgeOwnerId = () => {
  if (!knowledgeOwnerKey.value.startsWith('subagent-')) return null
  return Number(knowledgeOwnerKey.value.replace('subagent-', ''))
}

const getKnowledgeOwnerLabel = (item) => {
  if (!item?.sub_agent_id) return '专家'
  return subAgentNameMap.value[item.sub_agent_id] || '子智能体'
}

const saveKnowledgeItem = async () => {
  try {
    if (!knowledgeForm.value.name) {
      alert('请填写文档名称')
      return
    }

    if (!knowledgeForm.value.text && !knowledgeUploadFile.value) {
      alert('请填写文档内容或上传文件')
      return
    }

    // 如果有文件上传，先上传文件
    let fileData = null
    if (knowledgeUploadFile.value) {
      fileData = await uploadFile(knowledgeUploadFile.value, 'knowledge')
    }
    
    const payload = {
      name: knowledgeForm.value.name,
      text: knowledgeForm.value.text || null,
      file_path: fileData?.file_path || null,
      file_name: fileData?.file_name || null,
      sub_agent_id: resolveKnowledgeOwnerId(),
      indexing_technique: knowledgeForm.value.indexing_technique || null,
      doc_form: knowledgeForm.value.doc_form || null,
      doc_language: knowledgeForm.value.doc_language || null,
      process_rule: buildProcessRule(knowledgeForm.value.process_rule_text),
      retrieval_model: knowledgeForm.value.retrieval_model,
      embedding_model: knowledgeForm.value.embedding_model || null,
      embedding_model_provider: knowledgeForm.value.embedding_model_provider || null,
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

// Question Handlers
const openQuestionModal = (item = null) => {
  if (item) {
    questionEditingId.value = item.id
    questionForm.value = {
      question: item.question,
      answer: item.answer || '',
      category: item.category || '',
      tags: (item.tags || []).join(', '),
      difficulty: item.difficulty ?? null,
      enabled: item.enabled
    }
  } else {
    questionEditingId.value = null
    questionForm.value = {
      question: '',
      answer: '',
      category: '',
      tags: '',
      difficulty: null,
      enabled: true
    }
  }
  showQuestionModal.value = true
}

const saveQuestionItem = async () => {
  try {
    if (!questionForm.value.question) {
      alert('请填写问题内容')
      return
    }
    const payload = {
      question: questionForm.value.question,
      answer: questionForm.value.answer || null,
      category: questionForm.value.category || null,
      tags: toTagArray(questionForm.value.tags),
      difficulty: questionForm.value.difficulty || null,
      enabled: questionForm.value.enabled
    }
    if (questionEditingId.value) {
      await api.put(`/experts/${expertId.value}/questions/${questionEditingId.value}`, payload)
    } else {
      await api.post(`/experts/${expertId.value}/questions`, payload)
    }
    await fetchQuestions()
    closeModals()
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

const deleteQuestionItem = async (id) => {
  if (!confirm('确定要删除该问题吗？')) return
  try {
    await api.delete(`/experts/${expertId.value}/questions/${id}`)
    await fetchQuestions()
  } catch (err) {
    alert('删除失败: ' + err.message)
  }
}

// Session Handlers
const openSessionEditModal = (item = null) => {
  if (!item) return
  sessionEditingId.value = item.id
  sessionForm.value = {
    user_id: item.user_id,
    session_id: item.session_id || '',
    title: item.title || '',
    content: item.content || '',
    feedback_type: item.feedback_type || 'none',
    comment: item.comment || ''
  }
  showSessionEditModal.value = true
}

const saveSessionItem = async () => {
  try {
    if (!sessionTargetSubAgent.value) {
      alert('未选择子智能体')
      return
    }
    if (!sessionEditingId.value) {
      alert('当前仅支持编辑已有会话')
      return
    }
    if (!sessionForm.value.user_id) {
      alert('请填写用户ID')
      return
    }
    const payload = {
      user_id: sessionForm.value.user_id,
      session_id: sessionForm.value.session_id || null,
      title: sessionForm.value.title || null,
      content: sessionForm.value.content || null,
      feedback_type: sessionForm.value.feedback_type || 'none',
      comment: sessionForm.value.comment || null
    }
    await api.put(`/sub-agents/${sessionTargetSubAgent.value.id}/sessions/${sessionEditingId.value}`, payload)
    await fetchSessions()
    showSessionEditModal.value = false
  } catch (err) {
    alert('保存失败: ' + err.message)
  }
}

const deleteSessionItem = async (id) => {
  if (!sessionTargetSubAgent.value) return
  if (!confirm('确定要删除该会话吗？')) return
  try {
    await api.delete(`/sub-agents/${sessionTargetSubAgent.value.id}/sessions/${id}`)
    await fetchSessions()
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
      storage: item.storage
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
      storage: 'neo4j'
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
    await Promise.all([fetchExpert(), fetchKnowledge(), fetchSkills(), fetchQuestions(), fetchSubAgents(), fetchKnowledgeGraphs()])
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

.knowledge-layout {
  display: flex;
  gap: 16px;
}

.knowledge-sidebar {
  width: 220px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 12px;
  height: fit-content;
}

.knowledge-content {
  flex: 1;
  min-width: 0;
}

.sidebar-title {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.knowledge-menu {
  border-right: none;
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

.action-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  width: 80px;
  justify-content: center;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
