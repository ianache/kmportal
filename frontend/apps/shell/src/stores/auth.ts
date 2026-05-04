import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface User {
  id: string
  email: string
  roles: string[]
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

const BFF_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:3000'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.roles.includes('km-admin') ?? false)
  const isReader = computed(() => user.value?.roles.includes('km-reader') ?? false)

  // Actions
  async function fetchSession(): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${BFF_URL}/auth/session`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        if (data.authenticated && data.user) {
          user.value = data.user
          return true
        }
      }

      user.value = null
      return false
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch session'
      user.value = null
      return false
    } finally {
      isLoading.value = false
    }
  }

  function login(): void {
    // Redirect to BFF login endpoint
    window.location.href = `${BFF_URL}/auth/login`
  }

  function logout(): void {
    user.value = null
    window.location.href = `${BFF_URL}/auth/logout`
  }

  function handleAuthCallback(success: boolean, errorMsg?: string): void {
    if (success) {
      // Fetch session to get user info
      fetchSession()
    } else {
      error.value = errorMsg || 'Authentication failed'
      user.value = null
    }
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    user,
    isLoading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    isReader,
    // Actions
    fetchSession,
    login,
    logout,
    handleAuthCallback,
    clearError,
  }
})
