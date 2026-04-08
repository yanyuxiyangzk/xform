<template>
  <el-config-provider :locale="elLocale">
    <div id="app">
      <x-form-designer :designer-config="designerConfig" />
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElConfigProvider } from 'element-plus'
import zhCnLang from 'element-plus/es/locale/lang/zh-cn'
import enLang from 'element-plus/es/locale/lang/en'
import XFormDesigner from './components/form-designer/index.vue'

const designerConfig = {
  languageMenu: true,
  externalLink: true,
  formTemplates: true,
  eventCollapse: true,
  widgetNameReadonly: true,
  clearDesignerButton: true,
  previewFormButton: true,
  importJsonButton: true,
  exportJsonButton: true,
  exportCodeButton: true,
  generateSFCButton: true,
  dataSourceButton: false,
  logoHeader: true,
  toolbarMaxWidth: 420,
  toolbarMinWidth: 300,
  productName: 'XForm',
  productTitle: 'Form Designer',
  presetCssCode: '',
  languageName: 'zh-CN',
  resetFormJson: false,
}

const elLocaleMap = {
  'zh-CN': zhCnLang,
  'en-US': enLang,
}

const elLocale = computed(() => {
  const curLocale = localStorage.getItem('xform_locale') || 'zh-CN'
  return elLocaleMap[curLocale]
})
</script>

<style lang="scss">
#app {
  height: 100%;
}
</style>
