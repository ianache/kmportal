<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="brand">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <polygon points="14,2 25,8.5 25,19.5 14,26 3,19.5 3,8.5"
            fill="rgba(0,122,255,0.1)" stroke="#007AFF" stroke-width="1.5"/>
          <circle cx="14" cy="14" r="4.5" fill="#007AFF"/>
        </svg>
        <span class="brand-name">Lumina</span>
      </div>

      <nav class="nav">
        <span class="nav-label">Workspace</span>

        <!-- KM_VIEWER + KM_MANAGER + KM_ADMIN -->
        <RouterLink to="/search" active-class="nav-link--active" class="nav-link">
          <svg class="icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
            <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
          </svg>
          Search
        </RouterLink>

        <!-- KM_MANAGER + KM_ADMIN -->
        <template v-if="authStore.isManager">
          <RouterLink to="/domains" active-class="nav-link--active" class="nav-link">
            <svg class="icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
              <rect x="2" y="2" width="7" height="7" rx="1.5"/>
              <rect x="11" y="2" width="7" height="7" rx="1.5"/>
              <rect x="2" y="11" width="7" height="7" rx="1.5"/>
              <rect x="11" y="11" width="7" height="7" rx="1.5"/>
            </svg>
            Domains
          </RouterLink>
          <RouterLink to="/ingestion" active-class="nav-link--active" class="nav-link">
            <svg class="icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M10 13V4M6 8l4-4 4 4"/><path d="M3 16h14"/>
            </svg>
            Ingestion
          </RouterLink>
        </template>

        <!-- KM_ADMIN only -->
        <template v-if="authStore.isAdmin">
          <span class="nav-label" style="margin-top:12px">System</span>
          <RouterLink to="/admin" active-class="nav-link--active" class="nav-link">
            <svg class="icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
              <circle cx="10" cy="10" r="2.5"/>
              <path d="M10 2v1.5M10 16.5V18M2 10h1.5M16.5 10H18M4.4 4.4l1.1 1.1M14.5 14.5l1.1 1.1M4.4 15.6l1.1-1.1M14.5 5.5l1.1-1.1"/>
            </svg>
            Admin
          </RouterLink>
        </template>
      </nav>

      <div class="sidebar-footer">
        <div class="user-row" @click="handleLogout">
          <div class="avatar">{{ userInitials }}</div>
          <div class="user-info">
            <span class="user-name">{{ authStore.user?.email ?? 'Guest' }}</span>
            <span class="user-role">{{ primaryRole }}</span>
          </div>
          <svg class="logout-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M13 10H3M13 10l-3-3M13 10l-3 3M16 5v10"/>
          </svg>
        </div>
      </div>
    </aside>

    <!-- Content area -->
    <div class="content-wrap">
      <!-- Top bar -->
      <header class="topbar">
        <div class="topbar-left">
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="topbar-right">
          <div class="search-pill">
            <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
            </svg>
            <span class="search-placeholder">Search everything…</span>
            <kbd>⌘K</kbd>
          </div>
          
          <!-- Notification Bell Component -->
          <NotificationBell />

          <div class="topbar-avatar">{{ userInitials }}</div>
        </div>
      </header>

      <!-- Micro-UI content via Vue Router -->
      <main class="main">
        <RouterView />
      </main>
    </div>

    <!-- Toast Notifications -->
    <ToastNotification />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject, watch, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useNotificationStore } from '../../stores/notifications'
import { WebSocketKey, type WebSocketService } from '../../services/websocket'
import NotificationBell from '../NotificationBell.vue'
import ToastNotification from '../ToastNotification.vue'

const route  = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const wsService = inject<WebSocketService>(WebSocketKey)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/domains':   'Knowledge Domains',
    '/search':    'Semantic Search',
    '/ingestion': 'Data Ingestion',
    '/admin':     'Administration',
  }
  return titles[route.path] ?? 'Lumina'
})

const userInitials = computed(() => {
  const email = authStore.user?.email
  if (!email) return 'G'
  return email.slice(0, 2).toUpperCase()
})

const primaryRole = computed(() => {
  const roles = authStore.user?.roles ?? []
  if (roles.includes('KM_ADMIN')) return 'KM Admin'
  if (roles.includes('KM_MANAGER')) return 'KM Manager'
  if (roles.includes('KM_VIEWER')) return 'KM Viewer'
  return 'Guest'
})

// WebSocket Handlers
function handleJobCompleted(event: any) {
  notificationStore.addNotification({
    type: 'success',
    title: 'Ingestion Complete',
    message: `Document "${event.documentTitle}" has been successfully ingested.`,
    source: 'ingestion',
    domainId: event.domainId,
    metadata: {
      jobId: event.jobId,
      documentId: event.documentId,
      route: `/domains/${event.domainId}`
    }
  })
}

function handleJobFailed(event: any) {
  notificationStore.addNotification({
    type: 'error',
    title: 'Ingestion Failed',
    message: `Failed to ingest document "${event.documentTitle}": ${event.error}`,
    source: 'ingestion',
    domainId: event.domainId,
    metadata: {
      jobId: event.jobId,
      documentId: event.documentId,
      route: '/ingestion'
    }
  })
}

onMounted(() => {
  if (wsService) {
    wsService.on('job:completed', handleJobCompleted)
    wsService.on('job:failed', handleJobFailed)
  }
})

watch(
  () => wsService?.authFailed?.value,
  (failed) => {
    if (failed) {
      // The HTTP session expired. Clear local state and send to login so the
      // user can re-authenticate. Do NOT call authStore.logout() here — that
      // triggers a full BFF /auth/logout redirect which loops back to this page.
      authStore.clearSession()
      router.push({ name: 'Login' })
    }
  }
)

onUnmounted(() => {
  if (wsService) {
    wsService.off('job:completed', handleJobCompleted)
    wsService.off('job:failed', handleJobFailed)
  }
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ─────────────────────────────── */
.sidebar {
  width: var(--sidebar-w);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-filter);
  -webkit-backdrop-filter: var(--glass-filter);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 20px 12px;
  position: sticky;
  top: 0;
  height: 100vh;
  flex-shrink: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 8px 16px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
}

.brand-name {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
}

.nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-2);
  padding: 0 8px;
  margin: 8px 0 4px;
  display: block;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-2);
  transition: background 0.12s, color 0.12s;
}
.nav-link:hover { background: rgba(0,0,0,0.04); color: var(--text); }
.nav-link--active { background: var(--primary-soft) !important; color: var(--primary) !important; }

.icon { width: 18px; height: 18px; flex-shrink: 0; }

.sidebar-footer {
  border-top: 1px solid var(--border);
  padding-top: 12px;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.12s;
}
.user-row:hover { background: rgba(0,0,0,0.04); }

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.user-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role { font-size: 11px; color: var(--text-2); }

.logout-icon { width: 15px; height: 15px; color: var(--text-2); flex-shrink: 0; }

/* ── Content wrap ────────────────────────── */
.content-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ── Top bar ─────────────────────────────── */
.topbar {
  height: var(--topbar-h);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-filter);
  -webkit-backdrop-filter: var(--glass-filter);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.page-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.01em;
}

.topbar-right { display: flex; align-items: center; gap: 16px; }

.search-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0,0,0,0.04);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
  color: var(--text-2);
  transition: background 0.12s;
}
.search-pill:hover { background: rgba(0,0,0,0.07); }

.search-placeholder { font-size: 13px; color: var(--text-2); min-width: 130px; }

kbd {
  font-family: var(--font);
  font-size: 11px;
  color: var(--text-2);
  background: var(--border);
  border-radius: 4px;
  padding: 1px 5px;
}

.topbar-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

/* ── Main ────────────────────────────────── */
.main { flex: 1; overflow: auto; }
</style>
