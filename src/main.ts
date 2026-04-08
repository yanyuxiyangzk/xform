import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'
import App from './App.vue'
import './styles/main.scss'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(ElementPlus, {
  locale: localStorage.getItem('xform_locale') === 'en-US' ? en : zhCn,
})

app.mount('#app')
