import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// Import design tokens first
import './styles/design-tokens.css'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.mount('#app')