<template>
  <div class="search-app">
    <!-- Search Bar Section -->
    <header class="search-header" :class="{ 'search-header--compact': searchStore.hasResults }">
      <div class="search-container">
        <template v-if="!searchStore.hasResults">
          <h1 class="display-lg">Semantic Search</h1>
          <p class="body-base subtitle">Ask anything across your knowledge base.</p>
        </template>
        
        <div class="search-input-group">
          <div class="search-input-wrapper" :class="{ 'is-focused': isSearchFocused }">
            <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input 
              v-model="searchStore.query"
              type="text" 
              class="search-input" 
              placeholder="Search documents, concepts, knowledge..."
              @focus="isSearchFocused = true"
              @blur="isSearchFocused = false"
              @keydown.enter="handleSearch"
            >
            <button v-if="searchStore.query" class="clear-btn" @click="searchStore.clearResults()">
              ✕
            </button>
          </div>
          <BaseButton 
            primary 
            :loading="searchStore.isLoading" 
            class="search-btn"
            @click="handleSearch"
          >
            Search
          </BaseButton>
        </div>

        <div v-if="!searchStore.hasResults && !searchStore.isLoading" class="search-suggestions">
          <span class="label-caps">Try searching for:</span>
          <div class="suggestion-chips">
            <button 
              v-for="s in suggestions" 
              :key="s" 
              class="suggestion-chip"
              @click="searchWithSuggestion(s)"
            >
              {{ s }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main v-if="searchStore.hasResults || searchStore.isLoading" class="search-main">
      <div class="content-layout">
        <!-- Sidebar Filters -->
        <aside class="search-sidebar">
          <SearchFilters />
        </aside>

        <!-- Results Area -->
        <section class="results-area">
          <div v-if="searchStore.isLoading" class="loading-state">
            <div class="skeleton-list">
              <div v-for="i in 3" :key="i" class="skeleton-card"></div>
            </div>
          </div>

          <div v-else-if="searchStore.hasError" class="error-state">
            <BaseCard class="error-card">
              <p class="error-msg">{{ searchStore.error }}</p>
              <BaseButton secondary @click="handleSearch">Retry</BaseButton>
            </BaseCard>
          </div>

          <div v-else-if="searchStore.hasResults" class="results-container">
            <div class="results-header">
              <span class="results-info">
                Found {{ searchStore.total }} results 
                <span class="search-time">({{ searchStore.searchTimeMs }}ms)</span>
              </span>
            </div>

            <div class="results-list">
              <SearchResultCard 
                v-for="result in searchStore.filteredResults" 
                :key="result.chunk_id"
                :result="result"
                @open-document="handleOpenDocument"
              />
            </div>

            <div v-if="searchStore.total > searchStore.pageSize" class="pagination">
              <button 
                class="page-btn" 
                :disabled="searchStore.page === 1"
                @click="searchStore.setPage(searchStore.page - 1)"
              >
                ← Previous
              </button>
              <span class="page-info">Page {{ searchStore.page }} of {{ totalPages }}</span>
              <button 
                class="page-btn" 
                :disabled="searchStore.page >= totalPages"
                @click="searchStore.setPage(searchStore.page + 1)"
              >
                Next →
              </button>
            </div>
          </div>

          <div v-else class="empty-state">
            <h3 class="headline-md">No results found</h3>
            <p class="body-base">Try adjusting your filters or search terms.</p>
            <BaseButton secondary @click="searchStore.clearFilters()">Clear all filters</BaseButton>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSearchStore } from './stores/search'
import SearchFilters from './components/SearchFilters.vue'
import SearchResultCard from './components/SearchResultCard.vue'
import BaseButton from 'shell/BaseButton'
import BaseCard from 'shell/BaseCard'

const searchStore = useSearchStore()
const isSearchFocused = ref(false)

const suggestions = [
  'Vector embeddings',
  'Module Federation',
  'Micro-frontend architecture',
  'FastAPI best practices',
  'Keycloak integration'
]

const totalPages = computed(() => Math.ceil(searchStore.total / searchStore.pageSize))

onMounted(() => {
  searchStore.loadDomains()
})

function handleSearch() {
  searchStore.performSearch()
}

function searchWithSuggestion(suggestion: string) {
  searchStore.query = suggestion
  handleSearch()
}

function handleOpenDocument(id: string) {
  console.log('Opening document:', id)
  // Logic to open document (e.g., navigate to document view)
}
</script>

<style scoped>
.search-app {
  min-height: 100%;
  background: var(--background, #f9f9ff);
  color: var(--on-background, #181c23);
  font-family: Inter, sans-serif;
}

/* Header */
.search-header {
  padding: 80px 24px 40px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  justify-content: center;
}

.search-header--compact {
  padding: 32px 24px 24px;
  border-bottom: 1px solid var(--outline-variant, #E5E5E7);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: saturate(180%) blur(20px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.search-container {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.display-lg {
  font-size: 48px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  text-align: center;
}

.subtitle {
  color: var(--on-surface-variant, #86868B);
  margin: -8px 0 0;
  text-align: center;
}

.search-input-group {
  display: flex;
  width: 100%;
  gap: 12px;
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background: var(--surface-container-lowest, #ffffff);
  border: 1px solid var(--outline-variant, #E5E5E7);
  border-radius: 12px;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.search-input-wrapper.is-focused {
  border-color: var(--primary, #007AFF);
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1), 0 2px 8px rgba(0,0,0,0.05);
}

.search-icon {
  color: var(--on-surface-variant, #86868B);
  margin-right: 12px;
}

.search-input {
  flex: 1;
  height: 48px;
  border: none;
  outline: none;
  font-size: 16px;
  background: transparent;
  color: var(--on-surface, #1D1D1F);
}

.clear-btn {
  background: none;
  border: none;
  color: var(--on-surface-variant, #86868B);
  cursor: pointer;
  padding: 4px;
  font-size: 18px;
}

.search-btn {
  height: 50px;
  padding: 0 24px;
  border-radius: 12px;
}

/* Suggestions */
.search-suggestions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.label-caps {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--on-surface-variant, #86868B);
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.suggestion-chip {
  padding: 6px 16px;
  border-radius: 999px;
  background: var(--surface-container-low, #f1f3fe);
  border: 1px solid var(--outline-variant, #E5E5E7);
  font-size: 14px;
  color: var(--on-surface-variant, #414755);
  cursor: pointer;
  transition: all 0.15s;
}

.suggestion-chip:hover {
  background: var(--surface-container, #ecedf9);
  color: var(--on-surface, #1D1D1F);
  border-color: var(--outline, #717786);
}

/* Main Content Layout */
.search-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 24px;
}

.content-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 40px;
}

.search-sidebar {
  position: sticky;
  top: 120px;
  height: fit-content;
}

/* Results Area */
.results-area {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--outline-variant, #E5E5E7);
}

.results-info {
  font-size: 15px;
  font-weight: 500;
  color: var(--on-surface, #1D1D1F);
}

.search-time {
  font-size: 13px;
  color: var(--on-surface-variant, #86868B);
  margin-left: 8px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding-top: 32px;
}

.page-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #ffffff);
  color: var(--on-surface, #1D1D1F);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
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
  color: var(--on-surface-variant, #86868B);
}

/* Skeleton Loading */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-card {
  height: 160px;
  background: var(--surface-container, #ecedf9);
  border-radius: 12px;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* Empty/Error States */
.empty-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  text-align: center;
  gap: 16px;
}

.error-card {
  max-width: 400px;
  padding: 32px;
}

.error-msg {
  color: var(--error, #ba1a1a);
  margin-bottom: 16px;
}

/* Responsive */
@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
  
  .search-sidebar {
    position: static;
  }
}
</style>
