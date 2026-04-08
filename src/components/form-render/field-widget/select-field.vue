<template>
  <el-select
    v-model="value"
    :placeholder="field.options.placeholder"
    :size="field.options.size"
    :disabled="field.options.disabled"
    :clearable="field.options.clearable"
    :filterable="field.options.filterable"
    :allow-create="field.options.allowCreate"
    :default-first-option="field.options.defaultFirstOption"
    :multiple="field.options.multiple"
    :multiple-limit="field.options.multipleLimit || 0"
    @change="handleChange"
  >
    <el-option
      v-for="opt in field.options.optionItems"
      :key="opt.value"
      :label="opt.label"
      :value="opt.value"
    />
  </el-select>
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
