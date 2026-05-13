<template>
  <div class="editor">
    <!-- Header bar -->
    <header class="editor-header">
      <button class="back-btn" @click="handleClose">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        <span>{{ domainName }}</span>
      </button>
      <h2 class="editor-title">Ontology Editor</h2>
      
      <!-- Header actions: Export / Import / Save -->
      <div class="header-actions">
        <!-- Export OWL -->
        <button class="io-btn" :disabled="isExportDisabled" title="Exportar como OWL/XML" @click="handleExportOWL">
          <svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 3v10M6 9l4 4 4-4M3 16h14"/>
          </svg>
          <span class="io-badge">OWL</span>
        </button>
        <!-- Export TTL -->
        <button class="io-btn" :disabled="isExportDisabled" title="Exportar como Turtle (.ttl)" @click="handleExportTTL">
          <svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 3v10M6 9l4 4 4-4M3 16h14"/>
          </svg>
          <span class="io-badge">TTL</span>
        </button>

        <!-- Import OWL -->
        <button class="io-btn io-btn--import" :disabled="isImportDisabled" :title="importDisabledTitle" @click="importOwlRef?.click()">
          <svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 17V7M6 11l4-4 4 4M3 4h14"/>
          </svg>
          <span class="io-badge">OWL</span>
        </button>
        <!-- Import TTL -->
        <button class="io-btn io-btn--import" :disabled="isImportDisabled" :title="importDisabledTitle" @click="importTtlRef?.click()">
          <svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 17V7M6 11l4-4 4 4M3 4h14"/>
          </svg>
          <span class="io-badge">TTL</span>
        </button>

        <!-- Hidden file pickers -->
        <input ref="importOwlRef" type="file" accept=".owl,.rdf" hidden @change="onImportFileChange($event, 'owl')" />
        <input ref="importTtlRef" type="file" accept=".ttl" hidden @change="onImportFileChange($event, 'ttl')" />

        <div class="header-sep" />

        <!-- Save -->
        <button
          class="save-btn"
          :class="{ 'has-changes': store.hasUnsavedChanges }"
          :disabled="!store.hasUnsavedChanges || store.isSaving"
          @click="handleSave"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          <span>{{ store.isSaving ? 'Saving...' : 'Save' }}</span>
        </button>
      </div>
    </header>

    <!-- Tab bar -->
    <DiagramTabs />

    <!-- Main layout -->
    <div class="editor-body">
      <!-- Left palette -->
      <OntologyPalette @add-concept="addConceptToCanvas" />

      <!-- Canvas (relative, toolbox floats inside) -->
      <div class="canvas-area">
        <OntologyCanvas ref="canvasRef" />

        <!-- Floating toolbox -->
        <OntologyToolbox
          :snap-active="store.snapToGrid"
          @zoom-in="canvasRef?.zoomIn()"
          @zoom-out="canvasRef?.zoomOut()"
          @toggle-snap="store.toggleSnapToGrid()"
          @fit="canvasRef?.fitView()"
        />
      </div>

      <!-- Right panel: OWL Class Definition (create/edit) or Properties (edge view) -->
      <OWLClassPanel v-if="store.panelMode !== null" />
      <OntologyProperties v-else />
    </div>

    <!-- Loading overlay -->
    <div v-if="store.isLoading" class="loading-overlay">
      <div class="spinner" />
      <p>Loading ontology…</p>
    </div>

    <!-- Import flow modals -->
    <ImportOptionsModal
      :is-open="showImportOptions"
      :file-name="pendingImportFile?.name ?? ''"
      @cancel="cancelImport"
      @execute="onImportModeChosen"
    />
    <ImportReplaceConfirmModal
      :is-open="showReplaceConfirm"
      :class-count="store.concepts.length"
      :prop-count="store.properties.length"
      @cancel="cancelImport"
      @confirm="onReplaceConfirmed"
    />

    <!-- Toast notification -->
    <Transition name="toast">
      <div v-if="toastState" class="toast" :class="`toast--${toastState.type}`">
        <svg v-if="toastState.type === 'success'" width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <polyline points="4 10 8 14 16 6"/>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="10" cy="10" r="8"/><line x1="10" y1="7" x2="10" y2="10"/><line x1="10" y1="13" x2="10.01" y2="13"/>
        </svg>
        {{ toastState.message }}
      </div>
    </Transition>

    <!-- Unsaved changes modal -->
    <UnsavedChangesModal
      :is-open="showUnsavedModal"
      :is-saving="store.isSaving"
      :concept-operations="store.pendingConceptOperations.length"
      :property-operations="store.pendingPropertyOperations.length"
      :diagram-operations="store.pendingDiagramOperations.length"
      @save="onModalSave"
      @discard="onModalDiscard"
      @cancel="onModalCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import { useOntologyStore } from '../../stores/ontology'
import { ontologyApi } from '../../services/ontologyApi'
import type { OntologyConcept } from '../../types/ontology'
import DiagramTabs from './DiagramTabs.vue'
import OntologyCanvas from './OntologyCanvas.vue'
import OntologyPalette from './OntologyPalette.vue'
import OntologyProperties from './OntologyProperties.vue'
import OWLClassPanel from './OWLClassPanel.vue'
import OntologyToolbox from './OntologyToolbox.vue'
import UnsavedChangesModal from './UnsavedChangesModal.vue'
import ImportOptionsModal from './ImportOptionsModal.vue'
import ImportReplaceConfirmModal from './ImportReplaceConfirmModal.vue'

const props = defineProps<{ domainId: string; domainName: string }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const store = useOntologyStore()
const { panelMode } = storeToRefs(store)
const canvasRef = ref<InstanceType<typeof OntologyCanvas> | null>(null)
const showUnsavedModal = ref(false)
const pendingClose = ref(false)
const importOwlRef = ref<HTMLInputElement | null>(null)
const importTtlRef = ref<HTMLInputElement | null>(null)
const isImporting = ref(false)
const pendingImportFile = ref<File | null>(null)
const showImportOptions = ref(false)
const showReplaceConfirm = ref(false)
const toastState = ref<{ message: string; type: 'success' | 'error' } | null>(null)
let toastTimer: ReturnType<typeof setTimeout> | null = null

const isExportDisabled = computed(() => store.concepts.length === 0)
const isImportDisabled = computed(() => store.hasUnsavedChanges || isImporting.value)
const importDisabledTitle = computed(() =>
  store.hasUnsavedChanges ? 'Guarda los cambios antes de importar' : 'Importar ontología'
)

onMounted(() => store.loadForDomain(props.domainId))

onBeforeUnmount(() => {
  if (store.hasUnsavedChanges) store.clearPendingChanges()
})

async function addConceptToCanvas(concept: OntologyConcept) {
  await store.addClassToCanvas(concept, { x: 100 + Math.random() * 300, y: 100 + Math.random() * 200 })
}

function handleExportOWL() { ontologyApi.exportOntology(props.domainId, 'owl') }
function handleExportTTL() { ontologyApi.exportOntology(props.domainId, 'ttl') }

function showToast(message: string, type: 'success' | 'error') {
  if (toastTimer) clearTimeout(toastTimer)
  toastState.value = { message, type }
  toastTimer = setTimeout(() => { toastState.value = null }, 4000)
}

function onImportFileChange(event: Event, _fmt: 'owl' | 'ttl') {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  pendingImportFile.value = file
  showImportOptions.value = true
}

function cancelImport() {
  showImportOptions.value = false
  showReplaceConfirm.value = false
  pendingImportFile.value = null
}

function onImportModeChosen(mode: 'merge' | 'replace') {
  if (mode === 'replace') {
    showImportOptions.value = false
    showReplaceConfirm.value = true
  } else {
    showImportOptions.value = false
    executeImport('merge')
  }
}

function onReplaceConfirmed() {
  showReplaceConfirm.value = false
  executeImport('replace')
}

async function executeImport(mode: 'merge' | 'replace') {
  const file = pendingImportFile.value
  pendingImportFile.value = null
  if (!file) return
  isImporting.value = true
  try {
    const result = await ontologyApi.importOntology(props.domainId, file, mode)
    await store.loadForDomain(props.domainId)
    const msg = mode === 'replace'
      ? `Ontología reemplazada: ${result.concepts_created} clases importadas`
      : `Importación completada: ${result.concepts_created} creadas, ${result.concepts_updated} actualizadas`
    showToast(msg, 'success')
  } catch (err) {
    showToast('Error al importar: ' + (err instanceof Error ? err.message : String(err)), 'error')
  } finally {
    isImporting.value = false
  }
}

// Handle save button click
async function handleSave() {
  const success = await store.saveAllChanges()
  if (success) {
    // Show success notification or feedback
    console.log('All changes saved successfully')
  }
}

// Handle close button click
function handleClose() {
  if (store.hasUnsavedChanges) {
    pendingClose.value = true
    showUnsavedModal.value = true
  } else {
    emit('close')
  }
}

// Modal event handlers
async function onModalSave() {
  const success = await store.saveAllChanges()
  if (success) {
    showUnsavedModal.value = false
    if (pendingClose.value) {
      pendingClose.value = false
      emit('close')
    }
  }
}

function onModalDiscard() {
  store.clearPendingChanges()
  showUnsavedModal.value = false
  if (pendingClose.value) {
    pendingClose.value = false
    emit('close')
  }
}

function onModalCancel() {
  showUnsavedModal.value = false
  pendingClose.value = false
}
</script>

<style scoped>
.editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--background, #f9f9ff);
  font-family: Inter, sans-serif;
  position: relative;
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 20px;
  height: 52px;
  min-height: 52px;
  background: var(--surface-container-lowest, #fff);
  border-bottom: 1px solid var(--outline-variant, #e5e5e7);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary, #0058bc);
  cursor: pointer;
  padding: 0;
}

.editor-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--on-surface, #1d1d1f);
  margin: 0;
  flex: 1;
}

.saving-badge {
  font-size: 12px;
  color: var(--on-surface-variant, #86868b);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

.header-sep {
  width: 1px;
  height: 20px;
  background: var(--outline-variant, #e5e5e7);
  margin: 0 6px;
  flex-shrink: 0;
}

.io-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 9px;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--outline-variant, #e5e5e7);
  background: transparent;
  color: var(--on-surface-variant, #86868b);
  transition: all 0.12s ease;
  white-space: nowrap;
}

.io-btn:hover:not(:disabled) {
  background: var(--surface-container, #ecedf9);
  color: var(--on-surface, #1d1d1f);
  border-color: var(--primary, #0058bc);
}

.io-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.io-btn--import svg { transform: scaleY(-1) rotate(180deg); }

.io-badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

@media (max-width: 900px) {
  .io-badge { display: none; }
  .io-btn { padding: 6px 7px; }
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid var(--outline-variant, #e5e5e7);
  background: transparent;
  color: var(--on-surface-variant, #86868b);
}

.save-btn:hover:not(:disabled) {
  background: var(--surface-container, #ecedf9);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-btn.has-changes {
  background: var(--primary, #0058bc);
  color: white;
  border-color: var(--primary, #0058bc);
}

.save-btn.has-changes:hover:not(:disabled) {
  background: var(--primary-hover, #004494);
}

.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.canvas-area {
  flex: 1;
  position: relative;
  display: flex;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(249, 249, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 100;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--surface-container, #ecedf9);
  border-top-color: var(--primary, #0058bc);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Toast ────────────────────────────────────────────────────────────────── */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  z-index: 2000;
  max-width: 480px;
  white-space: nowrap;
}

.toast--success { background: #1a7a3c; color: #fff; }
.toast--error   { background: var(--error, #ba1a1a); color: #fff; }

.toast-enter-active, .toast-leave-active { transition: opacity 0.25s, transform 0.25s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }
</style>
