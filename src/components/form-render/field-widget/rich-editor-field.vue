<template>
  <div class="rich-editor-wrapper">
    <quill-editor
      v-model:content="value"
      :placeholder="field.options.placeholder"
      :read-only="field.options.readonly"
      :theme="'snow'"
      :style="{ minHeight: field.options.minHeight || '200px' }"
      @change="handleChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { quillEditor } from 'vue3-quill'
import { useRefExpose } from './useRefExpose'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
}>()

const { registerRef } = useRefExpose(props)
registerRef(props.field.options.name)

const value = ref(props.field.options.defaultValue)

watch(() => props.field.options.defaultValue, (newVal) => {
  value.value = newVal
})

watch(value, (newVal) => {
  const fieldName = props.field.options.name
  if (props.formModel.hasOwnProperty(fieldName)) {
    props.formModel[fieldName] = newVal
  }
})

function handleChange(content: any) {}
</script>

<style>
.ql-container {
  min-height: 200px;
}
</style>
