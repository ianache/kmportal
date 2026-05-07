/**
 * Admin UI Pinia Store
 * Manages API keys and admin settings
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiKeysApi } from '../services/apiKeysApi'
import { domainsApi } from '../services/domainsApi'
import type { 
  APIKey, APIKeyCreate, APIKeyCreateResponse, APIKeyListResponse,
  Domain, DomainCreate, DomainUpdate, DomainAccessGrant, DomainAccessResponse
} from '../types'

export const useAdminStore = defineStore('admin', () => {
  // ==================== State ====================
  // API Keys
  const apiKeys = ref<APIKey[]>([])
  const totalApiKeys = ref(0)
  const apiKeysPage = ref(1)
  
  // Domains
  const domains = ref<Domain[]>([])
  const totalDomains = ref(0)
  const domainsPage = ref(1)
  
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
  
  const apiKeysTotalPages = computed(() => 
    Math.ceil(totalApiKeys.value / pageSize.value)
  )

  const domainsTotalPages = computed(() => 
    Math.ceil(totalDomains.value / pageSize.value)
  )

  // ==================== Actions ====================
  
  // --- API Keys Actions ---

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
      apiKeysPage.value = response.page
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load API keys'
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
      error.value = err instanceof Error ? err.message : 'Failed to create API key'
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
      error.value = err instanceof Error ? err.message : 'Failed to revoke API key'
      console.error('Error revoking API key:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // --- Domains Actions ---

  /**
   * Load domains from the server
   */
  async function loadDomains(page: number = 1): Promise<void> {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsApi.listDomains(page, pageSize.value)
      domains.value = response.items
      totalDomains.value = response.total
      domainsPage.value = response.page
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load domains'
      console.error('Error loading domains:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new domain
   */
  async function createDomain(data: DomainCreate): Promise<boolean> {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsApi.createDomain(data)
      domains.value.unshift(response)
      totalDomains.value++
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create domain'
      console.error('Error creating domain:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update a domain
   */
  async function updateDomain(id: string, data: DomainUpdate): Promise<boolean> {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsApi.updateDomain(id, data)
      const index = domains.value.findIndex(d => d.id === id)
      if (index !== -1) {
        domains.value[index] = response
      }
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update domain'
      console.error('Error updating domain:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete a domain
   */
  async function deleteDomain(id: string): Promise<boolean> {
    isLoading.value = true
    error.value = null
    
    try {
      await domainsApi.deleteDomain(id)
      domains.value = domains.value.filter(d => d.id !== id)
      totalDomains.value--
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete domain'
      console.error('Error deleting domain:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // --- Domain Access Actions ---

  /**
   * Load access grants for a domain
   */
  async function loadDomainAccess(domainId: string): Promise<DomainAccessResponse[]> {
    isLoading.value = true
    error.value = null
    
    try {
      return await domainsApi.listAccess(domainId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load domain access'
      console.error('Error loading domain access:', err)
      return []
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Grant access to a domain
   */
  async function grantDomainAccess(domainId: string, data: DomainAccessGrant): Promise<boolean> {
    isLoading.value = true
    error.value = null
    
    try {
      await domainsApi.grantAccess(domainId, data)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to grant domain access'
      console.error('Error granting domain access:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Revoke access from a domain
   */
  async function revokeDomainAccess(domainId: string, userId: string): Promise<boolean> {
    isLoading.value = true
    error.value = null
    
    try {
      await domainsApi.revokeAccess(domainId, userId)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to revoke domain access'
      console.error('Error revoking domain access:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // --- UI Helpers ---

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
    apiKeysPage,
    domains,
    totalDomains,
    domainsPage,
    pageSize,
    isLoading,
    error,
    newlyCreatedKey,
    
    // Getters
    activeApiKeys,
    revokedApiKeys,
    apiKeysTotalPages,
    domainsTotalPages,
    
    // Actions
    loadApiKeys,
    createApiKey,
    revokeApiKey,
    loadDomains,
    createDomain,
    updateDomain,
    deleteDomain,
    loadDomainAccess,
    grantDomainAccess,
    revokeDomainAccess,
    clearNewlyCreatedKey,
    clearError,
  }
})
