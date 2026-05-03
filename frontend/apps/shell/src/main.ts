import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/search' },
    { path: '/domains', component: () => import('domainsUi/App') },
    { path: '/search', component: () => import('searchUi/App') },
    { path: '/ingestion', component: () => import('ingestionUi/App') },
    { path: '/admin', component: () => import('adminUi/App') },
  ]
})

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.mount('#app')