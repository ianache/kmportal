<template>
  <div class="search-filters">
    <div class="filters-header">
      <h3 class="filters-title">Filters</h3>
      <button 
        v-if="searchStore.activeFiltersCount > 0" 
        class="clear-all-btn"
        @click="searchStore.clearFilters()"
      >
        Clear All
      </button>
    </div>

    <div class="filter-sections">
      <!-- Domain Filter -->
      <div class="filter-section">
        <DomainSelector />
      </div>

      <!-- Type Filter -->
      <div v-if="searchStore.availableTypes.length > 0" class="filter-section">
        <label class="filter-label">Document Type</label>
        <div class="chip-grid">
          <button 
            v-for="type in searchStore.availableTypes" 
            :key="type"
            class="filter-chip"
            :class="{ 'filter-chip--active': searchStore.filters.types?.includes(type) }"
            @click="toggleType(type)"
          >
            {{ type }}
          </button>
        </div>
      </div>

      <!-- Source Filter -->
      <div v-if="searchStore.availableSources.length > 0" class="filter-section">
        <label class="filter-label">Source</label>
        <div class="chip-grid">
          <button 
            v-for="source in searchStore.availableSources" 
            :key="source"
            class="filter-chip"
            :class="{ 'filter-chip--active': searchStore.filters.sources?.includes(source) }"
            @click="toggleSource(source)"
          >
            {{ source }}
          </button>
        </div>
      </div>

      <!-- Date Filter -->
      <div class="filter-section">
        <label class="filter-label">Date Range</label>
        <div class="date-range">
          <div class="date-input-wrap">
            <span class="date-hint">From</span>
            <input 
              type="date" 
              class="date-input"
              :value="searchStore.filters.date_from"
              @change="updateDateFrom($event)"
            >
          </div>
          <div class="date-input-wrap">
            <span class="date-hint">To</span>
            <input 
              type="date" 
              class="date-input"
              :value="searchStore.filters.date_to"
              @change="updateDateTo($event)"
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSearchStore } from '../stores/search'
import DomainSelector from './DomainSelector.vue'

const searchStore = useSearchStore()

function toggleType(type: string) {
  const currentTypes = [...(searchStore.filters.types || [])]
  const index = currentTypes.indexOf(type)
  
  if (index === -1) {
    currentTypes.push(type)
  } else {
    currentTypes.splice(index, 1)
  }
  
  searchStore.setFilter('types', currentTypes)
}

function toggleSource(source: string) {
  const currentSources = [...(searchStore.filters.sources || [])]
  const index = currentSources.indexOf(source)
  
  if (index === -1) {
    currentSources.push(source)
  } else {
    currentSources.splice(index, 1)
  }
  
  searchStore.setFilter('sources', currentSources)
}

function updateDateFrom(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchStore.setFilter('date_from', value || undefined)
}

function updateDateTo(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchStore.setFilter('date_to', value || undefined)
}
</script>

<style scoped>
.search-filters {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: saturate(180%) blur(20px);
  border-radius: 16px;
  border: 1px solid var(--outline-variant, #E5E5E7);
}

.filters-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filters-title {
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--on-surface-variant, #86868B);
}

.clear-all-btn {
  font-size: 13px;
  color: var(--primary, #007AFF);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.clear-all-btn:hover {
  text-decoration: underline;
}

.filter-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
}

.domain-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 14px;
  color: var(--on-surface-variant, #414755);
  padding: 4px 0;
}

.filter-checkbox:hover .checkbox-label {
  color: var(--on-surface, #1D1D1F);
}

.checkbox-label {
  flex: 1;
  transition: color 0.15s;
}

.count {
  font-size: 11px;
  color: var(--on-surface-variant, #86868B);
  background: var(--surface-container, #ecedf9);
  padding: 2px 6px;
  border-radius: 999px;
}

.chip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-chip {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  background: var(--surface-container-low, #f1f3fe);
  border: 1px solid transparent;
  color: var(--on-surface-variant, #414755);
  cursor: pointer;
  transition: all 0.15s;
}

.filter-chip:hover {
  background: var(--surface-container, #ecedf9);
  color: var(--on-surface, #1D1D1F);
}

.filter-chip--active {
  background: var(--primary-container, #0070eb);
  color: var(--on-primary, #ffffff);
}

.date-range {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.date-input-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-hint {
  font-size: 11px;
  color: var(--on-surface-variant, #86868B);
}

.date-input {
  width: 100%;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #ffffff);
  font-size: 13px;
  color: var(--on-surface, #1D1D1F);
}

.date-input:focus {
  outline: none;
  border-color: var(--primary, #007AFF);
}
</style>
