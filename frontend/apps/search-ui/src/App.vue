<template>
  <div class="search-ui">
    <!-- Hero -->
    <div class="hero" :class="{ 'hero--compact': searchStore.hasResults }">
      <template v-if="!searchStore.hasResults">
        <h1 class="hero-title">Semantic Search</h1>
        <p class="hero-desc">Ask anything across your knowledge base.</p>
      </template>
      <div class="search-bar-wrap">
        <div class="search-bar" :class="{ 'search-bar--focused': focused, 'search-bar--loading': searchStore.isLoading }">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 20 20" fill="none"
            stroke="currentColor" stroke-width="1.8">
            <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
          </svg>
          <input
            ref="inputEl"
            v-model="searchStore.query"
            class="search-input"
            placeholder="Search documents, concepts, knowledge..."
            @focus="focused = true"
            @blur="focused = false"
            @keydown.enter="doSearch"
          />
          <button v-if="searchStore.query" class="clear-btn" @click="clearSearch">
            <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="4" y1="4" x2="16" y2="16"/><line x1="16" y1="4" x2="4" y2="16"/>
            </svg>
          </button>
          <button class="search-btn" :disabled="searchStore.isLoading" @click="doSearch">
            {{ searchStore.isLoading ? 'Searching...' : 'Search' }}
          </button>
        </div>
      </div>

      <!-- Suggestions (when empty) -->
      <div v-if="!searchStore.hasResults && !searchStore.isLoading" class="suggestions">
        <span class="suggestions-label">Try:</span>
        <button
          v-for="s in suggestions"
          :key="s"
          class="suggestion-pill"
          @click="searchWithSuggestion(s)"
        >{{ s }}</button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="searchStore.error" class="error-banner">
      <span>{{ searchStore.error }}</span>
      <button @click="searchStore.error = null">✕</button>
    </div>

    <!-- Filters Panel -->
    <div v-if="searchStore.hasResults" class="filters-panel">
      <div class="filters-header">
        <span class="results-count">
          {{ searchStore.total }} results for "<strong>{{ searchStore.query }}</strong>"
        </span>
        <button v-if="hasActiveFilters" class="clear-filters-btn" @click="clearFilters">
          Clear Filters
        </button>
      </div>
      
      <div class="filters-row">
        <!-- Domain Filter -->
        <div class="filter-group">
          <label>Domain</label>
          <div class="filter-chips">
            <button
              v-for="domain in searchStore.domains"
              :key="domain.id"
              class="chip"
              :class="{ 'chip--active': searchStore.selectedDomains.includes(domain.id) }"
              @click="searchStore.toggleDomain(domain.id)"
            >
              {{ domain.name }}
            </button>
          </div>
        </div>
        
        <!-- Type Filter -->
        <div v-if="searchStore.availableTypes.length > 0" class="filter-group">
          <label>Type</label>
          <div class="filter-chips">
            <button
              v-for="type in searchStore.availableTypes"
              :key="type"
              class="chip"
              :class="{ 'chip--active': searchStore.filters.types?.includes(type) }"
              @click="toggleTypeFilter(type)"
            >
              {{ type }}
            </button>
          </div>
        </div>
        
        <!-- Source Filter -->
        <div v-if="searchStore.availableSources.length > 0" class="filter-group">
          <label>Source</label>
          <div class="filter-chips">
            <button
              v-for="source in searchStore.availableSources"
              :key="source"
              class="chip"
              :class="{ 'chip--active': searchStore.filters.sources?.includes(source) }"
              @click="toggleSourceFilter(source)"
            >
              {{ source }}
            </button>
          </div>
        </div>
        
        <!-- Date Filter -->
        <div class="filter-group date-filter">
          <label>Date Range</label>
          <div class="date-inputs">
            <input
              type="date"
              :value="searchStore.filters.date_from"
              @change="updateDateFrom($event)"
              placeholder="From"
            />
            <span>to</span>
            <input
              type="date"
              :value="searchStore.filters.date_to"
              @change="updateDateTo($event)"
              placeholder="To"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Results -->
    <div v-if="searchStore.hasResults" class="results-grid">
      <div
        v-for="result in searchStore.filteredResults"
        :key="result.id"
        class="result-card"
      >
        <div class="result-meta">
          <span class="result-type" :style="getTypeStyle(result.document_type)">
            {{ result.document_type }}
          </span>
          <span class="result-domain">{{ result.domain }}</span>
        </div>
        <h3 class="result-title">{{ result.document_title }}</h3>
        <p class="result-excerpt" v-html="highlightText(result.chunk_text, searchStore.query)"></p>
        <div class="result-footer">
          <span class="result-score">
            <svg width="12" height="12" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
              <polygon points="10,2 12.4,7.4 18.4,7.6 14,11.8 15.6,17.6 10,14.4 4.4,17.6 6,11.8 1.6,7.6 7.6,7.4"/>
            </svg>
            {{ Math.round(result.score * 100) }}% relevance
          </span>
          <span class="result-source">{{ result.source }}</span>
        </div>
      </div>
    </div>
    
    <!-- Pagination -->
    <div v-if="searchStore.total > searchStore.pageSize" class="pagination">
      <button
        :disabled="searchStore.page === 1"
        class="page-btn"
        @click="changePage(searchStore.page - 1)"
      >
        ← Previous
      </button>
      <span class="page-info">Page {{ searchStore.page }} of {{ totalPages }}</span>
      <button
        :disabled="searchStore.page >= totalPages"
        class="page-btn"
        @click="changePage(searchStore.page + 1)"
      >
        Next →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSearchStore } from './stores/search'
import type { SearchFilters } from './types'

const searchStore = useSearchStore()
const focused = ref(false)

const suggestions = [
  'transformer architecture',
  'quantum entanglement',
  'urban planning theory',
  'Bayesian inference',
  'Renaissance political thought',
]

const hasActiveFilters = computed(() => {
  return searchStore.selectedDomains.length > 0 ||
    searchStore.filters.types?.length ||
    searchStore.filters.sources?.length ||
    searchStore.filters.date_from ||
    searchStore.filters.date_to
})

const totalPages = computed(() => {
  return Math.ceil(searchStore.total / searchStore.pageSize)
})

onMounted(() => {
  searchStore.fetchDomains()
})

function doSearch() {
  searchStore.performSearch()
}

function searchWithSuggestion(suggestion: string) {
  searchStore.query = suggestion
  doSearch()
}

function clearSearch() {
  searchStore.clearResults()
}

function clearFilters() {
  searchStore.clearFilters()
}

function toggleTypeFilter(type: string) {
  const currentTypes = searchStore.filters.types || []
  const index = currentTypes.indexOf(type)
  
  if (index === -1) {
    searchStore.setFilters({
      ...searchStore.filters,
      types: [...currentTypes, type]
    })
  } else {
    const newTypes = [...currentTypes]
    newTypes.splice(index, 1)
    searchStore.setFilters({
      ...searchStore.filters,
      types: newTypes.length > 0 ? newTypes : undefined
    })
  }
  
  searchStore.performSearch()
}

function toggleSourceFilter(source: string) {
  const currentSources = searchStore.filters.sources || []
  const index = currentSources.indexOf(source)
  
  if (index === -1) {
    searchStore.setFilters({
      ...searchStore.filters,
      sources: [...currentSources, source]
    })
  } else {
    const newSources = [...currentSources]
    newSources.splice(index, 1)
    searchStore.setFilters({
      ...searchStore.filters,
      sources: newSources.length > 0 ? newSources : undefined
    })
  }
  
  searchStore.performSearch()
}

function updateDateFrom(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchStore.setFilters({
    ...searchStore.filters,
    date_from: value || undefined
  })
  searchStore.performSearch()
}

function updateDateTo(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchStore.setFilters({
    ...searchStore.filters,
    date_to: value || undefined
  })
  searchStore.performSearch()
}

function changePage(newPage: number) {
  searchStore.setPage(newPage)
}

function getTypeStyle(type: string) {
  const colors: Record<string, string> = {
    'Document': '#007AFF',
    'PDF': '#FF3B30',
    'Text': '#34C759',
    'Markdown': '#5856D6',
    'Code': '#FF9500',
  }
  const color = colors[type] || '#8E8E93'
  return {
    background: color + '18',
    color: color
  }
}

function highlightText(text: string, query: string): string {
  if (!query.trim()) return text
  
  const words = query.trim().split(/\s+/)
  let highlighted = text
  
  words.forEach(word => {
    const regex = new RegExp(`(${escapeRegex(word)})`, 'gi')
    highlighted = highlighted.replace(regex, '<mark>$1</mark>')
  })
  
  return highlighted
}

function escapeRegex(string: string): string {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
</script>

<style scoped>
.search-ui {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

/* Hero */
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 40px 40px;
  text-align: center;
  transition: padding 0.3s;
}

.hero--compact {
  padding: 32px 40px 24px;
}

.hero-title {
  font-size: 40px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text, #1D1D1F);
  margin-bottom: 8px;
}

.hero-desc {
  font-size: 17px;
  color: var(--text-2, #86868B);
  margin-bottom: 32px;
}

.search-bar-wrap {
  width: 100%;
  max-width: 640px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--surface, #fff);
  border: 1.5px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.search-bar--focused {
  border-color: var(--primary, #007AFF);
  box-shadow: 0 0 0 3px rgba(0,122,255,0.12), 0 2px 8px rgba(0,0,0,0.06);
}

.search-bar--loading {
  opacity: 0.8;
}

.search-icon { 
  color: var(--text-2, #86868B); 
  flex-shrink: 0; 
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  font-family: inherit;
  color: var(--text, #1D1D1F);
  background: transparent;
}

.search-input::placeholder { 
  color: var(--text-2, #86868B); 
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0,0,0,0.06);
  color: var(--text-2, #86868B);
  cursor: pointer;
  border: none;
  transition: background 0.12s;
  flex-shrink: 0;
}

.clear-btn:hover { 
  background: rgba(0,0,0,0.12); 
}

.search-btn {
  background: var(--primary, #007AFF);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  padding: 7px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-family: inherit;
  flex-shrink: 0;
  transition: opacity 0.12s;
}

.search-btn:hover:not(:disabled) { 
  opacity: 0.88; 
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Suggestions */
.suggestions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestions-label {
  font-size: 13px;
  color: var(--text-2, #86868B);
}

.suggestion-pill {
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  font-size: 13px;
  color: var(--text, #1D1D1F);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, border-color 0.12s;
}

.suggestion-pill:hover {
  background: var(--primary-soft, rgba(0,122,255,0.1));
  border-color: var(--primary, #007AFF);
  color: var(--primary, #007AFF);
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 40px 20px;
  padding: 12px 16px;
  background: #ffdad6;
  border: 1px solid #ba1a1a;
  border-radius: 8px;
  color: #ba1a1a;
}

.error-banner button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

/* Filters Panel */
.filters-panel {
  padding: 0 40px 20px;
  border-bottom: 1px solid var(--border, #E5E5E7);
  margin-bottom: 20px;
}

.filters-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.results-count {
  font-size: 14px;
  color: var(--text-2, #86868B);
}

.results-count strong { 
  color: var(--text, #1D1D1F); 
}

.clear-filters-btn {
  font-size: 13px;
  color: var(--primary, #007AFF);
  background: none;
  border: none;
  cursor: pointer;
}

.clear-filters-btn:hover {
  text-decoration: underline;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-2, #86868B);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  color: var(--text-2, #86868B);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s;
}

.chip:hover { 
  background: rgba(0,0,0,0.04); 
  color: var(--text, #1D1D1F); 
}

.chip--active {
  background: var(--primary-soft, rgba(0,122,255,0.1));
  border-color: var(--primary, #007AFF);
  color: var(--primary, #007AFF);
}

.date-filter .date-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-filter input {
  padding: 6px 10px;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 6px;
  font-size: 13px;
}

/* Results Grid */
.results-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 40px 40px;
}

.result-card {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  box-shadow: var(--shadow-card, 0 1px 2px rgba(0,0,0,0.04));
  transition: box-shadow 0.15s, transform 0.15s;
}

.result-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.09);
  transform: translateY(-1px);
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-type {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  letter-spacing: 0.02em;
}

.result-domain {
  font-size: 12px;
  color: var(--text-2, #86868B);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  letter-spacing: -0.01em;
}

.result-excerpt {
  font-size: 14px;
  color: var(--text-2, #86868B);
  line-height: 1.5;
}

.result-excerpt :deep(mark) {
  background: rgba(0, 122, 255, 0.2);
  color: inherit;
  padding: 1px 2px;
  border-radius: 2px;
}

.result-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--border, #E5E5E7);
}

.result-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--primary, #007AFF);
}

.result-source {
  font-size: 12px;
  color: var(--text-2, #86868B);
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px 40px;
  border-top: 1px solid var(--border, #E5E5E7);
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 8px;
  background: var(--surface, #fff);
  color: var(--text, #1D1D1F);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.12s;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--primary, #007AFF);
  color: var(--primary, #007AFF);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: var(--text-2, #86868B);
}
</style>
