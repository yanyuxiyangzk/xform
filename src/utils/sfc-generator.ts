import type { FormJson } from '@/types/form'

// SFC (Single File Component) Generator for Vue 3
export function generateSFC(formJson: FormJson): string {
  const { widgetList, formConfig } = formJson

  const componentName = 'XFormSFC'

  const template = generateTemplate(widgetList)
  const script = generateScript(widgetList, formConfig)
  const style = generateStyle(formConfig)

  return `<template>
${template}
</template>

${script}

${style}`
}

function generateTemplate(widgetList: any[]): string {
  const widgets = widgetList.map(w => buildWidgetTemplate(w, 2)).join('\n')

  return `  <el-form :model="formData" label-width="80px" class="xform-container">
${widgets}
    <el-form-item>
      <el-button type="primary" @click="handleSubmit">提交</el-button>
      <el-button @click="handleReset">重置</el-button>
    </el-form-item>
  </el-form>`
}

function buildWidgetTemplate(widget: any, indent: number): string {
  const spaces = '  '.repeat(indent)

  if (widget.category === 'container') {
    return buildContainerTemplate(widget, indent)
  }

  if (widget.formItemFlag) {
    return buildFieldTemplate(widget, indent)
  }

  return ''
}

function buildContainerTemplate(widget: any, indent: number): string {
  const spaces = '  '.repeat(indent)

  switch (widget.type) {
    case 'grid':
      const cols = widget.cols?.map((col: any) => {
        const widgets = col.widgetList?.map((w: any) => buildWidgetTemplate(w, indent + 3)).join('\n') || ''
        return `${spaces}    <el-col :span="${col.options?.span || 12}">
${widgets}
${spaces}    </el-col>`
      }).join('\n') || ''

      return `${spaces}<el-row :gutter="${widget.options?.gutter || 0}">
${cols}
${spaces}</el-row>`

    case 'tab':
      const panes = widget.tabs?.map((tab: any) => {
        const widgets = tab.widgetList?.map((w: any) => buildWidgetTemplate(w, indent + 3)).join('\n') || ''
        return `${spaces}    <el-tab-pane label="${tab.options?.label || 'Tab'}" name="${tab.options?.name}">
${widgets}
${spaces}    </el-tab-pane>`
      }).join('\n') || ''

      return `${spaces}<el-tabs>
${panes}
${spaces}</el-tabs>`

    case 'sub-form':
      const subWidgets = widget.widgetList?.map((w: any) => buildWidgetTemplate(w, indent + 2)).join('\n') || ''
      return `${spaces}<div class="sub-form">
${spaces}  <h4>${widget.options?.label || '子表单'}</h4>
${subWidgets}
${spaces}</div>`

    case 'table':
      const rows = widget.rows?.map((row: any) => {
        const cells = row.cols?.map((cell: any) => {
          const cellWidgets = cell.widgetList?.map((w: any) => buildWidgetTemplate(w, indent + 3)).join('\n') || ''
          return `${spaces}      <td colspan="${cell.options?.colspan || 1}" rowspan="${cell.options?.rowspan || 1}">
${cellWidgets}
${spaces}      </td>`
        }).join('\n') || ''

        return `${spaces}    <tr>
${cells}
${spaces}    </tr>`
      }).join('\n') || ''

      return `${spaces}<table class="xform-table">
${spaces}  <tbody>
${rows}
${spaces}  </tbody>
${spaces}</table>`

    default:
      const defaultWidgets = widget.widgetList?.map((w: any) => buildWidgetTemplate(w, indent)).join('\n') || ''
      return defaultWidgets
  }
}

function buildFieldTemplate(widget: any, indent: number): string {
  const spaces = '  '.repeat(indent)
  const { options = {} } = widget
  const label = options.label || ''
  const name = options.name || ''
  const placeholder = options.placeholder || ''

  switch (widget.type) {
    case 'input':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-input v-model="formData.${name}" placeholder="${placeholder}" />
${spaces}</el-form-item>`

    case 'textarea':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-input v-model="formData.${name}" type="textarea" placeholder="${placeholder}" rows="${options.rows || 4}" />
${spaces}</el-form-item>`

    case 'number':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-input-number v-model="formData.${name}" :min="${options.min || 0}" :max="${options.max || 100}" />
${spaces}</el-form-item>`

    case 'select':
      const optionsList = (options.optionItems || []).map((opt: any) =>
        `${spaces}      <el-option label="${opt.label}" value="${opt.value}" />`
      ).join('\n')
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-select v-model="formData.${name}" placeholder="${placeholder}">
${optionsList}
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

    case 'checkbox':
      const checkboxes = (options.optionItems || []).map((opt: any) =>
        `${spaces}      <el-checkbox label="${opt.value}">${opt.label}</el-checkbox>`
      ).join('\n')
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-checkbox-group v-model="formData.${name}">
${checkboxes}
${spaces}  </el-checkbox-group>
${spaces}</el-form-item>`

    case 'date':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-date-picker v-model="formData.${name}" type="date" placeholder="${placeholder}" value-format="YYYY-MM-DD" />
${spaces}</el-form-item>`

    case 'time':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-time-picker v-model="formData.${name}" placeholder="${placeholder}" value-format="HH:mm:ss" />
${spaces}</el-form-item>`

    case 'switch':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-switch v-model="formData.${name}" />
${spaces}</el-form-item>`

    case 'slider':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-slider v-model="formData.${name}" :min="${options.min || 0}" :max="${options.max || 100}" />
${spaces}</el-form-item>`

    case 'rate':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-rate v-model="formData.${name}" />
${spaces}</el-form-item>`

    case 'color':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-color-picker v-model="formData.${name}" />
${spaces}</el-form-item>`

    case 'picture-upload':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <el-upload action="${options.action || '/upload'}" list-type="picture-card">
${spaces}    <el-icon><Plus /></el-icon>
${spaces}  </el-upload>
${spaces}</el-form-item>`

    case 'rich-editor':
      return `${spaces}<el-form-item label="${label}">
${spaces}  <div v-html="formData.${name}"></div>
${spaces}</el-form-item>`

    case 'static-text':
      return `${spaces}<div class="static-text">${options.textContent || ''}</div>`

    case 'divider':
      return `${spaces}<el-divider />`

    default:
      return `${spaces}<!-- Unknown field: ${widget.type} -->`
  }
}

function generateScript(widgetList: any[], formConfig: any): string {
  const formData: Record<string, any> = {}

  function collectData(widget: any) {
    if (widget.formItemFlag && widget.options?.name) {
      formData[widget.options.name] = widget.options.defaultValue
    }
    if (widget.widgetList) widget.widgetList.forEach(collectData)
    if (widget.cols) widget.cols.forEach((col: any) => col.widgetList?.forEach(collectData))
    if (widget.rows) widget.rows.forEach((row: any) => row.cols?.forEach((cell: any) => cell.widgetList?.forEach(collectData)))
    if (widget.tabs) widget.tabs.forEach((tab: any) => tab.widgetList?.forEach(collectData))
  }

  widgetList.forEach(collectData)

  return `<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const formData = reactive(${JSON.stringify(formData, null, 4)})

function handleSubmit() {
  console.log('Form Data:', formData)
  ElMessage.success('提交成功')
}

function handleReset() {
  Object.keys(formData).forEach(key => {
    formData[key] = null
  })
}
</script>`
}

function generateStyle(formConfig: any): string {
  let css = formConfig?.cssCode || ''

  return `<style scoped>
.xform-container {
  padding: 20px;
}

.sub-form {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.xform-table {
  width: 100%;
  border-collapse: collapse;
}

.xform-table td {
  border: 1px solid #dcdfe6;
  padding: 8px;
}

.static-text {
  padding: 8px 0;
}
${css}
</style>`
}
