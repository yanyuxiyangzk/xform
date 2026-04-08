<template>
  <el-container class="x-designer-container full-height">
    <el-header class="x-designer-header" v-if="designerConfig.logoHeader !== false">
      <div class="float-left main-title">
        <span class="bold">{{ productName }}</span> {{ productTitle }}
      </div>
      <div class="float-right external-link">
        <el-dropdown v-if="showLink('languageMenu')" :hide-timeout="2000" @command="handleLanguageChanged">
          <span class="el-dropdown-link">{{ curLangName }}<svg-icon icon-class="el-arrow-down"/></span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="zh-CN">{{ i18nText('zh-CN') }}</el-dropdown-item>
              <el-dropdown-item command="en-US">{{ i18nText('en-US') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container>
      <el-aside class="side-panel">
        <widget-panel :designer="designer" />
      </el-aside>

      <el-container class="center-layout-container">
        <el-header class="toolbar-header">
          <toolbar-panel :designer="designer" :global-dsv="globalDsv" ref="toolbarRef">
            <template v-for="(idx, slotName) in $slots" #[slotName]="scope">
              <slot :name="slotName" v-bind="scope" />
            </template>
          </toolbar-panel>
        </el-header>
        <el-main class="form-widget-main">
          <el-scrollbar class="container-scroll-bar" :style="{height: scrollerHeight}">
            <x-form-widget :designer="designer" :form-config="designer.formConfig" :global-dsv="globalDsv" ref="formRef" />
          </el-scrollbar>
        </el-main>
      </el-container>

      <el-aside>
        <setting-panel :designer="designer" :selected-widget="designer.selectedWidget" :global-dsv="globalDsv" :form-config="designer.formConfig" />
      </el-aside>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, provide } from 'vue'
import WidgetPanel from './widget-panel/index.vue'
import ToolbarPanel from './toolbar-panel/index.vue'
import SettingPanel from './setting-panel/index.vue'
import XFormWidget from './form-widget/index.vue'
import { createDesigner } from './designer'
import { addWindowResizeHandler, deepClone } from '@/utils/util'
import { changeLocale } from '@/utils/i18n'

const props = defineProps({
  designerConfig: {
    type: Object,
    default: () => ({
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
    }),
  },
  globalDsv: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['form-json-change'])

const designer = reactive(createDesigner())

const scrollerHeight = ref('0')
const toolbarRef = ref()
const formRef = ref()
const curLangName = ref('中文')
const curLocale = ref('zh-CN')

const productName = computed(() => props.designerConfig.productName || 'XForm')
const productTitle = computed(() => props.designerConfig.productTitle || 'Form Designer')

provide('serverFieldList', [])
provide('getDesignerConfig', () => props.designerConfig)
provide('getBannedWidgets', () => [])

function showLink(configName: string): boolean {
  if (props.designerConfig[configName] === undefined) {
    return true
  }
  return !!props.designerConfig[configName]
}

function i18nText(key: string): string {
  const map: Record<string, string> = {
    'zh-CN': '中文',
    'en-US': 'English',
  }
  return map[key] || key
}

function handleLanguageChanged(command: string) {
  changeLocale(command)
  curLangName.value = i18nText(command)
  curLocale.value = command
}

function initLocale() {
  curLocale.value = localStorage.getItem('xform_locale') || 'zh-CN'
  curLangName.value = i18nText(curLocale.value)
  changeLanguage(curLocale.value)
}

function changeLanguage(langName: string) {
  changeLocale(langName)
}

onMounted(() => {
  initLocale()

  let logoHeaderHeight = props.designerConfig.logoHeader !== false ? 48 : 0
  scrollerHeight.value = window.innerHeight - logoHeaderHeight - 42 + 'px'

  addWindowResizeHandler(() => {
    scrollerHeight.value = window.innerHeight - logoHeaderHeight - 42 + 'px'
  })

  designer.initDesigner(props.designerConfig.resetFormJson)
  designer.loadPresetCssCode(props.designerConfig.presetCssCode)
})

defineExpose({
  getFormJson: () => ({
    widgetList: deepClone(designer.widgetList),
    formConfig: deepClone(designer.formConfig),
  }),
  setFormJson: (formJson: any) => designer.loadFormJson(formJson),
  clearDesigner: () => toolbarRef.value?.clearFormWidget(),
  refreshDesigner: () => {
    const fJson = getFormJson()
    designer.clearDesigner(true)
    designer.loadFormJson(fJson)
  },
  previewForm: () => toolbarRef.value?.previewForm(),
  importJson: () => toolbarRef.value?.importJson(),
  exportJson: () => toolbarRef.value?.exportJson(),
  exportCode: () => toolbarRef.value?.exportCode(),
  generateSFC: () => toolbarRef.value?.generateSFC(),
})
</script>

<style lang="scss" scoped>
.x-designer-container {
  background: #fff;

  :deep(aside) {
    margin: 0;
    padding: 0;
    background: inherit;
  }
}

.full-height {
  height: 100%;
  overflow-y: hidden;
}

.center-layout-container {
  min-width: 680px;
  border-left: 2px dotted #EBEEF5;
  border-right: 2px dotted #EBEEF5;
}

.x-designer-header {
  border-bottom: 2px dotted #EBEEF5;
  height: 48px !important;
  line-height: 48px !important;
  min-width: 800px;
}

.main-title {
  font-size: 18px;
  color: #242424;
  display: flex;
  align-items: center;

  span.bold {
    font-size: 20px;
    font-weight: bold;
    margin: 0 6px;
    color: #667eea;
  }
}

.float-left {
  float: left;
}

.float-right {
  float: right;
}

.el-dropdown-link {
  margin-right: 12px;
  cursor: pointer;
}

.external-link {
  display: flex;
  align-items: center;
  justify-content: center;

  a {
    font-size: 13px;
    text-decoration: none;
    margin-right: 10px;
    color: #606266;
  }
}

.toolbar-header {
  font-size: 14px;
  border-bottom: 1px dotted #CCCCCC;
  height: 42px !important;
}

.side-panel {
  width: 260px !important;
  overflow-y: hidden;
}

.form-widget-main {
  padding: 0;
  position: relative;
  overflow-x: hidden;
}

.container-scroll-bar {
  :deep(.el-scrollbar__wrap), :deep(.el-scrollbar__view) {
    overflow-x: hidden;
  }
}
</style>
