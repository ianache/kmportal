<template>
  <aside class="props-panel" :class="{ open: isOpen }">
    <button class="toggle-btn" @click="isOpen = !isOpen" :title="isOpen ? 'Collapse' : 'Expand'">
      {{ isOpen ? '▶' : '◀' }}
    </button>

    <div v-if="isOpen" class="panel-content">
      <h4 class="panel-title">Properties</h4>

      <!-- ── Class editor ───────────────────────────────────────────────── -->
      <template v-if="selectedConcept">
        <label class="field-label">Label</label>
        <input class="field-input" v-model="editLabel" @blur="save" />
        <label class="field-label">URI</label>
        <input class="field-input" v-model="editUri" @blur="save" />
        <label class="field-label">Comment</label>
        <textarea class="field-input" rows="3" v-model="editComment" @blur="save" />

        <!-- ── Data Attributes ──────────────────────────────────────────── -->
        <div class="section-header">
          <span class="section-title">Data Attributes</span>
          <button class="btn-add-attr" @click="openAddForm" title="Add attribute">+</button>
        </div>

        <!-- Existing attributes list -->
        <div v-if="selectedConceptAttributes.length" class="attr-list">
          <template v-for="attr in selectedConceptAttributes" :key="attr.id">
            <!-- Edit form (inline, replaces the row) -->
            <div v-if="editingAttrId === attr.id" class="attr-form">
              <label class="field-label">Name</label>
              <input
                class="field-input"
                v-model="editForm.label"
                @keydown.enter="submitEditForm"
                @keydown.esc="closeEditForm"
              />
              <label class="field-label">XSD Type</label>
              <select class="field-input" v-model="editForm.xsdUri">
                <option v-for="t in XSD_TYPES" :key="t.uri" :value="t.uri">xsd:{{ t.label }}</option>
              </select>
              <label class="field-label">Comment</label>
              <input class="field-input" v-model="editForm.comment" placeholder="(optional)" />
              <div class="attr-form-actions">
                <button class="btn-secondary" @click="closeEditForm">Cancel</button>
                <button class="btn-primary" :disabled="!editForm.label" @click="submitEditForm">Save</button>
              </div>
            </div>
            <!-- Read-only row -->
            <div v-else class="attr-row">
              <div class="attr-info">
                <span class="attr-name">{{ attr.label }}</span>
                <span class="attr-type">{{ xsdLabel(attr.target_class_id) }}</span>
                <span v-if="attr.comment" class="attr-comment">{{ attr.comment }}</span>
              </div>
              <div class="attr-actions">
                <button class="btn-edit-attr" @click="openEditForm(attr)" title="Edit attribute">✎</button>
                <button class="btn-del-attr" @click="confirmDeleteAttr(attr)" title="Delete attribute">×</button>
              </div>
            </div>
          </template>
        </div>
        <p v-else class="attr-empty">No data attributes yet.</p>

        <!-- Add attribute form -->
        <div v-if="attrForm.visible" class="attr-form">
          <label class="field-label">Name</label>
          <input
            ref="attrLabelRef"
            class="field-input"
            v-model="attrForm.label"
            placeholder="e.g. hasLicensePlate"
            @keydown.enter="submitAttrForm"
            @keydown.esc="closeAddForm"
          />
          <label class="field-label">XSD Type</label>
          <select class="field-input" v-model="attrForm.xsdUri">
            <option v-for="t in XSD_TYPES" :key="t.uri" :value="t.uri">xsd:{{ t.label }}</option>
          </select>
          <label class="field-label">Comment</label>
          <input class="field-input" v-model="attrForm.comment" placeholder="(optional)" />
          <div class="attr-form-actions">
            <button class="btn-secondary" @click="closeAddForm">Cancel</button>
            <button class="btn-primary" :disabled="!attrForm.label" @click="submitAttrForm">Add</button>
          </div>
        </div>

        <div class="danger-zone">
          <button class="btn-danger" @click="confirmDeleteClass">Delete Class</button>
        </div>
      </template>

      <!-- ── Object-property (edge) viewer ─────────────────────────────── -->
      <template v-else-if="selectedProperty">
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

      <p v-else class="empty-msg">Select a class or relation on the canvas.</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { nextTick, reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useOntologyStore } from '../../stores/ontology'
import { XSD_TYPES, xsdLabel, type XsdTypeUri } from '../../types/ontology'
import type { OntologyProperty } from '../../types/ontology'

const store = useOntologyStore()
const { selectedConcept, selectedProperty, selectedConceptAttributes } = storeToRefs(store)
const isOpen = ref(true)

// ── Class metadata edit ──────────────────────────────────────────────────────
const editLabel = ref('')
const editUri = ref('')
const editComment = ref('')

// All reactive state that the immediate watch touches must be declared before the watch call
const attrForm = reactive({
  visible: false,
  label: '',
  xsdUri: XSD_TYPES[0].uri as string,
  comment: '',
})

const editingAttrId = ref<string | null>(null)
const editForm = reactive({ label: '', xsdUri: XSD_TYPES[0].uri as string, comment: '' })

watch(
  selectedConcept,
  (c) => {
    editLabel.value = c?.label ?? ''
    editUri.value = c?.uri ?? ''
    editComment.value = c?.comment ?? ''
    attrForm.visible = false
    editingAttrId.value = null
  },
  { immediate: true }
)

async function save() {
  if (!selectedConcept.value) return
  const current = selectedConcept.value
  if (
    editLabel.value === current.label &&
    editUri.value === current.uri &&
    editComment.value === (current.comment ?? '')
  ) return
  await store.updateSelectedConcept({
    label: editLabel.value,
    uri: editUri.value,
    comment: editComment.value || undefined,
  })
}

function confirmDeleteClass() {
  if (!selectedConcept.value) return
  if (!confirm(`Delete class "${selectedConcept.value.label}"?\n\nThis will permanently remove it from the ontology and from all diagrams.`)) return
  store.deleteSelectedConcept()
}

function confirmDeleteProperty() {
  if (!selectedProperty.value) return
  if (!confirm(`Delete property "${selectedProperty.value.label}"?\n\nThis will permanently remove it from the ontology and from all diagrams.`)) return
  store.deleteSelectedProperty()
}

// ── Data attributes ──────────────────────────────────────────────────────────
const attrLabelRef = ref<HTMLInputElement | null>(null)

function openEditForm(attr: OntologyProperty) {
  attrForm.visible = false
  editingAttrId.value = attr.id
  editForm.label = attr.label
  editForm.xsdUri = attr.target_class_id
  editForm.comment = attr.comment ?? ''
}

function closeEditForm() {
  editingAttrId.value = null
}

async function submitEditForm() {
  if (!editForm.label.trim() || !editingAttrId.value) return
  await store.updateDatatypeAttribute(
    editingAttrId.value,
    editForm.label.trim(),
    editForm.xsdUri,
    editForm.comment.trim() || undefined,
  )
  closeEditForm()
}

function openAddForm() {
  attrForm.label = ''
  attrForm.xsdUri = XSD_TYPES[0].uri
  attrForm.comment = ''
  attrForm.visible = true
  nextTick(() => attrLabelRef.value?.focus())
}

function closeAddForm() {
  attrForm.visible = false
}

async function submitAttrForm() {
  if (!attrForm.label.trim()) return
  await store.createDatatypeAttribute(
    attrForm.label.trim(),
    attrForm.xsdUri,
    attrForm.comment.trim() || undefined,
  )
  closeAddForm()
}

async function confirmDeleteAttr(attr: OntologyProperty) {
  if (!confirm(`Delete attribute "${attr.label}"?`)) return
  await store.deleteDatatypeAttribute(attr.id)
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
