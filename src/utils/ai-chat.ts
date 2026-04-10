/**
 * AI Chat Service
 * 处理与 AI API 的通信
 */

import axios from 'axios'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  formJson?: any
}

export interface ChatResponse {
  content: string
  error?: string
}

// System prompt for form generation
const SYSTEM_PROMPT = `你是一个表单生成助手。用户描述他们想要的表单，你会生成对应的 JSON 配置。

规则：
1. 只返回 JSON，不要其他解释
2. JSON 格式必须包含 widgetList 和 formConfig
3. widgetList 是组件数组，每个组件需要 type, formItemFlag 和 options
4. options 必须包含 name（字段名）和 label（标签）
5. formItemFlag 必须为 true，表示这是表单项
6. 支持的组件类型：input, textarea, select, radio, checkbox, date, time, switch, slider, rate, cascader, color, number
7. 每个组件需要有唯一的 name

示例输入：创建一个登录表单，包含用户名和密码
示例输出：
\`\`\`json
{
  "widgetList": [
    {"type": "input", "formItemFlag": true, "options": {"name": "username", "label": "用户名", "placeholder": "请输入用户名", "type": "text"}},
    {"type": "input", "formItemFlag": true, "options": {"name": "password", "label": "密码", "placeholder": "请输入密码", "type": "password"}}
  ],
  "formConfig": {}
}
\`\`\`

重要：只返回 JSON 代码块，不要其他文字！`

const AI_API_URL = import.meta.env.VITE_AI_API_URL || '/api/ai/chat'

export async function chatWithAI(userMessage: string): Promise<string> {
  try {
    const response = await axios.post<ChatResponse>(AI_API_URL, {
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userMessage }
      ],
      model: 'claude-3-sonnet-20240229',
      temperature: 0.7,
      max_tokens: 4096,
    })
    return response.data.content
  } catch (error: any) {
    // 如果是网络错误或 API 不可用，返回模拟响应用于测试
    if (error.code === 'ERR_NETWORK' || error.response?.status === 404) {
      console.warn('AI API 不可用，使用模拟响应')
      return generateMockResponse(userMessage)
    }
    throw new Error(error.message || 'AI 服务调用失败')
  }
}

/**
 * 解析 AI 返回的文本，提取 JSON
 */
export function parseFormJson(text: string): any {
  if (!text) return null

  // 尝试匹配 ```json ... ``` 包裹的 JSON
  let match = text.match(/```json\n?([\s\S]*?)\n?```/)
  if (match) {
    try {
      return JSON.parse(match[1])
    } catch {
      // 继续尝试其他格式
    }
  }

  // 尝试匹配 ``` ... ``` 包裹的内容
  match = text.match(/```\n?([\s\S]*?)\n?```/)
  if (match) {
    try {
      return JSON.parse(match[1])
    } catch {
      // 继续尝试
    }
  }

  // 尝试直接匹配 { ... }
  match = text.match(/(\{[\s\S]*\})/)
  if (match) {
    try {
      const parsed = JSON.parse(match[1])
      // 验证是否是表单 JSON
      if (parsed.widgetList || parsed.formConfig) {
        return parsed
      }
    } catch {
      // 不是有效的 JSON
    }
  }

  return null
}

/**
 * 生成模拟响应（用于测试或 API 不可用时）
 */
function generateMockResponse(userMessage: string): string {
  const lowerMsg = userMessage.toLowerCase()

  if (lowerMsg.includes('登录') || lowerMsg.includes('login')) {
    return `\`\`\`json
{
  "widgetList": [
    {"type": "input", "formItemFlag": true, "options": {"name": "username", "label": "用户名", "placeholder": "请输入用户名", "type": "text"}},
    {"type": "input", "formItemFlag": true, "options": {"name": "password", "label": "密码", "placeholder": "请输入密码", "type": "password"}}
  ],
  "formConfig": {}
}
\`\`\``
  }

  if (lowerMsg.includes('联系') || lowerMsg.includes('用户信息')) {
    return `\`\`\`json
{
  "widgetList": [
    {"type": "input", "formItemFlag": true, "options": {"name": "name", "label": "姓名", "placeholder": "请输入姓名"}},
    {"type": "input", "formItemFlag": true, "options": {"name": "phone", "label": "手机号", "placeholder": "请输入手机号", "type": "tel"}},
    {"type": "input", "formItemFlag": true, "options": {"name": "email", "label": "邮箱", "placeholder": "请输入邮箱", "type": "email"}}
  ],
  "formConfig": {}
}
\`\`\``
  }

  if (lowerMsg.includes('调查') || lowerMsg.includes('问卷')) {
    return `\`\`\`json
{
  "widgetList": [
    {"type": "input", "formItemFlag": true, "options": {"name": "title", "label": "问卷标题", "placeholder": "请输入问卷标题"}},
    {"type": "textarea", "formItemFlag": true, "options": {"name": "description", "label": "问卷说明", "placeholder": "请输入说明"}},
    {"type": "radio", "formItemFlag": true, "options": {"name": "satisfaction", "label": "总体满意度", "optionItems": [{"label": "非常满意", "value": "5"}, {"label": "满意", "value": "4"}, {"label": "一般", "value": "3"}]}},
    {"type": "checkbox", "formItemFlag": true, "options": {"name": "interests", "label": "感兴趣的领域", "optionItems": [{"label": "前端开发", "value": "frontend"}, {"label": "后端开发", "value": "backend"}]}}
  ],
  "formConfig": {}
}
\`\`\``
  }

  // 默认：简单输入框
  return `\`\`\`json
{
  "widgetList": [
    {"type": "input", "formItemFlag": true, "options": {"name": "field1", "label": "字段1", "placeholder": "请输入"}},
    {"type": "input", "formItemFlag": true, "options": {"name": "field2", "label": "字段2", "placeholder": "请输入"}}
  ],
  "formConfig": {}
}
\`\`\``
}
