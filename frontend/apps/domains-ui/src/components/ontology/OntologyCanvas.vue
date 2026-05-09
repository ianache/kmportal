<template>
  <div class="canvas-wrapper" ref="wrapper" @drop.prevent="onDrop" @dragover.prevent>
    <VueFlow
      :id="FLOW_ID"
      :nodes="flowNodes"
      :edges="flowEdges"
      :snap-to-grid="store.snapToGrid"
      :snap-grid="[20, 20]"
      :default-viewport="activeDiagram?.viewport ?? { x: 0, y: 0, zoom: 1 }"
      fit-view-on-init
      class="flow"
      @nodes-change="onNodesChange"
      @edges-change="onEdgesChange"
      @node-click="onNodeClick"
      @edge-click="onEdgeClick"
      @pane-click="store.selectElement(null)"
      @move-end="onMoveEnd"
      @connect="onConnect"
    />

    <!-- Inline property-creation form: shown after dropping "Property" OR connecting two nodes -->
    <div
      v-if="propertyForm.visible"
      class="prop-form-overlay"
      :style="{ top: `${propertyForm.y}px`, left: `${propertyForm.x}px` }"
    >
      <h4 class="pf-title">New Property</h4>
      <label class="pf-label">Label</label>
      <input ref="labelInputRef" class="pf-input" v-model="propertyForm.label" placeholder="e.g. hasRelation" @keydown.enter="confirmPropertyForm" @keydown.esc="cancelPropertyForm" />

      <template v-if="propertyForm.fromConnection">
        <label class="pf-label">Source</label>
        <p class="pf-value">{{ store.conceptMap[propertyForm.sourceId]?.label }}</p>
        <label class="pf-label">Target</label>
        <p class="pf-value">{{ store.conceptMap[propertyForm.targetId]?.label }}</p>
      </template>
      <template v-else>
        <label class="pf-label">Source class</label>
        <select class="pf-input" v-model="propertyForm.sourceId">
          <option value="">— select —</option>
          <option v-for="c in store.concepts" :key="c.id" :value="c.id">{{ c.label }}</option>
        </select>
        <label class="pf-label">Target class</label>
        <select class="pf-input" v-model="propertyForm.targetId">
          <option value="">— select —</option>
          <option v-for="c in store.concepts" :key="c.id" :value="c.id">{{ c.label }}</option>
        </select>
      </template>

      <div class="pf-actions">
        <button class="pf-cancel" @click="cancelPropertyForm">Cancel</button>
        <button
          class="pf-ok"
          :disabled="!propertyForm.label || !propertyForm.sourceId || !propertyForm.targetId"
          @click="confirmPropertyForm"
        >Create</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import {
  VueFlow,
  useVueFlow,
  type Connection,
  type Edge,
  type EdgeChange,
  type EdgeMouseEvent,
  type Node,
  type NodeChange,
  type NodeMouseEvent,
} from '@vue-flow/core'
import { useOntologyStore } from '../../stores/ontology'
import type { DiagramNode, DiagramViewport } from '../../types/ontology'

const FLOW_ID = 'km-ontology-flow'

const store = useOntologyStore()
const wrapper = ref<HTMLDivElement | null>(null)
const labelInputRef = ref<HTMLInputElement | null>(null)
const { fitView, zoomIn, zoomOut, getViewport } = useVueFlow({ id: FLOW_ID })

defineExpose({ fitView, zoomIn, zoomOut })

const activeDiagram = computed(() => store.activeDiagram)

// ── Map store nodes → Vue Flow nodes ─────────────────────────────────────────
const flowNodes = computed<Node[]>(() => {
  if (!activeDiagram.value) return []
  return activeDiagram.value.nodes.map(n => {
    const concept = store.conceptMap[n.concept_id]
    const isSelected = n.concept_id === store.selectedElementId
    return {
      id: n.id,
      type: 'default',
      position: n.position,
      data: {
        label: concept?.label ?? n.concept_id,
        conceptId: n.concept_id,
      },
      style: {
        background: '#fff',
        border: isSelected ? '2px solid #0058bc' : '1px solid #c6c6c8',
        borderRadius: '8px',
        padding: '10px 16px',
        fontSize: '13px',
        fontWeight: '600',
        color: '#1d1d1f',
        minWidth: '120px',
        boxShadow: isSelected ? '0 0 0 3px rgba(0,88,188,0.15)' : 'none',
      },
    }
  })
})

// ── Map store edges → Vue Flow edges ─────────────────────────────────────────
const flowEdges = computed<Edge[]>(() => {
  if (!activeDiagram.value) return []
  return activeDiagram.value.edges.map(e => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.label || '',
    type: 'default',
    markerEnd: { type: 'arrowclosed' },
    style: { stroke: e.id === store.selectedElementId ? '#8e44ad' : '#0058bc', strokeWidth: 2 },
    labelStyle: { fill: '#414755', fontSize: '11px' },
  }))
})

// ── Click handlers ────────────────────────────────────────────────────────────

function onNodeClick({ node }: NodeMouseEvent) {
  const storeNode = activeDiagram.value?.nodes.find(n => n.id === node.id)
  store.selectElement(storeNode?.concept_id ?? null)
}

function onEdgeClick({ edge }: EdgeMouseEvent) {
  store.selectElement(edge.id)
}

// ── Save position changes back to store ──────────────────────────────────────
let saveTimer: ReturnType<typeof setTimeout> | null = null

function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    if (!activeDiagram.value) return
    store.saveLayout(
      activeDiagram.value.nodes,
      activeDiagram.value.edges,
      getViewport() as DiagramViewport,
    )
  }, 600)
}

function onNodesChange(changes: NodeChange[]) {
  if (!activeDiagram.value) return

  // Visual-only delete: remove selected nodes from diagram without touching the ontology
  const removeIds = changes
    .filter(c => c.type === 'remove')
    .map(c => (c as { type: 'remove'; id: string }).id)
  if (removeIds.length) {
    store.removeNodesFromCanvas(removeIds)
    return
  }

  const posChanges = changes.filter(c => c.type === 'position' && 'position' in c && c.position)
  if (!posChanges.length) return
  const updated = activeDiagram.value.nodes.map(n => {
    const change = posChanges.find(c => 'id' in c && c.id === n.id)
    if (change && 'position' in change && change.position) {
      return { ...n, position: change.position }
    }
    return n
  })
  const idx = store.diagrams.findIndex(d => d.id === activeDiagram.value!.id)
  if (idx >= 0) store.diagrams[idx].nodes = updated
  scheduleSave()
}

function onEdgesChange(changes: EdgeChange[]) {
  // Visual-only delete: remove selected edges from diagram without touching the ontology
  const removeIds = changes
    .filter(c => c.type === 'remove')
    .map(c => (c as { type: 'remove'; id: string }).id)
  if (removeIds.length) {
    store.removeEdgesFromCanvas(removeIds)
    return
  }
  scheduleSave()
}

function onMoveEnd() {
  scheduleSave()
}

// ── Shift+Delete: remove selected node from diagram only (visual-only) ────────
function onShiftDelete(e: KeyboardEvent) {
  if (!e.shiftKey || (e.key !== 'Delete' && e.key !== 'Backspace')) return
  const tag = (e.target as HTMLElement).tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
  const selId = store.selectedElementId
  if (!selId || !store.activeDiagram) return
  // Only act when the selected element is a concept (node), not an edge
  if (!store.conceptMap[selId]) return
  e.preventDefault()
  const nodeIds = store.activeDiagram.nodes
    .filter(n => n.concept_id === selId)
    .map(n => n.id)
  if (nodeIds.length) store.removeNodesFromCanvas(nodeIds)
}

onMounted(() => document.addEventListener('keydown', onShiftDelete))
onBeforeUnmount(() => document.removeEventListener('keydown', onShiftDelete))

// ── Node connection by dragging handles ──────────────────────────────────────

function onConnect(connection: Connection) {
  if (!activeDiagram.value || !wrapper.value) return
  const srcNode = activeDiagram.value.nodes.find(n => n.id === connection.source)
  const tgtNode = activeDiagram.value.nodes.find(n => n.id === connection.target)
  if (!srcNode || !tgtNode) return

  // Center the form in the canvas wrapper
  const rect = wrapper.value.getBoundingClientRect()
  propertyForm.visible = true
  propertyForm.x = rect.width / 2 - 115
  propertyForm.y = rect.height / 2 - 110
  propertyForm.label = ''
  propertyForm.sourceId = srcNode.concept_id
  propertyForm.targetId = tgtNode.concept_id
  propertyForm.sourceNodeId = connection.source
  propertyForm.targetNodeId = connection.target
  propertyForm.fromConnection = true

  nextTick(() => labelInputRef.value?.focus())
}

// ── Drag & drop from palette ──────────────────────────────────────────────────

const propertyForm = reactive({
  visible: false,
  x: 0,
  y: 0,
  label: '',
  sourceId: '',
  targetId: '',
  sourceNodeId: '',
  targetNodeId: '',
  fromConnection: false,
})

async function onDrop(event: DragEvent) {
  const type = event.dataTransfer?.getData('application/km-palette-type')
  if (!type || !wrapper.value) return

  const rect = wrapper.value.getBoundingClientRect()
  const vp = getViewport()
  const canvasPos = {
    x: (event.clientX - rect.left - vp.x) / vp.zoom,
    y: (event.clientY - rect.top - vp.y) / vp.zoom,
  }

  if (type === 'class') {
    const label = window.prompt('Class label:')
    if (!label) return
    const uri =
      window.prompt('URI (leave blank for auto):') ||
      `http://km.local/ontology#${label.replace(/\s+/g, '_')}`
    const concept = await store.createConcept({ label, uri })
    if (concept) await store.addClassToCanvas(concept, canvasPos)
    return
  }

  if (type === 'property') {
    if (!store.concepts.length) {
      alert('Add at least two classes first before creating a property.')
      return
    }
    propertyForm.visible = true
    propertyForm.x = event.clientX - rect.left + 10
    propertyForm.y = event.clientY - rect.top + 10
    propertyForm.label = ''
    propertyForm.sourceId = ''
    propertyForm.targetId = ''
    propertyForm.sourceNodeId = ''
    propertyForm.targetNodeId = ''
    propertyForm.fromConnection = false

    nextTick(() => labelInputRef.value?.focus())
  }
}

function cancelPropertyForm() {
  propertyForm.visible = false
  propertyForm.fromConnection = false
}

async function confirmPropertyForm() {
  if (!propertyForm.label || !propertyForm.sourceId || !propertyForm.targetId) return
  propertyForm.visible = false

  const fromConnection = propertyForm.fromConnection
  const srcNodeId = propertyForm.sourceNodeId
  const tgtNodeId = propertyForm.targetNodeId
  propertyForm.fromConnection = false

  const prop = await store.createProperty({
    label: propertyForm.label,
    uri: `http://km.local/ontology#${propertyForm.label.replace(/\s+/g, '_')}`,
    property_type: 'ObjectProperty',
    source_class_id: propertyForm.sourceId,
    target_class_id: propertyForm.targetId,
  })
  if (!prop || !activeDiagram.value) return

  if (fromConnection) {
    // Node IDs are known precisely from the drag connection
    await store.addRelationToCanvas(prop.id, srcNodeId, tgtNodeId)
  } else {
    // From palette drop — find a representative node for each class
    const srcNode = activeDiagram.value.nodes.find(n => n.concept_id === propertyForm.sourceId)
    const tgtNode = activeDiagram.value.nodes.find(n => n.concept_id === propertyForm.targetId)
    if (srcNode && tgtNode) {
      await store.addRelationToCanvas(prop.id, srcNode.id, tgtNode.id)
    }
  }
}
</script>

<style scoped>
.canvas-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-color: var(--background, #f9f9ff);
  background-image: radial-gradient(circle, #c6c6c8 1px, transparent 1px);
  background-size: 20px 20px;
}

.flow {
  width: 100%;
  height: 100%;
  background: transparent;
}

/* Make connection handles clearly visible on node hover */
:deep(.vue-flow__handle) {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #0058bc;
  border: 2px solid #fff;
  opacity: 0;
  transition: opacity 0.15s, transform 0.15s;
}

:deep(.vue-flow__node:hover .vue-flow__handle),
:deep(.vue-flow__handle.connecting),
:deep(.vue-flow__handle.valid) {
  opacity: 1;
  transform: scale(1.2);
}

/* ── Inline property form ────────────────────────────────────────────────── */
.prop-form-overlay {
  position: absolute;
  z-index: 30;
  background: var(--surface-container-lowest, #fff);
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 10px;
  padding: 14px 16px;
  min-width: 230px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pf-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--on-surface, #1d1d1f);
  margin: 0 0 4px;
}

.pf-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--on-surface-variant, #86868b);
}

.pf-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--on-surface, #1d1d1f);
  margin: 0;
  padding: 4px 0;
}

.pf-input {
  padding: 6px 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 6px;
  font-size: 12px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}

.pf-input:focus {
  border-color: #8e44ad;
}

.pf-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.pf-cancel,
.pf-ok {
  flex: 1;
  padding: 6px 0;
  border-radius: 6px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.pf-cancel {
  background: var(--surface-container, #ecedf9);
  color: var(--on-surface, #1d1d1f);
}

.pf-ok {
  background: #8e44ad;
  color: #fff;
}

.pf-ok:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
