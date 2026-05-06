import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { wsService, WebSocketKey } from './services/websocket'
import { bffClient, BffClientKey } from './services/bffClient'

// Import design tokens first
import './styles/design-tokens.css'

const pinia = createPinia()
const app = createApp(App)

// Provide services
app.provide(WebSocketKey, wsService)
app.provide(BffClientKey, bffClient)

app.use(pinia)
app.use(router)

// Connect WebSocket when auth is ready
router.afterEach((to) => {
  // Connect WebSocket for authenticated routes
  if (to.meta.requiresAuth && !wsService.isConnected.value) {
    // Use empty string for relative URL - goes through shell's proxy
    wsService.connect('')
  }
})

app.mount('#app')
