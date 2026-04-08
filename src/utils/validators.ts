// Form Validators
import type { ValidationRule } from 'element-plus'

export interface ValidatorRule {
  type: 'required' | 'min' | 'max' | 'minLength' | 'maxLength' | 'pattern' | 'email' | 'url' | 'phone' | 'custom'
  message?: string
  value?: any
  validator?: (value: any) => boolean
}

export function createValidator(rules: ValidatorRule[]): any[] {
  return rules.map(rule => {
    const validator: Record<string, any> = {}

    switch (rule.type) {
      case 'required':
        validator.required = true
        validator.message = rule.message || '此字段为必填项'
        break
      case 'min':
        validator.min = rule.value
        validator.message = rule.message || `值不能小于 ${rule.value}`
        break
      case 'max':
        validator.max = rule.value
        validator.message = rule.message || `值不能大于 ${rule.value}`
        break
      case 'minLength':
        validator.min = rule.value
        validator.message = rule.message || `长度不能小于 ${rule.value}`
        break
      case 'maxLength':
        validator.max = rule.value
        validator.message = rule.message || `长度不能大于 ${rule.value}`
        break
      case 'pattern':
        validator.pattern = rule.value
        validator.message = rule.message || '格式不正确'
        break
      case 'email':
        validator.pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        validator.message = rule.message || '请输入有效的邮箱地址'
        break
      case 'url':
        validator.pattern = /^https?:\/\/[^\s]+$/
        validator.message = rule.message || '请输入有效的URL地址'
        break
      case 'phone':
        validator.pattern = /^1[3-9]\d{9}$/
        validator.message = rule.message || '请输入有效的手机号码'
        break
      case 'custom':
        if (rule.validator) {
          validator.validator = (_rule: any, value: any, callback: any) => {
            if (rule.validator!(value)) {
              callback()
            } else {
              callback(new Error(rule.message || '验证失败'))
            }
          }
        }
        break
    }

    return validator
  })
}

export function parseValidationString(validationStr: string): ValidatorRule[] {
  if (!validationStr) return []

  const rules: ValidatorRule[] = []
  const parts = validationStr.split('|')

  for (const part of parts) {
    const [type, value] = part.split(':')

    switch (type) {
      case 'required':
        rules.push({ type: 'required', message: value || undefined })
        break
      case 'min':
        rules.push({ type: 'min', value: Number(value), message: undefined })
        break
      case 'max':
        rules.push({ type: 'max', value: Number(value), message: undefined })
        break
      case 'minLength':
        rules.push({ type: 'minLength', value: Number(value), message: undefined })
        break
      case 'maxLength':
        rules.push({ type: 'maxLength', value: Number(value), message: undefined })
        break
      case 'pattern':
        rules.push({ type: 'pattern', value: new RegExp(value), message: undefined })
        break
      case 'email':
        rules.push({ type: 'email' })
        break
      case 'url':
        rules.push({ type: 'url' })
        break
      case 'phone':
        rules.push({ type: 'phone' })
        break
    }
  }

  return rules
}

export function validateField(value: any, rules: ValidatorRule[]): string | null {
  for (const rule of rules) {
    switch (rule.type) {
      case 'required':
        if (value === null || value === undefined || value === '') {
          return rule.message || '此字段为必填项'
        }
        break
      case 'min':
        if (typeof value === 'number' && value < rule.value!) {
          return rule.message || `值不能小于 ${rule.value}`
        }
        break
      case 'max':
        if (typeof value === 'number' && value > rule.value!) {
          return rule.message || `值不能大于 ${rule.value}`
        }
        break
      case 'minLength':
        if (typeof value === 'string' && value.length < rule.value!) {
          return rule.message || `长度不能小于 ${rule.value}`
        }
        break
      case 'maxLength':
        if (typeof value === 'string' && value.length > rule.value!) {
          return rule.message || `长度不能大于 ${rule.value}`
        }
        break
      case 'pattern':
        if (typeof value === 'string' && !rule.value!.test(value)) {
          return rule.message || '格式不正确'
        }
        break
      case 'email':
        if (typeof value === 'string' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          return rule.message || '请输入有效的邮箱地址'
        }
        break
      case 'url':
        if (typeof value === 'string' && !/^https?:\/\/[^\s]+$/.test(value)) {
          return rule.message || '请输入有效的URL地址'
        }
        break
      case 'phone':
        if (typeof value === 'string' && !/^1[3-9]\d{9}$/.test(value)) {
          return rule.message || '请输入有效的手机号码'
        }
        break
      case 'custom':
        if (rule.validator && !rule.validator(value)) {
          return rule.message || '验证失败'
        }
        break
    }
  }
  return null
}
