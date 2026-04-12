<template>
  <el-upload
    v-model:file-list="formModel[field.options.name]"
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
import { watch } from 'vue'
import { useRefExpose } from './useRefExpose'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
}>()

const { registerRef } = useRefExpose(props)
registerRef(props.field.options.name)

const uploadText = '点击上传'

function handleBeforeUpload(file: any) {
  const maxSize = (props.field.options.fileMaxSize || 10) * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${props.field.options.fileMaxSize}MB`)
    return false
  }
  return true
}

function handleSuccess(response: any, file: any, fileList: any[]) {
  // File list is automatically updated via v-model
}

function handleError(err: any, file: any, fileList: any[]) {
  ElMessage.error('上传失败')
}

function handleRemove(file: any, fileList: any[]) {
  // File list is automatically updated via v-model
}

function handlePreview(file: any) {
  // Preview file
}
</script>
