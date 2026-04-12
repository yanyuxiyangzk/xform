<template>
  <el-input-number
    v-model="formModel[field.options.name]"
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
import { watch } from 'vue'
import { useRefExpose } from './useRefExpose'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
}>()

const { registerRef } = useRefExpose(props)
registerRef(props.field.options.name)

function handleChange(val: any) {}
</script>
