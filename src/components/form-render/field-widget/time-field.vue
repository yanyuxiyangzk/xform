<template>
  <el-time-picker
    v-model="formModel[field.options.name]"
    :placeholder="field.options.placeholder"
    :size="field.options.size"
    :disabled="field.options.disabled"
    :readonly="field.options.readonly"
    :clearable="field.options.clearable"
    :format="field.options.format"
    :value-format="field.options.format"
    :is-range="field.options.isRange"
    :arrow-control="field.options.arrowControl"
    :start-placeholder="field.options.startPlaceholder"
    :end-placeholder="field.options.endPlaceholder"
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
