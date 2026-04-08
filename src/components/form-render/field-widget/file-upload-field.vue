<template>
  <el-upload
    v-model:file-list="fileList"
    :action="field.options.action"
    :accept="field.options.accept"
    :limit="field.options.limit"
    :list-type="field.options.listType || 'text'"
    :with-credentials="field.options.withCredentials"
    :headers="field.options.headers"
    :data="field.options.data"
    :before-upload="handleBeforeUpload"
    :on-success="handleSuccess"
    :on-error="handleError"
    :on-remove="handleRemove"
    :on-preview="handlePreview"
  >
    <el-button size="small" type="primary">{{ uploadText }}</el-button>
  </el-upload>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRefExpose } from './useRefExpose'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
}>()

const { registerRef } = useRefExpose(props)
registerRef(props.field.options.name)

const fileList = ref<any[]>([])
const uploadText = '点击上传'

watch(() => props.field.options.defaultValue, (newVal) => {
  if (newVal && Array.isArray(newVal)) {
    fileList.value = newVal
  }
}, { immediate: true })

watch(fileList, (newVal) => {
  const fieldName = props.field.options.name
  if (props.formModel.hasOwnProperty(fieldName)) {
    props.formModel[fieldName] = newVal
  }
}, { deep: true })

function handleBeforeUpload(file: any) {
  const maxSize = (props.field.options.fileMaxSize || 10) * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${props.field.options.fileMaxSize}MB`)
    return false
  }
  return true
}

function handleSuccess(response: any, file: any, fileList: any[]) {
  updateFileList(fileList)
}

function handleError(err: any, file: any, fileList: any[]) {
  ElMessage.error('上传失败')
}

function handleRemove(file: any, fileList: any[]) {
  updateFileList(fileList)
}

function handlePreview(file: any) {
  // Preview file
}

function updateFileList(list: any[]) {
  fileList.value = list.map(f => ({
    name: f.name,
    url: f.response?.url || f.url,
  }))
}
</script>
