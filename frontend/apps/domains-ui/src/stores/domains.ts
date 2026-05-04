import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { domainsApi } from '../services/domainsApi'
import type { Domain, Document, CreateDomainRequest, UpdateDomainRequest } from '../types'

export const useDomainsStore = defineStore('domains', () => {
  // State
  const domains = ref<Domain[]>([])
  const selectedDomain = ref<Domain | null>(null)
  const documents = ref<Document[]>([])
  const isLoading = ref(false)
  const isLoadingDocuments = ref(false)
  const error = ref<string | null>(null)
  const isCreating = ref(false)
  const isEditing = ref(false)

  // Getters
  const hasDomains = computed(() => domains.value.length > 0)
  const hasError = computed(() => error.value !== null)
  const sortedDomains = computed(() => {
    return [...domains.value].sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  })

  // Actions
  async function fetchDomains() {
    isLoading.value = true
    error.value = null
    
    try {
      domains.value = await domainsApi.getDomains()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch domains'
    } finally {
      isLoading.value = false
    }
  }

  async function selectDomain(domainId: string) {
    isLoadingDocuments.value = true
    error.value = null

    try {
      const [domain, docs] = await Promise.all([
        domainsApi.getDomain(domainId),
        domainsApi.getDomainDocuments(domainId)
      ])
      selectedDomain.value = domain
      documents.value = docs
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch domain details'
      selectedDomain.value = null
      documents.value = []
    } finally {
      isLoadingDocuments.value = false
    }
  }

  function clearSelection() {
    selectedDomain.value = null
    documents.value = []
  }

  async function createDomain(data: CreateDomainRequest) {
    isCreating.value = true
    error.value = null
    
    try {
      const newDomain = await domainsApi.createDomain(data)
      domains.value.unshift(newDomain)
      return newDomain
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create domain'
      throw err
    } finally {
      isCreating.value = false
    }
  }

  async function updateDomain(domainId: string, data: UpdateDomainRequest) {
    isEditing.value = true
    error.value = null
    
    try {
      const updated = await domainsApi.updateDomain(domainId, data)
      const index = domains.value.findIndex(d => d.id === domainId)
      if (index !== -1) {
        domains.value[index] = updated
      }
      if (selectedDomain.value?.id === domainId) {
        selectedDomain.value = updated
      }
      return updated
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update domain'
      throw err
    } finally {
      isEditing.value = false
    }
  }

  async function deleteDomain(domainId: string) {
    error.value = null
    
    try {
      await domainsApi.deleteDomain(domainId)
      domains.value = domains.value.filter(d => d.id !== domainId)
      if (selectedDomain.value?.id === domainId) {
        selectedDomain.value = null
        documents.value = []
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete domain'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    domains,
    selectedDomain,
    documents,
    isLoading,
    isLoadingDocuments,
    error,
    isCreating,
    isEditing,
    // Getters
    hasDomains,
    hasError,
    sortedDomains,
    // Actions
    fetchDomains,
    selectDomain,
    clearSelection,
    createDomain,
    updateDomain,
    deleteDomain,
    clearError,
  }
})
