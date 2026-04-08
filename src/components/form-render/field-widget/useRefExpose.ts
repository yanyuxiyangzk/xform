import { inject, shallowRef } from 'vue'

export function useRefExpose(props: any) {
  const refList = inject('refList', shallowRef({}))

  function registerRef(name: string) {
    // Register reference for external access
  }

  function setDisabled(disabled: boolean) {
    // Set disabled state
  }

  return {
    registerRef,
    setDisabled,
    refList,
  }
}
