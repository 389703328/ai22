<template>
  <div class="ai-chat">
    <h1>AI Chat Interface</h1>
    
    <div class="chat-container">
      <div class="messages">
        <div v-for="(message, index) in messages" :key="index" :class="message.type">
          <strong>{{ message.sender }}:</strong> {{ message.text }}
        </div>
      </div>
      
      <div class="input-area">
        <input 
          v-model="currentMessage" 
          @keyup.enter="sendMessage"
          placeholder="Type your message here..."
          class="message-input"
        />
        <button @click="sendMessage" class="send-btn" :disabled="loading">
          {{ loading ? 'Sending...' : 'Send' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'AIChat',
  data() {
    return {
      messages: [
        { type: 'system', sender: 'System', text: 'Welcome to AI Chat!' }
      ],
      currentMessage: '',
      loading: false
    }
  },
  methods: {
    async sendMessage() {
      if (!this.currentMessage.trim() || this.loading) return
      
      const userMessage = this.currentMessage
      this.messages.push({
        type: 'user',
        sender: 'You',
        text: userMessage
      })
      
      this.currentMessage = ''
      this.loading = true
      
      try {
        const response = await api.post('/ai/chat', {
          prompt: userMessage
        })
        
        this.messages.push({
          type: 'ai',
          sender: 'AI',
          text: response.data.response
        })
      } catch (error) {
        this.messages.push({
          type: 'error',
          sender: 'Error',
          text: 'Failed to get AI response. Please try again.'
        })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.ai-chat {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 32px 0;
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.chat-container {
  background: white;
  border-radius: 12px;
  height: 600px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  overflow: hidden;
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

.messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: linear-gradient(180deg, #f8f9fb 0%, #f5f5f8 100%);
}

.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: transparent;
}

.messages::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.messages > div {
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 80%;
  word-wrap: break-word;
  font-size: 14px;
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(30, 60, 114, 0.2);
  border-radius: 12px;
  border-bottom-right-radius: 2px;
}

.ai {
  align-self: flex-start;
  background: white;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  border-bottom-left-radius: 2px;
}

.system {
  align-self: center;
  background: #f0f0f5;
  color: #666;
  font-style: italic;
  font-size: 12px;
  padding: 8px 12px;
}

.error {
  align-self: center;
  background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
  color: #c53030;
  border: 1px solid #fc8181;
  font-size: 12px;
}

.input-area {
  display: flex;
  padding: 20px 24px;
  border-top: 1px solid #e8e8f0;
  gap: 12px;
  background: white;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.3s ease;
  resize: none;
  outline: none;
}

.message-input:focus {
  border-color: #1E3C72;
  box-shadow: 0 0 0 3px rgba(30, 60, 114, 0.1);
}

.message-input::placeholder {
  color: #999;
}

.send-btn {
  padding: 12px 28px;
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(30, 60, 114, 0.4);
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(30, 60, 114, 0.6);
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

@media (max-width: 768px) {
  .ai-chat {
    padding: 24px 16px;
  }

  h1 {
    font-size: 24px;
    margin-bottom: 24px;
  }

  .chat-container {
    height: 500px;
  }

  .messages > div {
    max-width: 90%;
    padding: 10px 14px;
  }

  .message-input {
    padding: 10px 12px;
    font-size: 14px;
  }

  .send-btn {
    padding: 10px 16px;
    font-size: 12px;
  }
}
</style>