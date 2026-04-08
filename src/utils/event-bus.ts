import mitt from 'mitt'

const eventBus = mitt()

export const eventTypes = {
  'widget-add': '添加组件',
  'widget-remove': '删除组件',
  'widget-options-change': '组件属性变更',
  'widget-selected': '组件选中',
  'widget-list-modified': '组件列表变更',
  'history-change': '历史记录变更',
  'form-css-change': '表单样式变更',
  'field-selected': '字段组件选中',
  'form-json-imported': '表单JSON导入',
  'reloadOptionItems': '重新加载选项',
  'setFormData': '设置表单数据',
}

export default eventBus
