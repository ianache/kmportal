<template>
  <div class="app-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">

    <!-- ── Sidebar ──────────────────────────────────────────────────── -->
    <aside class="sidebar">
      <nav class="sidebar-nav">
        <span class="nav-section">Workspace</span>

        <RouterLink to="/search" active-class="nav-link--active" class="nav-link">
          <svg class="nav-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
            <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
          </svg>
          <span class="nav-text">Search</span>
        </RouterLink>

        <template v-if="authStore.isManager">
          <RouterLink to="/domains" active-class="nav-link--active" class="nav-link">
            <svg class="nav-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
              <rect x="2" y="2" width="7" height="7" rx="1.5"/>
              <rect x="11" y="2" width="7" height="7" rx="1.5"/>
              <rect x="2" y="11" width="7" height="7" rx="1.5"/>
              <rect x="11" y="11" width="7" height="7" rx="1.5"/>
            </svg>
            <span class="nav-text">Knowledge Domains</span>
          </RouterLink>
          <RouterLink to="/ingestion" active-class="nav-link--active" class="nav-link">
            <svg class="nav-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M10 13V4M6 8l4-4 4 4"/><path d="M3 16h14"/>
            </svg>
            <span class="nav-text">Ingestion</span>
          </RouterLink>
        </template>

        <template v-if="authStore.isAdmin">
          <span class="nav-section" style="margin-top:12px">System</span>
          <RouterLink to="/admin" active-class="nav-link--active" class="nav-link">
            <svg class="nav-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
              <circle cx="10" cy="10" r="2.5"/>
              <path d="M10 2v1.5M10 16.5V18M2 10h1.5M16.5 10H18M4.4 4.4l1.1 1.1M14.5 14.5l1.1 1.1M4.4 15.6l1.1-1.1M14.5 5.5l1.1-1.1"/>
            </svg>
            <span class="nav-text">Administration</span>
          </RouterLink>
        </template>
      </nav>
    </aside>

    <!-- ── Content wrap ─────────────────────────────────────────────── -->
    <div class="content-wrap">

      <!-- ── Top Bar ──────────────────────────────────────────────── -->
      <header class="topbar">

        <!-- Left group: hamburger + brand + divider + breadcrumb -->
        <div class="topbar-left">

          <!-- Hamburger -->
          <button class="hamburger-btn" @click="sidebarCollapsed = !sidebarCollapsed" :aria-label="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
              <line x1="2" y1="4.5" x2="16" y2="4.5"/>
              <line x1="2" y1="9"   x2="16" y2="9"/>
              <line x1="2" y1="13.5" x2="16" y2="13.5"/>
            </svg>
          </button>

          <!-- Brand -->
          <RouterLink to="/" class="topbar-brand">
            <svg width="22" height="22" viewBox="0 0 28 28" fill="none">
              <polygon points="14,2 25,8.5 25,19.5 14,26 3,19.5 3,8.5"
                fill="rgba(0,88,188,0.12)" stroke="#0058bc" stroke-width="1.5"/>
              <circle cx="14" cy="14" r="4" fill="#0058bc"/>
            </svg>
            <span class="brand-name">Lumina Knowledge</span>
          </RouterLink>

          <!-- Vertical divider -->
          <div class="topbar-sep" />

          <!-- Breadcrumb -->
          <nav class="breadcrumb" aria-label="breadcrumb">
            <RouterLink to="/" class="bc-home" aria-label="Home">
              <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 2L2 8v10h5v-5h6v5h5V8L10 2z"/>
              </svg>
            </RouterLink>
            <template v-for="(crumb, i) in breadcrumbs" :key="crumb.path">
              <svg class="bc-arrow" width="12" height="12" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
                <polyline points="7 5 13 10 7 15"/>
              </svg>
              <RouterLink
                v-if="i < breadcrumbs.length - 1"
                :to="crumb.path"
                class="bc-item bc-link"
              >{{ crumb.label }}</RouterLink>
              <span v-else class="bc-item bc-current">{{ crumb.label }}</span>
            </template>
          </nav>
        </div>

        <!-- Right group: search + bell + user avatar -->
        <div class="topbar-right">

          <!-- Search input -->
          <div class="search-box" :class="{ focused: searchFocused }">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
            </svg>
            <input
              ref="searchInputRef"
              v-model="searchQuery"
              class="search-input"
              placeholder="Buscar conocimiento..."
              @focus="searchFocused = true"
              @blur="searchFocused = false"
              @keydown.enter="handleSearch"
            />
            <kbd @click="focusSearch">⌘K</kbd>
          </div>

          <!-- Notification bell -->
          <NotificationBell />

          <!-- User avatar + dropdown -->
          <div class="user-menu-wrap" ref="userMenuRef">
            <button class="user-avatar-btn" @click="toggleUserMenu" :aria-expanded="userMenuOpen">
              {{ userInitials }}
            </button>

            <Transition name="dropdown">
              <div v-if="userMenuOpen" class="user-dropdown" role="menu">
                <!-- User info header -->
                <div class="dropdown-header">
                  <div class="dh-avatar">{{ userInitials }}</div>
                  <div class="dh-info">
                    <span class="dh-name">{{ authStore.user?.email ?? 'Guest' }}</span>
                    <span class="dh-role">{{ primaryRole }}</span>
                  </div>
                </div>
                <div class="dropdown-divider" />
                <!-- Actions -->
                <button class="dropdown-item" role="menuitem" @click="goToProfile">
                  <svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
                    <circle cx="10" cy="7" r="3.5"/>
                    <path d="M3 18c0-3.87 3.13-7 7-7s7 3.13 7 7"/>
                  </svg>
                  User Profile
                </button>
                <button class="dropdown-item dropdown-item--danger" role="menuitem" @click="handleLogout">
                  <svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
                    <path d="M13 10H3M13 10l-3-3M13 10l-3 3M16 5v10"/>
                  </svg>
                  Logout
                </button>
              </div>
            </Transition>
          </div>

        </div>
      </header>

      <!-- ── Main content ──────────────────────────────────────────── -->
      <main class="main">
        <RouterView />
      </main>
    </div>

    <!-- Toast -->
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

// ── Sidebar collapse ───────────────────────────────────────────────────────
const sidebarCollapsed = ref(false)

// ── Breadcrumb ─────────────────────────────────────────────────────────────
const ROUTE_META: Record<string, string> = {
  '/search':    'Search',
  '/domains':   'Knowledge Domains',
  '/ingestion': 'Ingestion',
  '/admin':     'Administration',
}

const breadcrumbs = computed(() => {
  const path = route.path
  // Build up path segments incrementally so each crumb links correctly
  const segments = path.split('/').filter(Boolean)
  const crumbs: { label: string; path: string }[] = []
  let accumulated = ''
  for (const seg of segments) {
    accumulated += `/${seg}`
    const label = ROUTE_META[accumulated] ?? seg.charAt(0).toUpperCase() + seg.slice(1)
    crumbs.push({ label, path: accumulated })
  }
  return crumbs
})

// ── Search ─────────────────────────────────────────────────────────────────
const searchQuery   = ref('')
const searchFocused = ref(false)
const searchInputRef = ref<HTMLInputElement | null>(null)

function handleSearch() {
  if (!searchQuery.value.trim()) return
  router.push({ path: '/search', query: { q: searchQuery.value.trim() } })
  searchQuery.value = ''
}

function focusSearch() {
  searchInputRef.value?.focus()
}

// Keyboard shortcut ⌘K / Ctrl+K
function onKeyDown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    focusSearch()
  }
}

// ── User menu ──────────────────────────────────────────────────────────────
const userMenuOpen = ref(false)
const userMenuRef  = ref<HTMLElement | null>(null)

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

function closeUserMenu(e: MouseEvent) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target as Node)) {
    userMenuOpen.value = false
  }
}

function goToProfile() {
  userMenuOpen.value = false
  // Placeholder — profile page is not yet implemented
}

async function handleLogout() {
  userMenuOpen.value = false
  await authStore.logout()
  router.push('/login')
}

// ── Computed ───────────────────────────────────────────────────────────────
const userInitials = computed(() => {
  const email = authStore.user?.email
  if (!email) return 'G'
  return email.slice(0, 2).toUpperCase()
})

const primaryRole = computed(() => {
  const roles = authStore.user?.roles ?? []
  if (roles.includes('KM_ADMIN'))   return 'KM Admin'
  if (roles.includes('KM_MANAGER')) return 'KM Manager'
  if (roles.includes('KM_VIEWER'))  return 'KM Viewer'
  return 'Guest'
})

// ── WebSocket handlers ─────────────────────────────────────────────────────
function handleJobCompleted(event: any) {
  notificationStore.addNotification({
    type: 'success',
    title: 'Ingestion Complete',
    message: `Document "${event.documentTitle}" has been successfully ingested.`,
    source: 'ingestion',
    domainId: event.domainId,
    metadata: { jobId: event.jobId, documentId: event.documentId, route: `/domains/${event.domainId}` },
  })
}

function handleJobFailed(event: any) {
  notificationStore.addNotification({
    type: 'error',
    title: 'Ingestion Failed',
    message: `Failed to ingest document "${event.documentTitle}": ${event.error}`,
    source: 'ingestion',
    domainId: event.domainId,
    metadata: { jobId: event.jobId, documentId: event.documentId, route: '/ingestion' },
  })
}

onMounted(() => {
  if (wsService) {
    wsService.on('job:completed', handleJobCompleted)
    wsService.on('job:failed', handleJobFailed)
  }
  document.addEventListener('keydown', onKeyDown)
  document.addEventListener('mousedown', closeUserMenu)
})

watch(
  () => wsService?.authFailed?.value,
  (failed) => {
    if (failed) {
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
  document.removeEventListener('keydown', onKeyDown)
  document.removeEventListener('mousedown', closeUserMenu)
})
</script>

<style scoped>
/* ── Layout shell ────────────────────────────────────────────────────────── */
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-background, #f9f9ff);
  font-family: var(--font-family, Inter, sans-serif);
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
.sidebar {
  position: fixed;
  top: 56px;           /* below topbar */
  left: 0;
  bottom: 0;
  width: 224px;
  background: var(--color-surface-container-lowest, #fff);
  border-right: 1px solid var(--color-outline-variant, #c1c6d7);
  display: flex;
  flex-direction: column;
  padding: 16px 10px;
  overflow: hidden;
  transition: width 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 50;
}

.app-layout.sidebar-collapsed .sidebar {
  width: 60px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.nav-section {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-outline, #717786);
  padding: 0 10px;
  margin: 8px 0 4px;
  display: block;
  white-space: nowrap;
  overflow: hidden;
}

.app-layout.sidebar-collapsed .nav-section {
  opacity: 0;
  pointer-events: none;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--color-on-surface-variant, #414755);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  transition: background 0.12s, color 0.12s;
}

.nav-link:hover {
  background: var(--color-surface-container, #ecedf9);
  color: var(--color-on-surface, #181c23);
}

.nav-link--active {
  background: rgba(0, 88, 188, 0.1) !important;
  color: var(--color-primary, #0058bc) !important;
  font-weight: 600;
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-text {
  transition: opacity 0.15s, width 0.22s;
}

.app-layout.sidebar-collapsed .nav-text {
  opacity: 0;
  width: 0;
  overflow: hidden;
}

/* ── Content wrap ────────────────────────────────────────────────────────── */
.content-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 224px;
  transition: margin-left 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 0;
}

.app-layout.sidebar-collapsed .content-wrap {
  margin-left: 60px;
}

/* ── Top Bar ─────────────────────────────────────────────────────────────── */
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 56px;
  background: var(--color-surface-container-lowest, #fff);
  border-bottom: 1px solid var(--color-outline-variant, #c1c6d7);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px 0 12px;
  gap: 16px;
}

/* ── Topbar left ─────────────────────────────────────────────────────────── */
.topbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

/* Hamburger button */
.hamburger-btn {
  width: 34px;
  height: 34px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-on-surface-variant, #414755);
  flex-shrink: 0;
  transition: background 0.12s, color 0.12s;
}

.hamburger-btn:hover {
  background: var(--color-surface-container, #ecedf9);
  color: var(--color-on-surface, #181c23);
}

/* Brand */
.topbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-on-surface, #181c23);
  letter-spacing: -0.02em;
  white-space: nowrap;
}

/* Vertical separator */
.topbar-sep {
  width: 1px;
  height: 20px;
  background: var(--color-outline-variant, #c1c6d7);
  flex-shrink: 0;
  margin: 0 2px;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 2px;
  min-width: 0;
}

.bc-home {
  display: flex;
  align-items: center;
  color: var(--color-on-surface-variant, #414755);
  text-decoration: none;
  padding: 2px 4px;
  border-radius: 4px;
  transition: color 0.12s, background 0.12s;
}

.bc-home:hover {
  color: var(--color-primary, #0058bc);
  background: rgba(0, 88, 188, 0.06);
}

.bc-arrow {
  color: var(--color-outline, #717786);
  flex-shrink: 0;
}

.bc-item {
  font-size: 13px;
  white-space: nowrap;
  padding: 2px 4px;
  border-radius: 4px;
}

.bc-link {
  color: var(--color-primary, #0058bc);
  text-decoration: none;
  font-weight: 500;
  transition: background 0.12s;
}

.bc-link:hover {
  background: rgba(0, 88, 188, 0.06);
}

.bc-current {
  color: var(--color-on-surface-variant, #414755);
  font-weight: 400;
}

/* ── Topbar right ────────────────────────────────────────────────────────── */
.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* Search box */
.search-box {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 10px;
  background: var(--color-surface-container, #ecedf9);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: text;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  min-width: 200px;
}

.search-box.focused {
  background: var(--color-surface-container-lowest, #fff);
  border-color: var(--color-primary, #0058bc);
  box-shadow: 0 0 0 3px rgba(0, 88, 188, 0.1);
}

.search-icon {
  color: var(--color-outline, #717786);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 13px;
  font-family: var(--font-family, Inter, sans-serif);
  color: var(--color-on-surface, #181c23);
  outline: none;
  min-width: 0;
}

.search-input::placeholder {
  color: var(--color-outline, #717786);
}

kbd {
  font-family: var(--font-family, Inter, sans-serif);
  font-size: 10px;
  color: var(--color-outline, #717786);
  background: var(--color-outline-variant, #c1c6d7);
  border-radius: 4px;
  padding: 2px 5px;
  cursor: pointer;
  flex-shrink: 0;
  user-select: none;
}

/* ── User menu ───────────────────────────────────────────────────────────── */
.user-menu-wrap {
  position: relative;
}

.user-avatar-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 2px solid transparent;
  background: var(--color-primary, #0058bc);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-family, Inter, sans-serif);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.user-avatar-btn:hover,
.user-avatar-btn:focus-visible {
  border-color: var(--color-primary-container, #0070eb);
  box-shadow: 0 0 0 3px rgba(0, 88, 188, 0.15);
  outline: none;
}

/* Dropdown */
.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  background: var(--color-surface-container-lowest, #fff);
  border: 1px solid var(--color-outline-variant, #c1c6d7);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1), 0 2px 6px rgba(0, 0, 0, 0.06);
  z-index: 200;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px 12px;
}

.dh-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-primary, #0058bc);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dh-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.dh-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-on-surface, #181c23);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dh-role {
  font-size: 11px;
  color: var(--color-on-surface-variant, #414755);
}

.dropdown-divider {
  height: 1px;
  background: var(--color-outline-variant, #c1c6d7);
  margin: 0 10px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 11px 16px;
  border: none;
  background: transparent;
  font-family: var(--font-family, Inter, sans-serif);
  font-size: 13.5px;
  font-weight: 500;
  color: var(--color-on-surface, #181c23);
  cursor: pointer;
  text-align: left;
  transition: background 0.12s;
}

.dropdown-item:hover {
  background: var(--color-surface-container, #ecedf9);
}

.dropdown-item--danger {
  color: var(--color-error, #ba1a1a);
}

.dropdown-item--danger:hover {
  background: var(--color-error-container, #ffdad6);
}

/* ── Main area ───────────────────────────────────────────────────────────── */
.main {
  flex: 1;
  margin-top: 56px;  /* topbar height */
  overflow: auto;
  min-height: calc(100vh - 56px);
}

/* ── Dropdown transition ─────────────────────────────────────────────────── */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .search-box { min-width: 140px; }
  .brand-name { display: none; }
  .topbar-sep { display: none; }
}
</style>
