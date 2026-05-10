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
      
      <!-- Save button with disk icon -->
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
    </header>

    <!-- Tab bar -->
    <DiagramTabs />

    <!-- Main layout -->
    <div class="editor-body">
      <!-- Left palette -->
      <OntologyPalette
        @add-concept="addConceptToCanvas"
        @export-owl="exportOWL"
        @import-owl="importOWL"
      />

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

      <!-- Right properties panel -->
      <OntologyProperties />
    </div>

    <!-- Loading overlay -->
    <div v-if="store.isLoading" class="loading-overlay">
      <div class="spinner" />
      <p>Loading ontology…</p>
    </div>

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
import { onMounted, ref, onBeforeUnmount } from 'vue'
import { useOntologyStore } from '../../stores/ontology'
import { ontologyApi } from '../../services/ontologyApi'
import type { OntologyConcept } from '../../types/ontology'
import DiagramTabs from './DiagramTabs.vue'
import OntologyCanvas from './OntologyCanvas.vue'
import OntologyPalette from './OntologyPalette.vue'
import OntologyProperties from './OntologyProperties.vue'
import OntologyToolbox from './OntologyToolbox.vue'
import UnsavedChangesModal from './UnsavedChangesModal.vue'

const props = defineProps<{ domainId: string; domainName: string }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const store = useOntologyStore()
const canvasRef = ref<InstanceType<typeof OntologyCanvas> | null>(null)
const showUnsavedModal = ref(false)
const pendingClose = ref(false)

onMounted(() => store.loadForDomain(props.domainId))

onBeforeUnmount(() => {
  // Clean up any pending state
  if (store.hasUnsavedChanges) {
    store.clearPendingChanges()
  }
})

async function addConceptToCanvas(concept: OntologyConcept) {
  await store.addClassToCanvas(concept, { x: 100 + Math.random() * 300, y: 100 + Math.random() * 200 })
}

function exportOWL() {
  ontologyApi.exportOntology(props.domainId)
}

async function importOWL(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  // Call BFF proxy directly since apiClient doesn't support FormData
  const res = await fetch(`/api/v1/domains/${props.domainId}/ontology/import`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  })
  if (!res.ok) {
    alert('Import failed: ' + (await res.text()))
    return
  }
  // Reload ontology state
  await store.loadForDomain(props.domainId)
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
  margin-left: auto;
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
</style>
