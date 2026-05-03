<template>
  <div class="auth-callback">
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Completing authentication...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <h2>Authentication Failed</h2>
      <p>{{ error }}</p>
      <button @click="retryLogin" class="btn-primary">
        Try Again
      </button>
    </div>
    
    <div v-else class="success-container">
      <h2>Welcome!</h2>
      <p>Authentication successful. Redirecting...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  const success = route.query.success === 'true'
  const errorMsg = route.query.error as string | undefined

  if (success) {
    // Fetch session to confirm authentication
    const hasSession = await authStore.fetchSession()
    
    if (hasSession) {
      loading.value = false
      // Redirect to home after successful auth
      setTimeout(() => {
        router.push('/')
      }, 1000)
    } else {
      loading.value = false
      error.value = 'Could not verify session. Please try again.'
    }
  } else {
    loading.value = false
    error.value = errorMsg || 'Authentication was cancelled or failed.'
    authStore.handleAuthCallback(false, error.value)
  }
})

function retryLogin() {
  authStore.login()
}
</script>

<style scoped>
.auth-callback {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--color-background);
  padding: 24px;
}

.loading-container,
.error-container,
.success-container {
  text-align: center;
  max-width: 400px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-surface-container);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 24px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

h2 {
  font-family: var(--font-family);
  font-size: 24px;
  font-weight: 600;
  color: var(--color-on-surface);
  margin-bottom: 16px;
}

p {
  font-family: var(--font-family);
  font-size: 16px;
  color: var(--color-on-surface-variant);
  margin-bottom: 24px;
}

.btn-primary {
  font-family: var(--font-family);
  font-size: 16px;
  font-weight: 500;
  padding: 12px 24px;
  background: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.btn-primary:hover {
  opacity: 0.9;
}
</style>
