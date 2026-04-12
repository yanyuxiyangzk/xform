<template>
  <el-checkbox-group
    v-model="formModel[field.options.name]"
    :disabled="field.options.disabled"
    :min="field.options.min"
    :max="field.options.max"
    @change="handleChange"
  >
    <el-checkbox
      v-for="opt in field.options.optionItems"
      :key="opt.value"
      :value="opt.value"
    >
      {{ opt.label }}
    </el-checkbox>
  </el-checkbox-group>
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
