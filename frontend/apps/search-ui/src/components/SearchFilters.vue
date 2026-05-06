<template>
  <div class="search-filters-horizontal">
    <div class="filters-container">
      <!-- Domain Multi-select Combobox -->
      <DomainSelector />

      <!-- Date Range Filter -->
      <div class="date-filter-group">
        <div class="date-input-container">
          <label class="date-label">From</label>
          <input 
            type="date" 
            class="date-input"
            :value="searchStore.filters.date_from"
            @change="updateDateFrom($event)"
          >
        </div>
        <div class="date-input-container">
          <label class="date-label">To</label>
          <input 
            type="date" 
            class="date-input"
            :value="searchStore.filters.date_to"
            @change="updateDateTo($event)"
          >
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="filter-actions">
        <button 
          v-if="searchStore.activeFiltersCount > 0" 
          class="clear-all-btn"
          @click="searchStore.clearFilters()"
        >
          Clear All
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSearchStore } from '../stores/search'
import DomainSelector from './DomainSelector.vue'

const searchStore = useSearchStore()

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
.search-filters-horizontal {
  width: 100%;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: saturate(180%) blur(20px);
  border-radius: 16px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  padding: 12px 16px;
}

.filters-container {
  display: flex;
  align-items: center;
  gap: 24px;
}

.date-filter-group {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 16px;
  border-left: 1px solid var(--outline-variant, #E5E5E7);
  border-right: 1px solid var(--outline-variant, #E5E5E7);
}

.date-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868B);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.date-input {
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #ffffff);
  font-size: 13px;
  color: var(--on-surface, #1D1D1F);
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.date-input:focus {
  outline: none;
  border-color: var(--primary, #007AFF);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.filter-actions {
  margin-left: auto;
}

.clear-all-btn {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary, #007AFF);
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s;
}

.clear-all-btn:hover {
  background: var(--primary-soft, rgba(0, 122, 255, 0.05));
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 900px) {
  .filters-container {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .date-filter-group {
    border: none;
    padding: 0;
    flex-wrap: wrap;
  }
  
  .filter-actions {
    margin-left: 0;
    text-align: right;
  }
}
</style>
