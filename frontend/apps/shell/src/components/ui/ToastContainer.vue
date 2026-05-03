<template>
  <TransitionGroup name="toast" tag="div" class="toast-container">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      :class="['toast', `toast--${toast.type}`]"
      @click="remove(toast.id)"
    >
      <span class="toast-message">{{ toast.message }}</span>
      <button class="toast-close" @click.stop="remove(toast.id)">✕</button>
    </div>
  </TransitionGroup>
</template>

<script setup lang="ts">
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: number
  message: string
  type: ToastType
  duration: number
}

const toasts = ref<Toast[]>([])
let nextId = 1

function add(message: string, type: ToastType = 'info', duration = 5000): number {
  const id = nextId++
  const toast: Toast = { id, message, type, duration }
  toasts.value.push(toast)
  
  if (duration > 0) {
    setTimeout(() => remove(id), duration)
  }
  
  return id
}

function remove(id: number): void {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

function success(message: string, duration?: number): number {
  return add(message, 'success', duration)
}

function error(message: string, duration?: number): number {
  return add(message, 'error', duration)
}

function warning(message: string, duration?: number): number {
  return add(message, 'warning', duration)
}

function info(message: string, duration?: number): number {
  return add(message, 'info', duration)
}

defineExpose({
  add,
  remove,
  success,
  error,
  warning,
  info,
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-radius: var(--radius-card-sm);
  box-shadow: var(--shadow-floating);
  cursor: pointer;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast--success {
  background: var(--color-primary-fixed);
  color: var(--color-on-primary-fixed);
}

.toast--error {
  background: var(--color-error-container);
  color: var(--color-on-error-container);
}

.toast--warning {
  background: var(--color-tertiary-fixed);
  color: var(--color-on-tertiary-fixed);
}

.toast--info {
  background: var(--color-surface-container-high);
  color: var(--color-on-surface);
}

.toast-message {
  font-family: var(--font-family);
  font-size: 14px;
  font-weight: 500;
}

.toast-close {
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.toast-close:hover {
  opacity: 1;
}

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
