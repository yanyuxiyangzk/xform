import { App, defineComponent, h } from 'vue'
import XFormRender from './index.vue'

export default {
  install(app: App) {
    app.component('XFormRender', XFormRender)
    app.component('x-form-render', XFormRender)
  }
}

export { XFormRender }
