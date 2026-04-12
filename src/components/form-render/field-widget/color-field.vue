<template>
  <el-color-picker
    v-model="formModel[field.options.name]"
    :disabled="field.options.disabled"
    :size="field.options.size"
    :show-alpha="field.options.showAlpha"
    :color-format="field.options.colorFormat"
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
