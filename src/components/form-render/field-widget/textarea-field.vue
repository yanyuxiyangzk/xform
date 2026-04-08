<template>
  <el-input
    v-model="value"
    type="textarea"
    :placeholder="field.options.placeholder"
    :rows="field.options.rows || 4"
    :cols="field.options.cols || 30"
    :disabled="field.options.disabled"
    :readonly="field.options.readonly"
    :maxlength="field.options.maxLength"
    :show-word-limit="field.options.showWordLimit"
    @input="handleInput"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
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

function handleInput(val: any) {}
function handleChange(val: any) {}
</script>
