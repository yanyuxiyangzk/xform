<template>
  <el-cascader
    v-model="formModel[field.options.name]"
    :placeholder="field.options.placeholder"
    :size="field.options.size"
    :disabled="field.options.disabled"
    :clearable="field.options.clearable"
    :filterable="field.options.filterable"
    :options="field.options.optionItems"
    :separator="field.options.separator"
    :props="cascaderProps"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRefExpose } from './useRefExpose'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
}>()

const { registerRef } = useRefExpose(props)
registerRef(props.field.options.name)

const cascaderProps = computed(() => ({
  expandTrigger: 'hover' as const,
  emitPath: false,
  checkStrictly: true,
}))

function handleChange(val: any) {}
</script>
