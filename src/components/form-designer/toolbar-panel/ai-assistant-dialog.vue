<template>
  <el-dialog
    v-model="dialogVisible"
    title="AI 表单助手"
    width="700px"
    destroy-on-close
    class="ai-assistant-dialog"
  >
    <div class="ai-chat-container">
      <!-- 欢迎信息 -->
      <div v-if="messages.length === 0" class="welcome-tip">
        <div class="tip-icon">🤖</div>
        <div class="tip-title">欢迎使用 AI 表单助手</div>
        <div class="tip-desc">描述你想要的表单，我来帮你生成配置</div>
        <div class="tip-examples">
          <div class="tip-example" @click="useExample('创建一个登录表单，包含用户名和密码')">
            创建一个登录表单，包含用户名和密码
          </div>
          <div class="tip-example" @click="useExample('生成一个联系人信息表单，包含姓名、手机、邮箱')">
            生成一个联系人信息表单，包含姓名、手机、邮箱
          </div>
          <div class="tip-example" @click="useExample('创建一个调查问卷，有标题、说明和满意度选择')">
            创建一个调查问卷，有标题、说明和满意度选择
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-else class="message-list" ref="messageListRef">
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['message', msg.role]"
        >
          <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="content">
            <!-- 用户消息 -->
            <div v-if="msg.role === 'user'" class="user-content">
              {{ msg.content }}
            </div>

            <!-- AI 消息 -->
            <div v-else class="ai-content">
              <div v-if="msg.error" class="error-message">
                {{ msg.error }}
              </div>
              <div v-else-if="msg.formJson" class="form-json-result">
                <div class="success-message">
                  已生成表单配置，包含 {{ msg.formJson.widgetList?.length || 0 }} 个组件
                </div>
                <div class="json-preview">
                  <pre>{{ formatJson(msg.formJson) }}</pre>
                </div>
                <div class="action-buttons">
                  <el-button type="primary" size="small" @click="applyForm(msg.formJson)">
                    应用到画布
                  </el-button>
                  <el-button size="small" @click="copyJson(msg.formJson)">
                    复制 JSON
                  </el-button>
                </div>
              </div>
              <div v-else-if="msg.content" class="text-message">
                {{ msg.content }}
              </div>
            </div>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="message assistant loading">
          <div class="avatar">🤖</div>
          <div class="content">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="3"
        :placeholder="'描述你想要创建的表单...\n（支持 Ctrl + Enter 发送）'"
        resize="none"
        @keydown.enter.ctrl="sendMessage"
      />
      <div class="input-actions">
        <el-button @click="clearChat" size="small">清空对话</el-button>
        <el-button type="primary" @click="sendMessage" :loading="loading" :disabled="!inputText.trim()">
          发送
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { chatWithAI, parseFormJson, type ChatMessage } from '@/utils/ai-chat'
import { deepClone } from '@/utils/util'

const props = defineProps<{
  modelValue: boolean
  designer: any
}>()

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(false)
const messages = ref<ChatMessage[]>([])
const inputText = ref('')
const loading = ref(false)
const messageListRef = ref<HTMLElement | null>(null)

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

function useExample(text: string) {
  inputText.value = text
  sendMessage()
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  // 添加用户消息
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: text
  })

  inputText.value = ''
  loading.value = true
  scrollToBottom()

  try {
    // 调用 AI
    const response = await chatWithAI(text)

    // 解析 JSON
    const formJson = parseFormJson(response)

    // 添加 AI 响应
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: response,
      formJson
    })
  } catch (error: any) {
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: '',
      error: error.message || '抱歉，发生了错误，请稍后重试'
    })
  }

  loading.value = false
  nextTick(() => scrollToBottom())
}

function applyForm(formJson: any) {
  if (!formJson) return

  try {
    // 清除当前设计器
    props.designer.clearDesigner(true)

    // 加载新的表单配置
    if (formJson.widgetList && formJson.widgetList.length > 0) {
      props.designer.loadFormJson({
        widgetList: deepClone(formJson.widgetList),
        formConfig: deepClone(formJson.formConfig || {})
      })
    } else {
      props.designer.initDesigner()
    }

    ElMessage.success('表单已应用到画布')
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('应用表单失败：' + (error as Error).message)
  }
}

function copyJson(formJson: any) {
  const jsonStr = JSON.stringify(formJson, null, 2)
  navigator.clipboard.writeText(jsonStr).then(() => {
    ElMessage.success('JSON 已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

function formatJson(json: any): string {
  try {
    return JSON.stringify(json, null, 2)
  } catch {
    return String(json)
  }
}

function clearChat() {
  messages.value = []
}

function scrollToBottom() {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}
</script>

<style lang="scss" scoped>
.ai-assistant-dialog {
  .ai-chat-container {
    min-height: 300px;
    max-height: 400px;
    overflow-y: auto;
    padding: 0 8px;
  }

  .welcome-tip {
    text-align: center;
    padding: 40px 20px;
    color: #606266;

    .tip-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }

    .tip-title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 8px;
    }

    .tip-desc {
      font-size: 14px;
      color: #909399;
      margin-bottom: 24px;
    }

    .tip-examples {
      text-align: left;

      .tip-example {
        background: #f5f7fa;
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        font-size: 13px;
        color: #606266;
        transition: all 0.2s;

        &:hover {
          background: #e4e7ed;
          color: #667eea;
        }
      }
    }
  }

  .message-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 8px 0;
  }

  .message {
    display: flex;
    gap: 12px;
    align-items: flex-start;

    &.user {
      flex-direction: row-reverse;

      .content {
        align-items: flex-end;
      }

      .user-content {
        background: #667eea;
        color: #fff;
        border-radius: 16px 16px 4px 16px;
        padding: 10px 14px;
        max-width: 80%;
      }
    }

    &.assistant {
      .content {
        align-items: flex-start;
      }

      .ai-content {
        max-width: 85%;
      }
    }

    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #f5f7fa;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      flex-shrink: 0;
    }

    .content {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .success-message {
      color: #67c23a;
      font-size: 13px;
      margin-bottom: 8px;
    }

    .error-message {
      color: #f56c6c;
      font-size: 13px;
      padding: 8px 12px;
      background: #fef0f0;
      border-radius: 8px;
    }

    .json-preview {
      background: #1e1e1e;
      border-radius: 8px;
      padding: 12px;
      max-height: 200px;
      overflow-y: auto;

      pre {
        margin: 0;
        color: #d4d4d4;
        font-size: 12px;
        font-family: 'Monaco', 'Menlo', monospace;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }

    .action-buttons {
      display: flex;
      gap: 8px;
      margin-top: 8px;
    }

    .text-message {
      background: #f5f7fa;
      padding: 10px 14px;
      border-radius: 4px 16px 16px 16px;
      color: #303133;
      font-size: 14px;
    }

    &.loading {
      .avatar {
        background: #e4e7ed;
      }

      .loading-dots {
        display: flex;
        gap: 4px;
        padding: 8px 0;

        span {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #909399;
          animation: bounce 1.4s infinite ease-in-out both;

          &:nth-child(1) { animation-delay: -0.32s; }
          &:nth-child(2) { animation-delay: -0.16s; }
        }
      }
    }
  }

  .input-area {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #eee;

    .input-actions {
      display: flex;
      justify-content: space-between;
      margin-top: 12px;
    }
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

:deep(.el-dialog__body) {
  padding: 16px 20px;
}
</style>
