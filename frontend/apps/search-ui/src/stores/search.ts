import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { searchApi } from '../services/searchApi'
import type { SearchResult, SearchFilters, SearchParams, Domain } from '../types'

export const useSearchStore = defineStore('search', () => {
  // State
  const query = ref('')
  const results = ref<SearchResult[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const searchTimeMs = ref(0)
  const isLoading = ref(false)
  const isSearchActive = ref(false)
  const error = ref<string | null>(null)
  const availableDomains = ref<Domain[]>([])
  const selectedDomains = ref<string[]>([])
  const filters = ref<SearchFilters>({
    types: [],
    sources: [],
    date_from: undefined,
    date_to: undefined
  })
  
  // Getters
  const hasResults = computed(() => results.value.length > 0)
  const hasError = computed(() => error.value !== null)
  
  const activeFiltersCount = computed(() => {
    let count = selectedDomains.value.length
    if (filters.value.types?.length) count += filters.value.types.length
    if (filters.value.sources?.length) count += filters.value.sources.length
    if (filters.value.date_from) count += 1
    if (filters.value.date_to) count += 1
    return count
  })

  const availableTypes = computed(() => {
    const types = new Set<string>()
    results.value.forEach(r => {
      if (r.metadata?.type) types.add(r.metadata.type)
      // Fallback to document_type if metadata.type is not present
      else if ((r as any).document_type) types.add((r as any).document_type)
    })
    return Array.from(types)
  })
  
  const availableSources = computed(() => {
    const sources = new Set<string>()
    results.value.forEach(r => {
      if (r.metadata?.source) sources.add(r.metadata.source)
    })
    return Array.from(sources)
  })
  
  const filteredResults = computed(() => {
    let filtered = results.value
    
    if (filters.value.types?.length) {
      filtered = filtered.filter(r => {
        const type = r.metadata?.type || (r as any).document_type
        return filters.value.types?.includes(type)
      })
    }
    
    if (filters.value.sources?.length) {
      filtered = filtered.filter(r => {
        const source = r.metadata?.source
        return source && filters.value.sources?.includes(source)
      })
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
      total.value = 0
      isSearchActive.value = false
      return
    }
    
    isLoading.value = true
    isSearchActive.value = true
    error.value = null
    
    try {
      const params: SearchParams = {
        q: query.value,
        domains: selectedDomains.value.length > 0 ? selectedDomains.value : undefined,
        page: page.value,
        page_size: pageSize.value,
        // Backend filters mapping
        type: filters.value.types?.length === 1 ? filters.value.types[0] : undefined,
        source: filters.value.sources?.length === 1 ? filters.value.sources[0] : undefined,
        date_from: filters.value.date_from,
        date_to: filters.value.date_to,
      }
      
      const response = await searchApi.search(params)
      results.value = response.results
      total.value = response.total
      page.value = response.page
      pageSize.value = response.page_size
      searchTimeMs.value = response.search_time_ms
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Search failed'
      results.value = []
      total.value = 0
    } finally {
      isLoading.value = false
    }
  }

  async function loadDomains() {
    try {
      availableDomains.value = await searchApi.getDomains()
    } catch (err) {
      console.error('Failed to load domains:', err)
    }
  }

  function setPage(newPage: number) {
    page.value = newPage
    performSearch()
  }

  function setFilter(key: keyof SearchFilters, value: any) {
    (filters.value as any)[key] = value
    page.value = 1
    performSearch()
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
    filters.value = {
      types: [],
      sources: [],
      date_from: undefined,
      date_to: undefined
    }
    selectedDomains.value = []
    page.value = 1
    performSearch()
  }

  function clearResults() {
    query.value = ''
    results.value = []
    total.value = 0
    isSearchActive.value = false
    error.value = null
    searchTimeMs.value = 0
  }

  function highlightText(text: string, queryStr: string): string {
    if (!queryStr.trim()) return text
    
    // Simple highlighting for now, can be improved
    const words = queryStr.trim().split(/\s+/).filter(w => w.length > 2)
    if (words.length === 0) return text

    let highlighted = text
    const escapedWords = words.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    const regex = new RegExp(`(${escapedWords.join('|')})`, 'gi')
    
    return highlighted.replace(regex, '<mark>$1</mark>')
  }

  return {
    // State
    query,
    results,
    total,
    page,
    pageSize,
    searchTimeMs,
    isLoading,
    isSearchActive,
    error,
    availableDomains,
    selectedDomains,
    filters,
    // Getters
    hasResults,
    hasError,
    activeFiltersCount,
    availableTypes,
    availableSources,
    filteredResults,
    // Actions
    performSearch,
    loadDomains,
    setPage,
    setFilter,
    toggleDomain,
    clearFilters,
    clearResults,
    highlightText,
  }
})
