// Widget Schema Types
export interface WidgetSchema {
  type: string
  icon: string
  category?: 'container' | 'field'
  formItemFlag?: boolean
  tableFlag?: boolean
  options: Record<string, any>
  displayName?: string
  internal?: boolean
}

export interface ContainerSchema extends WidgetSchema {
  category: 'container'
  widgetList?: Array<ContainerSchema | FieldSchema>
  cols?: any[]
  rows?: any[]
  tabs?: any[]
  collapsed?: boolean
}

export interface FieldSchema extends WidgetSchema {
  category?: 'field'
  formItemFlag?: boolean
  options: Record<string, any>
}

// Widget Category
export type WidgetCategory = 'containers' | 'basicFields' | 'advancedFields' | 'customFields'

// Widget Type
export type WidgetType =
  | 'grid' | 'grid-col'
  | 'table' | 'table-cell'
  | 'tab' | 'tab-pane'
  | 'sub-form'
  | 'input' | 'textarea' | 'number'
  | 'select' | 'radio' | 'checkbox'
  | 'date' | 'time' | 'switch'
  | 'slider' | 'rate' | 'cascader'
  | 'color' | 'picture-upload' | 'file-upload'
  | 'rich-editor' | 'button' | 'divider'
  | 'static-text' | 'html-text' | 'slot'

// Drag & Drop
export interface DragContext {
  draggedContext: {
    element: WidgetSchema
    index: number
    futureIndex: number
  }
  to: {
    className: string
  }
}

// Widget Selection
export interface SelectionState {
  selectedId: string | null
  selectedWidget: WidgetSchema | null
  selectedWidgetName: string | null
}

// Container Operations
export interface ContainerOperation {
  type: 'add' | 'remove' | 'move' | 'clone'
  containerId: string
  widgetId?: string
  position?: number
  widget?: WidgetSchema
}

// History
export interface HistoryStep {
  widgetList: Array<ContainerSchema | FieldSchema>
  formConfig: any
}

export interface HistoryState {
  index: number
  maxStep: number
  steps: HistoryStep[]
}
