<template>
  <el-switch
    v-model="value"
    :disabled="field.options.disabled"
    :size="field.options.size || 'default'"
    :width="field.options.switchWidth"
    :active-text="field.options.activeText"
    :inactive-text="field.options.inactiveText"
    :active-color="field.options.activeColor"
    :inactive-color="field.options.inactiveColor"
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
