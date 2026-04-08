<template>
  <el-form-item
    v-if="field.options"
    :label="field.options.labelHidden ? '' : field.options.label"
    :label-width="field.options.labelHidden ? '0' : (field.options.labelWidth ? field.options.labelWidth + 'px' : undefined)"
    :required="field.options.required"
    :prop="field.options.name"
    :class="[field.options.customClass, { 'hidden-item': field.options.hidden }]"
  >
    <!-- Input Field -->
    <input-widget
      v-if="field.type === 'input'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Textarea Field -->
    <textarea-widget
      v-else-if="field.type === 'textarea'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Number Field -->
    <number-widget
      v-else-if="field.type === 'number'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Select Field -->
    <select-widget
      v-else-if="field.type === 'select'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Radio Field -->
    <radio-widget
      v-else-if="field.type === 'radio'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Checkbox Field -->
    <checkbox-widget
      v-else-if="field.type === 'checkbox'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Date Field -->
    <date-widget
      v-else-if="field.type === 'date'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Time Field -->
    <time-widget
      v-else-if="field.type === 'time'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Switch Field -->
    <switch-widget
      v-else-if="field.type === 'switch'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Slider Field -->
    <slider-widget
      v-else-if="field.type === 'slider'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Rate Field -->
    <rate-widget
      v-else-if="field.type === 'rate'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Cascader Field -->
    <cascader-widget
      v-else-if="field.type === 'cascader'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Color Field -->
    <color-widget
      v-else-if="field.type === 'color'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Picture Upload Field -->
    <picture-upload-widget
      v-else-if="field.type === 'picture-upload'"
      :field="field"
      :form-model="formModel"
    />

    <!-- File Upload Field -->
    <file-upload-widget
      v-else-if="field.type === 'file-upload'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Rich Editor Field -->
    <rich-editor-widget
      v-else-if="field.type === 'rich-editor'"
      :field="field"
      :form-model="formModel"
    />

    <!-- Static Text -->
    <static-text-widget
      v-else-if="field.type === 'static-text'"
      :field="field"
    />

    <!-- HTML Text -->
    <html-text-widget
      v-else-if="field.type === 'html-text'"
      :field="field"
    />

    <!-- Button -->
    <button-widget
      v-else-if="field.type === 'button'"
      :field="field"
    />

    <!-- Divider -->
    < divider-widget
      v-else-if="field.type === 'divider'"
      :field="field"
    />

    <!-- Unknown Field Type -->
    <span v-else class="unknown-field">{{ field.type }}</span>
  </el-form-item>
</template>

<script setup lang="ts">
import InputWidget from './field-widget/input-field.vue'
import TextareaWidget from './field-widget/textarea-field.vue'
import NumberWidget from './field-widget/number-field.vue'
import SelectWidget from './field-widget/select-field.vue'
import RadioWidget from './field-widget/radio-field.vue'
import CheckboxWidget from './field-widget/checkbox-field.vue'
import DateWidget from './field-widget/date-field.vue'
import TimeWidget from './field-widget/time-field.vue'
import SwitchWidget from './field-widget/switch-field.vue'
import SliderWidget from './field-widget/slider-field.vue'
import RateWidget from './field-widget/rate-field.vue'
import CascaderWidget from './field-widget/cascader-field.vue'
import ColorWidget from './field-widget/color-field.vue'
import PictureUploadWidget from './field-widget/picture-upload-field.vue'
import FileUploadWidget from './field-widget/file-upload-field.vue'
import RichEditorWidget from './field-widget/rich-editor-field.vue'
import StaticTextWidget from './field-widget/static-text-field.vue'
import HtmlTextWidget from './field-widget/html-text-field.vue'
import ButtonWidget from './field-widget/button-field.vue'
import DividerWidget from './field-widget/divider-field.vue'

defineProps<{
  field: any
  formModel: Record<string, any>
  parentList?: any[]
  indexOfParentList?: number
  parentWidget?: any
  subFormName?: string
  subFormRowIndex?: number
}>()
</script>

<style lang="scss" scoped>
.hidden-item {
  display: none !important;
}

.unknown-field {
  color: #909399;
  font-size: 12px;
}
</style>
