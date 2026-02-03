<template>
  <div class="chat-layout">
    <el-card class="chat-card" :body-style="{ padding: '0px', display: 'flex', flexDirection: 'column', height: '100%' }">
      <template #header>
        <div class="header-content">
          <div class="header-left">
            <el-icon :size="20" class="mr-2"><ChatDotRound /></el-icon>
            <span class="title">AI 智能助手</span>
          </div>
          <el-tag size="small" type="success" effect="dark" round>Online</el-tag>
        </div>
      </template>
      
      <div class="messages-area" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <el-empty description="开始一次新的对话" :image-size="120" />
        </div>
        
        <template v-for="(msg, index) in messages" :key="index">
          <!-- System Message -->
          <div v-if="msg.type === 'system'" class="message-row message-system">
            <el-divider content-position="center">{{ msg.text }}</el-divider>
          </div>

          <!-- User/AI Message -->
          <div v-else :class="['message-row', msg.type === 'user' ? 'message-right' : 'message-left']">
            
            <!-- AI Avatar -->
            <div class="avatar" v-if="msg.type !== 'user'">
              <el-avatar :size="36" shape="square" class="ai-avatar">AI</el-avatar>
            </div>
            
            <!-- Message Bubble -->
            <div :class="['message-bubble', msg.type === 'error' ? 'bubble-error' : '']">
               <div class="message-content">{{ msg.text }}</div>
               <div class="message-time" v-if="msg.timestamp">{{ formatTime(msg.timestamp) }}</div>
            </div>
            
            <!-- User Avatar -->
            <div class="avatar" v-if="msg.type === 'user'">
              <el-avatar :size="36" shape="square" class="user-avatar">Me</el-avatar>
            </div>
          </div>
        </template>
        
        <!-- Loading Indicator -->
        <div v-if="loading" class="message-row message-left">
           <div class="avatar">
             <el-avatar :size="36" shape="square" class="ai-avatar">AI</el-avatar>
           </div>
           <div class="typing-indicator">
             <span></span><span></span><span></span>
           </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-wrapper">
          <el-input
            v-model="currentMessage"
            placeholder="输入您的问题 (Enter 发送, Shift+Enter 换行)..."
            :autosize="{ minRows: 1, maxRows: 6 }"
            type="textarea"
            resize="none"
            @keydown.enter.exact.prevent="sendMessage"
            :disabled="loading"
          />
          <el-button type="primary" class="send-btn" @click="sendMessage" :loading="loading" circle>
            <el-icon><Position /></el-icon>
          </el-button>
        </div>
        <div class="input-tip">Generated content may be inaccurate.</div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ChatDotRound, Position } from '@element-plus/icons-vue'
import api from '../services/api.js'

const messages = ref([
  { type: 'system', text: '欢迎使用 AI 对话系统', timestamp: new Date() }
])
const currentMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const formatTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  const content = currentMessage.value.trim()
  if (!content || loading.value) return
  
  // Add User Message
  messages.value.push({
    type: 'user',
    sender: '我',
    text: content,
    timestamp: new Date()
  })
  
  currentMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const response = await api.post('/ai/chat', {
      prompt: content
    })

    // Add AI Response
    messages.value.push({
      type: 'ai',
      sender: 'AI',
      text: response.data.response,
      timestamp: new Date()
    })
  } catch (error) {
    console.error(error)
    messages.value.push({
      type: 'error',
      sender: '系统',
      text: '获取回复失败，请检查网络或后端服务。',
      timestamp: new Date()
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-layout {
  height: calc(100vh - 120px);
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--el-box-shadow-light);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title {
  font-weight: 600;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

.messages-area {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--el-bg-color-page);
  scroll-behavior: smooth;
}

.message-system {
  width: 100%;
  margin: 20px 0;
  color: var(--el-text-color-secondary);
}

.message-row {
  display: flex;
  margin-bottom: 24px;
  align-items: flex-start;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-right {
  flex-direction: row-reverse;
}

.user-avatar {
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
}

.ai-avatar {
  background: var(--el-fill-color-dark);
  color: var(--el-text-color-primary);
}

.message-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
  box-shadow: var(--el-box-shadow-lighter);
}

.message-left .message-bubble {
  background-color: #fff;
  border-top-left-radius: 2px;
  color: var(--el-text-color-primary);
}

.message-right .message-bubble {
  background-color: var(--el-color-primary);
  color: #fff;
  border-top-right-radius: 2px;
}

.bubble-error {
  background-color: var(--el-color-danger-light-9) !important;
  color: var(--el-color-danger) !important;
  border: 1px solid var(--el-color-danger-light-5);
}

.message-time {
  font-size: 11px;
  margin-top: 6px;
  opacity: 0.6;
  text-align: right;
}

.input-area {
  padding: 20px;
  background-color: #fff;
  border-top: 1px solid var(--el-border-color-light);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.send-btn {
  margin-bottom: 2px;
}

.input-tip {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  text-align: center;
  margin-top: 8px;
}

.typing-indicator {
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  border-top-left-radius: 2px;
  display: flex;
  gap: 5px;
  box-shadow: var(--el-box-shadow-lighter);
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: var(--el-text-color-secondary);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); opacity: 0.6; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
