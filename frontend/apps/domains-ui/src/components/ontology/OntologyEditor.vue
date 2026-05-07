<template>
  <div class="editor">
    <!-- Header bar -->
    <header class="editor-header">
      <button class="back-btn" @click="$emit('close')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        <span>{{ domainName }}</span>
      </button>
      <h2 class="editor-title">Ontology Editor</h2>
      <span v-if="store.isSaving" class="saving-badge">Saving…</span>
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
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useOntologyStore } from '../../stores/ontology'
import { ontologyApi } from '../../services/ontologyApi'
import type { OntologyConcept } from '../../types/ontology'
import DiagramTabs from './DiagramTabs.vue'
import OntologyCanvas from './OntologyCanvas.vue'
import OntologyPalette from './OntologyPalette.vue'
import OntologyProperties from './OntologyProperties.vue'
import OntologyToolbox from './OntologyToolbox.vue'

const props = defineProps<{ domainId: string; domainName: string }>()
defineEmits<{ (e: 'close'): void }>()

const store = useOntologyStore()
const canvasRef = ref<InstanceType<typeof OntologyCanvas> | null>(null)

onMounted(() => store.loadForDomain(props.domainId))

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
