<template>
  <div class="notification-bell-wrap">
    <button class="bell-btn" @click="isOpen = !isOpen" ref="bellBtn">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span v-if="store.unreadCount > 0" class="unread-badge">
        {{ store.unreadCount > 9 ? '9+' : store.unreadCount }}
      </span>
    </button>
    
    <transition name="fade">
      <NotificationDropdown v-if="isOpen" @close="isOpen = false" />
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '../stores/notifications'
import NotificationDropdown from './NotificationDropdown.vue'

const store = useNotificationStore()
const isOpen = ref(false)
const bellBtn = ref<HTMLElement | null>(null)

function handleClickOutside(e: MouseEvent) {
  if (isOpen.value && bellBtn.value && !bellBtn.value.contains(e.target as Node)) {
    const dropdown = document.querySelector('.notification-dropdown')
    if (dropdown && !dropdown.contains(e.target as Node)) {
      isOpen.value = false
    }
  }
}

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.notification-bell-wrap {
  position: relative;
}

.bell-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-container-low, #f1f3fe);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--on-surface, #1D1D1F);
  transition: all 0.2s;
  position: relative;
}

.bell-btn:hover {
  background: var(--surface-container, #ecedf9);
  color: var(--primary, #007AFF);
}

.unread-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  background: #FF3B30;
  color: white;
  font-size: 10px;
  font-weight: 700;
  min-width: 16px;
  height: 16px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid #ffffff;
}

.fade-enter-active, .fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
