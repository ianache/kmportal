import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { hybridSearchApi } from '../services/hybridSearchApi'
import type { HybridSearchResult } from '../types/semantic'

export const useHybridSearchStore = defineStore('hybridSearch', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  const isHybridMode = ref(false)
  const query = ref('')
  const selectedDomainId = ref<string | null>(null)
  const results = ref<HybridSearchResult[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ── Getters ────────────────────────────────────────────────────────────────
  const canSearch = computed(
    () => isHybridMode.value && !!query.value.trim() && !!selectedDomainId.value
  )

  const domainRequired = computed(
    () => isHybridMode.value && !selectedDomainId.value
  )

  const hasResults = computed(() => results.value.length > 0)

  // ── Actions ────────────────────────────────────────────────────────────────
  function toggleHybridMode() {
    isHybridMode.value = !isHybridMode.value
    results.value = []
    error.value = null
  }

  function selectDomain(domainId: string | null) {
    selectedDomainId.value = domainId
  }

  async function performHybridSearch(searchQuery?: string) {
    if (searchQuery !== undefined) query.value = searchQuery
    if (!canSearch.value) return

    isLoading.value = true
    error.value = null

    try {
      results.value = await hybridSearchApi.search({
        q: query.value,
        domain_id: selectedDomainId.value!,
        limit: 20,
      })
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Hybrid search failed'
      results.value = []
    } finally {
      isLoading.value = false
    }
  }

  function clearResults() {
    results.value = []
    error.value = null
    query.value = ''
  }

  return {
    isHybridMode,
    query,
    selectedDomainId,
    results,
    isLoading,
    error,
    canSearch,
    domainRequired,
    hasResults,
    toggleHybridMode,
    selectDomain,
    performHybridSearch,
    clearResults,
  }
})
