<template>
  <div
    class="field-wrapper"
    :class="[field.options.customClass, { 'selected': isSelected, 'hidden': field.options.hidden }]"
    @click.stop="selectWidget"
  >
    <el-form-item
      v-if="field.options"
      :label="field.options.labelHidden ? '' : field.options.label"
      :label-width="field.options.labelHidden ? '0' : (field.options.labelWidth ? field.options.labelWidth + 'px' : undefined)"
      :required="field.options.required"
    >
      <!-- Input Field -->
      <el-input
        v-if="field.type === 'input'"
        v-model="fieldValues[field.options.name]"
        :type="field.options.type || 'text'"
        :placeholder="field.options.placeholder"
        :size="field.options.size"
        :disabled="field.options.disabled"
        :readonly="field.options.readonly"
        :clearable="field.options.clearable"
        :show-password="field.options.showPassword"
      />

      <!-- Textarea Field -->
      <el-input
        v-else-if="field.type === 'textarea'"
        v-model="fieldValues[field.options.name]"
        type="textarea"
        :placeholder="field.options.placeholder"
        :rows="field.options.rows"
        :disabled="field.options.disabled"
        :readonly="field.options.readonly"
      />

      <!-- Number Field -->
      <el-input-number
        v-else-if="field.type === 'number'"
        v-model="fieldValues[field.options.name]"
        :placeholder="field.options.placeholder"
        :min="field.options.min"
        :max="field.options.max"
        :step="field.options.step"
        :precision="field.options.precision"
        :controls="field.options.controls"
        :disabled="field.options.disabled"
      />

      <!-- Select Field -->
      <el-select
        v-else-if="field.type === 'select'"
        v-model="fieldValues[field.options.name]"
        :placeholder="field.options.placeholder"
        :disabled="field.options.disabled"
        :clearable="field.options.clearable"
        :filterable="field.options.filterable"
        :multiple="field.options.multiple"
      >
        <el-option
          v-for="item in getOptions(field)"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>

      <!-- Radio Field -->
      <el-radio-group
        v-else-if="field.type === 'radio'"
        v-model="fieldValues[field.options.name]"
        :disabled="field.options.disabled"
      >
        <el-radio
          v-for="item in getOptions(field)"
          :key="item.value"
          :value="item.value"
        >
          {{ item.label }}
        </el-radio>
      </el-radio-group>

      <!-- Checkbox Field -->
      <el-checkbox-group
        v-else-if="field.type === 'checkbox'"
        v-model="fieldValues[field.options.name]"
        :disabled="field.options.disabled"
      >
        <el-checkbox
          v-for="item in getOptions(field)"
          :key="item.value"
          :label="item.value"
        >
          {{ item.label }}
        </el-checkbox>
      </el-checkbox-group>

      <!-- Date Field -->
      <el-date-picker
        v-else-if="field.type === 'date'"
        v-model="fieldValues[field.options.name]"
        type="date"
        :placeholder="field.options.placeholder"
        :disabled="field.options.disabled"
        :clearable="field.options.clearable"
        :format="field.options.format"
      />

      <!-- Time Field -->
      <el-time-picker
        v-else-if="field.type === 'time'"
        v-model="fieldValues[field.options.name]"
        :placeholder="field.options.placeholder"
        :disabled="field.options.disabled"
        :clearable="field.options.clearable"
        :format="field.options.format"
        :is-range="field.options.isRange"
      />

      <!-- Switch Field -->
      <el-switch
        v-else-if="field.type === 'switch'"
        v-model="fieldValues[field.options.name]"
        :disabled="field.options.disabled"
        :active-text="field.options.activeText"
        :inactive-text="field.options.inactiveText"
      />

      <!-- Slider Field -->
      <el-slider
        v-else-if="field.type === 'slider'"
        v-model="fieldValues[field.options.name]"
        :min="field.options.min"
        :max="field.options.max"
        :step="field.options.step"
        :show-input="field.options.showInput"
        :range="field.options.range"
        :disabled="field.options.disabled"
      />

      <!-- Rate Field -->
      <el-rate
        v-else-if="field.type === 'rate'"
        v-model="fieldValues[field.options.name]"
        :max="field.options.max"
        :allow-half="field.options.allowHalf"
        :show-text="field.options.showText"
        :show-score="field.options.showScore"
        :disabled="field.options.disabled"
      />

      <!-- Cascader Field -->
      <el-cascader
        v-else-if="field.type === 'cascader'"
        v-model="fieldValues[field.options.name]"
        :options="field.options.options"
        :placeholder="field.options.placeholder"
        :disabled="field.options.disabled"
        :clearable="field.options.clearable"
        :filterable="field.options.filterable"
        :separator="field.options.separator"
      />

      <!-- Color Field -->
      <el-color-picker
        v-else-if="field.type === 'color'"
        v-model="fieldValues[field.options.name]"
        :show-alpha="field.options.showAlpha"
        :disabled="field.options.disabled"
      />

      <!-- Picture Upload Field -->
      <el-upload
        v-else-if="field.type === 'picture-upload'"
        v-model:file-list="fieldValues[field.options.name]"
        :action="field.options.action"
        :accept="field.options.accept"
        :limit="field.options.limit"
        :list-type="field.options.listType"
      >
        <el-button type="primary">点击上传</el-button>
      </el-upload>

      <!-- File Upload Field -->
      <el-upload
        v-else-if="field.type === 'file-upload'"
        v-model:file-list="fieldValues[field.options.name]"
        :action="field.options.action"
        :accept="field.options.accept"
        :limit="field.options.limit"
      >
        <el-button type="primary">点击上传</el-button>
      </el-upload>

      <!-- Rich Editor Field -->
      <div v-else-if="field.type === 'rich-editor'" class="rich-editor-placeholder">
        <span>富文本编辑器</span>
      </div>

      <!-- Static Text -->
      <span v-else-if="field.type === 'static-text'">
        {{ field.options.textContent }}
      </span>

      <!-- HTML Text -->
      <div v-else-if="field.type === 'html-text'" v-html="field.options.htmlContent" />

      <!-- Button -->
      <el-button
        v-else-if="field.type === 'button'"
        :type="field.options.buttonType"
        :disabled="field.options.disabled"
        :icon="field.options.icon"
      >
        {{ field.options.label }}
      </el-button>

      <!-- Divider -->
      <el-divider
        v-else-if="field.type === 'divider'"
        :direction="field.options.direction"
        :content-position="field.options.contentPosition"
      />

      <!-- Unknown Field Type -->
      <span v-else class="unknown-field">{{ field.type }}</span>
    </el-form-item>

    <div class="field-actions" v-if="isSelected">
      <el-button link size="small" @click.stop="moveUp">↑</el-button>
      <el-button link size="small" @click.stop="moveDown">↓</el-button>
      <el-button link size="small" type="danger" @click.stop="deleteField">×</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import eventBus from '@/utils/event-bus'

const props = defineProps<{
  field: any
  parentList: any[]
  indexOfParentList: number
  parentWidget: any
  designer: any
}>()

const isSelected = computed(() => props.designer.selectedId === props.field.id)

const fieldValues = reactive<Record<string, any>>({})

function getOptions(field: any): Array<{label: string, value: any}> {
  if (field.options.dsEnabled && field.options.dsType === 'static' && field.options.optionItems?.length > 0) {
    return field.options.optionItems
  }
  if (field.options.options && field.options.options.length > 0) {
    return field.options.options
  }
  return []
}

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

.rich-editor-placeholder {
  min-height: 120px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  background: #fafafa;
}

.unknown-field {
  color: #909399;
  font-size: 12px;
}
</style>
