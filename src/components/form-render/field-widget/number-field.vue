<template>
  <el-input-number
    v-model="value"
    :placeholder="field.options.placeholder"
    :size="field.options.size"
    :disabled="field.options.disabled"
    :readonly="field.options.readonly"
    :min="field.options.min"
    :max="field.options.max"
    :step="field.options.step"
    :precision="field.options.precision"
    :controls="field.options.controls"
    :controls-position="field.options.controlsPosition"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
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

function handleChange(val: any) {}
</script>
