<template>
  <el-form
    :label-position="labelPosition"
    :size="formSize"
    :class="[customClass, readModeFlag ? 'readonly-mode-form' : '']"
    :label-width="labelWidth"
    :validate-on-rule-change="false"
    :model="formDataModel"
    ref="renderFormRef"
    @submit.prevent
  >
    <template v-for="(widget, index) in widgetList" :key="widget.id">
      <ContainerItem
        v-if="widget.category === 'container'"
        :widget="widget"
        :form-model="formDataModel"
        :parent-list="widgetList"
        :index-of-parent-list="index"
        :parent-widget="null"
      />
      <FieldRenderer
        v-else
        :field="widget"
        :form-model="formDataModel"
        :parent-list="widgetList"
        :index-of-parent-list="index"
        :parent-widget="null"
      />
    </template>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, provide, shallowRef } from 'vue'
import { buildDefaultFormJson, deepClone, generateId, traverseAllWidgets } from '@/utils/util'
import { changeLocale } from '@/utils/i18n'
import eventBus from '@/utils/event-bus'
import ContainerItem from './container-item/index.vue'
import FieldRenderer from './field-renderer.vue'

const props = defineProps<{
  formJson?: any
  formData?: any
  optionData?: any
  previewState?: boolean
  globalDsv?: any
}>()

const emit = defineEmits(['formChange', 'appendButtonClick', 'buttonClick'])

const formJsonObj = ref(props.formJson || buildDefaultFormJson())
const formDataModel = reactive<Record<string, any>>({})
const renderFormRef = ref()
const readModeFlag = ref(false)
const widgetRefList = shallowRef<Record<string, any>>({})
const subFormRefList = shallowRef<Record<string, any>>({})

provide('refList', widgetRefList)
provide('sfRefList', subFormRefList)
provide('previewState', props.previewState || false)
provide('getReadMode', () => readModeFlag.value)

const formConfig = computed(() => formJsonObj.value.formConfig)
const widgetList = computed(() => formJsonObj.value.widgetList || [])

const labelPosition = computed(() => formConfig.value?.labelPosition || 'left')
const labelWidth = computed(() => (formConfig.value?.labelWidth || 80) + 'px')
const formSize = computed(() => formConfig.value?.size || 'default')
const customClass = computed(() => formConfig.value?.customClass || '')

function buildFormModel(widgetList: any[]) {
  if (!widgetList || widgetList.length === 0) return

  widgetList.forEach(wItem => {
    buildDataFromWidget(wItem)
  })
}

function buildDataFromWidget(wItem: any) {
  if (wItem.category === 'container') {
    if (wItem.type === 'grid' && wItem.cols) {
      wItem.cols.forEach((col: any) => buildDataFromWidget(col))
    } else if (wItem.type === 'table' && wItem.rows) {
      wItem.rows.forEach((row: any) => {
        row.cols?.forEach((cell: any) => buildDataFromWidget(cell))
      })
    } else if (wItem.type === 'tab' && wItem.tabs) {
      wItem.tabs.forEach((tab: any) => buildDataFromWidget(tab))
    } else if (wItem.type === 'sub-form') {
      const subFormName = wItem.options.name
      if (!formDataModel.hasOwnProperty(subFormName)) {
        if (wItem.options.showBlankRow) {
          const subFormDataRow: Record<string, any> = {}
          wItem.widgetList?.forEach((subItem: any) => {
            if (subItem.formItemFlag) {
              subFormDataRow[subItem.options.name] = subItem.options.defaultValue
            }
          })
          formDataModel[subFormName] = [subFormDataRow]
        } else {
          formDataModel[subFormName] = []
        }
      }
    } else if ((wItem.type === 'grid-col' || wItem.type === 'table-cell') && wItem.widgetList) {
      wItem.widgetList.forEach((child: any) => buildDataFromWidget(child))
    } else if (wItem.widgetList) {
      wItem.widgetList.forEach((child: any) => buildDataFromWidget(child))
    }
  } else if (wItem.formItemFlag) {
    if (!formDataModel.hasOwnProperty(wItem.options.name)) {
      if (props.formData && Object.prototype.hasOwnProperty.call(props.formData, wItem.options.name)) {
        formDataModel[wItem.options.name] = deepClone(props.formData[wItem.options.name])
      } else {
        formDataModel[wItem.options.name] = wItem.options.defaultValue
      }
    }
  }
}

function handleFieldChange(fieldName: string, newValue: any, oldValue: any) {
  emit('formChange', fieldName, newValue, oldValue, formDataModel)

  if (formConfig.value?.onFormDataChange) {
    try {
      const customFunc = new Function('fieldName', 'newValue', 'oldValue', 'formModel', formConfig.value.onFormDataChange)
      customFunc.call(null, fieldName, newValue, oldValue, formDataModel)
    } catch (e) {
      console.error(e)
    }
  }
}

function handleOnCreated() {
  if (formConfig.value?.onFormCreated) {
    try {
      const customFunc = new Function(formConfig.value.onFormCreated)
      customFunc.call(null)
    } catch (e) {
      console.error(e)
    }
  }
}

function handleOnMounted() {
  if (formConfig.value?.onFormMounted) {
    try {
      const customFunc = new Function(formConfig.value.onFormMounted)
      customFunc.call(null)
    } catch (e) {
      console.error(e)
    }
  }
}

function initFormObject() {
  const formId = 'xformRender' + generateId()
  addFieldChangeEventHandler()
  registerFormToRefList()
  handleOnCreated()
}

function addFieldChangeEventHandler() {
  eventBus.on('fieldChange', (params: any[]) => {
    const [fieldName, newValue, oldValue] = params
    handleFieldChange(fieldName, newValue, oldValue)
  })
}

function registerFormToRefList() {
  widgetRefList.value['xform_ref'] = shallowRef({
    getFormData,
    setFormData,
    resetForm,
    validateForm,
    disableForm,
    enableForm,
    setReadMode,
    setFieldValue,
    getFieldValue,
  })
}

function initLocale() {
  const curLocale = localStorage.getItem('xform_locale') || 'zh-CN'
  changeLocale(curLocale as 'zh-CN' | 'en-US')
}

// Public API
function getFormData(needValidation = true): Promise<any> {
  if (!needValidation) {
    return Promise.resolve(deepClone(formDataModel))
  }

  return new Promise((resolve, reject) => {
    renderFormRef.value?.validate((valid: boolean) => {
      if (valid) {
        resolve(deepClone(formDataModel))
      } else {
        reject('Form validation failed')
      }
    })
  })
}

function setFormData(data: Record<string, any>) {
  Object.keys(formDataModel).forEach(propName => {
    if (data && data.hasOwnProperty(propName)) {
      formDataModel[propName] = deepClone(data[propName])
    }
  })
}

function resetForm() {
  Object.keys(formDataModel).forEach(key => {
    const widget = findWidgetByName(key)
    if (widget) {
      formDataModel[key] = deepClone(widget.options.defaultValue)
    }
  })
}

function validateForm(callback: (valid: boolean) => void) {
  renderFormRef.value?.validate((valid: boolean) => {
    callback(valid)
  })
}

function disableForm() {
  Object.keys(widgetRefList.value).forEach(wName => {
    const ref = widgetRefList.value[wName]
    if (ref?.setDisabled) {
      ref.setDisabled(true)
    }
  })
}

function enableForm() {
  Object.keys(widgetRefList.value).forEach(wName => {
    const ref = widgetRefList.value[wName]
    if (ref?.setDisabled) {
      ref.setDisabled(false)
    }
  })
}

function setReadMode(readonly = true) {
  readModeFlag.value = readonly
}

function setFieldValue(fieldName: string, value: any) {
  if (formDataModel.hasOwnProperty(fieldName)) {
    formDataModel[fieldName] = value
  }
}

function getFieldValue(fieldName: string) {
  return formDataModel[fieldName]
}

function findWidgetByName(name: string) {
  let found: any = null
  traverseAllWidgets(widgetList.value, (w) => {
    if (w.options?.name === name) {
      found = w
    }
  })
  return found
}

watch(() => props.formJson, (newVal) => {
  if (newVal) {
    formJsonObj.value = newVal
    Object.keys(formDataModel).forEach(key => delete formDataModel[key])
    buildFormModel(newVal.widgetList)
  }
}, { deep: true })

onMounted(() => {
  buildFormModel(widgetList.value)
  initLocale()
  initFormObject()
  handleOnMounted()
})

defineExpose({
  getFormData,
  setFormData,
  resetForm,
  validateForm,
  disableForm,
  enableForm,
  setReadMode,
  setFieldValue,
  getFieldValue,
  getNativeForm: () => renderFormRef.value,
})
</script>

<style lang="scss" scoped>
.el-form {
  :deep(.el-row) {
    padding: 8px;
  }
}
</style>
