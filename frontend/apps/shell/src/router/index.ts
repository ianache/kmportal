import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Views
import AuthCallback from '../views/AuthCallback.vue'
import LoginRequired from '../views/LoginRequired.vue'

// Layout
import ShellLayout from '../components/layout/ShellLayout.vue'

const routes = [
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback,
    meta: { public: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginRequired,
    meta: { public: true },
  },
  {
    path: '/',
    component: ShellLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/search',
      },
      {
        path: '/search',
        name: 'Search',
        component: () => import('searchUi/App'),
        meta: {
          title: 'Search',
          icon: 'search',
          roles: ['KM_VIEWER', 'KM_MANAGER', 'KM_ADMIN'],
        },
      },
      {
        path: '/domains',
        name: 'Domains',
        component: () => import('domainsUi/App'),
        meta: {
          title: 'Domains',
          icon: 'domains',
          roles: ['KM_MANAGER', 'KM_ADMIN'],
        },
      },
      {
        path: '/ingestion',
        name: 'Ingestion',
        component: () => import('ingestionUi/App'),
        meta: {
          title: 'Ingestion',
          icon: 'ingestion',
          roles: ['KM_MANAGER', 'KM_ADMIN'],
        },
      },
      {
        path: '/admin',
        name: 'Admin',
        component: () => import('adminUi/App'),
        meta: {
          title: 'Admin',
          icon: 'admin',
          roles: ['KM_ADMIN'],
        },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const BYPASS_AUTH = import.meta.env.VITE_BYPASS_AUTH === 'true'

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Dev bypass — set VITE_BYPASS_AUTH=true in .env.local
  if (BYPASS_AUTH) {
    if (!authStore.isAuthenticated) {
      await authStore.fetchSession().catch(() => {})
    }
    next()
    return
  }

  // Skip auth check for public routes
  if (to.meta.public) {
    next()
    return
  }

  // Ensure we have a session
  if (!authStore.isAuthenticated) {
    try {
      const hasSession = await authStore.fetchSession()
      if (!hasSession && to.path !== '/login') {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    } catch {
      // BFF unreachable — allow through rather than blocking the UI
      next()
      return
    }
  }

  // Role-based access control
  const requiredRoles = to.meta.roles as string[] | undefined
  if (requiredRoles && requiredRoles.length > 0 && authStore.user) {
    const userRoles = authStore.user.roles
    const allowed = requiredRoles.some(r => userRoles.includes(r))
    if (!allowed) {
      // Redirect to the highest-privilege route the user CAN access
      next({ name: 'Search' })
      return
    }
  }

  next()
})

export default router
