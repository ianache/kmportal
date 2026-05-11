<template>
  <aside class="palette">
    <h4 class="palette-title">Elements</h4>

    <!-- Drag sources -->
    <div
      class="palette-item"
      draggable="true"
      @dragstart="onDragStart($event, 'class')"
    >
      <div class="item-icon class-icon">C</div>
      <span>Class</span>
    </div>
    <div
      class="palette-item"
      draggable="true"
      @dragstart="onDragStart($event, 'property')"
    >
      <div class="item-icon prop-icon">P</div>
      <span>Property</span>
    </div>

    <div class="divider" />

    <!-- Concept list (click to add to canvas) -->
    <h4 class="palette-title">Concepts</h4>
    <div class="concept-list">
      <button
        v-for="c in store.concepts"
        :key="c.id"
        class="concept-chip"
        @click="$emit('add-concept', c)"
        :title="c.uri"
      >{{ c.label }}</button>
      <p v-if="!store.concepts.length" class="empty-hint">No classes yet</p>
    </div>

    <div class="divider" />

    <!-- Import / Export -->
    <h4 class="palette-title">OWL</h4>
    <label class="palette-btn import-btn">
      Import OWL
      <input type="file" accept=".owl,.rdf,.ttl" hidden @change="onImport" />
    </label>
    <button class="palette-btn export-btn" @click="$emit('export-owl')">Export OWL</button>
    <button class="palette-btn cleanup-btn" :disabled="cleaning" @click="runCleanup">
      {{ cleaning ? 'Limpiando…' : 'Fix Duplicates' }}
    </button>
    <p v-if="cleanupMsg" class="cleanup-msg">{{ cleanupMsg }}</p>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useOntologyStore } from '../../stores/ontology'
import { createLazyApiClient } from 'shell/microFrontendApi'
import type { OntologyConcept } from '../../types/ontology'

const store = useOntologyStore()
const emit = defineEmits<{
  (e: 'drag-start', type: 'class' | 'property'): void
  (e: 'add-concept', concept: OntologyConcept): void
  (e: 'export-owl'): void
  (e: 'import-owl', file: File): void
}>()

const cleaning = ref(false)
const cleanupMsg = ref('')
const apiClient = createLazyApiClient()

async function runCleanup() {
  if (!store.activeDomainId) return
  cleaning.value = true
  cleanupMsg.value = ''
  try {
    const res = await apiClient.post<{ deleted: number; message: string }>(
      `/v1/domains/${store.activeDomainId}/ontology/cleanup-duplicates`,
      {}
    )
    cleanupMsg.value = res.data?.message ?? 'Done.'
    if ((res.data?.deleted ?? 0) > 0) {
      // Reload ontology so UI reflects cleaned data
      const domainId = store.activeDomainId
      store.concepts = []
      store.properties = []
      store.activeDomainId = null as any
      await store.loadForDomain(domainId)
    }
  } catch {
    cleanupMsg.value = 'Error al limpiar.'
  } finally {
    cleaning.value = false
  }
}

function onDragStart(event: DragEvent, type: 'class' | 'property') {
  event.dataTransfer?.setData('application/km-palette-type', type)
  emit('drag-start', type)
}

function onImport(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) emit('import-owl', file)
  ;(event.target as HTMLInputElement).value = ''
}
</script>

<style scoped>
.palette {
  width: 180px;
  min-width: 180px;
  background: var(--surface-container-lowest, #fff);
  border-right: 1px solid var(--outline-variant, #e5e5e7);
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
}

.palette-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--on-surface-variant, #86868b);
  margin: 4px 0 2px;
}

.palette-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px dashed var(--outline-variant, #e5e5e7);
  cursor: grab;
  font-size: 13px;
  color: var(--on-surface, #1d1d1f);
  transition: background 0.15s;
}

.palette-item:hover {
  background: var(--surface-container, #ecedf9);
}

.item-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
}

.class-icon { background: var(--primary, #0058bc); }
.prop-icon  { background: #8e44ad; }

.concept-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.concept-chip {
  padding: 5px 10px;
  border-radius: 6px;
  border: 1px solid var(--surface-container, #ecedf9);
  background: var(--surface-container, #ecedf9);
  font-size: 12px;
  text-align: left;
  cursor: pointer;
  color: var(--on-surface, #1d1d1f);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: background 0.15s;
}

.concept-chip:hover {
  background: rgba(0, 88, 188, 0.1);
  border-color: var(--primary, #0058bc);
  color: var(--primary, #0058bc);
}

.empty-hint {
  font-size: 12px;
  color: var(--on-surface-variant, #86868b);
  font-style: italic;
  margin: 0;
}

.divider {
  height: 1px;
  background: var(--outline-variant, #e5e5e7);
  margin: 4px 0;
}

.palette-btn {
  display: block;
  width: 100%;
  padding: 7px 10px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  cursor: pointer;
  color: var(--on-surface, #1d1d1f);
  transition: background 0.15s;
  box-sizing: border-box;
}

.palette-btn:hover {
  background: var(--surface-container, #ecedf9);
}

.import-btn { cursor: pointer; }
.cleanup-btn { background: #fff3cd; color: #856404; border-color: #ffc107; }
.cleanup-btn:hover:not(:disabled) { background: #ffe69c; }
.cleanup-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.cleanup-msg { font-size: 10px; color: var(--on-surface-variant, #86868b); margin: 2px 0 0; text-align: center; }
</style>
