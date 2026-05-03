<template>
  <div class="domains">

    <!-- ── Explorer ──────────────────────── -->
    <template v-if="view === 'explorer'">
      <div class="page-header">
        <div>
          <h1 class="page-title">Knowledge Domains</h1>
          <p class="page-desc">Explore, manage, and curate your structured information vaults.</p>
        </div>
        <button class="btn-primary" @click="view = 'create'">
          <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="10" y1="4" x2="10" y2="16"/><line x1="4" y1="10" x2="16" y2="10"/>
          </svg>
          New Domain
        </button>
      </div>

      <!-- Filter bar -->
      <div class="filter-bar">
        <div class="filter-chips">
          <button
            v-for="f in filters"
            :key="f.value"
            class="chip"
            :class="{ 'chip--active': activeFilter === f.value }"
            @click="activeFilter = f.value"
          >{{ f.label }}</button>
        </div>
        <div class="search-input-wrap">
          <svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="#86868B" stroke-width="1.8">
            <circle cx="9" cy="9" r="6"/><path d="M17 17l-3.5-3.5"/>
          </svg>
          <input v-model="searchQ" class="search-input" placeholder="Search domains…" />
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="isLoading" class="domain-grid">
        <div v-for="n in 4" :key="n" class="domain-card skeleton">
          <div class="card-top">
            <div class="domain-icon" style="background: #f0f0f0;"></div>
            <div class="badge" style="background: #f0f0f0; color: transparent;">Status</div>
          </div>
          <div class="card-body">
            <div style="height: 18px; background: #f0f0f0; border-radius: 4px; margin-bottom: 8px;"></div>
            <div style="height: 36px; background: #f0f0f0; border-radius: 4px;"></div>
          </div>
          <div class="card-footer">
            <div style="height: 16px; width: 80px; background: #f0f0f0; border-radius: 4px;"></div>
          </div>
        </div>
      </div>

      <!-- Domain grid -->
      <div v-else class="domain-grid">
        <div
          v-for="d in filteredDomains"
          :key="d.id"
          class="domain-card"
          @click="openDomain(d)"
        >
          <div class="card-top">
            <div class="domain-icon" :style="{ background: '#007AFF18', color: '#007AFF' }">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
                <path d="M10 2C5.6 2 2 5.6 2 10s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8z"/>
                <path d="M2 10h16M10 2a12 12 0 0 1 0 16M10 2a12 12 0 0 0 0 16"/>
              </svg>
            </div>
            <span class="badge" :class="d.status === 'active' ? 'badge--active' : 'badge--archived'">
              {{ d.status }}
            </span>
          </div>
          <div class="card-body">
            <h3 class="domain-name">{{ d.name }}</h3>
            <p class="domain-desc">{{ d.description }}</p>
          </div>
          <div class="card-footer">
            <span class="resource-count">
              <svg width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6">
                <path d="M4 4h12v2H4zM4 9h12v2H4zM4 14h8v2H4z"/>
              </svg>
              {{ d.documentCount || 0 }} resources
            </span>
            <span class="domain-updated">{{ new Date(d.updatedAt).toLocaleDateString() }}</span>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="filteredDomains.length === 0" class="empty-state">
          <svg width="40" height="40" viewBox="0 0 20 20" fill="none" stroke="#86868B" stroke-width="1.2">
            <path d="M10 2C5.6 2 2 5.6 2 10s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8z"/>
            <path d="M2 10h16M10 2a12 12 0 0 1 0 16M10 2a12 12 0 0 0 0 16"/>
          </svg>
          <p>No domains found</p>
        </div>
      </div>
    </template>

    <!-- ── Create Domain ─────────────────── -->
    <template v-else-if="view === 'create'">
      <div class="page-header">
        <div class="back-row">
          <button class="btn-ghost" @click="view = 'explorer'">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 4l-6 6 6 6"/>
            </svg>
            Back
          </button>
        </div>
        <div>
          <h1 class="page-title">Create New Domain</h1>
          <p class="page-desc">Define a new structured knowledge vault.</p>
        </div>
      </div>

      <div class="create-layout">
        <div class="form-card">
          <section class="form-section">
            <h2 class="section-title">Domain Details</h2>

            <label class="field">
              <span class="field-label">Name <span class="required">*</span></span>
              <input v-model="form.name" class="field-input" placeholder="e.g. Artificial Intelligence" />
            </label>

            <label class="field">
              <span class="field-label">Description</span>
              <textarea
                v-model="form.description"
                class="field-input field-textarea"
                placeholder="Briefly describe the scope and purpose of this knowledge domain…"
                rows="3"
              />
            </label>

            <label class="field">
              <span class="field-label">Tags</span>
              <input v-model="form.tags" class="field-input" placeholder="ai, machine-learning, research (comma separated)" />
            </label>
          </section>

          <section class="form-section">
            <h2 class="section-title">Cover Image</h2>
            <div class="upload-area">
              <svg width="32" height="32" viewBox="0 0 20 20" fill="none" stroke="#86868B" stroke-width="1.4">
                <rect x="2" y="4" width="16" height="12" rx="2"/>
                <circle cx="7" cy="9" r="1.5"/>
                <path d="M2 14l4-4 3 3 3-3 4 4"/>
              </svg>
              <span class="upload-text">Drag and drop or <u>browse</u></span>
              <span class="upload-hint">PNG, JPG up to 4 MB</span>
            </div>
          </section>
        </div>

        <div class="sidebar-form">
          <div class="form-card">
            <section class="form-section">
              <h2 class="section-title">Publish Settings</h2>

              <label class="field">
                <span class="field-label">Status</span>
                <select v-model="form.status" class="field-input field-select">
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="archived">Archived</option>
                </select>
              </label>

              <label class="field">
                <span class="field-label">Visibility</span>
                <select v-model="form.visibility" class="field-input field-select">
                  <option value="private">Private</option>
                  <option value="public">Public</option>
                </select>
              </label>
            </section>

            <div class="form-actions">
              <button class="btn-ghost btn-full" @click="view = 'explorer'">Cancel</button>
              <button class="btn-primary btn-full" @click="handleCreate">Create Domain</button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Domain Detail ─────────────────── -->
    <template v-else-if="view === 'detail' && activeDomain">
      <div class="page-header">
        <div class="back-row">
          <button class="btn-ghost" @click="view = 'explorer'">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 4l-6 6 6 6"/>
            </svg>
            All Domains
          </button>
        </div>
        <div class="header-row">
          <div>
            <h1 class="page-title">{{ activeDomain.name }}</h1>
            <p class="page-desc">{{ activeDomain.description }}</p>
          </div>
          <span class="badge" :class="activeDomain.status === 'active' ? 'badge--active' : 'badge--archived'">
            {{ activeDomain.status }}
          </span>
        </div>
      </div>

      <div class="detail-stats">
        <div class="stat-card">
          <span class="stat-value">{{ activeDomain.documentCount || 0 }}</span>
          <span class="stat-label">Documents</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ activeDomain.metadata?.nodes || 0 }}</span>
          <span class="stat-label">Nodes</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ activeDomain.ownerId || '—' }}</span>
          <span class="stat-label">Owner</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ new Date(activeDomain.updatedAt).toLocaleDateString() }}</span>
          <span class="stat-label">Last updated</span>
        </div>
      </div>

      <!-- Document list -->
      <div class="documents-section">
        <h2 class="section-title">Documents</h2>
        <div v-if="store.isLoadingDocuments" class="documents-loading">
          <div v-for="n in 3" :key="n" class="doc-row skeleton">
            <div style="height: 16px; width: 40%; background: #f0f0f0; border-radius: 4px;"></div>
            <div style="height: 14px; width: 20%; background: #f0f0f0; border-radius: 4px;"></div>
          </div>
        </div>
        <div v-else-if="store.documents.length === 0" class="documents-empty">
          No documents in this domain yet.
        </div>
        <div v-else class="documents-list">
          <div v-for="doc in store.documents" :key="doc.id" class="doc-row">
            <div class="doc-info">
              <span class="doc-title">{{ doc.title || doc.filename }}</span>
              <span class="doc-meta">{{ doc.type }} • {{ doc.status }}</span>
            </div>
            <span class="doc-date">{{ new Date(doc.createdAt).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDomainsStore } from './stores/domains'
import type { Domain } from './types'

type View = 'explorer' | 'create' | 'detail'

const store = useDomainsStore()
const view = ref<View>('explorer')
const activeFilter = ref('all')
const searchQ = ref('')

const form = ref({
  name: '',
  description: '',
  tags: '',
  status: 'draft',
  visibility: 'private',
})

const filters = [
  { label: 'All', value: 'all' },
  { label: 'Active', value: 'active' },
  { label: 'Archived', value: 'archived' },
]

const filteredDomains = computed(() => {
  return store.domains.filter((d) => {
    const matchFilter = activeFilter.value === 'all' || d.status === activeFilter.value
    const matchSearch = !searchQ.value || d.name.toLowerCase().includes(searchQ.value.toLowerCase())
    return matchFilter && matchSearch
  })
})

const activeDomain = computed(() => store.selectedDomain)
const isLoading = computed(() => store.isLoading)

function openDomain(d: Domain) {
  store.selectDomain(d)
  view.value = 'detail'
}

async function handleCreate() {
  if (!form.value.name.trim()) return
  
  const newDomain = await store.createDomain({
    name: form.value.name,
    description: form.value.description,
    tags: form.value.tags.split(',').map(t => t.trim()).filter(Boolean),
    status: form.value.status as 'active' | 'draft' | 'archived',
    visibility: form.value.visibility as 'public' | 'private',
  })
  
  if (newDomain) {
    form.value = { name: '', description: '', tags: '', status: 'draft', visibility: 'private' }
    view.value = 'explorer'
  }
}

onMounted(() => {
  store.fetchDomains()
})
</script>

<style scoped>
.domains {
  padding: 32px 40px;
  min-height: 100%;
}

/* ── Page header ─────────────────────────── */
.page-header {
  margin-bottom: 24px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.back-row {
  margin-bottom: 12px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text, #1D1D1F);
  line-height: 1.2;
}

.page-desc {
  font-size: 14px;
  color: var(--text-2, #86868B);
  margin-top: 4px;
}

/* ── Buttons ─────────────────────────────── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--primary, #007AFF);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  padding: 9px 16px;
  border-radius: var(--radius-sm, 8px);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  transition: opacity 0.12s;
  font-family: inherit;
}
.btn-primary:hover { opacity: 0.88; }

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  color: var(--text-2, #86868B);
  font-size: 14px;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E5E7);
  cursor: pointer;
  transition: background 0.12s;
  font-family: inherit;
}
.btn-ghost:hover { background: rgba(0,0,0,0.04); color: var(--text, #1D1D1F); }

.btn-full { width: 100%; justify-content: center; }

/* ── Filter bar ──────────────────────────── */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-chips {
  display: flex;
  gap: 6px;
}

.chip {
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  color: var(--text-2, #86868B);
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
  font-family: inherit;
}
.chip:hover { background: rgba(0,0,0,0.04); color: var(--text, #1D1D1F); }
.chip--active {
  background: var(--primary-soft, rgba(0,122,255,0.1));
  border-color: var(--primary, #007AFF);
  color: var(--primary, #007AFF);
}

.search-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius-sm, 8px);
  padding: 7px 12px;
  min-width: 220px;
}

.search-input {
  border: none;
  outline: none;
  font-size: 14px;
  font-family: inherit;
  color: var(--text, #1D1D1F);
  background: transparent;
  flex: 1;
}

/* ── Domain grid ─────────────────────────── */
.domain-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.domain-card {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: box-shadow 0.15s, transform 0.15s;
  box-shadow: var(--shadow-card, 0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.06));
}
.domain-card:hover {
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  transform: translateY(-1px);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.domain-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  letter-spacing: 0.02em;
}
.badge--active { background: rgba(52,199,89,0.12); color: #1a7f37; }
.badge--archived { background: rgba(134,134,139,0.12); color: #636366; }

.card-body { flex: 1; }

.domain-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  letter-spacing: -0.01em;
  margin-bottom: 4px;
}

.domain-desc {
  font-size: 13px;
  color: var(--text-2, #86868B);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border, #E5E5E7);
}

.resource-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-2, #86868B);
  font-weight: 500;
}

.domain-updated {
  font-size: 12px;
  color: var(--text-2, #86868B);
}

/* ── Empty state ─────────────────────────── */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 64px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-2, #86868B);
  font-size: 14px;
}

/* ── Create layout ───────────────────────── */
.create-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 24px;
  align-items: start;
}

.form-card {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 24px;
  box-shadow: var(--shadow-card, 0 1px 2px rgba(0,0,0,0.04));
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.form-section { display: flex; flex-direction: column; gap: 16px; }

.section-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-2, #86868B);
}

.field { display: flex; flex-direction: column; gap: 6px; }

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text, #1D1D1F);
}

.required { color: var(--primary, #007AFF); }

.field-input {
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius-sm, 8px);
  padding: 9px 12px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text, #1D1D1F);
  background: var(--bg, #F5F5F7);
  outline: none;
  transition: border-color 0.12s, box-shadow 0.12s;
}
.field-input:focus {
  border-color: var(--primary, #007AFF);
  box-shadow: 0 0 0 3px rgba(0,122,255,0.12);
  background: #fff;
}

.field-textarea { resize: vertical; min-height: 80px; }

.field-select { appearance: none; cursor: pointer; }

.upload-area {
  border: 2px dashed var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 32px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.12s, background 0.12s;
}
.upload-area:hover {
  border-color: var(--primary, #007AFF);
  background: var(--primary-soft, rgba(0,122,255,0.04));
}

.upload-text {
  font-size: 14px;
  color: var(--text, #1D1D1F);
}
.upload-text u { color: var(--primary, #007AFF); text-decoration: underline; cursor: pointer; }

.upload-hint { font-size: 12px; color: var(--text-2, #86868B); }

.form-actions { display: flex; flex-direction: column; gap: 8px; }

/* ── Detail stats ────────────────────────── */
.detail-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.stat-card {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: var(--shadow-card);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text, #1D1D1F);
}

.stat-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-2, #86868B);
  letter-spacing: 0.02em;
}

/* ── Documents section ──────────────────── */
.documents-section {
  margin-top: 32px;
}

.documents-section .section-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-2, #86868B);
  margin-bottom: 16px;
}

.documents-list {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  overflow: hidden;
}

.doc-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border, #E5E5E7);
}
.doc-row:last-child { border-bottom: none; }
.doc-row:hover { background: rgba(0,0,0,0.02); }

.doc-row.skeleton {
  background: #f5f5f5;
  pointer-events: none;
}

.doc-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.doc-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text, #1D1D1F);
}

.doc-meta {
  font-size: 12px;
  color: var(--text-2, #86868B);
}

.doc-date {
  font-size: 12px;
  color: var(--text-2, #86868B);
}

.documents-empty {
  padding: 40px;
  text-align: center;
  color: var(--text-2, #86868B);
  font-size: 14px;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
}

.documents-loading {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  overflow: hidden;
}

/* ── Skeleton states ────────────────────── */
.skeleton {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
