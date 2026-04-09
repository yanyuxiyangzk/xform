import { App } from 'vue'
import SFormDesigner from './index.vue'

export default {
  install(app: App) {
    app.component('SFormDesigner', SFormDesigner)
    app.component('s-form-designer', SFormDesigner)
  }
}

export { SFormDesigner }
