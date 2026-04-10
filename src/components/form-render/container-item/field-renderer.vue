<template>
  <el-form-item
    v-if="!field.options.hidden"
    :label="!field.options.labelHidden ? field.options.label : ''"
    :prop="field.options.name"
    :required="field.options.required"
    :rules="validationRules"
  >
    <!-- Input -->
    <el-input
      v-if="field.type === 'input'"
      v-model="fieldValue"
      :type="field.options.type || 'text'"
      :placeholder="field.options.placeholder"
      :disabled="field.options.disabled || readOnly"
      :clearable="field.options.clearable"
      :show-password="field.options.showPassword"
      @change="handleChange"
      @focus="handleFocus"
      @blur="handleBlur"
    />

    <!-- Textarea -->
    <el-input
      v-else-if="field.type === 'textarea'"
      v-model="fieldValue"
      type="textarea"
      :placeholder="field.options.placeholder"
      :disabled="field.options.disabled || readOnly"
      :rows="field.options.rows || 4"
      @change="handleChange"
    />

    <!-- Number -->
    <el-input-number
      v-else-if="field.type === 'number'"
      v-model="fieldValue"
      :placeholder="field.options.placeholder"
      :disabled="field.options.disabled || readOnly"
      :min="field.options.min"
      :max="field.options.max"
      :step="field.options.step"
      :precision="field.options.precision"
      :controls="field.options.controls"
      @change="handleChange"
    />

    <!-- Select -->
    <el-select
      v-else-if="field.type === 'select'"
      v-model="fieldValue"
      :placeholder="field.options.placeholder"
      :disabled="field.options.disabled || readOnly"
      :clearable="field.options.clearable"
      :filterable="field.options.filterable"
      :multiple="field.options.multiple"
      @change="handleChange"
    >
      <el-option
        v-for="opt in field.options.options"
        :key="opt.value"
        :label="opt.label"
        :value="opt.value"
      />
    </el-select>

    <!-- Radio -->
    <el-radio-group
      v-else-if="field.type === 'radio'"
      v-model="fieldValue"
      :disabled="field.options.disabled || readOnly"
      @change="handleChange"
    >
      <el-radio
        v-for="opt in field.options.options"
        :key="opt.value"
        :value="opt.value"
      >
        {{ opt.label }}
      </el-radio>
    </el-radio-group>

    <!-- Checkbox -->
    <el-checkbox-group
      v-else-if="field.type === 'checkbox'"
      v-model="fieldValue"
      :disabled="field.options.disabled || readOnly"
      @change="handleChange"
    >
      <el-checkbox
        v-for="opt in field.options.options"
        :key="opt.value"
        :value="opt.value"
      >
        {{ opt.label }}
      </el-checkbox>
    </el-checkbox-group>

    <!-- Date -->
    <el-date-picker
      v-else-if="field.type === 'date'"
      v-model="fieldValue"
      :type="field.options.type || 'date'"
      :placeholder="field.options.placeholder"
      :disabled="field.options.disabled || readOnly"
      :format="field.options.format"
      :value-format="field.options.format"
      @change="handleChange"
    />

    <!-- Time -->
    <el-time-picker
      v-else-if="field.type === 'time'"
      v-model="fieldValue"
      :placeholder="field.options.placeholder"
      :disabled="field.options.disabled || readOnly"
      :format="field.options.format"
      :value-format="field.options.format"
      @change="handleChange"
    />

    <!-- Switch -->
    <el-switch
      v-else-if="field.type === 'switch'"
      v-model="fieldValue"
      :disabled="field.options.disabled || readOnly"
      @change="handleChange"
    />

    <!-- Slider -->
    <el-slider
      v-else-if="field.type === 'slider'"
      v-model="fieldValue"
      :disabled="field.options.disabled || readOnly"
      :min="field.options.min"
      :max="field.options.max"
      :step="field.options.step"
      :show-input="field.options.showInput"
      @change="handleChange"
    />

    <!-- Rate -->
    <el-rate
      v-else-if="field.type === 'rate'"
      v-model="fieldValue"
      :disabled="field.options.disabled || readOnly"
      :max="field.options.max"
      :allow-half="field.options.allowHalf"
      @change="handleChange"
    />

    <!-- Cascader -->
    <el-cascader
      v-else-if="field.type === 'cascader'"
      v-model="fieldValue"
      :options="field.options.options"
      :placeholder="field.options.placeholder"
      :disabled="field.options.disabled || readOnly"
      :clearable="field.options.clearable"
      :filterable="field.options.filterable"
      @change="handleChange"
    />

    <!-- Color -->
    <el-color-picker
      v-else-if="field.type === 'color'"
      v-model="fieldValue"
      :disabled="field.options.disabled || readOnly"
      :show-alpha="field.options.showAlpha"
      @change="handleChange"
    />

    <!-- Button -->
    <el-button
      v-else-if="field.type === 'button'"
      :type="field.options.type"
      :disabled="field.options.disabled"
      @click="handleButtonClick"
    >
      {{ field.options.label }}
    </el-button>

    <!-- Divider -->
    <el-divider
      v-else-if="field.type === 'divider'"
      :direction="field.options.direction"
      :content-position="field.options.contentPosition"
    />

    <!-- Static Text -->
    <span v-else-if="field.type === 'static-text'">
      {{ field.options.textContent }}
    </span>

    <!-- HTML Text -->
    <div v-else-if="field.type === 'html-text'" v-html="field.options.htmlContent" />

    <!-- Picture Upload -->
    <el-upload
      v-else-if="field.type === 'picture-upload'"
      v-model:file-list="fieldValue"
      :action="field.options.action"
      :accept="field.options.accept"
      :limit="field.options.limit"
      :list-type="field.options.listType"
      :disabled="field.options.disabled || readOnly"
      @change="handleChange"
    >
      <el-button type="primary">Upload</el-button>
    </el-upload>

    <!-- File Upload -->
    <el-upload
      v-else-if="field.type === 'file-upload'"
      v-model:file-list="fieldValue"
      :action="field.options.action"
      :accept="field.options.accept"
      :limit="field.options.limit"
      :disabled="field.options.disabled || readOnly"
      @change="handleChange"
    >
      <el-button type="primary">Upload</el-button>
    </el-upload>

    <!-- Rich Editor -->
    <div v-else-if="field.type === 'rich-editor'" class="rich-editor-placeholder">
      Rich Editor Component
    </div>

    <!-- Slot -->
    <slot v-else-if="field.type === 'slot'" :name="field.options.slotName" />

    <!-- Default -->
    <span v-else class="unknown-field">{{ field.type }}: {{ fieldValue }}</span>
  </el-form-item>
</template>

<script setup lang="ts">
import { ref, computed, watch, inject } from 'vue'
import eventBus from '@/utils/event-bus'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
  parentList?: any[]
  indexOfParentList?: number
  parentWidget?: any
  subFormName?: string
  subFormRowIndex?: number
}>()

const readOnly = inject<() => boolean>('getReadMode', () => false)

const fieldValue = computed({
  get() {
    const name = props.field.options.name
    if (props.subFormName !== undefined && props.subFormRowIndex !== undefined) {
      return props.formModel[name]
    }
    return props.formModel[name]
  },
  set(val) {
    const name = props.field.options.name
    if (props.subFormName !== undefined && props.subFormRowIndex !== undefined) {
      props.formModel[name] = val
    } else {
      props.formModel[name] = val
    }
  },
})

const validationRules = computed(() => {
  const rules: any[] = []
  if (props.field.options.required) {
    rules.push({ required: true, message: 'This field is required' })
  }
  if (props.field.options.validation) {
    rules.push({ pattern: new RegExp(props.field.options.validation), message: props.field.options.validationHint || 'Invalid value' })
  }
  return rules.length > 0 ? rules : undefined
})

function handleChange(val: any) {
  eventBus.emit('fieldChange', [props.field.options.name, val, fieldValue.value])
}

function handleFocus() {
  // emit focus event if needed
}

function handleBlur() {
  // emit blur event if needed
}

function handleButtonClick() {
  if (props.field.options.onClick) {
    try {
      const fn = new Function(props.field.options.onClick)
      fn.call(null)
    } catch (e) {
      console.error(e)
    }
  }
}
</script>

<style lang="scss" scoped>
.rich-editor-placeholder {
  padding: 20px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  text-align: center;
  color: #909399;
  min-height: 100px;
}

.unknown-field {
  color: #909399;
  font-style: italic;
}
</style>
