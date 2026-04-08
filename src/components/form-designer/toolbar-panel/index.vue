<template>
  <div class="toolbar-container">
    <div class="left-toolbar">
      <el-button link :disabled="!undoDisabled" :title="i18nText('designer.toolbar.undoHint')" @click="undoHistory">
        <span>↩</span>
      </el-button>
      <el-button link :disabled="!redoDisabled" :title="i18nText('designer.toolbar.redoHint')" @click="redoHistory">
        <span>↪</span>
      </el-button>
    </div>

    <div class="right-toolbar">
      <el-button link @click="clearFormWidget">{{ i18nText('designer.toolbar.clear') }}</el-button>
      <el-button link @click="previewForm">{{ i18nText('designer.toolbar.preview') }}</el-button>
      <el-button link @click="importJson">{{ i18nText('designer.toolbar.importJson') }}</el-button>
      <el-button link @click="exportJson">{{ i18nText('designer.toolbar.exportJson') }}</el-button>
    </div>

    <!-- Preview Dialog -->
    <el-dialog
      v-model="showPreviewDialogFlag"
      :title="i18nText('designer.toolbar.preview')"
      width="75%"
      center
      destroy-on-close
    >
      <div class="form-preview-wrapper">
        <x-form-render
          ref="preFormRef"
          :form-json="formJson"
          :form-data="testFormData"
          :preview-state="true"
        />
      </div>
      <template #footer>
        <el-button @click="showPreviewDialogFlag = false">{{ i18nText('designer.hint.closePreview') }}</el-button>
        <el-button type="primary" @click="getFormData">{{ i18nText('designer.hint.getFormData') }}</el-button>
      </template>
    </el-dialog>

    <!-- Import JSON Dialog -->
    <el-dialog
      v-model="showImportJsonDialogFlag"
      :title="i18nText('designer.toolbar.importJson')"
      width="60%"
      center
      destroy-on-close
    >
      <el-alert type="info" :title="i18nText('designer.hint.importJsonHint')" show-icon />
      <div class="code-editor-wrapper">
        <textarea v-model="importTemplate" class="json-textarea" />
      </div>
      <template #footer>
        <el-button @click="showImportJsonDialogFlag = false">{{ i18nText('designer.hint.cancel') }}</el-button>
        <el-button type="primary" @click="doJsonImport">{{ i18nText('designer.hint.import') }}</el-button>
      </template>
    </el-dialog>

    <!-- Export JSON Dialog -->
    <el-dialog
      v-model="showExportJsonDialogFlag"
      :title="i18nText('designer.toolbar.exportJson')"
      width="60%"
      center
      destroy-on-close
    >
      <div class="code-editor-wrapper">
        <pre class="json-output">{{ jsonContent }}</pre>
      </div>
      <template #footer>
        <el-button @click="showExportJsonDialogFlag = false">{{ i18nText('designer.hint.closePreview') }}</el-button>
        <el-button type="primary" @click="copyJson">{{ i18nText('designer.hint.copyJson') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { deepClone, generateId, copyToClipboard } from '@/utils/util'
import XFormRender from '@/components/form-render/index.vue'

const props = defineProps<{
  designer: any
  globalDsv: any
}>()

const showPreviewDialogFlag = ref(false)
const showImportJsonDialogFlag = ref(false)
const showExportJsonDialogFlag = ref(false)
const importTemplate = ref('')
const jsonContent = ref('')
const preFormRef = ref()
const testFormData = ref({})

const formJson = computed(() => ({
  widgetList: deepClone(props.designer.widgetList),
  formConfig: deepClone(props.designer.formConfig),
}))

const undoDisabled = computed(() => props.designer.undoEnabled())
const redoDisabled = computed(() => props.designer.redoEnabled())

function i18nText(key: string): string {
  const map: Record<string, string> = {
    'designer.toolbar.undoHint': '撤销',
    'designer.toolbar.redoHint': '重做',
    'designer.toolbar.clear': '清空',
    'designer.toolbar.preview': '预览',
    'designer.toolbar.importJson': '导入JSON',
    'designer.toolbar.exportJson': '导出JSON',
    'designer.hint.cancel': '取消',
    'designer.hint.confirm': '确定',
    'designer.hint.closePreview': '关闭',
    'designer.hint.getFormData': '获取数据',
    'designer.hint.importJsonHint': '请粘贴有效的JSON格式表单配置',
    'designer.hint.copyJson': '复制JSON',
  }
  return map[key] || key
}

function undoHistory() {
  props.designer.undoHistoryStep()
}

function redoHistory() {
  props.designer.redoHistoryStep()
}

function clearFormWidget() {
  props.designer.clearDesigner()
}

function previewForm() {
  showPreviewDialogFlag.value = true
}

function importJson() {
  importTemplate.value = JSON.stringify(props.designer.getImportTemplate(), null, '  ')
  showImportJsonDialogFlag.value = true
}

function doJsonImport() {
  try {
    const importObj = JSON.parse(importTemplate.value)
    if (!importObj || !importObj.formConfig) {
      throw new Error(i18nText('designer.hint.invalidJsonFormat'))
    }
    props.designer.loadFormJson(importObj)
    showImportJsonDialogFlag.value = false
  } catch (ex: any) {
    alert(ex.message)
  }
}

function exportJson() {
  const widgetList = deepClone(props.designer.widgetList)
  const formConfig = deepClone(props.designer.formConfig)
  jsonContent.value = JSON.stringify({ widgetList, formConfig }, null, '  ')
  showExportJsonDialogFlag.value = true
}

function copyJson() {
  copyToClipboard(jsonContent.value, { target: {} }, { success: () => alert('Copied!') }, 'Copied!', 'Failed!')
}

function getFormData() {
  if (preFormRef.value) {
    preFormRef.value.getFormData().then((data: any) => {
      alert(JSON.stringify(data))
    }).catch((error: any) => {
      alert(error)
    })
  }
}
</script>

<style lang="scss" scoped>
.toolbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 10px;
}

.left-toolbar, .right-toolbar {
  display: flex;
  gap: 8px;
}

.right-toolbar {
  :deep(.el-button) {
    margin-left: 10px;
  }
}

.form-preview-wrapper {
  max-height: 60vh;
  overflow-y: auto;
}

.code-editor-wrapper {
  margin-top: 10px;

  .json-textarea {
    width: 100%;
    min-height: 200px;
    font-family: monospace;
    padding: 10px;
    border: 1px solid #DCDFE6;
    border-radius: 4px;
    resize: vertical;
  }

  .json-output {
    background: #f5f7fa;
    padding: 15px;
    border-radius: 4px;
    max-height: 400px;
    overflow: auto;
    white-space: pre-wrap;
    word-break: break-all;
  }
}
</style>
