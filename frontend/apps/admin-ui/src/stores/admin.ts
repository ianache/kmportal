/**
 * Admin UI Pinia Store
 * Manages API keys and admin settings
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiKeysApi, ApiKeyError } from '../services/apiKeysApi'
import type { APIKey, APIKeyCreate, APIKeyCreateResponse, APIKeyListResponse } from '../types'

export const useAdminStore = defineStore('admin', () => {
  // ==================== State ====================
  const apiKeys = ref<APIKey[]>([])
  const totalApiKeys = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Track newly created key (only shown once)
  const newlyCreatedKey = ref<string | null>(null)
  
  // ==================== Getters ====================
  const activeApiKeys = computed(() => 
    apiKeys.value.filter(key => key.is_active)
  )
  
  const revokedApiKeys = computed(() => 
    apiKeys.value.filter(key => !key.is_active)
  )
  
  const totalPages = computed(() => 
    Math.ceil(totalApiKeys.value / pageSize.value)
  )

  // ==================== Actions ====================
  
  /**
   * Load API keys from the server
   */
  async function loadApiKeys(page: number = 1): Promise<void> {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await apiKeysApi.listApiKeys(page, pageSize.value)
      apiKeys.value = response.items
      totalApiKeys.value = response.total
      currentPage.value = response.page
    } catch (err) {
      if (err instanceof ApiKeyError) {
        error.value = err.message
      } else {
        error.value = 'Failed to load API keys'
      }
      console.error('Error loading API keys:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new API key
   */
  async function createApiKey(keyData: APIKeyCreate): Promise<boolean> {
    isLoading.value = true
    error.value = null
    newlyCreatedKey.value = null
    
    try {
      const response = await apiKeysApi.createApiKey(keyData)
      apiKeys.value.unshift(response)
      totalApiKeys.value++
      newlyCreatedKey.value = response.key // Save the plain key (shown only once)
      return true
    } catch (err) {
      if (err instanceof ApiKeyError) {
        error.value = err.message
      } else {
        error.value = 'Failed to create API key'
      }
      console.error('Error creating API key:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Revoke an API key
   */
  async function revokeApiKey(id: string): Promise<boolean> {
    isLoading.value = true
    error.value = null
    
    try {
      await apiKeysApi.revokeApiKey(id)
      // Update local state
      const key = apiKeys.value.find(k => k.id === id)
      if (key) {
        key.is_active = false
      }
      return true
    } catch (err) {
      if (err instanceof ApiKeyError) {
        error.value = err.message
      } else {
        error.value = 'Failed to revoke API key'
      }
      console.error('Error revoking API key:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear the newly created key from display
   */
  function clearNewlyCreatedKey(): void {
    newlyCreatedKey.value = null
  }

  /**
   * Clear any error
   */
  function clearError(): void {
    error.value = null
  }

  return {
    // State
    apiKeys,
    totalApiKeys,
    currentPage,
    pageSize,
    isLoading,
    error,
    newlyCreatedKey,
    
    // Getters
    activeApiKeys,
    revokedApiKeys,
    totalPages,
    
    // Actions
    loadApiKeys,
    createApiKey,
    revokeApiKey,
    clearNewlyCreatedKey,
    clearError,
  }
})
