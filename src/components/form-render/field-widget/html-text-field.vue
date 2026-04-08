<template>
  <div class="html-text" :class="field.options.customClass" v-html="field.options.htmlContent" />
</template>

<script setup lang="ts">
defineProps<{
  field: any
}>()
</script>

<style lang="scss" scoped>
.html-text {
  width: 100%;
}
</style>
