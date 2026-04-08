import Clipboard from 'clipboard'

export function isNull(value: any): boolean {
  return value === null || value === undefined
}

export function isNotNull(value: any): boolean {
  return value !== null && value !== undefined
}

export function isEmptyStr(str: any): boolean {
  return str === undefined || (!str && str !== 0 && str !== '0') || !/[^\s]/.test(str)
}

export function isEmptyObj(obj: any): boolean {
  return obj === undefined || Object.keys(obj).length === 0
}

export function isTable(type: string): boolean {
  const tables = ['edit-table', 'data-table']
  return tables.includes(type)
}

export function generateId(): number {
  return Math.floor(Math.random() * 100000 + Math.random() * 20000 + Math.random() * 5000)
}

export function deepClone<T>(origin: T): T {
  if (origin === undefined) {
    return undefined as T
  }
  return JSON.parse(JSON.stringify(origin))
}

export function overwriteObj(obj1: any, obj2: any): void {
  Object.keys(obj2).forEach(prop => {
    obj1[prop] = obj2[prop]
  })
}

export function addWindowResizeHandler(handler: () => void): void {
  const oldHandler = (window as any).onresize
  if (typeof (window as any).onresize !== 'function') {
    (window as any).onresize = handler
  } else {
    (window as any).onresize = function () {
      oldHandler()
      handler()
    }
  }
}

export function insertCustomCssToHead(cssCode: string, formId: string = ''): void {
  const head = document.getElementsByTagName('head')[0]
  let oldStyle = document.getElementById('xform-custom-css')
  if (oldStyle) {
    head.removeChild(oldStyle)
  }
  if (formId) {
    oldStyle = document.getElementById('xform-custom-css' + '-' + formId)
    oldStyle && head.removeChild(oldStyle)
  }

  const newStyle = document.createElement('style')
  newStyle.type = 'text/css'
  newStyle.rel = 'stylesheet'
  newStyle.id = formId ? 'xform-custom-css' + '-' + formId : 'xform-custom-css'
  try {
    newStyle.appendChild(document.createTextNode(cssCode))
  } catch (ex) {
    (newStyle as any).styleSheet.cssText = cssCode
  }
  head.appendChild(newStyle)
}

export function insertGlobalFunctionsToHtml(functionsCode: string, formId: string = ''): void {
  const bodyEle = document.getElementsByTagName('body')[0]
  let oldScriptEle = document.getElementById('xform_global_functions')
  oldScriptEle && bodyEle.removeChild(oldScriptEle)
  if (formId) {
    oldScriptEle = document.getElementById('xform_global_functions' + '-' + formId)
    oldScriptEle && bodyEle.removeChild(oldScriptEle)
  }

  const newScriptEle = document.createElement('script')
  newScriptEle.id = formId ? 'xform_global_functions' + '-' + formId : 'xform_global_functions'
  newScriptEle.type = 'text/javascript'
  newScriptEle.innerHTML = functionsCode
  bodyEle.appendChild(newScriptEle)
}

export function optionExists(optionsObj: any, optionName: string): boolean {
  if (!optionsObj) {
    return false
  }
  return Object.keys(optionsObj).indexOf(optionName) > -1
}

export function loadRemoteScript(srcPath: string, callback: () => void): void {
  const sid = encodeURIComponent(srcPath)
  const oldScriptEle = document.getElementById(sid)
  if (!oldScriptEle) {
    let s = document.createElement('script')
    s.src = srcPath
    s.id = sid
    document.body.appendChild(s)
    s.onload = s.onreadystatechange = function (_, isAbort) {
      if (isAbort || !s.readyState || s.readyState === 'loaded' || s.readyState === 'complete') {
        s = s.onload = s.onreadystatechange = null
        if (!isAbort) {
          callback()
        }
      }
    }
  }
}

export function traverseFieldWidgets(widgetList: any[], handler: (w: any) => void): void {
  widgetList.map(w => {
    if (w.formItemFlag || w.tableFlag) {
      handler(w)
    } else if (w.type === 'grid') {
      w.cols.map((col: any) => traverseFieldWidgets(col.widgetList, handler))
    } else if (w.type === 'table') {
      w.rows.map((row: any) => row.cols.map((cell: any) => traverseFieldWidgets(cell.widgetList, handler)))
    } else if (w.type === 'tab') {
      w.tabs.map((tab: any) => traverseFieldWidgets(tab.widgetList, handler))
    } else if (w.type === 'sub-form') {
      traverseFieldWidgets(w.widgetList, handler)
    } else if (w.category === 'container') {
      traverseFieldWidgets(w.widgetList, handler)
    }
  })
}

export function traverseContainWidgets(widgetList: any[], handler: (w: any) => void): void {
  widgetList.map(w => {
    if (w.category === 'container') {
      handler(w)
    }
    if (w.type === 'grid') {
      w.cols.map((col: any) => traverseContainWidgets(col.widgetList, handler))
    } else if (w.type === 'table') {
      w.rows.map((row: any) => row.cols.map((cell: any) => traverseContainWidgets(cell.widgetList, handler)))
    } else if (w.type === 'tab') {
      w.tabs.map((tab: any) => traverseContainWidgets(tab.widgetList, handler))
    } else if (w.type === 'sub-form') {
      traverseContainWidgets(w.widgetList, handler)
    } else if (w.category === 'container' && w.widgetList.length > 0) {
      traverseContainWidgets(w.widgetList, handler)
    }
  })
}

export function traverseAllWidgets(widgetList: any[], handler: (w: any) => void): void {
  widgetList?.map(w => {
    handler(w)
    if (w.type === 'grid') {
      w.cols.map((col: any) => {
        handler(col)
        traverseAllWidgets(col.widgetList, handler)
      })
    } else if (w.type === 'table') {
      w.rows.map((row: any) => row.cols.map((cell: any) => {
        handler(cell)
        traverseAllWidgets(cell.widgetList, handler)
      }))
    } else if (w.type === 'tab') {
      w.tabs.map((tab: any) => traverseAllWidgets(tab.widgetList, handler))
    } else if (w.type === 'sub-form') {
      traverseAllWidgets(w.widgetList, handler)
    } else if (w.category === 'container' && w?.widgetList?.length > 0) {
      traverseAllWidgets(w.widgetList, handler)
    }
  })
}

export function getAllFieldWidgets(widgetList: any[]): any[] {
  const result: any[] = []
  const handlerFn = (w: any) => {
    result.push({
      id: w.id,
      type: w.type,
      name: w.options.name,
      label: w.options.label,
      field: w,
    })
  }
  traverseFieldWidgets(widgetList, handlerFn)
  return result
}

export function getAllContainerWidgets(widgetList: any[]): any[] {
  const result: any[] = []
  const handlerFn = (w: any) => {
    result.push({
      type: w.type,
      name: w.options.name,
      container: w,
    })
  }
  traverseContainWidgets(widgetList, handlerFn)
  return result
}

export function copyToClipboard(content: string, clickEvent: any, $message: any, successMsg: string, errorMsg: string): void {
  const clipboard = new Clipboard(clickEvent.target, {
    text: () => content,
  })
  clipboard.on('success', () => {
    $message.success(successMsg)
    clipboard.destroy()
  })
  clipboard.on('error', () => {
    $message.error(errorMsg)
    clipboard.destroy()
  })
  clipboard.onClick(clickEvent)
}

export function getQueryParam(variable: string): string | undefined {
  const query = window.location.search.substring(1)
  const vars = query.split('&')
  for (let i = 0; i < vars.length; i++) {
    const pair = vars[i].split('=')
    if (pair[0] === variable) {
      return pair[1]
    }
  }
  return undefined
}

export function getDefaultFormConfig() {
  return {
    modelName: 'formData',
    refName: 'xForm',
    rulesName: 'rules',
    labelWidth: 80,
    labelPosition: 'left',
    size: '',
    labelAlign: 'label-left-align',
    cssCode: '',
    customClass: '',
    functions: '',
    layoutType: 'PC',
    jsonVersion: 3,
    dataSources: [],
    onFormCreated: '',
    onFormMounted: '',
    onFormDataChange: '',
  }
}

export function buildDefaultFormJson() {
  return {
    widgetList: [],
    formConfig: deepClone(getDefaultFormConfig()),
  }
}

export function translateOptionItems(rawData: any[], widgetType: string, labelKey: string, valueKey: string): any[] {
  if (widgetType === 'cascader') {
    return deepClone(rawData)
  }
  const result: any[] = []
  if (rawData && rawData.length > 0) {
    rawData.forEach(ri => {
      const label = ri[labelKey]
      const value = ri[valueKey]
      if (isNotNull(label) && isNotNull(value)) {
        result.push({ ...ri })
      } else {
        result.push({ label, value })
      }
    })
  }
  return result
}

export function debounce(fn: (...args: any[]) => void, wait: number): (...args: any[]) => void {
  let timer: any = null
  return function (...args: any[]) {
    if (timer !== null) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => fn(...args), wait)
  }
}
