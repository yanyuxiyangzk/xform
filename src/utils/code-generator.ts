import { deepClone } from './util'
import type { FormJson, WidgetSchema, FieldWidget, ContainerWidget } from '@/types/form'

// Code Generator for Form Export
export function generateFormCode(formJson: FormJson): string {
  const { widgetList, formConfig } = formJson

  const imports = [
    "import { reactive, ref } from 'vue'",
    "import { ElMessage } from 'element-plus'",
  ]

  const componentName = 'XFormGenerated'

  const formData = generateFormData(widgetList)
  const formTemplate = generateFormTemplate(widgetList)
  const formStyles = generateFormStyles(widgetList, formConfig)

  const scriptContent = `
${imports.join('\n')}

export default {
  name: '${componentName}',
  setup() {
    const formData = reactive(${JSON.stringify(formData, null, 2)})

    ${generateFormMethods(widgetList)}

    return {
      formData,
    }
  },
  methods: {
    submitForm() {
      console.log('Form Data:', this.formData)
      ElMessage.success('Submit success')
    },
    resetForm() {
      Object.keys(this.formData).forEach(key => {
        this.formData[key] = null
      })
    }
  }
}

${formTemplate}

<style scoped>
${formStyles}
</style>
`

  return scriptContent
}

function generateFormData(widgetList: any[]): Record<string, any> {
  const data: Record<string, any> = {}

  function processWidget(widget: any) {
    if (widget.formItemFlag && widget.options?.name) {
      data[widget.options.name] = widget.options.defaultValue
    }

    if (widget.widgetList) {
      widget.widgetList.forEach(processWidget)
    }
    if (widget.cols) {
      widget.cols.forEach((col: any) => {
        if (col.widgetList) {
          col.widgetList.forEach(processWidget)
        }
      })
    }
    if (widget.rows) {
      widget.rows.forEach((row: any) => {
        row.cols?.forEach((cell: any) => {
          if (cell.widgetList) {
            cell.widgetList.forEach(processWidget)
          }
        })
      })
    }
    if (widget.tabs) {
      widget.tabs.forEach((tab: any) => {
        if (tab.widgetList) {
          tab.widgetList.forEach(processWidget)
        }
      })
    }
  }

  widgetList.forEach(processWidget)
  return data
}

function generateFormTemplate(widgetList: any[]): string {
  const widgets = widgetList.map(w => generateWidgetTemplate(w)).join('\n')

  return `
<template>
  <el-form :model="formData" label-width="80px">
    ${widgets}
    <el-form-item>
      <el-button type="primary" @click="submitForm">提交</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
</template>
`
}

function generateWidgetTemplate(widget: any): string {
  if (widget.category === 'container') {
    return generateContainerTemplate(widget)
  } else if (widget.formItemFlag) {
    return generateFieldTemplate(widget)
  }
  return ''
}

function generateContainerTemplate(widget: any): string {
  switch (widget.type) {
    case 'grid':
      return generateGridTemplate(widget)
    case 'tab':
      return generateTabTemplate(widget)
    case 'sub-form':
      return generateSubFormTemplate(widget)
    case 'table':
      return generateTableTemplate(widget)
    default:
      return widget.widgetList?.map((w: any) => generateWidgetTemplate(w)).join('\n') || ''
  }
}

function generateGridTemplate(widget: any): string {
  const cols = widget.cols?.map((col: any) => {
    const widgets = col.widgetList?.map((w: any) => generateWidgetTemplate(w)).join('\n') || ''
    return `      <el-col :span="${col.options?.span || 12}">\n        ${widgets}\n      </el-col>`
  }).join('\n') || ''

  return `
    <el-row :gutter="${widget.options?.gutter || 0}">
${cols}
    </el-row>
`
}

function generateTabTemplate(widget: any): string {
  const panes = widget.tabs?.map((tab: any) => {
    const widgets = tab.widgetList?.map((w: any) => generateWidgetTemplate(w)).join('\n') || ''
    return `      <el-tab-pane label="${tab.options?.label || 'Tab'}" name="${tab.options?.name}">
        ${widgets}
      </el-tab-pane>`
  }).join('\n') || ''

  return `
    <el-tabs>
${panes}
    </el-tabs>
`
}

function generateSubFormTemplate(widget: any): string {
  const widgets = widget.widgetList?.map((w: any) => generateWidgetTemplate(w)).join('\n') || ''
  return `
    <div class="sub-form">
      <h3>${widget.options?.label || 'Sub Form'}</h3>
      ${widgets}
    </div>
`
}

function generateTableTemplate(widget: any): string {
  const rows = widget.rows?.map((row: any) => {
    const cells = row.cols?.map((cell: any) => {
      const widgets = cell.widgetList?.map((w: any) => generateWidgetTemplate(w)).join('\n') || ''
      return `        <td>${widgets}</td>`
    }).join('\n') || ''

    return `      <tr>
${cells}
      </tr>`
  }).join('\n') || ''

  return `
    <table>
      <tbody>
${rows}
      </tbody>
    </table>
`
}

function generateFieldTemplate(widget: any): string {
  const { options = {} } = widget
  const label = options.label || ''
  const name = options.name || ''
  const placeholder = options.placeholder || ''

  switch (widget.type) {
    case 'input':
      return `<el-form-item label="${label}">
        <el-input v-model="formData.${name}" placeholder="${placeholder}" />
      </el-form-item>`

    case 'textarea':
      return `<el-form-item label="${label}">
        <el-input v-model="formData.${name}" type="textarea" placeholder="${placeholder}" />
      </el-form-item>`

    case 'number':
      return `<el-form-item label="${label}">
        <el-input-number v-model="formData.${name}" />
      </el-form-item>`

    case 'select':
      return `<el-form-item label="${label}">
        <el-select v-model="formData.${name}" placeholder="${placeholder}">
          ${(options.optionItems || []).map((opt: any) => `<el-option label="${opt.label}" value="${opt.value}" />`).join('\n')}
        </el-select>
      </el-form-item>`

    case 'radio':
      return `<el-form-item label="${label}">
        <el-radio-group v-model="formData.${name}">
          ${(options.optionItems || []).map((opt: any) => `<el-radio label="${opt.value}">${opt.label}</el-radio>`).join('\n')}
        </el-radio-group>
      </el-form-item>`

    case 'checkbox':
      return `<el-form-item label="${label}">
        <el-checkbox-group v-model="formData.${name}">
          ${(options.optionItems || []).map((opt: any) => `<el-checkbox label="${opt.value}">${opt.label}</el-checkbox>`).join('\n')}
        </el-checkbox-group>
      </el-form-item>`

    case 'date':
      return `<el-form-item label="${label}">
        <el-date-picker v-model="formData.${name}" type="date" placeholder="${placeholder}" />
      </el-form-item>`

    case 'switch':
      return `<el-form-item label="${label}">
        <el-switch v-model="formData.${name}" />
      </el-form-item>`

    case 'slider':
      return `<el-form-item label="${label}">
        <el-slider v-model="formData.${name}" />
      </el-form-item>`

    case 'rate':
      return `<el-form-item label="${label}">
        <el-rate v-model="formData.${name}" />
      </el-form-item>`

    default:
      return `<!-- Unknown field type: ${widget.type} -->`
  }
}

function generateFormMethods(widgetList: any[]): string {
  return ''
}

function generateFormStyles(widgetList: any[], formConfig: any): string {
  let styles = `
.form-container {
  padding: 20px;
}
`

  if (formConfig?.cssCode) {
    styles += `\n${formConfig.cssCode}`
  }

  return styles
}

// Vue SFC Generator
export function generateSFC(formJson: FormJson): string {
  const template = generateSFCTemplate(formJson)
  const script = generateSFCScript(formJson)
  const style = generateSFCStyle(formJson)

  return `${template}

${script}

${style}`
}

function generateSFCTemplate(formJson: FormJson): string {
  return `<template>
  <div class="xform-sfc">
    ${generateFormTemplate(formJson.widgetList)}
  </div>
</template>`
}

function generateSFCScript(formJson: FormJson): string {
  return `<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const formData = reactive(${JSON.stringify(generateFormData(formJson.widgetList), null, 2)})

function submitForm() {
  console.log('Form Data:', formData)
  ElMessage.success('Submit success')
}

function resetForm() {
  Object.keys(formData).forEach(key => {
    formData[key] = null
  })
}
</script>`
}

function generateSFCStyle(formJson: FormJson): string {
  return `<style scoped>
.xform-sfc {
  padding: 20px;
}
</style>`
}
