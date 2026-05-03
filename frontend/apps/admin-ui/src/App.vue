<template>
  <div class="admin-ui">

    <!-- Page header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Administration</h1>
        <p class="page-desc">Manage system settings, API keys, and user access.</p>
      </div>
    </div>

    <!-- Stats row -->
    <div class="stats-row">
      <div v-for="s in stats" :key="s.label" class="stat-card">
        <div class="stat-icon" :style="{ background: s.color + '18', color: s.color }">
          <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6"
            v-html="s.iconPath"/>
        </div>
        <div class="stat-body">
          <span class="stat-value">{{ s.value }}</span>
          <span class="stat-label">{{ s.label }}</span>
        </div>
        <span v-if="s.trend !== undefined" class="stat-trend" :class="s.trend > 0 ? 'trend--up' : 'trend--down'">
          {{ s.trend > 0 ? '↑' : '↓' }} {{ Math.abs(s.trend) }}%
        </span>
      </div>
    </div>

    <!-- Settings grid -->
    <div class="settings-grid">
      <div
        v-for="section in settingSections"
        :key="section.id"
        class="settings-card"
        :class="{ 'settings-card--active': activeSection === section.id }"
        @click="activeSection = section.id"
      >
        <div class="sc-header">
          <div class="sc-icon" :style="{ background: section.color + '18', color: section.color }">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"
              v-html="section.iconPath"/>
          </div>
          <span class="sc-badge" v-if="section.badge">{{ section.badge }}</span>
        </div>
        <h3 class="sc-title">{{ section.title }}</h3>
        <p class="sc-desc">{{ section.description }}</p>
        <div class="sc-footer">
          <span class="sc-items">{{ section.items }} settings</span>
          <span class="sc-arrow">→</span>
        </div>
      </div>
    </div>

    <!-- Detail panel -->
    <div v-if="activeSectionData" class="detail-panel">
      <!-- API Keys Panel -->
      <template v-if="activeSection === 'api'">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">API Keys</h2>
            <p class="panel-subtitle">Manage API keys for external integrations</p>
          </div>
          <div class="panel-actions-header">
            <button class="btn-primary" @click="showCreateKeyModal = true">
              <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10 4v12M4 10h12"/>
              </svg>
              Create Key
            </button>
            <button class="btn-ghost-sm" @click="activeSection = null">Close</button>
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="store.isLoading" class="api-keys-loading">
          <div v-for="n in 3" :key="n" class="api-key-row skeleton">
            <div class="skeleton-line" style="width: 40%;"></div>
            <div class="skeleton-line" style="width: 20%;"></div>
          </div>
        </div>

        <!-- Error state -->
        <div v-else-if="store.error" class="api-keys-error">
          <svg width="40" height="40" viewBox="0 0 20 20" fill="none" stroke="#FF3B30" stroke-width="1.5">
            <circle cx="10" cy="10" r="8"/>
            <path d="M7 7l6 6M13 7l-6 6"/>
          </svg>
          <p>{{ store.error }}</p>
          <button class="btn-ghost" @click="store.loadApiKeys()">Retry</button>
        </div>

        <!-- API Keys list -->
        <div v-else-if="store.apiKeys.length > 0" class="api-keys-list">
          <div v-for="key in store.apiKeys" :key="key.id" class="api-key-row" :class="{ revoked: !key.is_active }">
            <div class="api-key-info">
              <div class="api-key-header">
                <span class="api-key-name">{{ key.name }}</span>
                <span class="api-key-status" :class="key.is_active ? 'status--active' : 'status--revoked'">
                  {{ key.is_active ? 'Active' : 'Revoked' }}
                </span>
              </div>
              <div class="api-key-meta">
                <span>Scopes: {{ key.scopes.join(', ') || 'read' }}</span>
                <span>•</span>
                <span>Rate: {{ key.rate_limit }}/hr</span>
                <span>•</span>
                <span>Created: {{ formatDate(key.created_at) }}</span>
                <span v-if="key.last_used_at">• Last used: {{ formatDate(key.last_used_at) }}</span>
              </div>
            </div>
            <button 
              v-if="key.is_active" 
              class="btn-revoke"
              @click="confirmRevoke(key)"
              :disabled="store.isLoading"
            >
              Revoke
            </button>
          </div>

          <!-- Pagination -->
          <div v-if="store.totalPages > 1" class="pagination">
            <button 
              class="btn-ghost-sm" 
              :disabled="store.currentPage === 1"
              @click="store.loadApiKeys(store.currentPage - 1)"
            >
              ← Previous
            </button>
            <span class="page-info">Page {{ store.currentPage }} of {{ store.totalPages }}</span>
            <button 
              class="btn-ghost-sm" 
              :disabled="store.currentPage === store.totalPages"
              @click="store.loadApiKeys(store.currentPage + 1)"
            >
              Next →
            </button>
          </div>
        </div>

        <!-- Empty state -->
        <div v-else class="api-keys-empty">
          <svg width="48" height="48" viewBox="0 0 20 20" fill="none" stroke="#86868B" stroke-width="1.5">
            <path d="M15 11a3 3 0 11-5.7-1.3L3 6V3h3l1 1 1-1h2l.7 5z"/>
            <path d="M9 13l3-3"/>
          </svg>
          <h3>No API keys yet</h3>
          <p>Create your first API key to enable external integrations</p>
        </div>
      </template>

      <!-- Other sections -->
      <template v-else>
        <div class="panel-header">
          <h2 class="panel-title">{{ activeSectionData.title }}</h2>
          <button class="btn-ghost-sm" @click="activeSection = null">Close</button>
        </div>

        <div class="settings-list">
          <div v-for="item in activeSectionData.settingItems" :key="item.key" class="setting-row">
            <div class="setting-info">
              <span class="setting-name">{{ item.name }}</span>
              <span class="setting-desc">{{ item.description }}</span>
            </div>
            <div class="setting-control">
              <template v-if="item.type === 'toggle'">
                <button
                  class="toggle"
                  :class="{ 'toggle--on': item.value }"
                  @click="item.value = !item.value"
                >
                  <span class="toggle-thumb"/>
                </button>
              </template>
              <template v-else-if="item.type === 'select'">
                <select class="setting-select" v-model="item.value">
                  <option v-for="opt in item.options" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </template>
              <template v-else>
                <input class="setting-input" v-model="item.value" :type="item.type" />
              </template>
            </div>
          </div>
        </div>

        <div class="panel-actions">
          <button class="btn-ghost" @click="activeSection = null">Cancel</button>
          <button class="btn-primary">Save Changes</button>
        </div>
      </template>
    </div>

    <!-- Create Key Modal -->
    <div v-if="showCreateKeyModal" class="modal-overlay" @click.self="showCreateKeyModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Create API Key</h3>
          <button class="modal-close" @click="showCreateKeyModal = false">✕</button>
        </div>

        <!-- New key display (shown after creation) -->
        <div v-if="store.newlyCreatedKey" class="new-key-display">
          <div class="key-warning">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#FF9500" stroke-width="2">
              <path d="M10 2v8M10 17.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
            </svg>
            <span>Copy this key now. It won't be shown again!</span>
          </div>
          <div class="key-value">
            <code>{{ store.newlyCreatedKey }}</code>
            <button class="btn-copy" @click="copyKey">{{ copied ? 'Copied!' : 'Copy' }}</button>
          </div>
          <button class="btn-primary btn-full" @click="closeModal">Done</button>
        </div>

        <!-- Create form -->
        <form v-else @submit.prevent="handleCreateKey" class="modal-form">
          <label class="field">
            <span class="field-label">Key Name <span class="required">*</span></span>
            <input 
              v-model="newKeyForm.name" 
              class="field-input" 
              placeholder="e.g., Production Integration"
              required
            />
          </label>

          <label class="field">
            <span class="field-label">Scopes</span>
            <div class="checkbox-group">
              <label class="checkbox">
                <input type="checkbox" v-model="newKeyForm.scopes" value="read" />
                <span>Read</span>
              </label>
              <label class="checkbox">
                <input type="checkbox" v-model="newKeyForm.scopes" value="write" />
                <span>Write</span>
              </label>
              <label class="checkbox">
                <input type="checkbox" v-model="newKeyForm.scopes" value="admin" />
                <span>Admin</span>
              </label>
            </div>
          </label>

          <label class="field">
            <span class="field-label">Rate Limit (requests/hour)</span>
            <select v-model="newKeyForm.rate_limit" class="field-input">
              <option :value="100">100/hour</option>
              <option :value="1000">1,000/hour</option>
              <option :value="10000">10,000/hour</option>
            </select>
          </label>

          <label class="field">
            <span class="field-label">Expires At (optional)</span>
            <input 
              v-model="newKeyForm.expires_at" 
              type="datetime-local" 
              class="field-input"
            />
          </label>

          <div v-if="store.error" class="form-error">
            {{ store.error }}
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-ghost" @click="showCreateKeyModal = false">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="store.isLoading || !newKeyForm.name.trim()">
              {{ store.isLoading ? 'Creating...' : 'Create Key' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Revoke Confirmation Modal -->
    <div v-if="showRevokeModal" class="modal-overlay" @click.self="showRevokeModal = false">
      <div class="modal modal-confirm">
        <div class="modal-header">
          <h3>Revoke API Key</h3>
        </div>
        <p class="confirm-text">
          Are you sure you want to revoke "<strong>{{ keyToRevoke?.name }}</strong>"? 
          This action cannot be undone and any integrations using this key will stop working.
        </p>
        <div class="modal-actions">
          <button class="btn-ghost" @click="showRevokeModal = false">Cancel</button>
          <button class="btn-danger" :disabled="store.isLoading" @click="handleRevoke">
            {{ store.isLoading ? 'Revoking...' : 'Revoke Key' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from './stores/admin'
import type { APIKey, SettingSection } from './types'

const store = useAdminStore()
const activeSection = ref<string | null>(null)

// Modals
const showCreateKeyModal = ref(false)
const showRevokeModal = ref(false)
const keyToRevoke = ref<APIKey | null>(null)
const copied = ref(false)

// New key form
const newKeyForm = ref({
  name: '',
  scopes: ['read'],
  rate_limit: 1000,
  expires_at: '',
})

// Stats
const stats = computed(() => [
  { 
    label: 'Active API Keys', 
    value: store.activeApiKeys.length.toString(), 
    color: '#AF52DE', 
    iconPath: '<path d="M15 11a3 3 0 11-5.7-1.3L3 6V3h3l1 1 1-1h2l.7 5z"/><path d="M9 13l3-3"/>' 
  },
  { 
    label: 'Total Keys', 
    value: store.totalApiKeys.toString(), 
    color: '#007AFF', 
    iconPath: '<path d="M13 6a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M5 16a6 6 0 0110 0"/>' 
  },
  { 
    label: 'Storage Used', 
    value: '2.4 GB', 
    color: '#FF9500', 
    iconPath: '<rect x="2" y="5" width="16" height="12" rx="2"/><path d="M2 9h16"/>' 
  },
  { 
    label: 'Uptime', 
    value: '99.9%', 
    color: '#34C759', 
    iconPath: '<path d="M10 3a7 7 0 100 14A7 7 0 0010 3z"/><path d="M10 7v4l2.5 2.5"/>' 
  },
])

// Setting sections
const settingSections = ref<SettingSection[]>([
  {
    id: 'api',
    title: 'API Keys',
    description: 'Create and manage API keys for external integrations.',
    color: '#AF52DE',
    items: 4,
    badge: computed(() => store.activeApiKeys.length > 0 ? `${store.activeApiKeys.length} active` : null) as unknown as string | null,
    iconPath: '<path d="M15 11a3 3 0 11-5.7-1.3L3 6V3h3l1 1 1-1h2l.7 5z"/><path d="M9 13l3-3"/>',
    settingItems: [],
  },
  {
    id: 'users',
    title: 'Users & Access',
    description: 'Manage members, roles, and access permissions.',
    color: '#34C759',
    items: 8,
    badge: null,
    iconPath: '<path d="M14 10a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M4 18a7 7 0 0112 0"/>',
    settingItems: [
      { key: 'signup', name: 'Open Signup', description: 'Allow new users to register without invitation.', type: 'toggle', value: false },
      { key: 'mfa', name: 'Require MFA', description: 'Enforce multi-factor authentication for all users.', type: 'toggle', value: true },
    ],
  },
  {
    id: 'storage',
    title: 'Storage',
    description: 'Configure storage backends and retention policies.',
    color: '#FF9500',
    items: 5,
    badge: null,
    iconPath: '<rect x="2" y="5" width="16" height="12" rx="2"/><path d="M2 9h16"/>',
    settingItems: [
      { key: 'backend', name: 'Storage Backend', description: 'Where documents are persisted.', type: 'select', value: 'Local', options: ['Local', 'S3', 'GCS', 'Azure Blob'] },
      { key: 'retention', name: 'Auto-Archive', description: 'Move inactive documents to cold storage.', type: 'toggle', value: false },
    ],
  },
  {
    id: 'ai',
    title: 'AI & Embeddings',
    description: 'Model selection, API endpoints, and embedding configuration.',
    color: '#FF3B30',
    items: 7,
    badge: null,
    iconPath: '<circle cx="10" cy="10" r="4"/><path d="M10 2v3M10 15v3M2 10h3M15 10h3"/>',
    settingItems: [
      { key: 'model', name: 'Embedding Model', description: 'Model used for vector generation.', type: 'select', value: 'text-embedding-ada-002', options: ['text-embedding-ada-002', 'text-embedding-3-small', 'text-embedding-3-large'] },
      { key: 'dim', name: 'Vector Dimensions', description: 'Output vector size.', type: 'select', value: '1536', options: ['768', '1536', '3072'] },
    ],
  },
])

const activeSectionData = computed(() =>
  activeSection.value ? settingSections.value.find(s => s.id === activeSection.value) : null
)

// Load API keys on mount
onMounted(() => {
  store.loadApiKeys()
})

// Create key
async function handleCreateKey() {
  const success = await store.createApiKey({
    name: newKeyForm.value.name,
    scopes: newKeyForm.value.scopes,
    domain_ids: [], // Could add domain selection
    rate_limit: newKeyForm.value.rate_limit,
    expires_at: newKeyForm.value.expires_at || null,
  })

  if (success) {
    // Reset form
    newKeyForm.value = {
      name: '',
      scopes: ['read'],
      rate_limit: 1000,
      expires_at: '',
    }
  }
}

// Revoke key
function confirmRevoke(key: APIKey) {
  keyToRevoke.value = key
  showRevokeModal.value = true
}

async function handleRevoke() {
  if (!keyToRevoke.value) return

  const success = await store.revokeApiKey(keyToRevoke.value.id)
  if (success) {
    showRevokeModal.value = false
    keyToRevoke.value = null
  }
}

// Copy key to clipboard
async function copyKey() {
  if (!store.newlyCreatedKey) return
  await navigator.clipboard.writeText(store.newlyCreatedKey)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

// Close modal and reset
function closeModal() {
  showCreateKeyModal.value = false
  store.clearNewlyCreatedKey()
  copied.value = false
}

// Format date
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}
</script>

<style scoped>
.admin-ui {
  padding: 32px 40px;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* ── Page header ─────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text, #1D1D1F);
}

.page-desc {
  font-size: 14px;
  color: var(--text-2, #86868B);
  margin-top: 4px;
}

/* ── Stats ───────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.stat-card {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow-card, 0 1px 2px rgba(0,0,0,0.04));
}

.stat-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body { flex: 1; display: flex; flex-direction: column; gap: 2px; }

.stat-value {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text, #1D1D1F);
}

.stat-label {
  font-size: 12px;
  color: var(--text-2, #86868B);
  font-weight: 500;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
}
.trend--up { color: #34C759; }
.trend--down { color: #FF3B30; }

/* ── Settings grid ───────────────────────── */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.settings-card {
  background: var(--surface, #fff);
  border: 1.5px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: box-shadow 0.15s, border-color 0.15s, transform 0.15s;
  box-shadow: var(--shadow-card, 0 1px 2px rgba(0,0,0,0.04));
}
.settings-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.09);
  transform: translateY(-1px);
}
.settings-card--active {
  border-color: var(--primary, #007AFF);
  box-shadow: 0 0 0 3px rgba(0,122,255,0.1), 0 4px 20px rgba(0,0,0,0.09);
}

.sc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sc-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sc-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(175,82,222,0.12);
  color: #8e44ad;
}

.sc-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  letter-spacing: -0.01em;
}

.sc-desc {
  font-size: 13px;
  color: var(--text-2, #86868B);
  line-height: 1.4;
  flex: 1;
}

.sc-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--border, #E5E5E7);
}

.sc-items { font-size: 12px; color: var(--text-2, #86868B); }
.sc-arrow { font-size: 14px; color: var(--text-2, #86868B); }

/* ── Detail panel ────────────────────────── */
.detail-panel {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  padding: 24px;
  box-shadow: var(--shadow-card);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.panel-header > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.panel-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  letter-spacing: -0.01em;
}

.panel-subtitle {
  font-size: 13px;
  color: var(--text-2, #86868B);
}

.panel-actions-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid var(--border, #E5E5E7);
  gap: 16px;
}
.setting-row:last-child { border-bottom: none; }

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.setting-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text, #1D1D1F);
}

.setting-desc { font-size: 12px; color: var(--text-2, #86868B); }

.setting-control { flex-shrink: 0; }

/* Toggle */
.toggle {
  width: 44px;
  height: 26px;
  border-radius: 999px;
  background: var(--border, #E5E5E7);
  border: none;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
  padding: 0;
}
.toggle--on { background: var(--primary, #007AFF); }

.toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  transition: left 0.2s;
}
.toggle--on .toggle-thumb { left: 21px; }

.setting-select, .setting-input {
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 7px;
  padding: 6px 10px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text, #1D1D1F);
  background: var(--bg, #F5F5F7);
  outline: none;
  min-width: 160px;
  transition: border-color 0.12s;
}
.setting-select:focus, .setting-input:focus {
  border-color: var(--primary, #007AFF);
  box-shadow: 0 0 0 3px rgba(0,122,255,0.12);
  background: #fff;
}

.panel-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border, #E5E5E7);
}

/* ── API Keys specific styles ────────────── */
.api-keys-loading {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.api-keys-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  text-align: center;
  color: var(--text-2, #86868B);
}

.api-keys-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.api-key-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg, #F5F5F7);
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E5E7);
}
.api-key-row.revoked {
  opacity: 0.6;
}

.api-key-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.api-key-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.api-key-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
}

.api-key-status {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}
.api-key-status.status--active {
  background: rgba(52,199,89,0.12);
  color: #1a7f37;
}
.api-key-status.status--revoked {
  background: rgba(134,134,139,0.12);
  color: #636366;
}

.api-key-meta {
  font-size: 12px;
  color: var(--text-2, #86868B);
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-revoke {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #FF3B30;
  background: transparent;
  color: #FF3B30;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.12s;
}
.btn-revoke:hover:not(:disabled) {
  background: #FF3B30;
  color: white;
}
.btn-revoke:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.api-keys-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 24px;
  text-align: center;
  color: var(--text-2, #86868B);
}

.api-keys-empty h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border, #E5E5E7);
}

.page-info {
  font-size: 13px;
  color: var(--text-2, #86868B);
}

/* ── Buttons ─────────────────────────────── */
.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E5E7);
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-2, #86868B);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s;
}
.btn-ghost:hover:not(:disabled) { background: rgba(0,0,0,0.04); }
.btn-ghost:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-ghost-sm {
  padding: 6px 12px;
  border-radius: 7px;
  border: 1px solid var(--border, #E5E5E7);
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-2, #86868B);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s;
}
.btn-ghost-sm:hover:not(:disabled) { background: rgba(0,0,0,0.04); }
.btn-ghost-sm:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-sm, 8px);
  border: none;
  background: var(--primary, #007AFF);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.12s;
}
.btn-primary:hover:not(:disabled) { opacity: 0.88; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-danger {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  border-radius: var(--radius-sm, 8px);
  border: none;
  background: #FF3B30;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.12s;
}
.btn-danger:hover:not(:disabled) { opacity: 0.88; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-full { width: 100%; justify-content: center; }

/* ── Modal ───────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.modal {
  background: var(--surface, #fff);
  border-radius: var(--radius, 16px);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  animation: modal-in 0.2s ease;
}

@keyframes modal-in {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border, #E5E5E7);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  margin: 0;
}

.modal-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.06);
  color: var(--text-2, #86868B);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.12s;
}
.modal-close:hover { background: rgba(0,0,0,0.1); }

.modal-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-confirm {
  padding: 24px;
}

.confirm-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text, #1D1D1F);
  margin: 16px 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid var(--border, #E5E5E7);
}

/* ── Form Fields ─────────────────────────── */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text, #1D1D1F);
}

.required { color: #FF3B30; }

.field-input {
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius-sm, 8px);
  padding: 10px 12px;
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

.checkbox-group {
  display: flex;
  gap: 16px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text, #1D1D1F);
}

.form-error {
  padding: 12px;
  background: rgba(255,59,48,0.08);
  border: 1px solid rgba(255,59,48,0.2);
  border-radius: var(--radius-sm, 8px);
  color: #FF3B30;
  font-size: 13px;
}

/* ── New Key Display ─────────────────────── */
.new-key-display {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.key-warning {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255,149,0,0.1);
  border: 1px solid rgba(255,149,0,0.2);
  border-radius: var(--radius-sm, 8px);
  font-size: 13px;
  color: #bf6900;
}

.key-value {
  display: flex;
  gap: 10px;
  align-items: stretch;
}

.key-value code {
  flex: 1;
  padding: 12px;
  background: var(--bg, #F5F5F7);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: var(--radius-sm, 8px);
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 13px;
  word-break: break-all;
}

.btn-copy {
  padding: 8px 16px;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--border, #E5E5E7);
  background: var(--surface, #fff);
  font-size: 13px;
  font-weight: 500;
  color: var(--text, #1D1D1F);
  cursor: pointer;
  transition: background 0.12s;
  white-space: nowrap;
}
.btn-copy:hover { background: var(--bg, #F5F5F7); }

/* ── Skeleton Loading ────────────────────── */
.skeleton {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.skeleton-line {
  height: 16px;
  background: #e0e0e0;
  border-radius: 4px;
}
</style>
