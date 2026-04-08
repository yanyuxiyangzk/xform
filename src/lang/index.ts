import zhCN from './zh-CN'
import enUS from './en-US'

export type LocaleType = 'zh-CN' | 'en-US'

export const locales = {
  'zh-CN': zhCN,
  'en-US': enUS,
}

export function getLocale(): LocaleType {
  return (localStorage.getItem('xform_locale') as LocaleType) || 'zh-CN'
}

export function setLocale(locale: LocaleType) {
  localStorage.setItem('xform_locale', locale)
}

export function t(key: string): string {
  const locale = getLocale()
  const messages = locales[locale] || locales['zh-CN']
  const keys = key.split('.')
  let result: any = messages

  for (const k of keys) {
    if (result && typeof result === 'object' && k in result) {
      result = result[k]
    } else {
      return key
    }
  }

  return typeof result === 'string' ? result : key
}

export { zhCN, enUS }
