import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { wsService, WebSocketKey } from './services/websocket'

// Import design tokens first
import './styles/design-tokens.css'

const pinia = createPinia()
const app = createApp(App)

// Provide WebSocket service
app.provide(WebSocketKey, wsService)

app.use(pinia)
app.use(router)

// Connect WebSocket when auth is ready
router.afterEach((to) => {
  // Connect WebSocket for authenticated routes
  if (to.meta.requiresAuth && !wsService.isConnected.value) {
    const BFF_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:3000'
    wsService.connect(BFF_URL)
  }
})

app.mount('#app')
