import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { domainsApi as api } from '../services/domainsApi'
import type { Domain, Document, DocumentFilters } from '../types/domains'

export const useDomainsStore = defineStore('domains', () => {
  // State
  const domains = ref<Domain[]>([])
  const selectedDomain = ref<Domain | null>(null)
  const documents = ref<Document[]>([])
  const isLoading = ref(false)
  const isLoadingDocuments = ref(false)
  const error = ref<string | null>(null)
  
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    pages: 0
  })

  const documentPagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    pages: 0
  })

  const documentFilters = ref<DocumentFilters>({
    status: undefined,
    type: undefined,
    query: undefined
  })

  // Getters
  const hasDomains = computed(() => domains.value.length > 0)
  const hasSelectedDomain = computed(() => selectedDomain.value !== null)
  
  const sortedDomains = computed(() => {
    return [...domains.value].sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  })

  const filteredDocuments = computed(() => documents.value)

  // Actions
  async function loadDomains() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.getDomains(pagination.value.page, pagination.value.pageSize)
      domains.value = response.items
      pagination.value.total = response.total
      pagination.value.pages = response.pages
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load domains'
    } finally {
      isLoading.value = false
    }
  }

  async function loadDocuments(domainId: string) {
    isLoadingDocuments.value = true
    error.value = null
    
    try {
      const response = await api.getDomainDocuments(
        domainId, 
        documentPagination.value.page, 
        documentPagination.value.pageSize,
        documentFilters.value
      )
      documents.value = response.items
      documentPagination.value.total = response.total
      documentPagination.value.pages = response.pages
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load documents'
    } finally {
      isLoadingDocuments.value = false
    }
  }

  async function selectDomain(domainId: string) {
    isLoadingDocuments.value = true
    error.value = null

    try {
      const domain = await api.getDomain(domainId)
      selectedDomain.value = domain
      documentPagination.value.page = 1
      await loadDocuments(domainId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to select domain'
      selectedDomain.value = null
      documents.value = []
    } finally {
      isLoadingDocuments.value = false
    }
  }

  function setDocumentFilter(key: keyof DocumentFilters, value: any) {
    documentFilters.value[key] = value
    documentPagination.value.page = 1
    if (selectedDomain.value) {
      loadDocuments(selectedDomain.value.id)
    }
  }

  function clearFilters() {
    documentFilters.value = {
      status: undefined,
      type: undefined,
      query: undefined
    }
    documentPagination.value.page = 1
    if (selectedDomain.value) {
      loadDocuments(selectedDomain.value.id)
    }
  }

  function clearSelection() {
    selectedDomain.value = null
    documents.value = []
    error.value = null
  }

  function setPage(page: number) {
    pagination.value.page = page
    loadDomains()
  }

  function setDocumentPage(page: number) {
    documentPagination.value.page = page
    if (selectedDomain.value) {
      loadDocuments(selectedDomain.value.id)
    }
  }

  return {
    // State
    domains,
    selectedDomain,
    documents,
    isLoading,
    isLoadingDocuments,
    error,
    pagination,
    documentPagination,
    documentFilters,
    // Getters
    hasDomains,
    hasSelectedDomain,
    sortedDomains,
    filteredDocuments,
    // Actions
    loadDomains,
    loadDocuments,
    selectDomain,
    setDocumentFilter,
    clearFilters,
    clearSelection,
    setPage,
    setDocumentPage
  }
})
