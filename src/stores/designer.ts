import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { deepClone, generateId, getDefaultFormConfig, overwriteObj } from '@/utils/util'
import eventBus from '@/utils/event-bus'

export const useDesignerStore = defineStore('designer', () => {
  // State
  const widgetList = ref<any[]>([])
  const formConfig = ref<any>(deepClone(getDefaultFormConfig()))
  const selectedId = ref<string | null>(null)
  const selectedWidget = ref<any>(null)
  const selectedWidgetName = ref<string | null>(null)
  const formWidget = ref<any>(null)
  const cssClassList = ref<string[]>([])
  const historyData = ref({
    index: -1,
    maxStep: 20,
    steps: [] as any[],
  })

  // Getters
  const hasSelected = computed(() => selectedId.value !== null)
  const canUndo = computed(() => historyData.value.index > 0)
  const canRedo = computed(() => historyData.value.index < historyData.value.steps.length - 1)

  // Actions
  function initDesigner(resetFormJson?: boolean) {
    widgetList.value = []
    formConfig.value = deepClone(getDefaultFormConfig())
    console.info(`%cXForm %cVer1.0.0 %chttps://xform.dev`,
      "color:#667eea;font-size: 22px;font-weight:bolder",
      "color:#999;font-size: 12px",
      "color:#333"
    )
    if (!resetFormJson) {
      initHistoryData()
    }
  }

  function clearDesigner(skipHistoryChange?: boolean) {
    const emptyWidgetListFlag = widgetList.value.length === 0
    widgetList.value = []
    selectedId.value = null
    selectedWidgetName.value = null
    selectedWidget.value = {}
    overwriteObj(formConfig.value, getDefaultFormConfig())

    if (skipHistoryChange) {
      // do nothing
    } else if (!emptyWidgetListFlag) {
      emitHistoryChange()
    } else {
      saveCurrentHistoryStep()
    }
  }

  function setSelected(selected: any) {
    if (!selected) {
      clearSelected()
      return
    }
    selectedWidget.value = selected
    if (!!selected.id) {
      selectedId.value = selected.id
      selectedWidgetName.value = selected.options?.name
    }
  }

  function clearSelected() {
    selectedId.value = null
    selectedWidgetName.value = null
    selectedWidget.value = {}
  }

  function loadFormJson(formJson: any): boolean {
    let modifiedFlag = false
    if (!!formJson && !!formJson.widgetList) {
      widgetList.value = formJson.widgetList
      modifiedFlag = true
    }
    if (!!formJson && !!formJson.formConfig) {
      overwriteObj(formConfig.value, formJson.formConfig)
      modifiedFlag = true
    }
    if (modifiedFlag) {
      emitEvent('form-json-imported', [])
    }
    return modifiedFlag
  }

  function copyNewFieldWidget(origin: any) {
    const newWidget = deepClone(origin)
    const tempId = generateId()
    newWidget.key = generateId()
    newWidget.id = newWidget.type.replace(/-/g, '') + tempId
    newWidget.options.name = newWidget.id
    newWidget.options.label = newWidget.options.label || newWidget.type.toLowerCase()
    delete newWidget.displayName
    return newWidget
  }

  function copyNewContainerWidget(origin: any) {
    const newCon = deepClone(origin)
    newCon.key = generateId()
    newCon.id = newCon.type.replace(/-/g, '') + generateId()
    newCon.options.name = newCon.id
    delete newCon.displayName
    return newCon
  }

  function addFieldByDbClick(widget: any) {
    const newWidget = copyNewFieldWidget(widget)
    if (!!selectedWidget.value && selectedWidget.value.type === 'tab') {
      let activeTab = selectedWidget.value.tabs?.[0]
      selectedWidget.value.tabs?.forEach((tabPane: any) => {
        if (!!tabPane.options?.active) {
          activeTab = tabPane
        }
      })
      activeTab?.widgetList?.push(newWidget)
    } else if (!!selectedWidget.value?.widgetList) {
      selectedWidget.value.widgetList.push(newWidget)
    } else {
      widgetList.value.push(newWidget)
    }
    setSelected(newWidget)
    emitHistoryChange()
  }

  function addContainerByDbClick(container: any) {
    const newCon = copyNewContainerWidget(container)
    widgetList.value.push(newCon)
    setSelected(newCon)
  }

  // History Management
  function initHistoryData() {
    loadFormContentFromStorage()
    historyData.value.index++
    historyData.value.steps[historyData.value.index] = {
      widgetList: deepClone(widgetList.value),
      formConfig: deepClone(formConfig.value),
    }
  }

  function emitHistoryChange() {
    if (historyData.value.index === historyData.value.maxStep - 1) {
      historyData.value.steps.shift()
    } else {
      historyData.value.index++
    }
    historyData.value.steps[historyData.value.index] = {
      widgetList: deepClone(widgetList.value),
      formConfig: deepClone(formConfig.value),
    }
    saveFormContentToStorage()
    if (historyData.value.index < historyData.value.steps.length - 1) {
      historyData.value.steps = historyData.value.steps.slice(0, historyData.value.index + 1)
    }
  }

  function saveCurrentHistoryStep() {
    historyData.value.steps[historyData.value.index] = deepClone({
      widgetList: widgetList.value,
      formConfig: formConfig.value,
    })
    saveFormContentToStorage()
  }

  function undoHistoryStep() {
    if (historyData.value.index !== 0) {
      historyData.value.index--
    }
    widgetList.value = deepClone(historyData.value.steps[historyData.value.index].widgetList)
    formConfig.value = deepClone(historyData.value.steps[historyData.value.index].formConfig)
  }

  function redoHistoryStep() {
    if (historyData.value.index !== historyData.value.steps.length - 1) {
      historyData.value.index++
    }
    widgetList.value = deepClone(historyData.value.steps[historyData.value.index].widgetList)
    formConfig.value = deepClone(historyData.value.steps[historyData.value.index].formConfig)
  }

  function undoEnabled(): boolean {
    return (historyData.value.index > 0) && (historyData.value.steps.length > 0)
  }

  function redoEnabled(): boolean {
    return historyData.value.index < historyData.value.steps.length - 1
  }

  // LocalStorage
  function saveFormContentToStorage() {
    window.localStorage.setItem('xform_widget_list_backup', JSON.stringify(widgetList.value))
    window.localStorage.setItem('xform_config_backup', JSON.stringify(formConfig.value))
  }

  function loadFormContentFromStorage() {
    const widgetListBackup = window.localStorage.getItem('xform_widget_list_backup')
    if (widgetListBackup) {
      widgetList.value = JSON.parse(widgetListBackup)
    }
    const formConfigBackup = window.localStorage.getItem('xform_config_backup')
    if (formConfigBackup) {
      overwriteObj(formConfig.value, JSON.parse(formConfigBackup))
    }
  }

  // Event
  function emitEvent(evtName: string, evtData: any) {
    eventBus.emit(evtName, evtData)
  }

  function handleEvent(evtName: string, callback: (data: any) => void) {
    eventBus.on(evtName, (data) => callback(data))
  }

  return {
    // State
    widgetList,
    formConfig,
    selectedId,
    selectedWidget,
    selectedWidgetName,
    formWidget,
    cssClassList,
    historyData,
    // Getters
    hasSelected,
    canUndo,
    canRedo,
    // Actions
    initDesigner,
    clearDesigner,
    setSelected,
    clearSelected,
    loadFormJson,
    copyNewFieldWidget,
    copyNewContainerWidget,
    addFieldByDbClick,
    addContainerByDbClick,
    undoHistoryStep,
    redoHistoryStep,
    undoEnabled,
    redoEnabled,
    saveCurrentHistoryStep,
    emitHistoryChange,
    emitEvent,
    handleEvent,
  }
})
