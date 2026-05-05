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

  /** KM_ADMIN — full platform access including Admin panel. */
  const isAdmin = computed(() =>
    user.value?.roles.includes('KM_ADMIN') ?? false
  )
  /** KM_MANAGER or KM_ADMIN — access to Domains and Ingestion. */
  const isManager = computed(() =>
    user.value?.roles.some(r => r === 'KM_MANAGER' || r === 'KM_ADMIN') ?? false
  )
  /** Any authenticated role — access to Search. */
  const isViewer = computed(() =>
    user.value?.roles.some(r => r === 'KM_VIEWER' || r === 'KM_MANAGER' || r === 'KM_ADMIN') ?? false
  )

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

  /** Clear local session state without triggering BFF/Keycloak logout. */
  function clearSession(): void {
    user.value = null
    error.value = null
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
    isManager,
    isViewer,
    // Actions
    fetchSession,
    login,
    logout,
    clearSession,
    handleAuthCallback,
    clearError,
  }
})
