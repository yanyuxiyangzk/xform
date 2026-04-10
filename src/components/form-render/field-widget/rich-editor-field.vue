<template>
  <div class="rich-editor-wrapper">
    <div ref="editorRef" class="quill-editor" :style="{ minHeight: field.options.minHeight || '200px' }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
}>()

const editorRef = ref<HTMLElement | null>(null)
let quill: Quill | null = null

onMounted(() => {
  if (editorRef.value) {
    quill = new Quill(editorRef.value, {
      theme: 'snow',
      placeholder: props.field.options.placeholder || '请输入内容...',
      readOnly: props.field.options.readonly || false,
    })

    // 设置初始值
    if (props.field.options.defaultValue) {
      quill.root.innerHTML = props.field.options.defaultValue
    }

    // 监听内容变化
    quill.on('text-change', () => {
      const html = quill?.root.innerHTML || ''
      const fieldName = props.field.options.name
      if (props.formModel && fieldName) {
        props.formModel[fieldName] = html
      }
    })
  }
})

onUnmounted(() => {
  quill = null
})

watch(() => props.field.options.defaultValue, (newVal) => {
  if (quill && newVal !== quill.root.innerHTML) {
    quill.root.innerHTML = newVal || ''
  }
})
</script>

<style scoped>
.rich-editor-wrapper {
  width: 100%;
}

.quill-editor {
  min-height: 200px;
}

:deep(.ql-toolbar) {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

:deep(.ql-container) {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  font-size: 14px;
}

:deep(.ql-container.ql-snow) {
  border: 1px solid #dcdfe6;
}

:deep(.ql-toolbar.ql-snow) {
  border: 1px solid #dcdfe6;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
}

:deep(.ql-container.ql-snow) {
  border-radius: 0 0 4px 4px;
}
</style>
