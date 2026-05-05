<template>
  <div class="notification-dropdown">
    <div class="dropdown-header">
      <h3 class="dropdown-title">Notifications</h3>
      <button class="mark-all" @click="store.markAllAsRead()">Mark all as read</button>
    </div>

    <div class="notification-list">
      <div 
        v-for="n in store.recentNotifications" 
        :key="n.id"
        class="notification-item"
        :class="{ 'is-unread': !n.read }"
        @click="handleNotificationClick(n)"
      >
        <div class="item-icon" :class="`icon--${n.type}`">
          <svg v-if="n.type === 'success'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <svg v-else-if="n.type === 'error'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
        </div>
        <div class="item-content">
          <div class="item-header">
            <span class="item-title">{{ n.title }}</span>
            <span class="item-time">{{ formatTime(n.createdAt) }}</span>
          </div>
          <p class="item-msg">{{ n.message }}</p>
        </div>
        <div v-if="!n.read" class="unread-dot"></div>
      </div>

      <div v-if="store.notifications.length === 0" class="empty-state">
        <p>No notifications yet</p>
      </div>
    </div>

    <div class="dropdown-footer">
      <button class="view-all">View all notifications</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNotificationStore } from '../stores/notifications'
import type { Notification } from '../types/notifications'
import { useRouter } from 'vue-router'

const store = useNotificationStore()
const router = useRouter()

const emit = defineEmits(['close'])

function handleNotificationClick(n: Notification) {
  store.markAsRead(n.id)
  
  if (n.metadata?.route) {
    router.push(n.metadata.route)
  } else if (n.source === 'ingestion') {
    router.push('/ingestion')
  }
  
  emit('close')
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 12px;
  width: 320px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid var(--outline-variant, #E5E5E7);
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow: hidden;
}

.dropdown-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--outline-variant, #E5E5E7);
}

.dropdown-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0;
}

.mark-all {
  font-size: 12px;
  color: var(--primary, #007AFF);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 14px 16px;
  display: flex;
  gap: 12px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.notification-item:hover {
  background: rgba(0, 0, 0, 0.03);
}

.notification-item.is-unread {
  background: rgba(0, 88, 188, 0.03);
}

.item-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon--success { background: rgba(52, 199, 89, 0.1); color: #34C759; }
.icon--error { background: rgba(255, 59, 48, 0.1); color: #FF3B30; }
.icon--info { background: rgba(0, 122, 255, 0.1); color: #007AFF; }

.item-content {
  flex: 1;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
}

.item-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
}

.is-unread .item-title {
  font-weight: 700;
}

.item-time {
  font-size: 11px;
  color: var(--on-surface-variant, #86868B);
}

.item-msg {
  font-size: 12px;
  color: var(--on-surface-variant, #414755);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.unread-dot {
  position: absolute;
  top: 16px;
  right: 8px;
  width: 6px;
  height: 6px;
  background: var(--primary, #007AFF);
  border-radius: 50%;
}

.empty-state {
  padding: 40px 16px;
  text-align: center;
  color: var(--on-surface-variant, #86868B);
  font-size: 14px;
}

.dropdown-footer {
  padding: 12px;
  text-align: center;
  border-top: 1px solid var(--outline-variant, #E5E5E7);
}

.view-all {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
  background: none;
  border: none;
  cursor: pointer;
}
</style>
