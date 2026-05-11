<template>
  <aside class="props-panel" :class="{ open: isOpen }">
    <button class="toggle-btn" @click="isOpen = !isOpen" :title="isOpen ? 'Collapse' : 'Expand'">
      {{ isOpen ? '▶' : '◀' }}
    </button>

    <div v-if="isOpen" class="panel-content">
      <h4 class="panel-title">Properties</h4>

      <!-- ── Object-property (edge) viewer ─────────────────────────────── -->
      <template v-if="selectedProperty">
        <label class="field-label">Label</label>
        <p class="field-value">{{ selectedProperty!.label }}</p>
        <label class="field-label">Type</label>
        <p class="field-value">{{ selectedProperty!.property_type }}</p>
        <label class="field-label">URI</label>
        <p class="field-value mono">{{ selectedProperty!.uri }}</p>
        <div class="danger-zone">
          <button class="btn-danger" @click="confirmDeleteProperty">Delete Property</button>
        </div>
      </template>

      <p v-else class="empty-msg">Select a relation on the canvas,<br>or click a class to edit it.</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useOntologyStore } from '../../stores/ontology'

const store = useOntologyStore()
const { selectedProperty } = storeToRefs(store)
const isOpen = ref(true)

function confirmDeleteProperty() {
  if (!selectedProperty.value) return
  if (!confirm(`Delete property "${selectedProperty.value.label}"?\n\nThis will permanently remove it from the ontology and from all diagrams.`)) return
  store.deleteSelectedProperty()
}
</script>

<style scoped>
.props-panel {
  position: relative;
  background: var(--surface-container-lowest, #fff);
  border-left: 1px solid var(--outline-variant, #e5e5e7);
  display: flex;
  flex-direction: row;
  transition: width 0.2s;
  width: 44px;
  overflow: hidden;
}

.props-panel.open {
  width: 260px;
}

.toggle-btn {
  position: absolute;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  width: 22px;
  height: 48px;
  border: none;
  background: var(--surface-container, #ecedf9);
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  font-size: 10px;
  color: var(--on-surface-variant, #414755);
  z-index: 5;
}

.panel-content {
  padding: 16px 14px 16px 28px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 100%;
  overflow-y: auto;
}

.panel-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--on-surface-variant, #86868b);
  margin: 0 0 6px;
}

.field-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868b);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 4px;
}

.field-input {
  padding: 5px 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 6px;
  font-size: 12px;
  outline: none;
  resize: vertical;
  width: 100%;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: var(--primary, #0058bc);
}

.field-value {
  font-size: 12px;
  color: var(--on-surface, #1d1d1f);
  margin: 0;
}

.mono {
  font-family: monospace;
  font-size: 10px;
  word-break: break-all;
}

/* ── Section header ──────────────────────────────────────────────────────── */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--outline-variant, #e5e5e7);
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--on-surface-variant, #86868b);
}

.btn-add-attr {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: var(--primary, #0058bc);
  color: #fff;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-add-attr:hover {
  background: #0047a0;
}

/* ── Attribute list ──────────────────────────────────────────────────────── */
.attr-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
}

.attr-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface-container, #f4f4f8);
  border-radius: 6px;
  padding: 5px 8px;
  gap: 4px;
}

.attr-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.attr-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--on-surface, #1d1d1f);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.attr-type {
  font-size: 10px;
  font-family: monospace;
  color: var(--on-surface-variant, #86868b);
}

.attr-comment {
  font-size: 10px;
  color: var(--on-surface-variant, #86868b);
  font-style: italic;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 1px;
}

.attr-actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.btn-edit-attr,
.btn-del-attr {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: var(--on-surface-variant, #86868b);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-edit-attr:hover {
  background: #e8f0fe;
  color: #0058bc;
}

.btn-del-attr:hover {
  background: #fee2e2;
  color: #c0392b;
}

.attr-empty {
  font-size: 11px;
  color: var(--on-surface-variant, #86868b);
  font-style: italic;
  margin: 4px 0 0;
}

/* ── Add attribute form ──────────────────────────────────────────────────── */
.attr-form {
  background: var(--surface-container, #f4f4f8);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
  border: 1px solid var(--outline-variant, #e5e5e7);
}

.attr-form-actions {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 5px 0;
  border-radius: 6px;
  border: none;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary, #0058bc);
  color: #fff;
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--surface-container-highest, #e0e0e6);
  color: var(--on-surface, #1d1d1f);
}

/* ── Danger zone ─────────────────────────────────────────────────────────── */
.danger-zone {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--outline-variant, #e5e5e7);
}

.btn-danger {
  width: 100%;
  padding: 7px 12px;
  border-radius: 8px;
  border: none;
  background: #c0392b;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-danger:hover {
  background: #a93226;
}

.empty-msg {
  font-size: 13px;
  color: var(--on-surface-variant, #86868b);
  font-style: italic;
  margin: 0;
  text-align: center;
  padding-top: 24px;
}
</style>
