<template>
  <el-container class="panel-container">
    <el-tabs v-model="activeTab" style="height: 100%; width: 100%; overflow: hidden">
      <el-tab-pane :label="i18nText('designer.hint.widgetSetting')" name="1">
        <el-scrollbar class="setting-scrollbar" :style="{height: scrollerHeight}">
          <template v-if="selectedWidget">
            <el-form :model="optionModel" size="small" label-position="left" label-width="100px" class="setting-form">
              <el-collapse v-model="collapseNames" class="setting-collapse">
                <el-collapse-item name="1" :title="i18nText('designer.setting.commonSetting')">
                  <el-form-item :label="t('label')" v-if="hasOption('label')">
                    <el-input v-model="optionModel.label" @input="updateOption('label', optionModel.label)" />
                  </el-form-item>
                  <el-form-item :label="t('name')" v-if="hasOption('name')">
                    <el-input v-model="optionModel.name" @input="updateOption('name', optionModel.name)" />
                  </el-form-item>
                  <el-form-item :label="t('placeholder')" v-if="hasOption('placeholder')">
                    <el-input v-model="optionModel.placeholder" @input="updateOption('placeholder', optionModel.placeholder)" />
                  </el-form-item>
                  <el-form-item :label="t('defaultValue')" v-if="hasOption('defaultValue')">
                    <el-input v-model="optionModel.defaultValue" @input="updateOption('defaultValue', optionModel.defaultValue)" />
                  </el-form-item>
                  <el-form-item :label="t('disabled')" v-if="hasOption('disabled')">
                    <el-switch v-model="optionModel.disabled" @change="updateOption('disabled', optionModel.disabled)" />
                  </el-form-item>
                  <el-form-item :label="t('hidden')" v-if="hasOption('hidden')">
                    <el-switch v-model="optionModel.hidden" @change="updateOption('hidden', optionModel.hidden)" />
                  </el-form-item>
                  <el-form-item :label="t('required')" v-if="hasOption('required')">
                    <el-switch v-model="optionModel.required" @change="updateOption('required', optionModel.required)" />
                  </el-form-item>
                  <el-form-item :label="t('readonly')" v-if="hasOption('readonly')">
                    <el-switch v-model="optionModel.readonly" @change="updateOption('readonly', optionModel.readonly)" />
                  </el-form-item>
                  <el-form-item :label="t('clearable')" v-if="hasOption('clearable')">
                    <el-switch v-model="optionModel.clearable" @change="updateOption('clearable', optionModel.clearable)" />
                  </el-form-item>
                </el-collapse-item>

                <el-collapse-item name="2" :title="i18nText('designer.setting.advancedSetting')">
                  <el-form-item :label="t('customClass')" v-if="hasOption('customClass')">
                    <el-input v-model="optionModel.customClass" @input="updateOption('customClass', optionModel.customClass)" />
                  </el-form-item>
                  <el-form-item :label="t('labelWidth')" v-if="hasOption('labelWidth')">
                    <el-input-number v-model="optionModel.labelWidth" @change="updateOption('labelWidth', optionModel.labelWidth)" />
                  </el-form-item>
                  <el-form-item :label="t('labelHidden')" v-if="hasOption('labelHidden')">
                    <el-switch v-model="optionModel.labelHidden" @change="updateOption('labelHidden', optionModel.labelHidden)" />
                  </el-form-item>
                </el-collapse-item>
              </el-collapse>
            </el-form>
          </template>

          <template v-else>
            <el-empty :description="i18nText('designer.hint.noSelectedWidgetHint')" />
          </template>
        </el-scrollbar>
      </el-tab-pane>

      <el-tab-pane :label="i18nText('designer.hint.dataSourceSetting')" name="3">
        <el-scrollbar class="setting-scrollbar" :style="{height: scrollerHeight}">
          <template v-if="selectedWidget">
            <data-source-panel
              :designer="designer"
              :selected-widget="selectedWidget"
              :global-dsv="globalDsv"
            />
          </template>
          <template v-else>
            <el-empty :description="i18nText('designer.hint.noSelectedWidgetHint')" />
          </template>
        </el-scrollbar>
      </el-tab-pane>

      <el-tab-pane :label="i18nText('designer.hint.formSetting')" name="2">
        <el-scrollbar class="setting-scrollbar" :style="{height: scrollerHeight}">
          <form-setting :designer="designer" :form-config="formConfig" />
        </el-scrollbar>
      </el-tab-pane>
    </el-tabs>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import FormSetting from './form-setting.vue'
import DataSourcePanel from './data-source-panel.vue'

const props = defineProps<{
  designer: any
  selectedWidget: any
  formConfig: any
  globalDsv: any
}>()

const activeTab = ref('1')
const scrollerHeight = ref('0')
const collapseNames = ref(['1', '2'])

const optionModel = computed(() => props.selectedWidget?.options || {})

function i18nText(key: string): string {
  const map: Record<string, string> = {
    'designer.hint.widgetSetting': '组件配置',
    'designer.hint.formSetting': '表单设置',
    'designer.hint.dataSourceSetting': '数据源',
    'designer.hint.noSelectedWidgetHint': '请选择组件',
    'designer.setting.commonSetting': '公共属性',
    'designer.setting.advancedSetting': '高级属性',
    'label': '标签',
    'name': '字段名',
    'placeholder': '占位符',
    'defaultValue': '默认值',
    'disabled': '禁用',
    'hidden': '隐藏',
    'required': '必填',
    'readonly': '只读',
    'clearable': '可清除',
    'customClass': '自定义类',
    'labelWidth': '标签宽度',
    'labelHidden': '隐藏标签',
  }
  return map[key] || key
}

function t(key: string): string {
  return i18nText(key)
}

function hasOption(optionName: string): boolean {
  return props.selectedWidget?.options?.hasOwnProperty(optionName) || false
}

function updateOption(optionName: string, value: any) {
  if (props.selectedWidget && props.selectedWidget.options) {
    props.designer.saveCurrentHistoryStep()
  }
}

watch(() => props.designer.selectedWidget, (val) => {
  if (val) {
    activeTab.value = '1'
  }
})

onMounted(() => {
  scrollerHeight.value = window.innerHeight - 56 - 48 + 'px'
})
</script>

<style lang="scss" scoped>
.panel-container {
  padding: 0 8px;
}

.setting-scrollbar {
  :deep(.el-scrollbar__wrap) {
    overflow-x: hidden;
  }
}

.setting-collapse {
  :deep(.el-collapse-item__content) {
    padding-bottom: 6px;
  }

  :deep(.el-collapse-item__header) {
    font-style: italic;
    font-weight: bold;
  }
}

.setting-form {
  :deep(.el-form-item__label) {
    font-size: 13px;
    overflow: hidden;
    white-space: nowrap;
  }

  :deep(.el-form-item--small.el-form-item) {
    margin-bottom: 10px;
  }
}
</style>
