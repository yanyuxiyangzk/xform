<template>
  <el-switch
    v-model="formModel[field.options.name]"
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
