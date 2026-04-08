<template>
  <el-cascader
    v-model="value"
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
import { ref, watch, computed } from 'vue'
import { useRefExpose } from './useRefExpose'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
}>()

const { registerRef } = useRefExpose(props)
registerRef(props.field.options.name)

const value = ref(props.field.options.defaultValue)

const cascaderProps = computed(() => ({
  expandTrigger: 'hover' as const,
  emitPath: false,
  checkStrictly: true,
}))

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
