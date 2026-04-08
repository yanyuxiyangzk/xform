<template>
  <div
    class="field-wrapper"
    :class="[field.options.customClass, { 'selected': isSelected, 'hidden': field.options.hidden }]"
    @click.stop="selectWidget"
  >
    <div class="field-content">
      <span class="field-label" v-if="!field.options.labelHidden && field.options.label">
        {{ field.options.label }}:
      </span>
      <span class="field-value">
        {{ fieldDisplayValue }}
      </span>
    </div>
    <div class="field-actions" v-if="isSelected">
      <el-button link size="small" @click.stop="moveUp">↑</el-button>
      <el-button link size="small" @click.stop="moveDown">↓</el-button>
      <el-button link size="small" type="danger" @click.stop="deleteField">×</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import eventBus from '@/utils/event-bus'

const props = defineProps<{
  field: any
  parentList: any[]
  indexOfParentList: number
  parentWidget: any
  designer: any
}>()

const isSelected = computed(() => props.designer.selectedId === props.field.id)

const fieldDisplayValue = computed(() => {
  const opt = props.field.options
  const type = props.field.type

  switch (type) {
    case 'input':
      return opt.placeholder || 'Input Field'
    case 'textarea':
      return opt.placeholder || 'Textarea'
    case 'number':
      return opt.placeholder || 'Number'
    case 'select':
      return opt.placeholder || 'Select'
    case 'radio':
      return 'Radio Group'
    case 'checkbox':
      return 'Checkbox Group'
    case 'date':
      return opt.placeholder || 'Date'
    case 'time':
      return opt.placeholder || 'Time'
    case 'switch':
      return opt.placeholder || 'Switch'
    case 'slider':
      return 'Slider'
    case 'rate':
      return 'Rate'
    case 'color':
      return 'Color Picker'
    case 'button':
      return opt.label || 'Button'
    case 'divider':
      return '---'
    case 'static-text':
      return opt.textContent || 'Text'
    case 'picture-upload':
      return 'Image Upload'
    case 'file-upload':
      return 'File Upload'
    case 'rich-editor':
      return 'Rich Editor'
    default:
      return opt.label || type
  }
})

function selectWidget() {
  props.designer.setSelected(props.field)
  eventBus.emit('widget-selected', props.field)
}

function moveUp() {
  props.designer.moveUpWidget(props.parentList, props.indexOfParentList)
}

function moveDown() {
  props.designer.moveDownWidget(props.parentList, props.indexOfParentList)
}

function deleteField() {
  props.parentList.splice(props.indexOfParentList, 1)
  props.designer.clearSelected()
  props.designer.emitHistoryChange()
}
</script>

<style lang="scss" scoped>
.field-wrapper {
  position: relative;
  padding: 8px 12px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  margin-bottom: 4px;
  background: #fff;
  cursor: move;
  transition: all 0.2s;

  &:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.02);
  }

  &.selected {
    border-color: #667eea;
    border-style: solid;
    background: rgba(102, 126, 234, 0.05);
  }

  &.hidden {
    opacity: 0.5;
  }
}

.field-content {
  display: flex;
  align-items: center;
  gap: 4px;

  .field-label {
    font-weight: 500;
    color: #606266;
  }

  .field-value {
    color: #909399;
    font-size: 13px;
  }
}

.field-actions {
  position: absolute;
  top: -10px;
  right: -8px;
  display: flex;
  gap: 2px;
  background: #667eea;
  border-radius: 4px;
  padding: 2px;
  opacity: 0;
  transition: opacity 0.2s;

  .field-wrapper:hover &,
  .field-wrapper.selected & {
    opacity: 1;
  }

  .el-button {
    color: #fff;
    padding: 2px 6px;
    min-height: auto;
  }
}
</style>
