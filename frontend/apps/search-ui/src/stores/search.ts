import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { searchApi } from '../services/searchApi'
import type { SearchResult, SearchFilters, SearchRequest, Domain } from '../types'

export const useSearchStore = defineStore('search', () => {
  // State
  const query = ref('')
  const results = ref<SearchResult[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const domains = ref<Domain[]>([])
  const selectedDomains = ref<string[]>([])
  const filters = ref<SearchFilters>({})
  
  // Getters
  const hasResults = computed(() => results.value.length > 0)
  const hasError = computed(() => error.value !== null)
  
  const availableTypes = computed(() => {
    const types = new Set<string>()
    results.value.forEach(r => types.add(r.document_type))
    return Array.from(types)
  })
  
  const availableSources = computed(() => {
    const sources = new Set<string>()
    results.value.forEach(r => sources.add(r.source))
    return Array.from(sources)
  })
  
  const filteredResults = computed(() => {
    let filtered = results.value
    
    if (filters.value.types?.length) {
      filtered = filtered.filter(r => filters.value.types?.includes(r.document_type))
    }
    
    if (filters.value.sources?.length) {
      filtered = filtered.filter(r => filters.value.sources?.includes(r.source))
    }
    
    return filtered
  })

  // Actions
  async function performSearch(searchQuery?: string) {
    if (searchQuery !== undefined) {
      query.value = searchQuery
    }
    
    if (!query.value.trim()) {
      results.value = []
      return
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      const request: SearchRequest = {
        query: query.value,
        domains: selectedDomains.value.length > 0 ? selectedDomains.value : undefined,
        filters: filters.value,
        page: page.value,
        page_size: pageSize.value,
      }
      
      const response = await searchApi.search(request)
      results.value = response.results
      total.value = response.total
      page.value = response.page
      pageSize.value = response.page_size
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Search failed'
      results.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDomains() {
    try {
      domains.value = await searchApi.getDomains()
    } catch (err) {
      console.error('Failed to fetch domains:', err)
    }
  }

  function setPage(newPage: number) {
    page.value = newPage
    performSearch()
  }

  function setPageSize(size: number) {
    pageSize.value = size
    page.value = 1
    performSearch()
  }

  function setFilters(newFilters: SearchFilters) {
    filters.value = { ...newFilters }
    page.value = 1
  }

  function toggleDomain(domainId: string) {
    const index = selectedDomains.value.indexOf(domainId)
    if (index === -1) {
      selectedDomains.value.push(domainId)
    } else {
      selectedDomains.value.splice(index, 1)
    }
    page.value = 1
    performSearch()
  }

  function clearFilters() {
    filters.value = {}
    selectedDomains.value = []
    page.value = 1
    performSearch()
  }

  function clearResults() {
    query.value = ''
    results.value = []
    total.value = 0
    error.value = null
  }

  return {
    // State
    query,
    results,
    total,
    page,
    pageSize,
    isLoading,
    error,
    domains,
    selectedDomains,
    filters,
    // Getters
    hasResults,
    hasError,
    availableTypes,
    availableSources,
    filteredResults,
    // Actions
    performSearch,
    fetchDomains,
    setPage,
    setPageSize,
    setFilters,
    toggleDomain,
    clearFilters,
    clearResults,
  }
})
