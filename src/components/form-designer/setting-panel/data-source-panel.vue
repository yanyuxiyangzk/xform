<template>
  <div class="data-source-panel">
    <el-form :model="optionModel" size="small" label-position="left" label-width="110px" class="ds-form">
      <!-- Data Source Type -->
      <el-form-item :label="t('dsEnabled')">
        <el-switch v-model="optionModel.dsEnabled" @change="onDsEnabledChange" />
      </el-form-item>

      <template v-if="optionModel.dsEnabled">
        <el-divider />

        <!-- Data Source Type Selection -->
        <el-form-item :label="t('dsType')">
          <el-radio-group v-model="optionModel.dsType" @change="onDsTypeChange">
            <el-radio label="static">{{ t('dsTypeStatic') }}</el-radio>
            <el-radio label="api">{{ t('dsTypeApi') }}</el-radio>
            <el-radio label="dataLinkage">{{ t('dsTypeDataLinkage') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- Static Options -->
        <template v-if="optionModel.dsType === 'static'">
          <el-form-item :label="t('optionItems')">
            <div class="static-options">
              <div v-for="(item, index) in optionModel.optionItems" :key="index" class="option-item">
                <el-input v-model="item.label" :placeholder="t('label')" />
                <el-input v-model="item.value" :placeholder="t('value')" />
                <el-button link type="danger" @click="removeOptionItem(index)" :disabled="optionModel.optionItems.length <= 1">
                  {{ t('remove') }}
                </el-button>
              </div>
              <el-button link type="primary" @click="addOptionItem">
                + {{ t('addOption') }}
              </el-button>
            </div>
          </el-form-item>
        </template>

        <!-- API Data Source -->
        <template v-if="optionModel.dsType === 'api'">
          <el-form-item :label="t('dsName')" required>
            <el-select v-model="optionModel.dsName" :placeholder="t('selectDs')" filterable allow-create>
              <el-option
                v-for="ds in globalDataSources"
                :key="ds.id || ds.name"
                :label="ds.name"
                :value="ds.name"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('labelKey')">
            <el-input v-model="optionModel.labelKey" :placeholder="t('labelKeyPlaceholder')" />
          </el-form-item>

          <el-form-item :label="t('valueKey')">
            <el-input v-model="optionModel.valueKey" :placeholder="t('valueKeyPlaceholder')" />
          </el-form-item>

          <el-form-item :label="t('requestMethod')">
            <el-select v-model="optionModel.dsMethod" style="width: 100%">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="DELETE" value="DELETE" />
              <el-option label="PUT" value="PUT" />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('dataPath')">
            <el-input v-model="optionModel.dsDataPath" :placeholder="t('dataPathPlaceholder')" />
          </el-form-item>

          <el-form-item :label="t('paramsMapping')">
            <div class="params-mapping">
              <div v-for="(param, index) in optionModel.dsParams" :key="index" class="param-item">
                <el-input v-model="param.field" :placeholder="t('paramField')" />
                <span class="param-arrow">→</span>
                <el-input v-model="param.target" :placeholder="t('paramTarget')" />
                <el-button link type="danger" @click="removeParam(index)">
                  {{ t('remove') }}
                </el-button>
              </div>
              <el-button link type="primary" @click="addParam">
                + {{ t('addParam') }}
              </el-button>
            </div>
          </el-form-item>
        </template>

        <!-- Data Linkage -->
        <template v-if="optionModel.dsType === 'dataLinkage'">
          <el-form-item :label="t('dataTarget')">
            <el-select v-model="optionModel.dataTarget" :placeholder="t('selectTargetField')" @focus="loadFieldOptions">
              <el-option
                v-for="field in availableFields"
                :key="field.name"
                :label="field.label || field.name"
                :value="field.name"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('linkageType')">
            <el-radio-group v-model="optionModel.linkageType">
              <el-radio label="filter">{{ t('linkageTypeFilter') }}</el-radio>
              <el-radio label="fetch">{{ t('linkageTypeFetch') }}</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item :label="t('targetValueKey')" v-if="optionModel.linkageType === 'fetch'">
            <el-input v-model="optionModel.targetValueKey" :placeholder="t('targetValueKeyPlaceholder')" />
          </el-form-item>

          <el-form-item :label="t('targetLabelKey')" v-if="optionModel.linkageType === 'fetch'">
            <el-input v-model="optionModel.targetLabelKey" :placeholder="t('targetLabelKeyPlaceholder')" />
          </el-form-item>
        </template>
      </template>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'

const props = defineProps<{
  designer: any
  selectedWidget: any
  globalDsv: any
}>()

const optionModel = computed(() => props.selectedWidget?.options || {})

const globalDataSources = computed(() => {
  return props.designer?.formConfig?.dataSources || []
})

const availableFields = computed(() => {
  const fields: any[] = []
  const traverse = (list: any[]) => {
    list.forEach(widget => {
      if (widget.formItemFlag && widget.options?.name && widget.id !== props.selectedWidget?.id) {
        fields.push({
          name: widget.options.name,
          label: widget.options.label,
          type: widget.type
        })
      }
      if (widget.widgetList) {
        traverse(widget.widgetList)
      }
      if (widget.tabs) {
        widget.tabs.forEach((tab: any) => traverse(tab.widgetList || []))
      }
      if (widget.cols) {
        widget.cols.forEach((col: any) => traverse(col.widgetList || []))
      }
      if (widget.rows) {
        widget.rows.forEach((row: any) => row.cols?.forEach((col: any) => traverse(col.widgetList || [])))
      }
    })
  }
  traverse(props.designer?.widgetList || [])
  return fields
})

function t(key: string): string {
  const map: Record<string, string> = {
    'dsEnabled': '启用数据源',
    'dsType': '数据源类型',
    'dsTypeStatic': '静态数据',
    'dsTypeApi': 'API数据源',
    'dsTypeDataLinkage': '数据联动',
    'optionItems': '静态选项',
    'label': '显示文本',
    'value': '对应值',
    'addOption': '添加选项',
    'remove': '删除',
    'dsName': '数据源',
    'selectDs': '选择数据源',
    'labelKey': '标签字段',
    'labelKeyPlaceholder': '如: name, label',
    'valueKey': '值字段',
    'valueKeyPlaceholder': '如: id, value',
    'requestMethod': '请求方式',
    'dataPath': '数据路径',
    'dataPathPlaceholder': '如: data.items',
    'paramsMapping': '参数映射',
    'paramField': '源字段',
    'paramTarget': '目标参数',
    'addParam': '添加映射',
    'dataTarget': '联动目标',
    'selectTargetField': '选择目标字段',
    'linkageType': '联动方式',
    'linkageTypeFilter': '过滤选项',
    'linkageTypeFetch': '获取选项',
    'targetValueKey': '目标值字段',
    'targetValueKeyPlaceholder': '联动字段的值',
    'targetLabelKey': '目标标签字段',
    'targetLabelKeyPlaceholder': '联动字段的标签',
  }
  return map[key] || key
}

function initDsOptions() {
  if (!optionModel.value.dsType) {
    optionModel.value.dsType = 'static'
  }
  if (!optionModel.value.optionItems) {
    optionModel.value.optionItems = [{ label: '', value: '' }]
  }
  if (!optionModel.value.dsParams) {
    optionModel.value.dsParams = []
  }
  if (!optionModel.value.dsMethod) {
    optionModel.value.dsMethod = 'GET'
  }
  if (!optionModel.value.dsDataPath) {
    optionModel.value.dsDataPath = 'data'
  }
  if (!optionModel.value.linkageType) {
    optionModel.value.linkageType = 'filter'
  }
}

function onDsEnabledChange(val: boolean) {
  if (val) {
    initDsOptions()
  }
}

function onDsTypeChange() {
  initDsOptions()
}

function addOptionItem() {
  if (!optionModel.value.optionItems) {
    optionModel.value.optionItems = []
  }
  optionModel.value.optionItems.push({ label: '', value: '' })
}

function removeOptionItem(index: number) {
  optionModel.value.optionItems.splice(index, 1)
}

function addParam() {
  if (!optionModel.value.dsParams) {
    optionModel.value.dsParams = []
  }
  optionModel.value.dsParams.push({ field: '', target: '' })
}

function removeParam(index: number) {
  optionModel.value.dsParams.splice(index, 1)
}

function loadFieldOptions() {
  // Field options are loaded reactively via computed
}

watch(() => props.selectedWidget, (widget) => {
  if (widget && widget.options) {
    initDsOptions()
  }
}, { immediate: true })
</script>

<style lang="scss" scoped>
.data-source-panel {
  padding: 8px;
}

.ds-form {
  :deep(.el-form-item__label) {
    font-size: 13px;
  }

  :deep(.el-form-item--small.el-form-item) {
    margin-bottom: 12px;
  }
}

.static-options {
  width: 100%;

  .option-item {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
    align-items: center;

    .el-input {
      flex: 1;
    }
  }
}

.params-mapping {
  width: 100%;

  .param-item {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
    align-items: center;

    .el-input {
      flex: 1;
    }

    .param-arrow {
      color: #909399;
    }
  }
}

.el-divider {
  margin: 8px 0;
}
</style>
