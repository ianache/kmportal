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
        <RouterLink to="/domains" active-class="nav-link--active" class="nav-link">
          <svg class="icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
            <rect x="2" y="2" width="7" height="7" rx="1.5"/>
            <rect x="11" y="2" width="7" height="7" rx="1.5"/>
            <rect x="2" y="11" width="7" height="7" rx="1.5"/>
            <rect x="11" y="11" width="7" height="7" rx="1.5"/>
          </svg>
          Domains
        </RouterLink>
        <RouterLink to="/search" active-class="nav-link--active" class="nav-link">
          <svg class="icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
            <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
          </svg>
          Search
        </RouterLink>
        <RouterLink to="/ingestion" active-class="nav-link--active" class="nav-link">
          <svg class="icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M10 13V4M6 8l4-4 4 4"/><path d="M3 16h14"/>
          </svg>
          Ingestion
        </RouterLink>

        <template v-if="authStore.isAdmin || bypassAuth">
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
          <button class="icon-btn notification-btn" :class="{ 'has-unread': unreadCount > 0 }" aria-label="Notifications" @click="showNotifications">
            <svg width="17" height="17" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M10 2a6 6 0 0 0-6 6v3l-1.5 2.5h15L16 11V8a6 6 0 0 0-6-6z"/>
              <path d="M8.5 17.5a1.5 1.5 0 0 0 3 0"/>
            </svg>
            <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
          </button>
          <div class="topbar-avatar">{{ userInitials }}</div>
        </div>
      </header>

      <!-- Micro-UI content via Vue Router -->
      <main class="main">
        <RouterView />
      </main>
    </div>

    <!-- Notification drawer -->
    <div v-if="showNotificationDrawer" class="notification-drawer" @click.self="showNotificationDrawer = false">
      <div class="notification-panel">
        <div class="notification-header">
          <span class="notification-title">Notifications</span>
          <div class="notification-actions">
            <button class="action-btn" @click="markAllRead">Mark all read</button>
            <button class="close-btn" @click="showNotificationDrawer = false">✕</button>
          </div>
        </div>
        <div class="notification-list">
          <div v-if="notifications.length === 0" class="notification-empty">
            No notifications yet
          </div>
          <div
            v-for="notif in notifications"
            :key="notif.id"
            class="notification-item"
            :class="{ unread: !notif.read }"
            @click="markAsRead(notif.id)"
          >
            <div class="notification-icon" :class="`icon--${notif.type}`">
              <svg v-if="notif.type === 'success'" width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 10l4 4 8-8"/>
              </svg>
              <svg v-else-if="notif.type === 'error'" width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M6 6l8 8M14 6l-8 8"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="10" cy="10" r="7"/>
                <path d="M10 6v4l3 3"/>
              </svg>
            </div>
            <div class="notification-content">
              <span class="notification-item-title">{{ notif.title }}</span>
              <span class="notification-message">{{ notif.message }}</span>
              <span class="notification-time">{{ formatTime(notif.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { WebSocketKey, type WebSocketService } from '../../services/websocket'

const route  = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const wsService = inject<WebSocketService>(WebSocketKey)

const bypassAuth = import.meta.env.VITE_BYPASS_AUTH === 'true'

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
  if (roles.includes('km-admin')) return 'Administrator'
  if (roles.includes('km-reader')) return 'Reader'
  return 'Knowledge Curator'
})

const unreadCount = computed(() => wsService?.unreadCount.value ?? 0)
const isConnected = computed(() => wsService?.isConnected.value ?? false)
const notifications = computed(() => wsService?.notifications ?? [])

const showNotificationDrawer = ref(false)

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

function showNotifications() {
  showNotificationDrawer.value = true
  wsService?.markAllAsRead()
}

function markAllRead() {
  wsService?.markAllAsRead()
}

function markAsRead(id: string) {
  wsService?.markAsRead(id)
}

function formatTime(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
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

.topbar-right { display: flex; align-items: center; gap: 10px; }

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

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-2);
  transition: background 0.12s;
}
.icon-btn:hover { background: rgba(0,0,0,0.06); color: var(--text); }

.topbar-avatar {
  width: 30px;
  height: 30px;
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

/* ── Notification button ────────────────── */
.notification-btn {
  position: relative;
}

.notification-btn.has-unread {
  color: var(--primary);
}

.notification-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #FF3B30;
  color: white;
  font-size: 10px;
  font-weight: 700;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Notification drawer ────────────────── */
.notification-drawer {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.notification-panel {
  width: 380px;
  max-width: 100%;
  height: 100%;
  background: var(--surface);
  box-shadow: -4px 0 24px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.notification-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
}

.notification-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-btn {
  font-size: 13px;
  font-weight: 500;
  color: var(--primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.12s;
}
.action-btn:hover { background: var(--primary-soft); }

.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0,0,0,0.06);
  border: none;
  font-size: 12px;
  color: var(--text-2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.12s;
}
.close-btn:hover { background: rgba(0,0,0,0.1); }

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.notification-empty {
  padding: 60px 24px;
  text-align: center;
  color: var(--text-2);
  font-size: 14px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.12s;
  margin-bottom: 4px;
}
.notification-item:hover { background: rgba(0,0,0,0.03); }
.notification-item.unread { background: var(--primary-soft); }
.notification-item.unread:hover { background: rgba(0,122,255,0.12); }

.notification-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.notification-icon.icon--success { background: rgba(52,199,89,0.12); color: #1a7f37; }
.notification-icon.icon--error { background: rgba(255,59,48,0.12); color: #FF3B30; }
.notification-icon.icon--info { background: rgba(0,122,255,0.12); color: #007AFF; }
.notification-icon.icon--warning { background: rgba(255,149,0,0.12); color: #FF9500; }

.notification-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notification-item-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.notification-message {
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.4;
}

.notification-time {
  font-size: 12px;
  color: var(--text-2);
  opacity: 0.7;
  margin-top: 4px;
}
</style>
