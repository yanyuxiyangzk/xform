# AI表单生成功能 - 技术设计

## 一、技术方案

### 1.1 技术栈

- **前端框架**: Vue3 + TypeScript
- **UI组件**: Element Plus
- **AI接口**: Claude API ( Anthropic )
- **构建工具**: Vite

### 1.2 组件结构

```
src/components/form-designer/
├── toolbar-panel/
│   └── ai-assistant-dialog.vue    # AI 对话弹窗 ⭐
└── ai-assistant/
    ├── index.vue                  # AI助手主组件
    └── message-list.vue           # 消息列表
```

### 1.3 核心接口

```typescript
// AI 对话服务
interface AiChatService {
  // 发送消息并获取响应
  chat(messages: ChatMessage[]): Promise<AiResponse>
}

// 解析 AI 返回的表单 JSON
interface FormParser {
  parse(text: string): FormJson | null
}
```

### 1.4 数据流

```
用户输入
    ↓
组装 messages (包含 system prompt + 用户输入)
    ↓
调用 Claude API
    ↓
解析响应文本，提取 JSON
    ↓
验证 JSON 格式
    ↓
调用 designer.loadFormJson()
    ↓
渲染到画布
```

## 二、API 设计

### 2.1 AI 接口

```typescript
// POST /api/ai/chat
interface ChatRequest {
  messages: ChatMessage[]
  model?: string
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

interface ChatResponse {
  content: string  // AI 响应文本
  error?: string
}
```

### 2.2 System Prompt

```
你是一个表单生成助手。用户描述他们想要的表单，你会生成对应的 JSON 配置。

规则：
1. 只返回 JSON，不要其他解释
2. JSON 格式：
{
  "widgetList": [...],
  "formConfig": {...}
}
3. 支持的组件类型：input, textarea, select, radio, checkbox, date, switch, slider 等
4. 每个组件需要包含：type, options (包含 name, label, placeholder 等)

示例输入：创建一个登录表单，包含用户名和密码
示例输出：
{
  "widgetList": [
    {"type": "input", "options": {"name": "username", "label": "用户名", "placeholder": "请输入用户名"}},
    {"type": "input", "options": {"name": "password", "label": "密码", "placeholder": "请输入密码", "type": "password"}}
  ],
  "formConfig": {}
}
```

## 三、组件设计

### 3.1 AIAssistantDialog

```vue
<template>
  <el-dialog
    v-model="visible"
    title="AI 表单助手"
    width="700px"
  >
    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef">
      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['message', msg.role]"
      >
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="content">
          <div v-if="msg.role === 'assistant' && msg.formJson" class="form-preview">
            <el-button size="small" type="primary" @click="applyForm(msg.formJson)">
              应用到画布
            </el-button>
            <pre>{{ msg.formJson }}</pre>
          </div>
          <div v-else>{{ msg.content }}</div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="描述你想要创建的表单..."
        @keydown.enter.ctrl="sendMessage"
      />
      <el-button type="primary" @click="sendMessage" :loading="loading">
        发送
      </el-button>
    </div>
  </el-dialog>
</template>
```

### 3.2 核心方法

```typescript
// 发送消息
async function sendMessage() {
  if (!inputText.value.trim()) return

  // 1. 添加用户消息
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: inputText.value
  })

  loading.value = true

  try {
    // 2. 调用 AI
    const response = await chatWithAI(inputText.value)

    // 3. 解析 JSON
    const formJson = parseFormJson(response)

    // 4. 添加 AI 响应
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: response,
      formJson
    })
  } catch (error) {
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: '抱歉，发生了错误：' + error.message
    })
  }

  loading.value = false
}

// 解析表单 JSON
function parseFormJson(text: string): any {
  // 提取 ```json ... ``` 包裹的 JSON
  const match = text.match(/```json\n([\s\S]*?)\n```/) ||
                text.match(/```\n?([\s\S]*?)\n?```/) ||
                text.match(/\{[\s\S]*\}/)

  if (match) {
    try {
      return JSON.parse(match[1])
    } catch {
      return null
    }
  }
  return null
}

// 应用到画布
function applyForm(formJson: any) {
  designer.clearDesigner(true)
  designer.loadFormJson(formJson)
  visible.value = false
}
```

## 四、配置文件

### 4.1 AI 配置 (src/config/ai.ts)

```typescript
export const AI_CONFIG = {
  apiUrl: import.meta.env.VITE_AI_API_URL || '/api/ai/chat',
  model: 'claude-3-sonnet-20240229',
  temperature: 0.7,
  maxTokens: 4096,
}
```

## 五、注意事项

1. **错误处理**: 网络错误、超时、API 限额等需要友好提示
2. **JSON 解析**: AI 返回可能不是标准 JSON，需要容错处理
3. **安全**: 不要在 client 端暴露 API Key，使用代理
4. **体验**: 添加 loading 状态，禁用重复提交

---
