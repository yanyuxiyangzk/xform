<template>
  <el-radio-group
    v-model="formModel[field.options.name]"
    :disabled="field.options.disabled"
    :size="field.options.size"
    @change="handleChange"
  >
    <el-radio
      v-for="opt in field.options.optionItems"
      :key="opt.value"
      :value="opt.value"
    >
      {{ opt.label }}
    </el-radio>
  </el-radio-group>
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
