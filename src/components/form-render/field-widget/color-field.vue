<template>
  <el-color-picker
    v-model="value"
    :disabled="field.options.disabled"
    :size="field.options.size"
    :show-alpha="field.options.showAlpha"
    :color-format="field.options.colorFormat"
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
