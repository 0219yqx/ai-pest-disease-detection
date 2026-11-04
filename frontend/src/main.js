import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import { vCount } from './countUp.js'

const app = createApp(App)
app.directive('count', vCount)
app.use(router)
app.mount('#app')
