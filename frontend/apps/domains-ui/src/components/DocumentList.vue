<template>
  <div class="document-list">
    <div class="list-filters">
      <div class="search-box">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
        </svg>
        <input 
          type="text" 
          placeholder="Filter documents..."
          v-model="query"
          @input="handleFilterChange"
        >
      </div>
      
      <div class="filters-row">
        <select v-model="statusFilter" @change="handleFilterChange">
          <option value="">All Statuses</option>
          <option value="done">Done</option>
          <option value="processing">Processing</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>

        <select v-model="typeFilter" @change="handleFilterChange">
          <option value="">All Types</option>
          <option value="upload">Upload</option>
          <option value="s3">S3</option>
          <option value="api">API</option>
          <option value="kafka">Kafka</option>
        </select>
      </div>
    </div>

    <div v-if="domainsStore.isLoadingDocuments" class="loading-state">
      <div class="skeleton-grid">
        <div v-for="i in 4" :key="i" class="skeleton-card"></div>
      </div>
    </div>

    <div v-else-if="domainsStore.documents.length === 0" class="empty-state">
      <p>No documents found matching the filters.</p>
    </div>

    <div v-else class="documents-grid">
      <DocumentCard 
        v-for="doc in domainsStore.documents" 
        :key="doc.id"
        :document="doc"
      />
    </div>

    <!-- Pagination -->
    <div v-if="domainsStore.documentPagination.total > domainsStore.documentPagination.pageSize" class="pagination">
      <button 
        class="page-btn" 
        :disabled="domainsStore.documentPagination.page === 1"
        @click="domainsStore.setDocumentPage(domainsStore.documentPagination.page - 1)"
      >
        ← Previous
      </button>
      <span class="page-info">
        Page {{ domainsStore.documentPagination.page }} of {{ domainsStore.documentPagination.pages }}
      </span>
      <button 
        class="page-btn" 
        :disabled="domainsStore.documentPagination.page >= domainsStore.documentPagination.pages"
        @click="domainsStore.setDocumentPage(domainsStore.documentPagination.page + 1)"
      >
        Next →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDomainsStore } from '../stores/domains'
import DocumentCard from './DocumentCard.vue'

const domainsStore = useDomainsStore()

const query = ref('')
const statusFilter = ref('')
const typeFilter = ref('')

let debounceTimer: any = null

function handleFilterChange() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    domainsStore.setDocumentFilter('query', query.value || undefined)
    domainsStore.setDocumentFilter('status', statusFilter.value || undefined)
    domainsStore.setDocumentFilter('type', typeFilter.value || undefined)
  }, 300)
}
</script>

<style scoped>
.document-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.list-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  background: var(--surface-container-lowest, #ffffff);
  border: 1px solid var(--outline-variant, #E5E5E7);
  border-radius: 10px;
  height: 40px;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  background: transparent;
}

.filters-row {
  display: flex;
  gap: 12px;
}

.filters-row select {
  padding: 0 12px;
  height: 40px;
  border-radius: 10px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #ffffff);
  font-size: 14px;
  outline: none;
  cursor: pointer;
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding-top: 20px;
}

.page-btn {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #E5E5E7);
  background: var(--surface-container-lowest, #ffffff);
  color: var(--on-surface, #1D1D1F);
  font-size: 13px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: var(--on-surface-variant, #86868B);
}

.loading-state {
  padding: 40px 0;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.skeleton-card {
  height: 140px;
  background: var(--surface-container, #ecedf9);
  border-radius: 12px;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

@media (max-width: 600px) {
  .list-filters {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
