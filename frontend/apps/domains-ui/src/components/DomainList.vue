<template>
  <div class="domain-list-view">
    <div class="list-header">
      <h2 class="display-lg">Knowledge Domains</h2>
      <p class="body-base subtitle">Explore and manage knowledge organized by specialized domains.</p>
    </div>

    <div v-if="domainsStore.isLoading && !domainsStore.hasDomains" class="loading-state">
      <div class="skeleton-grid">
        <div v-for="i in 6" :key="i" class="skeleton-card"></div>
      </div>
    </div>

    <div v-else-if="domainsStore.error && !domainsStore.hasDomains" class="error-state">
      <BaseCard class="error-card">
        <p class="error-msg">{{ domainsStore.error }}</p>
        <BaseButton secondary @click="domainsStore.loadDomains()">Retry</BaseButton>
      </BaseCard>
    </div>

    <div v-else-if="domainsStore.hasDomains" class="domains-grid">
      <BaseCard
        v-for="domain in domainsStore.sortedDomains"
        :key="domain.id"
        class="domain-card"
        clickable
        @click="domainsStore.selectDomain(domain.id)"
      >
        <div class="domain-info">
          <div class="domain-header">
            <h3 class="domain-name">{{ domain.name }}</h3>
            <span class="doc-count-badge">
              {{ domain.document_count || 0 }} docs
            </span>
          </div>
          <p class="domain-desc">{{ domain.description || 'No description available.' }}</p>
          <div class="domain-meta">
            <span class="meta-item">
              <strong>Created:</strong> {{ formatDate(domain.created_at) }}
            </span>
            <span class="meta-item">
              <strong>Model:</strong> {{ domain.embedding_model }}
            </span>
          </div>
        </div>
        <div class="card-footer">
          <div class="card-action">
            <span>View Documents</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </div>
          <button
            class="ontology-btn"
            title="Open Ontology Editor"
            @click.stop="$emit('open-ontology', domain)"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <circle cx="4" cy="6" r="2"/><line x1="6" y1="6" x2="9" y2="11"/>
              <circle cx="20" cy="6" r="2"/><line x1="18" y1="6" x2="15" y2="11"/>
              <circle cx="4" cy="18" r="2"/><line x1="6" y1="18" x2="9" y2="13"/>
              <circle cx="20" cy="18" r="2"/><line x1="18" y1="18" x2="15" y2="13"/>
            </svg>
            <span>Ontology</span>
          </button>
        </div>
      </BaseCard>
    </div>

    <div v-else class="empty-state">
      <h3 class="headline-md">No domains found</h3>
      <p class="body-base">You don't have access to any knowledge domains yet.</p>
    </div>

    <!-- Pagination -->
    <div v-if="domainsStore.pagination.total > domainsStore.pagination.pageSize" class="pagination">
      <button 
        class="page-btn" 
        :disabled="domainsStore.pagination.page === 1"
        @click="domainsStore.setPage(domainsStore.pagination.page - 1)"
      >
        ← Previous
      </button>
      <span class="page-info">Page {{ domainsStore.pagination.page }} of {{ domainsStore.pagination.pages }}</span>
      <button 
        class="page-btn" 
        :disabled="domainsStore.pagination.page >= domainsStore.pagination.pages"
        @click="domainsStore.setPage(domainsStore.pagination.page + 1)"
      >
        Next →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useDomainsStore } from '../stores/domains'
import BaseButton from 'shell/BaseButton'
import BaseCard from 'shell/BaseCard'

import type { Domain } from '../types/domains'

const domainsStore = useDomainsStore()
defineEmits<{ (e: 'open-ontology', domain: Domain): void }>()

onMounted(() => {
  domainsStore.loadDomains()
})

function formatDate(dateStr: string) {
  try {
    return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>

<style scoped>
.domain-list-view {
  padding: 40px 24px;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.list-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.display-lg {
  font-size: 48px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
}

.subtitle {
  color: var(--on-surface-variant, #86868B);
  max-width: 600px;
}

.domains-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.domain-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px;
  transition: all 0.3s ease;
}

.domain-card:hover {
  border-color: var(--primary, #007AFF);
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.08);
}

.domain-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.domain-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.domain-name {
  font-size: 24px;
  font-weight: 600;
  color: var(--on-surface, #1D1D1F);
  margin: 0;
  letter-spacing: -0.01em;
}

.doc-count-badge {
  background: var(--primary-soft, rgba(0, 88, 188, 0.08));
  color: var(--primary, #007AFF);
  font-size: 13px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 999px;
  white-space: nowrap;
}

.domain-desc {
  font-size: 16px;
  color: var(--on-surface-variant, #414755);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.domain-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--surface-container, #ecedf9);
}

.meta-item {
  font-size: 12px;
  color: var(--on-surface-variant, #86868B);
}

.meta-item strong {
  color: var(--on-surface, #1D1D1F);
  font-weight: 500;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24px;
}

.card-action {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary, #007AFF);
}

.ontology-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: #8e44ad;
  cursor: pointer;
  transition: background 0.15s;
}

.ontology-btn:hover {
  background: rgba(142, 68, 173, 0.08);
  border-color: #8e44ad;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #ffffff);
  color: var(--on-surface, #1D1D1F);
  font-weight: 500;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* States */
.loading-state, .error-state, .empty-state {
  padding: 80px 0;
  text-align: center;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.skeleton-card {
  height: 240px;
  background: var(--surface-container, #ecedf9);
  border-radius: 12px;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

@media (max-width: 768px) {
  .domains-grid, .skeleton-grid {
    grid-template-columns: 1fr;
  }
}
</style>
