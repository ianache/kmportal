<template>
  <div class="canvas-wrapper" ref="wrapper" @drop="onDrop" @dragover.prevent>
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
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  VueFlow,
  useVueFlow,
  type Node,
  type Edge,
  type NodeChange,
  type EdgeChange,
} from '@vue-flow/core'
// CSS imported via index.html or main.ts to avoid federation resolution issues
import { useOntologyStore } from '../../stores/ontology'
import type { DiagramEdge, DiagramNode, DiagramViewport, OntologyConcept } from '../../types/ontology'

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
    return {
      id: n.id,
      type: 'default',
      position: n.position,
      data: {
        label: concept?.label ?? n.concept_id,
        uri: concept?.uri,
        conceptId: n.concept_id,
      },
      selected: n.id === store.selectedElementId,
      style: {
        background: '#fff',
        border: n.id === store.selectedElementId ? '2px solid #0058bc' : '1px solid #c6c6c8',
        borderRadius: '8px',
        padding: '10px 16px',
        fontSize: '13px',
        fontWeight: '600',
        color: '#1d1d1f',
        minWidth: '120px',
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
    selected: e.id === store.selectedElementId,
    style: { stroke: '#0058bc', strokeWidth: 2 },
    labelStyle: { fill: '#414755', fontSize: '11px' },
  }))
})

// ── Sync node position changes back to store ──────────────────────────────────
let saveTimer: ReturnType<typeof setTimeout> | null = null

function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    if (!activeDiagram.value) return
    const nodes = activeDiagram.value.nodes
    const edges = activeDiagram.value.edges
    const vp = getViewport() as DiagramViewport
    store.saveLayout(nodes, edges, vp)
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
  // Patch directly into store for immediate reactivity
  const idx = store.diagrams.findIndex(d => d.id === activeDiagram.value!.id)
  if (idx >= 0) store.diagrams[idx].nodes = updated
  scheduleSave()
}

function onEdgesChange(changes: EdgeChange[]) {
  scheduleSave()
}

function onMoveEnd() {
  scheduleSave()
}

function onNodeClick(_: any, node: Node) {
  store.selectElement(node.id)
  // Also select the underlying concept
  const storeNode = activeDiagram.value?.nodes.find(n => n.id === node.id)
  if (storeNode) store.selectElement(storeNode.concept_id)
}

function onEdgeClick(_: any, edge: Edge) {
  store.selectElement(edge.id)
}

// ── Drag & drop from palette ──────────────────────────────────────────────────
async function onDrop(event: DragEvent) {
  const type = event.dataTransfer?.getData('application/km-palette-type')
  if (!type || !wrapper.value) return

  const rect = wrapper.value.getBoundingClientRect()
  const vp = getViewport()
  const position = {
    x: (event.clientX - rect.left - vp.x) / vp.zoom,
    y: (event.clientY - rect.top - vp.y) / vp.zoom,
  }

  if (type === 'class') {
    const label = window.prompt('Class label:')
    if (!label) return
    const uri = window.prompt('URI (optional, press Enter to skip):') || `http://km.local/ontology#${label.replace(/\s+/g, '_')}`
    const concept = await store.createConcept({ label, uri })
    if (concept) await store.addClassToCanvas(concept, position)
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
</style>
