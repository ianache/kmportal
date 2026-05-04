<template>
  <div class="domain-selector">
    <label class="filter-label">Domains</label>
    <div class="domain-list">
      <label 
        v-for="domain in searchStore.availableDomains" 
        :key="domain.id"
        class="domain-item"
        :class="{ 'is-selected': searchStore.selectedDomains.includes(domain.id) }"
      >
        <input 
          type="checkbox" 
          :value="domain.id" 
          :checked="searchStore.selectedDomains.includes(domain.id)"
          class="hidden-checkbox"
          @change="searchStore.toggleDomain(domain.id)"
        >
        <div class="checkbox-ui">
          <svg v-if="searchStore.selectedDomains.includes(domain.id)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </div>
        <span class="domain-name">{{ domain.name }}</span>
        <span class="domain-count">{{ domain.document_count || 0 }}</span>
      </label>
    </div>
    <div v-if="searchStore.availableDomains.length === 0" class="no-domains">
      No domains available.
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSearchStore } from '../stores/search'

const searchStore = useSearchStore()
</script>

<style scoped>
.domain-selector {
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
  gap: 4px;
}

.domain-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}

.domain-item:hover {
  background: var(--surface-container, #ecedf9);
}

.domain-item.is-selected {
  background: var(--primary-soft, rgba(0, 88, 188, 0.08));
}

.hidden-checkbox {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkbox-ui {
  width: 18px;
  height: 18px;
  border: 2px solid var(--outline-variant, #E5E5E7);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-container-lowest, #ffffff);
  color: var(--primary, #007AFF);
  transition: all 0.15s;
}

.is-selected .checkbox-ui {
  background: var(--primary, #007AFF);
  border-color: var(--primary, #007AFF);
  color: white;
}

.domain-name {
  flex: 1;
  font-size: 14px;
  color: var(--on-surface, #1D1D1F);
  font-weight: 500;
}

.domain-count {
  font-size: 11px;
  color: var(--on-surface-variant, #86868B);
  background: var(--surface-container-high, #e6e8f3);
  padding: 2px 6px;
  border-radius: 999px;
}

.no-domains {
  font-size: 13px;
  color: var(--on-surface-variant, #86868B);
  font-style: italic;
  padding: 8px;
}
</style>
