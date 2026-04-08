// Form Configuration Types
export interface FormConfig {
  modelName: string
  refName: string
  rulesName: string
  labelWidth: number
  labelPosition: 'left' | 'right' | 'top'
  size: 'large' | 'default' | 'small'
  labelAlign: 'label-left-align' | 'label-center-align' | 'label-right-align'
  cssCode: string
  customClass: string
  functions: string
  layoutType: 'PC' | 'Pad' | 'H5'
  jsonVersion: number
  dataSources: DataSource[]
  onFormCreated: string
  onFormMounted: string
  onFormDataChange: string
}

export interface DataSource {
  type: string
  url: string
  method: 'GET' | 'POST'
  headers: Record<string, string>
  params: Record<string, any>
  dataPath: string
  labelKey: string
  valueKey: string
}

// Widget Types
export interface BaseWidget {
  id: string
  key: string
  type: string
  options: Record<string, any>
  customClass?: string
  hidden?: boolean
}

export interface ContainerWidget extends BaseWidget {
  category: 'container'
  widgetList: Array<ContainerWidget | FieldWidget>
  collapsed?: boolean
  internal?: boolean
}

export interface FieldWidget extends BaseWidget {
  category?: 'field'
  formItemFlag?: boolean
  tableFlag?: boolean
  options: FieldOptions
}

export interface GridWidget extends ContainerWidget {
  type: 'grid'
  cols: GridCol[]
  options: GridOptions
}

export interface GridCol {
  id: string
  type: 'grid-col'
  options: GridColOptions
  widgetList: Array<ContainerWidget | FieldWidget>
  collapsed?: boolean
}

export interface GridOptions {
  name: string
  hidden: boolean
  customClass: string
  responsive: boolean
  colHeight: string
  gutter: number
}

export interface GridColOptions {
  name: string
  span: number
  offset: number
  push: number
  pull: number
  responsive: string
  md: number
  sm: number
  xs: number
  customClass: string
}

export interface TableWidget extends ContainerWidget {
  type: 'table'
  options: TableOptions
  rows: TableRow[]
}

export interface TableOptions {
  name: string
  hidden: boolean
  customClass: string
  width: string
  height: string
  rows: TableRow[]
}

export interface TableRow {
  id: string
  cols: TableCell[]
  merged?: boolean
}

export interface TableCell {
  id: string
  options: TableCellOptions
  widgetList: Array<ContainerWidget | FieldWidget>
  merged: boolean
}

export interface TableCellOptions {
  name: string
  colspan: number
  rowspan: number
  width: string
  height: string
}

export interface TabWidget extends ContainerWidget {
  type: 'tab'
  options: TabOptions
  tabs: TabPane[]
}

export interface TabOptions {
  name: string
  hidden: boolean
  customClass: string
  tabType: 'border-card' | 'card' | ''
  tabPosition: 'top' | 'right' | 'bottom' | 'left'
  defineTabs: TabDefine[]
}

export interface TabPane {
  id: string
  options: TabPaneOptions
  widgetList: Array<ContainerWidget | FieldWidget>
}

export interface TabPaneOptions {
  name: string
  label: string
  active: boolean
}

export interface TabDefine {
  name: string
  label: string
}

export interface SubFormWidget extends ContainerWidget {
  type: 'sub-form'
  options: SubFormOptions
}

export interface SubFormOptions {
  name: string
  label: string
  hidden: boolean
  customClass: string
  showBlankRow: boolean
  showRowNumber: boolean
  labelAlign: 'left' | 'center' | 'right'
}

// Field Options
export interface FieldOptions {
  name: string
  label: string
  labelAlign: 'left' | 'center' | 'right'
  defaultValue: any
  placeholder: string
  columnWidth: string
  size: 'large' | 'default' | 'small'
  labelWidth: number | null
  labelHidden: boolean
  readonly: boolean
  disabled: boolean
  hidden: boolean
  clearable: boolean
  required: boolean
  validation: string
  validationHint: string
  customClass: string
  // Input specific
  type: 'text' | 'password' | 'email' | 'number' | 'url'
  showPassword: boolean
  minLength: number | null
  maxLength: number | null
  showWordLimit: boolean
  prefixIcon: string
  suffixIcon: string
  // Select specific
  filterable: boolean
  allowCreate: boolean
  defaultFirstOption: boolean
  multiple: boolean
  multipleLimit: number
  options: Array<{ label: string; value: any }>
  showLabel: boolean
  optionItems: Array<{ label: string; value: any }>
  // Date specific
  dateType: 'date' | 'datetime' | 'week' | 'month' | 'year'
  format: string
  timestamp: boolean
  placeholderType: 'normal' | 'string'
  startPlaceholder: string
  endPlaceholder: string
  // Number specific
  min: number | null
  max: number | null
  step: number
  precision: number | null
  controls: boolean
  controlsPosition: 'right' | 'default'
  // Switch specific
  switchWidth: number
  activeText: string
  inactiveText: string
  activeColor: string
  inactiveColor: string
  // Slider specific
  range: boolean
  showStops: boolean
  showInput: boolean
  // Rate specific
  max: number
  allowHalf: boolean
  showText: boolean
  showScore: boolean
  // Cascader specific
  separator: string
  filter: boolean
  collapseTags: boolean
  // Upload specific
  accept: string
  limit: number
  fileMaxSize: number
  showTip: boolean
  action: string
  listType: 'text' | 'picture-card' | 'picture'
  withCredentials: boolean
  headers: Record<string, string>
  data: Record<string, any>
  // Color specific
  showAlpha: boolean
  colorFormat: string
  // Rich editor specific
  minHeight: string
  // Event handlers
  onCreated: string
  onMounted: string
  onInput: string
  onChange: string
  onFocus: string
  onBlur: string
  onValidate: string
  onClick: string
}

// Form JSON structure
export interface FormJson {
  widgetList: Array<ContainerWidget | FieldWidget>
  formConfig: FormConfig
}

// Form Data
export interface FormData {
  [key: string]: any
}
