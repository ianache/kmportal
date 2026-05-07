<template>
  <div class="domain-detail-view">
    <nav class="breadcrumb">
      <button class="breadcrumb-link" @click="domainsStore.clearSelection()">Domains</button>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-current">{{ domainsStore.selectedDomain?.name }}</span>
    </nav>

    <header class="domain-header">
      <div class="header-content">
        <div class="header-main">
          <button class="back-btn" @click="domainsStore.clearSelection()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div class="title-wrap">
            <h2 class="domain-title">{{ domainsStore.selectedDomain?.name }}</h2>
            <p class="domain-desc">{{ domainsStore.selectedDomain?.description }}</p>
          </div>
        </div>
        
        <div class="domain-stats">
          <div class="stat-item">
            <span class="stat-label">Documents</span>
            <span class="stat-value">{{ domainsStore.selectedDomain?.document_count }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Model</span>
            <span class="stat-value">{{ domainsStore.selectedDomain?.embedding_model }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Created</span>
            <span class="stat-value">{{ formatDate(domainsStore.selectedDomain?.created_at) }}</span>
          </div>
        </div>
      </div>
    </header>

    <main class="domain-content">
      <div class="tabs">
        <button 
          class="tab-item" 
          :class="{ active: activeTab === 'documents' }"
          @click="activeTab = 'documents'"
        >
          Documents
        </button>
        <button 
          class="tab-item" 
          :class="{ active: activeTab === 'settings' }"
          :disabled="!authStore.isAdmin"
          :title="!authStore.isAdmin ? 'Admin access required' : ''"
          @click="activeTab = 'settings'"
        >
          Settings (Admin only)
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'documents'">
          <DocumentList v-if="domainsStore.selectedDomain" :domainId="domainsStore.selectedDomain.id" />
        </div>
        <div v-else-if="activeTab === 'settings'" class="settings-placeholder">
          <BaseCard class="placeholder-card">
            <h3 class="headline-sm">Domain Settings</h3>
            <p class="body-base">Administration tools for <strong>{{ domainsStore.selectedDomain?.name }}</strong> will be available here.</p>
            <div class="coming-soon">
              <span class="badge">Coming Soon</span>
            </div>
          </BaseCard>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDomainsStore } from '../stores/domains'
import { useAuthStore } from 'shell/authStore'
import DocumentList from './DocumentList.vue'
import BaseCard from 'shell/BaseCard'

const domainsStore = useDomainsStore()
const authStore = useAuthStore()

const activeTab = ref<'documents' | 'settings'>('documents')

function formatDate(dateStr?: string) {
  if (!dateStr) return 'N/A'
  try {
    return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch (e) {
    return dateStr
  }
}
</script>

<style scoped>
.domain-detail-view {
  padding: 40px 24px;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-link {
  color: var(--primary, #007AFF);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-weight: 500;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: var(--on-surface-variant, #86868B);
}

.breadcrumb-current {
  color: var(--on-surface, #1D1D1F);
  font-weight: 500;
}

.domain-header {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: saturate(180%) blur(20px);
  border: 1px solid var(--outline-variant, #E5E5E7);
  border-radius: 16px;
  padding: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 40px;
  flex-wrap: wrap;
}

.header-main {
  display: flex;
  gap: 20px;
  flex: 1;
  min-width: 300px;
}

.back-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: var(--surface-container-low, #f1f3fe);
  border: none;
  color: var(--on-surface, #1D1D1F);
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--surface-container, #ecedf9);
  color: var(--primary, #007AFF);
}

.title-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.domain-title {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  color: var(--on-surface, #1D1D1F);
}

.domain-desc {
  font-size: 16px;
  color: var(--on-surface-variant, #414755);
  line-height: 1.5;
  margin: 0;
  max-width: 700px;
}

.domain-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868B);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary, #007AFF);
}

.domain-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.tabs {
  display: flex;
  gap: 32px;
  border-bottom: 1px solid var(--outline-variant, #E5E5E7);
  padding: 0 8px;
}

.tab-item {
  padding: 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868B);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item:hover:not(:disabled) {
  color: var(--on-surface, #1D1D1F);
}

.tab-item.active {
  color: var(--primary, #007AFF);
  border-bottom-color: var(--primary, #007AFF);
}

.tab-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.settings-placeholder {
  padding: 40px 0;
}

.placeholder-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 16px;
  padding: 60px;
  background: var(--surface-container-low, #f1f3fe);
  border: 1px dashed var(--outline-variant, #E5E5E7);
}

.coming-soon {
  margin-top: 8px;
}

.badge {
  background: var(--secondary-container, #e1e2ec);
  color: var(--on-secondary-container, #191b23);
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
  }
  .domain-stats {
    width: 100%;
    justify-content: space-between;
    padding-top: 24px;
    border-top: 1px solid var(--outline-variant, #E5E5E7);
  }
}
</style>
