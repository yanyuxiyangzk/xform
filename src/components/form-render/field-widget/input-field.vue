<template>
  <el-input
    v-model="value"
    :type="field.options.type || 'text'"
    :placeholder="field.options.placeholder"
    :size="field.options.size"
    :disabled="field.options.disabled"
    :readonly="field.options.readonly"
    :clearable="field.options.clearable"
    :show-password="field.options.showPassword"
    :prefix-icon="field.options.prefixIcon"
    :suffix-icon="field.options.suffixIcon"
    :maxlength="field.options.maxLength"
    :minlength="field.options.minLength"
    :show-word-limit="field.options.showWordLimit"
    @input="handleInput"
    @change="handleChange"
    @focus="handleFocus"
    @blur="handleBlur"
  />
</template>

<script setup lang="ts">
import { ref, watch, inject, computed } from 'vue'
import { useRefExpose } from './useRefExpose'

const props = defineProps<{
  field: any
  formModel: Record<string, any>
}>()

const { registerRef } = useRefExpose(props)
const refName = computed(() => props.field.options.name)
registerRef(refName.value)

const value = ref(props.field.options.defaultValue)

watch(() => props.field.options.defaultValue, (newVal) => {
  value.value = newVal
})

watch(value, (newVal) => {
  const fieldName = props.field.options.name
  if (props.formModel.hasOwnProperty(fieldName)) {
    props.formModel[fieldName] = newVal
  }
})

function handleInput(val: any) {
  // Real-time input handling
}

function handleChange(val: any) {
  // Change event
}

function handleFocus(event: any) {
  if (props.field.options.onFocus) {
    try {
      const func = new Function('field', 'value', event, props.field.options.onFocus)
      func(props.field, value.value, event)
    } catch (e) {
      console.error(e)
    }
  }
}

function handleBlur(event: any) {
  if (props.field.options.onBlur) {
    try {
      const func = new Function('field', 'value', event, props.field.options.onBlur)
      func(props.field, value.value, event)
    } catch (e) {
      console.error(e)
    }
  }
}
</script>
