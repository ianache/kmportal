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
        <span class="stat-trend" :class="s.trend > 0 ? 'trend--up' : 'trend--down'">
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
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const activeSection = ref<string | null>(null)

const stats = [
  { label: 'Active Users', value: '12', trend: 8, color: '#007AFF', iconPath: '<path d="M13 6a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M5 16a6 6 0 0110 0"/>' },
  { label: 'API Keys', value: '4', trend: 0, color: '#AF52DE', iconPath: '<path d="M15 11a3 3 0 11-5.7-1.3L3 6V3h3l1 1 1-1h2l.7 5z"/><path d="M9 13l3-3"/>' },
  { label: 'Storage Used', value: '2.4 GB', trend: 12, color: '#FF9500', iconPath: '<rect x="2" y="5" width="16" height="12" rx="2"/><path d="M2 9h16"/>' },
  { label: 'Uptime', value: '99.9%', trend: 0, color: '#34C759', iconPath: '<path d="M10 3a7 7 0 100 14A7 7 0 0010 3z"/><path d="M10 7v4l2.5 2.5"/>' },
]

interface SettingItem {
  key: string
  name: string
  description: string
  type: string
  value: any
  options?: string[]
}

interface SettingSection {
  id: string
  title: string
  description: string
  color: string
  items: number
  badge: string | null
  iconPath: string
  settingItems: SettingItem[]
}

const settingSections = ref<SettingSection[]>([
  {
    id: 'general',
    title: 'General',
    description: 'Workspace name, language, timezone, and display preferences.',
    color: '#007AFF',
    items: 6,
    badge: null,
    iconPath: '<circle cx="10" cy="10" r="3"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2"/>',
    settingItems: [
      { key: 'workspace', name: 'Workspace Name', description: 'Display name for your workspace.', type: 'text', value: 'Knowledge Center' },
      { key: 'lang', name: 'Language', description: 'UI language.', type: 'select', value: 'English', options: ['English', 'Español', 'Français'] },
      { key: 'timezone', name: 'Timezone', description: 'Used for timestamps and scheduling.', type: 'select', value: 'UTC-5', options: ['UTC', 'UTC-5', 'UTC+1', 'UTC+8'] },
    ],
  },
  {
    id: 'users',
    title: 'Users & Access',
    description: 'Manage members, roles, and access permissions.',
    color: '#34C759',
    items: 8,
    badge: '2 pending',
    iconPath: '<path d="M14 10a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M4 18a7 7 0 0112 0"/>',
    settingItems: [
      { key: 'signup', name: 'Open Signup', description: 'Allow new users to register without invitation.', type: 'toggle', value: false },
      { key: 'mfa', name: 'Require MFA', description: 'Enforce multi-factor authentication for all users.', type: 'toggle', value: true },
    ],
  },
  {
    id: 'api',
    title: 'API Keys',
    description: 'Create and manage API keys for external integrations.',
    color: '#AF52DE',
    items: 4,
    badge: null,
    iconPath: '<path d="M15 11a3 3 0 11-5.7-1.3L3 6V3h3l1 1 1-1h2l.7 5z"/><path d="M9 13l3-3"/>',
    settingItems: [
      { key: 'rate', name: 'Rate Limit', description: 'Max requests per minute per key.', type: 'select', value: '1000/min', options: ['100/min', '1000/min', '10000/min', 'Unlimited'] },
      { key: 'expiry', name: 'Key Expiry', description: 'Auto-expire keys after inactivity.', type: 'toggle', value: true },
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
  {
    id: 'notifications',
    title: 'Notifications',
    description: 'Alerts, digest emails, and webhook integrations.',
    color: '#5AC8FA',
    items: 4,
    badge: null,
    iconPath: '<path d="M10 2a6 6 0 00-6 6v3l-1.5 2.5h15L16 11V8a6 6 0 00-6-6z"/><path d="M8.5 17.5a1.5 1.5 0 003 0"/>',
    settingItems: [
      { key: 'email', name: 'Email Digest', description: 'Receive a daily activity summary.', type: 'toggle', value: true },
      { key: 'webhook', name: 'Webhook URL', description: 'POST events to an external endpoint.', type: 'text', value: '' },
    ],
  },
])

const activeSectionData = computed(() =>
  activeSection.value ? settingSections.value.find(s => s.id === activeSection.value) : null
)
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
  background: rgba(255,149,0,0.12);
  color: #bf6900;
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

.panel-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  letter-spacing: -0.01em;
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
.btn-ghost:hover { background: rgba(0,0,0,0.04); }

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
.btn-ghost-sm:hover { background: rgba(0,0,0,0.04); }

.btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 8px 18px;
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
.btn-primary:hover { opacity: 0.88; }
</style>
