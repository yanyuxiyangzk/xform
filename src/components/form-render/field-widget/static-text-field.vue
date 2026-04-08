<template>
  <component
    :is="field.options.tag || 'span'"
    class="static-text"
    :class="field.options.customClass"
    v-html="field.options.textContent"
  />
</template>

<script setup lang="ts">
defineProps<{
  field: any
}>()
</script>

<style lang="scss" scoped>
.static-text {
  display: inline-block;
}
</style>
