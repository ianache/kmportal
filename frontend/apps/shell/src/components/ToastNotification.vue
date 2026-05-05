<template>
  <transition name="slide-fade">
    <div 
      v-if="store.showToast && store.currentToast" 
      class="toast-notification"
      :class="`toast--${store.currentToast.type}`"
      @mouseenter="pauseTimer"
      @mouseleave="resumeTimer"
    >
      <div class="toast-content">
        <div class="toast-icon">
          <svg v-if="store.currentToast.type === 'success'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <svg v-else-if="store.currentToast.type === 'error'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
        </div>
        <div class="toast-body">
          <h4 class="toast-title">{{ store.currentToast.title }}</h4>
          <p class="toast-msg">{{ store.currentToast.message }}</p>
        </div>
        <button class="toast-close" @click="store.clearToast()">✕</button>
      </div>
      <div class="toast-progress">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useNotificationStore } from '../stores/notifications'

const store = useNotificationStore()
const progress = ref(100)
let timer: any = null
const duration = 5000
const step = 50

function startTimer() {
  if (timer) clearInterval(timer)
  progress.value = 100
  const dec = 100 / (duration / step)
  
  timer = setInterval(() => {
    progress.value -= dec
    if (progress.value <= 0) {
      clearInterval(timer)
      store.clearToast()
    }
  }, step)
}

function pauseTimer() {
  clearInterval(timer)
}

function resumeTimer() {
  startTimer()
}

watch(() => store.showToast, (val) => {
  if (val) startTimer()
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped>
.toast-notification {
  position: fixed;
  top: 24px;
  right: 24px;
  width: 360px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 14px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  z-index: 9999;
  overflow: hidden;
}

.toast-content {
  display: flex;
  padding: 16px;
  gap: 14px;
  align-items: flex-start;
}

.toast-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast--success .toast-icon { background: rgba(52, 199, 89, 0.1); color: #34C759; }
.toast--error .toast-icon { background: rgba(255, 59, 48, 0.1); color: #FF3B30; }
.toast--info .toast-icon { background: rgba(0, 122, 255, 0.1); color: #007AFF; }
.toast--warning .toast-icon { background: rgba(255, 149, 0, 0.1); color: #FF9500; }

.toast-body {
  flex: 1;
}

.toast-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--on-surface, #1D1D1F);
}

.toast-msg {
  font-size: 13px;
  color: var(--on-surface-variant, #86868B);
  margin: 0;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  color: var(--on-surface-variant, #86868B);
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  line-height: 1;
}

.toast-progress {
  height: 3px;
  background: rgba(0, 0, 0, 0.05);
  width: 100%;
}

.progress-fill {
  height: 100%;
  background: var(--primary, #007AFF);
  transition: width 0.05s linear;
}

.toast--success .progress-fill { background: #34C759; }
.toast--error .progress-fill { background: #FF3B30; }

.slide-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.7, 0, 0.84, 0);
}

.slide-fade-enter-from {
  transform: translateX(100%) scale(0.9);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
