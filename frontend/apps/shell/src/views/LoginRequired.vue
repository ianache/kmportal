<template>
  <div class="login-required">
    <div class="login-card">
      <h1>Knowledge Management Center</h1>
      <p>Please sign in to access the platform</p>
      
      <button 
        @click="login" 
        class="btn-primary"
        :disabled="authStore.isLoading"
      >
        {{ authStore.isLoading ? 'Signing in...' : 'Sign In' }}
      </button>
      
      <p v-if="authStore.error" class="error-message">
        {{ authStore.error }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

function login() {
  authStore.clearError()
  authStore.login()
}
</script>

<style scoped>
.login-required {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--color-background);
  padding: 24px;
}

.login-card {
  background: var(--color-surface);
  border: 1px solid var(--color-outline-variant);
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

h1 {
  font-family: var(--font-family);
  font-size: 28px;
  font-weight: 700;
  color: var(--color-on-surface);
  margin-bottom: 12px;
}

p {
  font-family: var(--font-family);
  font-size: 16px;
  color: var(--color-on-surface-variant);
  margin-bottom: 32px;
}

.btn-primary {
  font-family: var(--font-family);
  font-size: 17px;
  font-weight: 500;
  padding: 14px 32px;
  background: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background: var(--color-error-container);
  color: var(--color-on-error-container);
  border-radius: 8px;
  font-size: 14px;
}
</style>
