<template>
  <div class="domain-selector" ref="containerRef">
    <div 
      class="combobox-trigger" 
      :class="{ 'is-open': isOpen }"
      @click="isOpen = !isOpen"
    >
      <div class="selected-info">
        <span class="label">Domains</span>
        <span v-if="searchStore.selectedDomains.length" class="selection-badge">
          {{ searchStore.selectedDomains.length }} selected
        </span>
        <span v-else class="placeholder">All domains</span>
      </div>
      <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </div>

    <transition name="fade-slide">
      <div v-if="isOpen" class="combobox-dropdown">
        <div class="dropdown-header">
          <span class="dropdown-title">Select Domains</span>
          <button v-if="searchStore.selectedDomains.length" class="clear-link" @click.stop="searchStore.selectedDomains = []">
            Clear
          </button>
        </div>
        
        <div class="domain-list">
          <label 
            v-for="domain in searchStore.availableDomains" 
            :key="domain.id"
            class="domain-item"
            @click.stop
          >
            <input 
              type="checkbox" 
              :value="domain.id" 
              :checked="searchStore.selectedDomains.includes(domain.id)"
              class="hidden-checkbox"
              @change="searchStore.toggleDomain(domain.id)"
            >
            <div class="checkbox-ui">
              <svg v-if="searchStore.selectedDomains.includes(domain.id)" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <span class="domain-name">{{ domain.name }}</span>
            <span class="domain-count">{{ domain.document_count || 0 }}</span>
          </label>
        </div>
        
        <div v-if="searchStore.availableDomains.length === 0" class="no-domains">
          No domains available
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useSearchStore } from '../stores/search'

const searchStore = useSearchStore()
const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)

function handleClickOutside(event: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.domain-selector {
  position: relative;
  width: 260px;
}

.combobox-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 48px;
  background: var(--surface-container-lowest, #ffffff);
  border: 1px solid var(--outline-variant, #E5E5E7);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.combobox-trigger:hover {
  border-color: var(--outline, #717786);
}

.combobox-trigger.is-open {
  border-color: var(--primary, #007AFF);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.selected-info {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.label {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868B);
}

.selection-badge {
  background: var(--primary, #007AFF);
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

.placeholder {
  font-size: 14px;
  color: var(--on-surface, #1D1D1F);
  font-weight: 500;
}

.chevron {
  color: var(--on-surface-variant, #86868B);
  transition: transform 0.2s;
}

.is-open .chevron {
  transform: rotate(180deg);
}

.combobox-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 320px;
  background: var(--surface-container-lowest, #ffffff);
  border: 1px solid var(--outline-variant, #E5E5E7);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  z-index: 50;
  padding: 8px;
}

.dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid var(--outline-variant, #E5E5E7);
  margin-bottom: 8px;
}

.dropdown-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--on-surface-variant, #86868B);
  letter-spacing: 0.05em;
}

.clear-link {
  font-size: 12px;
  color: var(--primary, #007AFF);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.domain-list {
  max-height: 280px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.domain-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.domain-item:hover {
  background: var(--surface-container-low, #f1f3fe);
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
  background: white;
  color: white;
  flex-shrink: 0;
}

.domain-item:has(input:checked) .checkbox-ui {
  background: var(--primary, #007AFF);
  border-color: var(--primary, #007AFF);
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
  padding: 20px;
  text-align: center;
  color: var(--on-surface-variant, #86868B);
  font-size: 14px;
}

/* Animations */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease-out;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
