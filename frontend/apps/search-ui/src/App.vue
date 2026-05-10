<template>
  <div class="search-app">
    <!-- ── Header / Search bar ──────────────────────────────────────────── -->
    <header class="search-header" :class="{ 'search-header--compact': isSearchActive }">
      <div class="search-container">

        <template v-if="!isSearchActive">
          <h1 class="display-lg">Semantic Search</h1>
          <p class="body-base subtitle">Ask anything across your knowledge base.</p>
        </template>

        <!-- Mode toggle -->
        <div class="mode-toggle">
          <button
            class="mode-btn"
            :class="{ 'mode-btn--active': !hybridStore.isHybridMode }"
            @click="setStandardMode"
          >Standard</button>
          <button
            class="mode-btn mode-btn--hybrid"
            :class="{ 'mode-btn--active': hybridStore.isHybridMode }"
            @click="hybridStore.toggleHybridMode()"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="5" r="3"/><circle cx="19" cy="19" r="3"/><circle cx="5" cy="19" r="3"/>
              <line x1="12" y1="8" x2="12" y2="14"/><line x1="12" y1="17" x2="19" y2="17"/>
              <line x1="12" y1="17" x2="5" y2="17"/>
            </svg>
            Hybrid Lineage
          </button>
        </div>

        <!-- Search input -->
        <div class="search-input-group">
          <div class="search-input-wrapper" :class="{ 'is-focused': isSearchFocused }">
            <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input
              v-model="activeQuery"
              type="text"
              class="search-input"
              placeholder="Search documents, concepts, knowledge..."
              @focus="isSearchFocused = true"
              @blur="isSearchFocused = false"
              @keydown.enter="handleSearch"
            />
            <button v-if="activeQuery" class="clear-btn" @click="handleClear">✕</button>
          </div>
          <BaseButton
            primary
            :loading="isLoading"
            :disabled="hybridStore.isHybridMode && !hybridStore.selectedDomainId"
            class="search-btn"
            @click="handleSearch"
          >
            Search
          </BaseButton>
        </div>

        <!-- Hybrid: single-domain selector + warning -->
        <template v-if="hybridStore.isHybridMode">
          <div class="hybrid-domain-bar">
            <label class="domain-label">Domain:</label>
            <select
              class="domain-select"
              :value="hybridStore.selectedDomainId ?? ''"
              @change="onDomainChange"
            >
              <option value="">— select a domain —</option>
              <option v-for="d in searchStore.availableDomains" :key="d.id" :value="d.id">
                {{ d.name }}
              </option>
            </select>
          </div>
          <p v-if="hybridStore.domainRequired" class="hybrid-warning">
            ⚠ Select exactly one domain to use Hybrid Lineage search.
          </p>
        </template>

        <!-- Standard mode suggestions -->
        <div v-if="!isSearchActive && !isLoading && !hybridStore.isHybridMode" class="search-suggestions">
          <span class="label-caps">Try searching for:</span>
          <div class="suggestion-chips">
            <button
              v-for="s in suggestions"
              :key="s"
              class="suggestion-chip"
              @click="searchWithSuggestion(s)"
            >{{ s }}</button>
          </div>
        </div>
      </div>
    </header>

    <!-- ── Main content ─────────────────────────────────────────────────── -->
    <main v-if="isSearchActive || isLoading" class="search-main">
      <div class="content-layout">

        <!-- Standard mode filters -->
        <div v-if="!hybridStore.isHybridMode" class="search-filters-bar">
          <SearchFilters />
        </div>

        <!-- Results area -->
        <section class="results-area">

          <!-- Loading skeleton -->
          <div v-if="isLoading" class="loading-state">
            <div class="skeleton-list">
              <div v-for="i in 3" :key="i" class="skeleton-card"></div>
            </div>
          </div>

          <!-- Error -->
          <div v-else-if="activeError" class="error-state">
            <BaseCard class="error-card">
              <p class="error-msg">{{ activeError }}</p>
              <BaseButton secondary @click="handleSearch">Retry</BaseButton>
            </BaseCard>
          </div>

          <!-- ── Hybrid results ── -->
          <template v-else-if="hybridStore.isHybridMode">
            <div v-if="hybridStore.hasResults" class="results-container">
              <div class="results-header">
                <span class="results-info">
                  {{ hybridStore.results.length }} semantic result{{ hybridStore.results.length !== 1 ? 's' : '' }}
                </span>
              </div>
              <div class="results-list">
                <HybridSearchCard
                  v-for="r in hybridStore.results"
                  :key="r.link_id"
                  :result="r"
                  @show-lineage="openLineage"
                />
              </div>
            </div>
            <div v-else class="empty-state">
              <h3 class="headline-md">No hybrid results found</h3>
              <p class="body-base">Try adjusting your query or selecting a different domain.</p>
            </div>
          </template>

          <!-- ── Standard results ── -->
          <template v-else>
            <div v-if="searchStore.hasResults" class="results-container">
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
                <button class="page-btn" :disabled="searchStore.page === 1" @click="searchStore.setPage(searchStore.page - 1)">← Previous</button>
                <span class="page-info">Page {{ searchStore.page }} of {{ totalPages }}</span>
                <button class="page-btn" :disabled="searchStore.page >= totalPages" @click="searchStore.setPage(searchStore.page + 1)">Next →</button>
              </div>
            </div>
            <div v-else class="empty-state">
              <h3 class="headline-md">No results found</h3>
              <p class="body-base">Try adjusting your filters or search terms.</p>
              <BaseButton secondary @click="searchStore.clearFilters()">Clear all filters</BaseButton>
            </div>
          </template>

        </section>
      </div>
    </main>

    <!-- ── Lineage modal ──────────────────────────────────────────────────── -->
    <LineageGraphModal
      :is-open="lineageOpen"
      :result-data="lineageResult"
      @close="lineageOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSearchStore } from './stores/search'
import { useHybridSearchStore } from './stores/hybridSearch'
import SearchFilters from './components/SearchFilters.vue'
import SearchResultCard from './components/SearchResultCard.vue'
import HybridSearchCard from './components/HybridSearchCard.vue'
import LineageGraphModal from './components/LineageGraphModal.vue'
import BaseButton from 'shell/BaseButton'
import BaseCard from 'shell/BaseCard'
import type { HybridSearchResult } from './types/semantic'

const searchStore = useSearchStore()
const hybridStore = useHybridSearchStore()
const isSearchFocused = ref(false)

// ── Lineage modal state ────────────────────────────────────────────────────
const lineageOpen = ref(false)
const lineageResult = ref<HybridSearchResult | null>(null)

function openLineage(result: HybridSearchResult) {
  lineageResult.value = result
  lineageOpen.value = true
}

// ── Unified computed helpers ───────────────────────────────────────────────
const isLoading = computed(() =>
  hybridStore.isHybridMode ? hybridStore.isLoading : searchStore.isLoading
)

const activeError = computed(() =>
  hybridStore.isHybridMode ? hybridStore.error : searchStore.error
)

const activeQuery = computed({
  get: () => hybridStore.isHybridMode ? hybridStore.query : searchStore.query,
  set: (v) => {
    if (hybridStore.isHybridMode) hybridStore.query = v
    else searchStore.query = v
  },
})

const isSearchActive = computed(() =>
  hybridStore.isHybridMode
    ? hybridStore.hasResults || hybridStore.isLoading
    : searchStore.isSearchActive || searchStore.isLoading
)

const totalPages = computed(() => Math.ceil(searchStore.total / searchStore.pageSize))

// ── Actions ────────────────────────────────────────────────────────────────
const suggestions = ['Vector embeddings', 'Module Federation', 'Micro-frontend architecture', 'FastAPI best practices', 'Keycloak integration']

function handleSearch() {
  if (hybridStore.isHybridMode) {
    hybridStore.performHybridSearch()
  } else {
    searchStore.isSearchActive = true
    searchStore.performSearch()
  }
}

function handleClear() {
  if (hybridStore.isHybridMode) hybridStore.clearResults()
  else searchStore.clearResults()
}

function setStandardMode() {
  if (hybridStore.isHybridMode) hybridStore.toggleHybridMode()
}

function searchWithSuggestion(s: string) {
  searchStore.query = s
  searchStore.isSearchActive = true
  searchStore.performSearch()
}

function handleOpenDocument(id: string) {
  console.log('Opening document:', id)
}

function onDomainChange(e: Event) {
  const val = (e.target as HTMLSelectElement).value
  hybridStore.selectDomain(val || null)
}

onMounted(() => searchStore.loadDomains())
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
  transition: padding 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  justify-content: center;
}

.search-header--compact {
  padding: 16px 24px;
  border-bottom: 1px solid var(--outline-variant, #E5E5E7);
  background: rgba(255, 255, 255, 0.85);
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
  gap: 16px;
}

.display-lg {
  font-size: 48px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  text-align: center;
}

.search-header--compact .display-lg { font-size: 0; opacity: 0; margin: 0; }

.subtitle {
  color: var(--on-surface-variant, #86868B);
  margin: -8px 0 0;
  text-align: center;
}

.search-header--compact .subtitle { font-size: 0; opacity: 0; margin: 0; }

/* Mode toggle */
.mode-toggle {
  display: flex;
  background: var(--surface-container, #ecedf9);
  border-radius: 10px;
  padding: 3px;
  gap: 2px;
}

.mode-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  border: none;
  background: transparent;
  color: var(--on-surface-variant, #86868b);
  cursor: pointer;
  transition: all 0.15s;
}

.mode-btn--active {
  background: var(--surface-container-lowest, #ffffff);
  color: var(--on-surface, #1d1d1f);
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  font-weight: 600;
}

.mode-btn--hybrid.mode-btn--active {
  color: var(--primary, #0058bc);
}

/* Search input */
.search-input-group {
  display: flex;
  width: 100%;
  gap: 12px;
  padding: 4px 0;
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
  box-shadow: 0 0 0 4px rgba(0,122,255,0.1), 0 2px 8px rgba(0,0,0,0.05);
}

.search-icon { color: var(--on-surface-variant, #86868B); margin-right: 12px; }

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

.search-btn { height: 50px; padding: 0 24px; border-radius: 12px; }

/* Hybrid domain bar */
.hybrid-domain-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.domain-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface-variant, #414755);
  white-space: nowrap;
}

.domain-select {
  flex: 1;
  height: 38px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  background: var(--surface-container-lowest, #ffffff);
  color: var(--on-surface, #1d1d1f);
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.domain-select:focus {
  border-color: var(--primary, #0058bc);
  box-shadow: 0 0 0 3px rgba(0,88,188,0.1);
}

.hybrid-warning {
  font-size: 13px;
  color: #ea580c;
  margin: 0;
  text-align: center;
}

/* Suggestions */
.search-suggestions { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.label-caps { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--on-surface-variant, #86868B); }
.suggestion-chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
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
.suggestion-chip:hover { background: var(--surface-container, #ecedf9); color: var(--on-surface, #1D1D1F); }

/* Main */
.search-main { max-width: 1400px; margin: 0 auto; padding: 40px 24px; }
.content-layout { display: flex; flex-direction: column; gap: 32px; }
.search-filters-bar { width: 100%; }
.results-area { display: flex; flex-direction: column; gap: 24px; }
.results-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid var(--outline-variant, #E5E5E7); }
.results-info { font-size: 15px; font-weight: 500; color: var(--on-surface, #1D1D1F); }
.search-time { font-size: 13px; color: var(--on-surface-variant, #86868B); margin-left: 8px; }
.results-list { display: flex; flex-direction: column; gap: 16px; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 20px; padding-top: 32px; }
.page-btn { padding: 8px 16px; border-radius: 8px; border: 1px solid var(--outline-variant, #E5E5E7); background: var(--surface-container-lowest, #fff); color: var(--on-surface, #1D1D1F); font-weight: 500; cursor: pointer; transition: all 0.15s; }
.page-btn:hover:not(:disabled) { border-color: var(--primary, #007AFF); color: var(--primary, #007AFF); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 14px; color: var(--on-surface-variant, #86868B); }
.skeleton-list { display: flex; flex-direction: column; gap: 16px; }
.skeleton-card { height: 160px; background: var(--surface-container, #ecedf9); border-radius: 12px; animation: pulse 1.5s infinite ease-in-out; }
@keyframes pulse { 0% { opacity: 0.6 } 50% { opacity: 1 } 100% { opacity: 0.6 } }
.empty-state, .error-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 0; text-align: center; gap: 16px; }
.error-card { max-width: 400px; padding: 32px; }
.error-msg { color: var(--error, #ba1a1a); margin-bottom: 16px; }
</style>
