import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Notification, NotificationType } from '../types/notifications'

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref<Notification[]>([])
  const showToast = ref(false)
  const currentToast = ref<Notification | null>(null)

  // Getters
  const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)
  const recentNotifications = computed(() => [...notifications.value].sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  ).slice(0, 10))

  // Actions
  function addNotification(n: Omit<Notification, 'id' | 'read' | 'createdAt'>) {
    const notification: Notification = {
      ...n,
      id: crypto.randomUUID(),
      read: false,
      createdAt: new Date().toISOString()
    }
    
    notifications.value.unshift(notification)
    
    // Trigger toast
    currentToast.value = notification
    showToast.value = true
    
    // Auto-dismiss toast logic is usually in the component
  }

  function markAsRead(id: string) {
    const n = notifications.value.find(n => n.id === id)
    if (n) n.read = true
  }

  function markAllAsRead() {
    notifications.value.forEach(n => n.read = true)
  }

  function dismissNotification(id: string) {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  function clearToast() {
    showToast.value = false
    currentToast.value = null
  }

  return {
    notifications,
    unreadCount,
    recentNotifications,
    showToast,
    currentToast,
    addNotification,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    clearToast
  }
})
