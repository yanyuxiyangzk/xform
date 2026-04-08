import type { FormJson } from '@/types/form'
import { generateSFC } from './sfc-generator'

export interface ExportOptions {
  format: 'json' | 'vue' | 'html'
  fileName?: string
  includeStyle?: boolean
}

export function exportFormJson(formJson: FormJson, fileName = 'form-design.json') {
  const jsonStr = JSON.stringify(formJson, null, 2)
  downloadFile(jsonStr, fileName, 'application/json')
}

export function exportVueSFC(formJson: FormJson, fileName = 'FormComponent.vue') {
  const vueCode = generateSFC(formJson)
  downloadFile(vueCode, fileName, 'text/plain')
}

export function exportHtml(formJson: FormJson, fileName = 'form-preview.html') {
  const htmlContent = generateHtmlPreview(formJson)
  downloadFile(htmlContent, fileName, 'text/html')
}

function downloadFile(content: string, fileName: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function generateHtmlPreview(formJson: FormJson): string {
  const { formConfig } = formJson

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${formConfig?.title || '表单预览'}</title>
  <link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css">
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <script src="https://unpkg.com/element-plus"></script>
  <script src="https://unpkg.com/@element-plus/icons-vue"></script>
  <style>
    #app {
      font-family: Avenir, Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      padding: 20px;
    }
    ${formConfig?.cssCode || ''}
  </style>
</head>
<body>
  <div id="app">
    <el-form :model="formData" label-width="80px">
      ${generateFormHtml(formJson.widgetList)}
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>

  <script>
    const { createApp, reactive } = Vue

    const app = createApp({
      setup() {
        const formData = reactive(${JSON.stringify(generateFormDataObj(formJson.widgetList), null, 2)})

        function handleSubmit() {
          console.log('Form Data:', formData)
          ElementPlus.ElMessage.success('提交成功')
        }

        function handleReset() {
          Object.keys(formData).forEach(key => {
            formData[key] = null
          })
        }

        return {
          formData,
          handleSubmit,
          handleReset
        }
      }
    })

    app.use(ElementPlus)
    app.mount('#app')
  </script>
</body>
</html>`
}

function generateFormHtml(widgetList: any[]): string {
  return widgetList.map(w => buildWidgetHtml(w, 4)).join('\n')
}

function buildWidgetHtml(widget: any, indent: number): string {
  const spaces = '  '.repeat(indent)

  if (widget.category === 'container') {
    return buildContainerHtml(widget, indent)
  }

  if (widget.formItemFlag) {
    return buildFieldHtml(widget, indent)
  }

  return ''
}

function buildContainerHtml(widget: any, indent: number): string {
  const spaces = '  '.repeat(indent)

  switch (widget.type) {
    case 'grid':
      const cols = widget.cols?.map((col: any) => {
        const widgets = col.widgetList?.map((w: any) => buildWidgetHtml(w, indent + 3)).join('\n') || ''
        return `${spaces}    <el-col :span="${col.options?.span || 12}">
${widgets}
${spaces}    </el-col>`
      }).join('\n') || ''

      return `${spaces}<el-row :gutter="${widget.options?.gutter || 0}">
${cols}
${spaces}</el-row>`

    case 'tab':
      const panes = widget.tabs?.map((tab: any) => {
        const widgets = tab.widgetList?.map((w: any) => buildWidgetHtml(w, indent + 3)).join('\n') || ''
        return `${spaces}    <el-tab-pane label="${tab.options?.label || 'Tab'}" name="${tab.options?.name}">
${widgets}
${spaces}    </el-tab-pane>`
      }).join('\n') || ''

      return `${spaces}<el-tabs>
${panes}
${spaces}</el-tabs>`

    default:
      return ''
  }
}

function buildFieldHtml(widget: any, indent: number): string {
  const spaces = '  '.repeat(indent)
  const { options = {} } = widget
  const label = options.label || ''
  const name = options.name || ''
  const placeholder = options.placeholder || ''

  switch (widget.type) {
    case 'input':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-input v-model="formData.${name}" placeholder="${placeholder}"></el-input>
${spaces}</el-form-item>`

    case 'textarea':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-input v-model="formData.${name}" type="textarea" placeholder="${placeholder}"></el-input>
${spaces}</el-form-item>`

    case 'number':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-input-number v-model="formData.${name}"></el-input-number>
${spaces}</el-form-item>`

    case 'select':
      const opts = (options.optionItems || []).map((opt: any) =>
        `${spaces}      <el-option label="${opt.label}" value="${opt.value}"></el-option>`
      ).join('\n')
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-select v-model="formData.${name}" placeholder="${placeholder}">
${opts}
${spaces}  </el-select>
${spaces}</el-form-item>`

    case 'radio':
      const radios = (options.optionItems || []).map((opt: any) =>
        `${spaces}      <el-radio label="${opt.value}">${opt.label}</el-radio>`
      ).join('\n')
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-radio-group v-model="formData.${name}">
${radios}
${spaces}  </el-radio-group>
${spaces}</el-form-item>`

    case 'switch':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-switch v-model="formData.${name}"></el-switch>
${spaces}</el-form-item>`

    case 'date':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-date-picker v-model="formData.${name}" type="date" placeholder="${placeholder}"></el-date-picker>
${spaces}</el-form-item>`

    case 'rate':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-rate v-model="formData.${name}"></el-rate>
${spaces}</el-form-item>`

    default:
      return `${spaces}<!-- ${widget.type} -->`
  }
}

function generateFormDataObj(widgetList: any[]): Record<string, any> {
  const data: Record<string, any> = {}

  function collect(w: any) {
    if (w.formItemFlag && w.options?.name) {
      data[w.options.name] = w.options.defaultValue
    }
    if (w.widgetList) w.widgetList.forEach(collect)
    if (w.cols) w.cols.forEach((col: any) => col.widgetList?.forEach(collect))
    if (w.rows) w.rows.forEach((row: any) => row.cols?.forEach((cell: any) => cell.widgetList?.forEach(collect)))
    if (w.tabs) w.tabs.forEach((tab: any) => tab.widgetList?.forEach(collect))
  }

  widgetList.forEach(collect)
  return data
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text)
}
