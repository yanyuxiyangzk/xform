<template>
  <el-divider
    :direction="field.options.direction || 'horizontal'"
    :content-position="field.options.contentPosition || 'center'"
    :border-style="field.options.borderStyle || 'solid'"
    :color="field.options.color || '#DCDFE6'"
  >
    <span v-if="field.options.label" class="divider-label">{{ field.options.label }}</span>
  </el-divider>
</template>

<script setup lang="ts">
defineProps<{
  field: any
}>()
</script>

<style lang="scss" scoped>
.divider-label {
  font-size: 14px;
  color: #606266;
}
</style>
