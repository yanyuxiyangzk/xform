<template>
  <el-form :model="formConfig" size="small" label-position="left" label-width="120px" class="form-setting-form">
    <el-form-item :label="t('modelName')">
      <el-input v-model="formConfig.modelName" />
    </el-form-item>
    <el-form-item :label="t('refName')">
      <el-input v-model="formConfig.refName" />
    </el-form-item>
    <el-form-item :label="t('labelWidth')">
      <el-input-number v-model="formConfig.labelWidth" :min="0" />
    </el-form-item>
    <el-form-item :label="t('labelPosition')">
      <el-select v-model="formConfig.labelPosition">
        <el-option label="Left" value="left" />
        <el-option label="Top" value="top" />
      </el-select>
    </el-form-item>
    <el-form-item :label="t('size')">
      <el-select v-model="formConfig.size" clearable>
        <el-option label="Default" value="" />
        <el-option label="Small" value="small" />
        <el-option label="Large" value="large" />
      </el-select>
    </el-form-item>
    <el-form-item :label="t('layoutType')">
      <el-radio-group v-model="formConfig.layoutType">
        <el-radio label="PC">PC</el-radio>
        <el-radio label="Pad">Pad</el-radio>
        <el-radio label="H5">H5</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item :label="t('cssCode')">
      <el-input v-model="formConfig.cssCode" type="textarea" :rows="4" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
const props = defineProps<{
  designer: any
  formConfig: any
}>()

function t(key: string): string {
  const map: Record<string, string> = {
    'modelName': '数据模型',
    'refName': '引用名称',
    'labelWidth': '标签宽度',
    'labelPosition': '标签位置',
    'size': '组件尺寸',
    'layoutType': '布局类型',
    'cssCode': '自定义CSS',
  }
  return map[key] || key
}
</script>

<style lang="scss" scoped>
.form-setting-form {
  padding: 10px;

  :deep(.el-form-item__label) {
    font-size: 13px;
  }

  :deep(.el-form-item--small.el-form-item) {
    margin-bottom: 12px;
  }
}
</style>
