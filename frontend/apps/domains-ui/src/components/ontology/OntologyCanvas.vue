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
    />

    <!-- Inline property-creation form shown after dropping "Property" from palette -->
    <div
      v-if="propertyForm.visible"
      class="prop-form-overlay"
      :style="{ top: `${propertyForm.y}px`, left: `${propertyForm.x}px` }"
    >
      <h4 class="pf-title">New Property</h4>
      <label class="pf-label">Label</label>
      <input class="pf-input" v-model="propertyForm.label" placeholder="e.g. hasRelation" />
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
import { computed, reactive, ref } from 'vue'
import {
  VueFlow,
  useVueFlow,
  type Node,
  type Edge,
  type NodeChange,
  type EdgeChange,
  type NodeMouseEvent,
  type EdgeMouseEvent,
} from '@vue-flow/core'
import { useOntologyStore } from '../../stores/ontology'
import type { DiagramNode, DiagramViewport } from '../../types/ontology'

const FLOW_ID = 'km-ontology-flow'

const store = useOntologyStore()
const wrapper = ref<HTMLDivElement | null>(null)
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

// ── Click handlers (Vue Flow v1: single NodeMouseEvent / EdgeMouseEvent arg) ──

function onNodeClick({ node }: NodeMouseEvent) {
  // Select by concept_id so Properties panel can look up semantic data
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

function onEdgesChange(_changes: EdgeChange[]) {
  scheduleSave()
}

function onMoveEnd() {
  scheduleSave()
}

// ── Drag & drop from palette ──────────────────────────────────────────────────

const propertyForm = reactive({
  visible: false,
  x: 0,
  y: 0,
  label: '',
  sourceId: '',
  targetId: '',
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
    // Show inline form near the drop position (in screen coords)
    propertyForm.visible = true
    propertyForm.x = event.clientX - rect.left + 10
    propertyForm.y = event.clientY - rect.top + 10
    propertyForm.label = ''
    propertyForm.sourceId = ''
    propertyForm.targetId = ''
  }
}

function cancelPropertyForm() {
  propertyForm.visible = false
}

async function confirmPropertyForm() {
  if (!propertyForm.label || !propertyForm.sourceId || !propertyForm.targetId) return
  propertyForm.visible = false

  const prop = await store.createProperty({
    label: propertyForm.label,
    uri: `http://km.local/ontology#${propertyForm.label.replace(/\s+/g, '_')}`,
    property_type: 'ObjectProperty',
    source_class_id: propertyForm.sourceId,
    target_class_id: propertyForm.targetId,
  })
  if (!prop || !activeDiagram.value) return

  // Find nodes that correspond to the source/target classes
  const srcNode = activeDiagram.value.nodes.find(n => n.concept_id === propertyForm.sourceId)
  const tgtNode = activeDiagram.value.nodes.find(n => n.concept_id === propertyForm.targetId)
  if (srcNode && tgtNode) {
    await store.addRelationToCanvas(prop.id, srcNode.id, tgtNode.id)
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

/* ── Inline property form ────────────────────────────────────────────────── */
.prop-form-overlay {
  position: absolute;
  z-index: 30;
  background: var(--surface-container-lowest, #fff);
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 10px;
  padding: 14px 16px;
  min-width: 220px;
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
