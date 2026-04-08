import { App } from 'vue'
import XFormDesigner from './index.vue'

export default {
  install(app: App) {
    app.component('XFormDesigner', XFormDesigner)
    app.component('x-form-designer', XFormDesigner)
  }
}

export { XFormDesigner }
