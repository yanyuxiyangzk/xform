import { defineStore } from 'pinia'
import { ref, reactive, computed, watch } from 'vue'
import { deepClone, generateId, buildDefaultFormJson } from '@/utils/util'
import eventBus from '@/utils/event-bus'

export const useFormStore = defineStore('form', () => {
  // State
  const formJson = ref<any>(buildDefaultFormJson())
  const formData = reactive<Record<string, any>>({})
  const optionData = ref<any>({})
  const readModeFlag = ref(false)
  const widgetRefList = ref<Record<string, any>>({})
  const subFormRefList = ref<Record<string, any>>({})

  // Getters
  const widgetList = computed(() => formJson.value.widgetList || [])
  const formConfig = computed(() => formJson.value.formConfig || {})
  const labelPosition = computed(() => formConfig.value.labelPosition || 'left')
  const labelWidth = computed(() => (formConfig.value.labelWidth || 80) + 'px')
  const formSize = computed(() => formConfig.value.size || 'default')
  const customClass = computed(() => formConfig.value.customClass || '')

  // Actions
  function setFormJson(json: any) {
    formJson.value = json
    resetFormData()
  }

  function setFormData(data: Record<string, any>) {
    Object.keys(formData).forEach(key => {
      if (data && data.hasOwnProperty(key)) {
        formData[key] = deepClone(data[key])
      }
    })
  }

  function resetFormData() {
    Object.keys(formData).forEach(key => delete formData[key])
    buildFormModel(widgetList.value)
  }

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
        if (!formData.hasOwnProperty(subFormName)) {
          if (wItem.options.showBlankRow) {
            const subFormDataRow: Record<string, any> = {}
            wItem.widgetList?.forEach((subItem: any) => {
              if (subItem.formItemFlag) {
                subFormDataRow[subItem.options.name] = deepClone(subItem.options.defaultValue)
              }
            })
            formData[subFormName] = [subFormDataRow]
          } else {
            formData[subFormName] = []
          }
        }
      } else if ((wItem.type === 'grid-col' || wItem.type === 'table-cell') && wItem.widgetList) {
        wItem.widgetList.forEach((child: any) => buildDataFromWidget(child))
      } else if (wItem.widgetList) {
        wItem.widgetList.forEach((child: any) => buildDataFromWidget(child))
      }
    } else if (wItem.formItemFlag) {
      if (!formData.hasOwnProperty(wItem.options.name)) {
        formData[wItem.options.name] = deepClone(wItem.options.defaultValue)
      }
    }
  }

  function getFormData(needValidation = true): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!needValidation) {
        resolve(deepClone(formData))
        return
      }
      // Validation would be handled by the form component
      resolve(deepClone(formData))
    })
  }

  function validateForm(): Promise<boolean> {
    return new Promise((resolve) => {
      // Validation would be handled by the form component
      resolve(true)
    })
  }

  function resetForm() {
    Object.keys(formData).forEach(key => {
      delete formData[key]
    })
    buildFormModel(widgetList.value)
  }

  function setFieldValue(fieldName: string, value: any) {
    if (formData.hasOwnProperty(fieldName)) {
      formData[fieldName] = value
    }
  }

  function getFieldValue(fieldName: string) {
    return formData[fieldName]
  }

  function setReadMode(readonly = true) {
    readModeFlag.value = readonly
  }

  function setOptionData(data: Record<string, any>) {
    optionData.value = data
  }

  // Field Change Handler
  function handleFieldChange(fieldName: string, newValue: any, oldValue: any) {
    eventBus.emit('fieldChange', [fieldName, newValue, oldValue])

    if (formConfig.value?.onFormDataChange) {
      try {
        const customFunc = new Function('fieldName', 'newValue', 'oldValue', 'formModel', formConfig.value.onFormDataChange)
        customFunc.call(null, fieldName, newValue, oldValue, formData)
      } catch (e) {
        console.error(e)
      }
    }
  }

  // Register Ref
  function registerRef(name: string, ref: any) {
    widgetRefList.value[name] = ref
  }

  function getRef(name: string) {
    return widgetRefList.value[name]
  }

  return {
    // State
    formJson,
    formData,
    optionData,
    readModeFlag,
    widgetRefList,
    subFormRefList,
    // Getters
    widgetList,
    formConfig,
    labelPosition,
    labelWidth,
    formSize,
    customClass,
    // Actions
    setFormJson,
    setFormData,
    resetFormData,
    buildFormModel,
    getFormData,
    validateForm,
    resetForm,
    setFieldValue,
    getFieldValue,
    setReadMode,
    setOptionData,
    handleFieldChange,
    registerRef,
    getRef,
  }
})
