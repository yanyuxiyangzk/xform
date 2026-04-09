import { deepClone, generateId, getDefaultFormConfig, overwriteObj, traverseAllWidgets } from '@/utils/util'
import { advancedFields, basicFields, containers, customFields } from './widget-panel/widgetsConfig'
import eventBus from '@/utils/event-bus'

export function createDesigner() {
  const defaultFormConfig = deepClone(getDefaultFormConfig())

  return {
    widgetList: [] as any[],
    formConfig: { cssCode: '' } as any,
    selectedId: null as string | null,
    selectedWidget: null as any,
    selectedWidgetName: null as string | null,
    formWidget: null as any,
    cssClassList: [] as string[],
    historyData: {
      index: -1,
      maxStep: 20,
      steps: [] as any[],
    },

    initDesigner(resetFormJson?: boolean) {
      this.widgetList = []
      this.formConfig = deepClone(defaultFormConfig)
      console.info(`%cXForm %cVer1.0.0 %chttps://xform.dev`,
        "color:#667eea;font-size: 22px;font-weight:bolder",
        "color:#999;font-size: 12px",
        "color:#333"
      )
      if (!resetFormJson) {
        this.initHistoryData()
      }
    },

    clearDesigner(skipHistoryChange?: boolean) {
      const emptyWidgetListFlag = this.widgetList.length === 0
      this.widgetList = []
      this.selectedId = null
      this.selectedWidgetName = null
      this.selectedWidget = {}
      overwriteObj(this.formConfig, defaultFormConfig)

      if (skipHistoryChange) {
        // do nothing
      } else if (!emptyWidgetListFlag) {
        this.emitHistoryChange()
      } else {
        this.saveCurrentHistoryStep()
      }
    },

    loadPresetCssCode(preCssCode: string) {
      if ((this.formConfig.cssCode === '') && !!preCssCode) {
        this.formConfig.cssCode = preCssCode
      }
    },

    getLayoutType(): string {
      return this.formConfig.layoutType || 'PC'
    },

    changeLayoutType(newType: string) {
      this.formConfig.layoutType = newType
    },

    getImportTemplate() {
      return {
        widgetList: [],
        formConfig: deepClone(defaultFormConfig),
      }
    },

    loadFormJson(formJson: any): boolean {
      let modifiedFlag = false
      if (!!formJson && !!formJson.widgetList) {
        this.widgetList = formJson.widgetList
        modifiedFlag = true
      }
      if (!!formJson && !!formJson.formConfig) {
        overwriteObj(this.formConfig, formJson.formConfig)
        modifiedFlag = true
      }
      if (modifiedFlag) {
        this.emitEvent('form-json-imported', [])
      }
      return modifiedFlag
    },

    setSelected(selected: any) {
      if (!selected) {
        this.clearSelected()
        return
      }
      this.selectedWidget = selected
      if (!!selected.id) {
        this.selectedId = selected.id
        this.selectedWidgetName = selected.options.name
      }
    },

    updateSelectedWidgetNameAndLabel(selectedWidget: any, newName: string, newLabel: string) {
      this.selectedWidgetName = newName
      if (!!newLabel && (Object.keys(selectedWidget.options).indexOf('label') > -1)) {
        selectedWidget.options.label = newLabel
      }
    },

    clearSelected() {
      this.selectedId = null
      this.selectedWidgetName = null
      this.selectedWidget = {}
    },

    checkWidgetMove(evt: any): boolean {
      if (!!evt.draggedContext && !!evt.draggedContext.element) {
        const wgCategory = evt.draggedContext.element.category
        if (!!evt.to) {
          if ((evt.to.className === 'sub-form-table') && (wgCategory === 'container')) {
            return false
          }
        }
      }
      return true
    },

    checkFieldMove(evt: any): boolean {
      if (!!evt.draggedContext && !!evt.draggedContext.element) {
        const wgType = evt.draggedContext.element.type + ''
        if (!!evt.to) {
          if ((evt.to.className === 'sub-form-table') && (wgType === 'slot')) {
            return false
          }
        }
      }
      return true
    },

    appendTableRow(widget: any) {
      const rowIdx = widget.rows.length
      const newRow = deepClone(widget.rows[widget.rows.length - 1])
      newRow.id = 'table-row-' + generateId()
      newRow.merged = false
      newRow.cols.forEach((col: any) => {
        col.id = 'table-cell-' + generateId()
        col.options.name = col.id
        col.merged = false
        col.options.colspan = 1
        col.options.rowspan = 1
        col.widgetList.length = 0
      })
      widget.rows.splice(rowIdx, 0, newRow)
      this.emitHistoryChange()
    },

    appendTableCol(widget: any) {
      const colIdx = widget.rows[0].cols.length
      widget.rows.forEach((row: any) => {
        const newCol = deepClone(this.getContainerByType('table-cell'))
        newCol.id = 'table-cell-' + generateId()
        newCol.options.name = newCol.id
        newCol.merged = false
        newCol.options.colspan = 1
        newCol.options.rowspan = 1
        newCol.widgetList.length = 0
        row.cols.splice(colIdx, 0, newCol)
      })
      this.emitHistoryChange()
    },

    insertTableRow(widget: any, insertPos: number, cloneRowIdx: number, curCol: number, aboveFlag: boolean) {
      let newRowIdx = aboveFlag ? insertPos : insertPos + 1
      if (!aboveFlag) {
        let tmpRowIdx = newRowIdx
        let rowFoundFlag = false
        while (tmpRowIdx < widget.rows.length) {
          if (!widget.rows[tmpRowIdx].cols[curCol].merged) {
            newRowIdx = tmpRowIdx
            rowFoundFlag = true
            break
          }
          tmpRowIdx++
        }
        if (!rowFoundFlag) {
          newRowIdx = widget.rows.length
        }
      }

      const newRow = deepClone(widget.rows[cloneRowIdx])
      newRow.id = 'table-row-' + generateId()
      newRow.merged = false
      newRow.cols.forEach((col: any) => {
        col.id = 'table-cell-' + generateId()
        col.options.name = col.id
        col.merged = false
        col.options.colspan = 1
        col.options.rowspan = 1
        col.widgetList.length = 0
      })
      widget.rows.splice(newRowIdx, 0, newRow)
      this.emitHistoryChange()
    },

    insertTableCol(widget: any, insertPos: number, curRow: number, leftFlag: boolean) {
      let newColIdx = leftFlag ? insertPos : insertPos + 1
      if (!leftFlag) {
        let tmpColIdx = newColIdx
        let colFoundFlag = false
        while (tmpColIdx < widget.rows[curRow].cols.length) {
          if (!widget.rows[curRow].cols[tmpColIdx].merged) {
            newColIdx = tmpColIdx
            colFoundFlag = true
            break
          }
          tmpColIdx++
        }
        if (!colFoundFlag) {
          newColIdx = widget.rows[curRow].cols.length
        }
      }

      widget.rows.forEach((row: any) => {
        const newCol = deepClone(this.getContainerByType('table-cell'))
        newCol.id = 'table-cell-' + generateId()
        newCol.options.name = newCol.id
        newCol.merged = false
        newCol.options.colspan = 1
        newCol.options.rowspan = 1
        newCol.widgetList.length = 0
        row.cols.splice(newColIdx, 0, newCol)
      })
      this.emitHistoryChange()
    },

    setPropsOfMergedCols(rowArray: any[], startRowIndex: number, startColIndex: number, newColspan: number, rowspan: number) {
      for (let i = startRowIndex; i < startRowIndex + rowspan; i++) {
        for (let j = startColIndex; j < startColIndex + newColspan; j++) {
          if ((i === startRowIndex) && (j === startColIndex)) {
            rowArray[i].cols[j].options.colspan = newColspan
            continue
          }
          rowArray[i].cols[j].merged = true
          rowArray[i].cols[j].options.colspan = newColspan
          rowArray[i].cols[j].widgetList = []
        }
      }
    },

    setPropsOfMergedRows(rowArray: any[], startRowIndex: number, startColIndex: number, colspan: number, newRowspan: number) {
      for (let i = startRowIndex; i < startRowIndex + newRowspan; i++) {
        for (let j = startColIndex; j < startColIndex + colspan; j++) {
          if ((i === startRowIndex) && (j === startColIndex)) {
            rowArray[i].cols[j].options.rowspan = newRowspan
            continue
          }
          rowArray[i].cols[j].merged = true
          rowArray[i].cols[j].options.rowspan = newRowspan
          rowArray[i].cols[j].widgetList = []
        }
      }
    },

    mergeTableCol(rowArray: any[], colArray: any[], curRow: number, curCol: number, leftFlag: boolean, cellWidget: any) {
      let mergedColIdx = leftFlag ? curCol : curCol + colArray[curCol].options.colspan
      let remainedColIdx = leftFlag ? curCol - 1 : curCol
      if (leftFlag) {
        let tmpColIdx = remainedColIdx
        while (tmpColIdx >= 0) {
          if (!rowArray[curRow].cols[tmpColIdx].merged) {
            remainedColIdx = tmpColIdx
            break
          }
          tmpColIdx--
        }
      }

      if (colArray[mergedColIdx].widgetList && colArray[mergedColIdx].widgetList.length > 0) {
        if (!colArray[remainedColIdx].widgetList || colArray[remainedColIdx].widgetList.length === 0) {
          colArray[remainedColIdx].widgetList = deepClone(colArray[mergedColIdx].widgetList)
        }
      }

      const newColspan = colArray[mergedColIdx].options.colspan * 1 + colArray[remainedColIdx].options.colspan * 1
      this.setPropsOfMergedCols(rowArray, curRow, remainedColIdx, newColspan, cellWidget.options.rowspan)
      this.emitHistoryChange()
    },

    mergeTableRow(rowArray: any[], curRow: number, curCol: number, aboveFlag: boolean, cellWidget: any) {
      let mergedRowIdx = aboveFlag ? curRow : curRow + cellWidget.options.rowspan
      let remainedRowIdx = aboveFlag ? curRow - 1 : curRow
      if (aboveFlag) {
        let tmpRowIdx = remainedRowIdx
        while (tmpRowIdx >= 0) {
          if (!rowArray[tmpRowIdx].cols[curCol].merged) {
            remainedRowIdx = tmpRowIdx
            break
          }
          tmpRowIdx--
        }
      }

      if (rowArray[mergedRowIdx].cols[curCol].widgetList && rowArray[mergedRowIdx].cols[curCol].widgetList.length > 0) {
        if (!rowArray[remainedRowIdx].cols[curCol].widgetList || rowArray[remainedRowIdx].cols[curCol].widgetList.length === 0) {
          rowArray[remainedRowIdx].cols[curCol].widgetList = deepClone(rowArray[mergedRowIdx].cols[curCol].widgetList)
        }
      }

      const newRowspan = rowArray[mergedRowIdx].cols[curCol].options.rowspan * 1 + rowArray[remainedRowIdx].cols[curCol].options.rowspan * 1
      this.setPropsOfMergedRows(rowArray, remainedRowIdx, curCol, cellWidget.options.colspan, newRowspan)
      this.emitHistoryChange()
    },

    getContainerByType(typeName: string) {
      const allWidgets = [...containers, ...basicFields, ...advancedFields, ...customFields]
      let foundCon = null
      allWidgets.forEach(con => {
        if (!!con.category && !!con.type && con.type === typeName) {
          foundCon = con
        }
      })
      return foundCon
    },

    getFieldWidgetByType(typeName: string) {
      const allWidgets = [...containers, ...basicFields, ...advancedFields, ...customFields]
      let foundWidget = null
      allWidgets.forEach(widget => {
        if (!widget.category && widget.type && widget.type === typeName) {
          foundWidget = widget
        }
      })
      return foundWidget
    },

    hasConfig(widget: any, configName: string): boolean {
      let originalWidget = null
      if (!!widget.category) {
        originalWidget = this.getContainerByType(widget.type)
      } else {
        originalWidget = this.getFieldWidgetByType(widget.type)
      }
      if (!originalWidget || !originalWidget.options) {
        return false
      }
      return Object.keys(originalWidget.options).indexOf(configName) > -1
    },

    upgradeWidgetConfig(oldWidget: any) {
      let newWidget = null
      if (!!oldWidget.category) {
        newWidget = this.getContainerByType(oldWidget.type)
      } else {
        newWidget = this.getFieldWidgetByType(oldWidget.type)
      }
      if (!newWidget || !newWidget.options) {
        return
      }
      Object.keys(newWidget.options).forEach(ck => {
        if (!oldWidget.hasOwnProperty(ck)) {
          oldWidget.options[ck] = deepClone(newWidget.options[ck])
        }
      })
    },

    upgradeFormConfig(oldFormConfig: any) {
      Object.keys(this.formConfig).forEach(fc => {
        if (!oldFormConfig.hasOwnProperty(fc)) {
          oldFormConfig[fc] = deepClone(this.formConfig[fc])
        }
      })
    },

    cloneGridCol(widget: any, parentWidget: any) {
      const newGridCol = deepClone(this.getContainerByType('grid-col'))
      newGridCol.options.span = widget.options.span
      const tmpId = generateId()
      newGridCol.id = 'grid-col-' + tmpId
      newGridCol.options.name = 'gridCol' + tmpId
      parentWidget.cols.push(newGridCol)
    },

    cloneContainer(containWidget: any) {
      if (containWidget.type === 'grid') {
        const newGrid = deepClone(this.getContainerByType('grid'))
        newGrid.id = newGrid.type + generateId()
        newGrid.options.name = newGrid.id
        containWidget.cols.forEach((gridCol: any) => {
          const newGridCol = deepClone(this.getContainerByType('grid-col'))
          const tmpId = generateId()
          newGridCol.id = 'grid-col-' + tmpId
          newGridCol.options.name = 'gridCol' + tmpId
          newGridCol.options.span = gridCol.options.span
          newGrid.cols.push(newGridCol)
        })
        return newGrid
      } else if (containWidget.type === 'table') {
        const newTable = deepClone(this.getContainerByType('table'))
        newTable.id = newTable.type + generateId()
        newTable.options.name = newTable.id
        containWidget.rows.forEach((tRow: any) => {
          const newRow = deepClone(tRow)
          newRow.id = 'table-row-' + generateId()
          newRow.cols.forEach((col: any) => {
            col.id = 'table-cell-' + generateId()
            col.options.name = col.id
            col.widgetList = []
          })
          newTable.rows.push(newRow)
        })
        return newTable
      }
      return null
    },

    moveUpWidget(parentList: any[], indexOfParentList: number) {
      if (parentList) {
        if (indexOfParentList === 0) {
          return
        }
        const tempWidget = parentList[indexOfParentList]
        parentList.splice(indexOfParentList, 1)
        parentList.splice(indexOfParentList - 1, 0, tempWidget)
      }
    },

    moveDownWidget(parentList: any[], indexOfParentList: number) {
      if (parentList) {
        if (indexOfParentList === parentList.length - 1) {
          return
        }
        const tempWidget = parentList[indexOfParentList]
        parentList.splice(indexOfParentList, 1)
        parentList.splice(indexOfParentList + 1, 0, tempWidget)
      }
    },

    copyNewFieldWidget(origin: any) {
      const newWidget = deepClone(origin)
      const tempId = generateId()
      newWidget.key = generateId()
      newWidget.id = newWidget.type.replace(/-/g, '') + tempId
      newWidget.options.name = newWidget.id
      newWidget.options.label = newWidget.options.label || newWidget.type.toLowerCase()
      delete newWidget.displayName
      console.log('[xform] clone field widget:', newWidget.type, 'key:', newWidget.key, 'id:', newWidget.id)
      return newWidget
    },

    copyNewContainerWidget(origin: any) {
      const newCon = deepClone(origin)
      newCon.key = generateId()
      newCon.id = newCon.type.replace(/-/g, '') + generateId()
      newCon.options.name = newCon.id
      if (newCon.type === 'grid') {
        const newCol = deepClone(this.getContainerByType('grid-col'))
        const tmpId = generateId()
        newCol.id = 'grid-col-' + tmpId
        newCol.options.name = 'gridCol' + tmpId
        newCon.cols.push(newCol)
        const anotherCol = deepClone(newCol)
        anotherCol.id = 'grid-col-' + generateId()
        anotherCol.options.name = 'gridCol' + generateId()
        newCon.cols.push(anotherCol)
      } else if (newCon.type === 'table') {
        const newRow = { cols: [] }
        newRow.id = 'table-row-' + generateId()
        newRow.merged = false
        const newCell = deepClone(this.getContainerByType('table-cell'))
        newCell.id = 'table-cell-' + generateId()
        newCell.options.name = newCell.id
        newCell.merged = false
        newCell.options.colspan = 1
        newCell.options.rowspan = 1
        newRow.cols.push(newCell)
        newCon.rows.push(newRow)
      } else if (newCon.type === 'tab') {
        const newTabPane = deepClone(this.getContainerByType('tab-pane'))
        newTabPane.id = 'tab-pane-' + generateId()
        newTabPane.options.name = 'tab1'
        newTabPane.options.label = 'tab 1'
        newCon.tabs.push(newTabPane)
      }
      delete newCon.displayName
      return newCon
    },

    addContainerByDbClick(container: any) {
      const newCon = this.copyNewContainerWidget(container)
      this.widgetList.push(newCon)
      this.setSelected(newCon)
    },

    addFieldByDbClick(widget: any) {
      const newWidget = this.copyNewFieldWidget(widget)
      if (!!this.selectedWidget && this.selectedWidget.type === 'tab') {
        let activeTab = this.selectedWidget.tabs[0]
        this.selectedWidget.tabs.forEach((tabPane: any) => {
          if (!!tabPane.options.active) {
            activeTab = tabPane
          }
        })
        activeTab && activeTab.widgetList.push(newWidget)
      } else if (!!this.selectedWidget && !!this.selectedWidget.widgetList) {
        this.selectedWidget.widgetList.push(newWidget)
      } else {
        this.widgetList.push(newWidget)
      }
      this.setSelected(newWidget)
      this.emitHistoryChange()
    },

    deleteColOfGrid(gridWidget: any, colIdx: number) {
      if (gridWidget && gridWidget.cols) {
        gridWidget.cols.splice(colIdx, 1)
      }
    },

    addNewColOfGrid(gridWidget: any) {
      const cols = gridWidget.cols
      const newGridCol = deepClone(this.getContainerByType('grid-col'))
      const tmpId = generateId()
      newGridCol.id = 'grid-col-' + tmpId
      newGridCol.options.name = 'gridCol' + tmpId
      if (cols && cols.length > 0) {
        let spanSum = 0
        cols.forEach((col: any) => {
          spanSum += col.options.span
        })
        if (spanSum >= 24) {
          gridWidget.cols.push(newGridCol)
        } else {
          newGridCol.options.span = (24 - spanSum) > 12 ? 12 : (24 - spanSum)
          gridWidget.cols.push(newGridCol)
        }
      } else {
        gridWidget.cols = [newGridCol]
      }
    },

    addTabPaneOfTabs(tabsWidget: any) {
      const tabPanes = tabsWidget.tabs
      const newTabPane = deepClone(this.getContainerByType('tab-pane'))
      newTabPane.id = 'tab-pane-' + generateId()
      newTabPane.options.name = newTabPane.id
      newTabPane.options.label = 'tab ' + (tabPanes.length + 1)
      tabPanes.push(newTabPane)
    },

    deleteTabPaneOfTabs(tabsWidget: any, tpIdx: number) {
      tabsWidget.tabs.splice(tpIdx, 1)
    },

    emitEvent(evtName: string, evtData: any) {
      eventBus.emit(evtName, evtData)
    },

    handleEvent(evtName: string, callback: (data: any) => void) {
      eventBus.on(evtName, (data) => callback(data))
    },

    setCssClassList(cssClassList: string[]) {
      this.cssClassList = cssClassList
    },

    getCssClassList(): string[] {
      return this.cssClassList
    },

    registerFormWidget(formWidget: any) {
      this.formWidget = formWidget
    },

    initHistoryData() {
      this.loadFormContentFromStorage()
      this.historyData.index++
      this.historyData.steps[this.historyData.index] = {
        widgetList: deepClone(this.widgetList),
        formConfig: deepClone(this.formConfig),
      }
    },

    emitHistoryChange() {
      if (this.historyData.index === this.historyData.maxStep - 1) {
        this.historyData.steps.shift()
      } else {
        this.historyData.index++
      }
      this.historyData.steps[this.historyData.index] = {
        widgetList: deepClone(this.widgetList),
        formConfig: deepClone(this.formConfig),
      }
      this.saveFormContentToStorage()
      if (this.historyData.index < this.historyData.steps.length - 1) {
        this.historyData.steps = this.historyData.steps.slice(0, this.historyData.index + 1)
      }
    },

    saveCurrentHistoryStep() {
      this.historyData.steps[this.historyData.index] = deepClone({
        widgetList: this.widgetList,
        formConfig: this.formConfig,
      })
      this.saveFormContentToStorage()
    },

    undoHistoryStep() {
      if (this.historyData.index !== 0) {
        this.historyData.index--
      }
      this.widgetList = deepClone(this.historyData.steps[this.historyData.index].widgetList)
      this.formConfig = deepClone(this.historyData.steps[this.historyData.index].formConfig)
    },

    redoHistoryStep() {
      if (this.historyData.index !== this.historyData.steps.length - 1) {
        this.historyData.index++
      }
      this.widgetList = deepClone(this.historyData.steps[this.historyData.index].widgetList)
      this.formConfig = deepClone(this.historyData.steps[this.historyData.index].formConfig)
    },

    undoEnabled(): boolean {
      return (this.historyData.index > 0) && (this.historyData.steps.length > 0)
    },

    redoEnabled(): boolean {
      return this.historyData.index < this.historyData.steps.length - 1
    },

    saveFormContentToStorage() {
      window.localStorage.setItem('xform_widget_list_backup', JSON.stringify(this.widgetList))
      window.localStorage.setItem('xform_config_backup', JSON.stringify(this.formConfig))
    },

    loadFormContentFromStorage() {
      const widgetListBackup = window.localStorage.getItem('xform_widget_list_backup')
      if (widgetListBackup) {
        this.widgetList = JSON.parse(widgetListBackup)
      }
      const formConfigBackup = window.localStorage.getItem('xform_config_backup')
      if (formConfigBackup) {
        overwriteObj(this.formConfig, JSON.parse(formConfigBackup))
      }
    },

    /* ==================== Data Source Methods ==================== */

    getDataSourceByName(dsName: string): any {
      if (!dsName || !this.formConfig.dataSources) {
        return null
      }
      return this.formConfig.dataSources.find((ds: any) => ds.name === dsName) || null
    },

    getWidgetDataSource(widget: any): any {
      if (!widget || !widget.options) {
        return null
      }
      const opts = widget.options
      if (!opts.dsEnabled) {
        return null
      }

      return {
        type: opts.dsType,
        dsName: opts.dsName,
        labelKey: opts.labelKey || 'label',
        valueKey: opts.valueKey || 'value',
        method: opts.dsMethod || 'GET',
        dataPath: opts.dsDataPath || 'data',
        params: opts.dsParams || [],
        optionItems: opts.optionItems || [],
        dataTarget: opts.dataTarget,
        linkageType: opts.linkageType || 'filter',
        targetValueKey: opts.targetValueKey,
        targetLabelKey: opts.targetLabelKey,
      }
    },

    async fetchDataSourceData(dsConfig: any): Promise<any[]> {
      if (!dsConfig || dsConfig.type !== 'api' || !dsConfig.dsName) {
        return []
      }

      const dataSource = this.getDataSourceByName(dsConfig.dsName)
      if (!dataSource) {
        console.warn(`Data source "${dsConfig.dsName}" not found`)
        return []
      }

      try {
        const method = dataSource.method || 'GET'
        const url = dataSource.url
        let options: RequestInit = {
          method,
          headers: {
            'Content-Type': 'application/json',
          },
        }

        if (method === 'GET' && dataSource.params) {
          const params = new URLSearchParams()
          dataSource.params.forEach((p: any) => {
            if (p.name && p.value) {
              params.append(p.name, p.value)
            }
          })
          const queryString = params.toString()
          if (queryString) {
            // URL already contains query string check
          }
        } else if (method === 'POST' && dataSource.data) {
          options.body = JSON.stringify(dataSource.data)
        }

        const response = await fetch(url, options)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const result = await response.json()
        const dataPath = dataSource.dataPath || 'data'
        const pathParts = dataPath.split('.')
        let data = result
        for (const part of pathParts) {
          data = data?.[part]
        }

        if (Array.isArray(data)) {
          return data.map((item: any) => ({
            label: item[dataSource.labelKey || 'label'] || item.name || '',
            value: item[dataSource.valueKey || 'value'] || item.id || '',
          }))
        }

        return []
      } catch (error) {
        console.error('Failed to fetch data source:', error)
        return []
      }
    },

    getLinkedWidget(widget: any): any {
      if (!widget || !widget.options || !widget.options.dsEnabled) {
        return null
      }

      const dsConfig = this.getWidgetDataSource(widget)
      if (!dsConfig || dsConfig.type !== 'dataLinkage' || !dsConfig.dataTarget) {
        return null
      }

      return this.findWidgetByName(dsConfig.dataTarget)
    },

    findWidgetByName(name: string): any {
      let found: any = null
      const traverse = (list: any[]) => {
        for (const w of list) {
          if (w.options?.name === name) {
            found = w
            return
          }
          if (w.widgetList) {
            traverse(w.widgetList)
          }
          if (w.tabs) {
            w.tabs.forEach((tab: any) => traverse(tab.widgetList || []))
          }
          if (w.cols) {
            w.cols.forEach((col: any) => traverse(col.widgetList || []))
          }
          if (w.rows) {
            w.rows.forEach((row: any) => row.cols?.forEach((col: any) => traverse(col.widgetList || [])))
          }
        }
      }
      traverse(this.widgetList)
      return found
    },

    getLinkedOptions(widget: any, targetValue: any): any[] {
      const linkedWidget = this.getLinkedWidget(widget)
      if (!linkedWidget) {
        return []
      }

      const dsConfig = this.getWidgetDataSource(linkedWidget)
      if (!dsConfig) {
        // Use static options
        return linkedWidget.options?.optionItems || linkedWidget.options?.options || []
      }

      if (dsConfig.type === 'static') {
        return dsConfig.optionItems || []
      }

      if (dsConfig.type === 'api') {
        // Return empty array and let the component handle async fetch
        return []
      }

      return []
    },

    initWidgetOptionsFromDataSource(widget: any, dataSource: any): any[] {
      if (!widget || !dataSource) {
        return []
      }

      if (dataSource.type === 'static') {
        return dataSource.optionItems || []
      }

      if (dataSource.type === 'api') {
        // Return empty and let the component do the fetch
        return []
      }

      return []
    },
  }
}
