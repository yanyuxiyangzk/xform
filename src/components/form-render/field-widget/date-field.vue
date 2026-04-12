<template>
  <el-date-picker
    v-model="formModel[field.options.name]"
    :type="field.options.type || 'date'"
    :placeholder="field.options.placeholder"
    :size="field.options.size"
    :disabled="field.options.disabled"
    :readonly="field.options.readonly"
    :clearable="field.options.clearable"
    :format="field.options.format"
    :value-format="field.options.format"
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
