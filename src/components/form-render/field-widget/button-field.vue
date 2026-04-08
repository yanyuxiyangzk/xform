<template>
  <el-button
    :type="field.options.type || 'default'"
    :size="field.options.size"
    :plain="field.options.plain"
    :round="field.options.round"
    :circle="field.options.circle"
    :loading="field.options.loading"
    :disabled="field.options.disabled"
    :icon="field.options.icon"
    @click="handleClick"
  >
    {{ field.options.label }}
  </el-button>
</template>

<script setup lang="ts">
defineProps<{
  field: any
}>()

const emit = defineEmits(['buttonClick'])

function handleClick(event: MouseEvent) {
  if (event.target?.__vueParentComponent?.props?.field?.options?.onClick) {
    try {
      const func = new Function('event', event.target.__vueParentComponent.props.field.options.onClick)
      func(event)
    } catch (e) {
      console.error(e)
    }
  }
  emit('buttonClick', event)
}
</script>
