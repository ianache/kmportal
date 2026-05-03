<template>
  <div class="ingestion-ui">

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <span class="flow-name">{{ flowName }}</span>
        <span class="flow-meta">Modified 5 min ago · Draft</span>
      </div>
      <div class="toolbar-right">
        <button class="btn-ghost-sm">
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M3 10h14M10 3v14"/>
          </svg>
          Add Pipeline
        </button>
        <button class="btn-ghost-sm">
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M3 5h14M3 10h14M3 15h14"/>
          </svg>
          Save
        </button>
        <button class="btn-primary-sm" @click="running = !running">
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
            <polygon v-if="!running" points="5,3 19,10 5,17"/>
            <g v-else>
              <rect x="4" y="4" width="5" height="12" rx="1"/>
              <rect x="11" y="4" width="5" height="12" rx="1"/>
            </g>
          </svg>
          {{ running ? 'Stop' : 'Run Flow' }}
        </button>
        <button class="btn-primary-sm btn-publish">Publish</button>
      </div>
    </div>

    <!-- Main area -->
    <div class="editor-layout">

      <!-- Node Palette -->
      <aside class="palette">
        <div class="palette-header">
          <span>Components</span>
        </div>

        <div v-for="cat in nodeCategories" :key="cat.label" class="palette-category">
          <span class="cat-label">{{ cat.label }}</span>
          <div
            v-for="node in cat.nodes"
            :key="node.id"
            class="palette-node"
            :style="{ '--node-color': node.color }"
          >
            <div class="node-icon-sm" :style="{ background: node.color + '18', color: node.color }">
              <component :is="'svg'" width="14" height="14" viewBox="0 0 20 20" fill="none"
                stroke="currentColor" stroke-width="1.7" v-html="node.iconPath"/>
            </div>
            <span class="node-name">{{ node.name }}</span>
          </div>
        </div>
      </aside>

      <!-- Canvas -->
      <div class="canvas">
        <div class="canvas-bg"/>

        <!-- Flow nodes -->
        <div class="flow">
          <div
            v-for="(node, i) in flowNodes"
            :key="node.id"
            class="flow-node"
            :class="{ 'flow-node--selected': selectedNode === node.id }"
            :style="{ top: node.y + 'px', left: node.x + 'px', '--nc': node.color }"
            @click="selectedNode = node.id"
          >
            <div class="fn-header" :style="{ background: node.color + '20', borderBottom: '1px solid ' + node.color + '30' }">
              <span class="fn-type" :style="{ color: node.color }">{{ node.category }}</span>
              <button class="fn-menu">⋯</button>
            </div>
            <div class="fn-body">
              <div class="fn-icon" :style="{ color: node.color }">
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6"
                  v-html="node.iconPath"/>
              </div>
              <div class="fn-info">
                <span class="fn-name">{{ node.name }}</span>
                <span class="fn-sub">{{ node.subtitle }}</span>
              </div>
            </div>
            <div class="fn-status" :class="'fn-status--' + node.status">{{ node.status }}</div>
          </div>

          <!-- Edges (SVG) -->
          <svg class="edges-svg" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none">
            <defs>
              <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                <path d="M0,0 L0,6 L8,3 z" fill="#C1C6D7"/>
              </marker>
            </defs>
            <path v-for="e in edges" :key="e.id" :d="e.d"
              fill="none" stroke="#C1C6D7" stroke-width="1.5"
              stroke-dasharray="5 3" marker-end="url(#arrow)"/>
          </svg>
        </div>

        <!-- Canvas toolbar -->
        <div class="canvas-toolbar">
          <button class="ct-btn" title="Zoom in">+</button>
          <button class="ct-btn" title="Zoom out">−</button>
          <button class="ct-btn" title="Fit">⤢</button>
          <button class="ct-btn" title="Grid">⊞</button>
        </div>
      </div>

      <!-- Inspector -->
      <aside v-if="selectedNodeData" class="inspector">
        <div class="inspector-header">
          <span class="inspector-title">{{ selectedNodeData.name }}</span>
          <button class="close-btn" @click="selectedNode = null">✕</button>
        </div>
        <div class="inspector-body">
          <div class="insp-field">
            <span class="insp-label">Type</span>
            <span class="insp-value">{{ selectedNodeData.category }}</span>
          </div>
          <div class="insp-field">
            <span class="insp-label">Config</span>
            <span class="insp-value">{{ selectedNodeData.subtitle }}</span>
          </div>
          <div class="insp-field">
            <span class="insp-label">Status</span>
            <span class="badge-sm" :class="'badge-sm--' + selectedNodeData.status">
              {{ selectedNodeData.status }}
            </span>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const running = ref(false)
const selectedNode = ref<string | null>(null)
const flowName = ref('User Data Ingestion Flow')

const nodeCategories = [
  {
    label: 'Sources',
    nodes: [
      { id: 's1', name: 'Folder', color: '#007AFF', iconPath: '<path d="M2 6h16v10H2z"/><path d="M2 6l3-3h6l3 3"/>' },
      { id: 's2', name: 'S3 Bucket', color: '#FF9500', iconPath: '<path d="M10 2a8 8 0 100 16A8 8 0 0010 2z"/><path d="M2 10h16"/>' },
      { id: 's3', name: 'Kafka', color: '#34C759', iconPath: '<path d="M10 3v14M3 10h14"/><circle cx="10" cy="10" r="2"/>' },
      { id: 's4', name: 'RabbitMQ', color: '#AF52DE', iconPath: '<rect x="3" y="3" width="14" height="14" rx="2"/><path d="M7 10h6"/>' },
    ],
  },
  {
    label: 'Transformation',
    nodes: [
      { id: 't1', name: 'Script JS', color: '#FF9500', iconPath: '<path d="M4 4h12v12H4z"/><path d="M8 12l2-4 2 4"/>' },
      { id: 't2', name: 'Embeddings', color: '#AF52DE', iconPath: '<circle cx="10" cy="10" r="4"/><path d="M10 2v3M10 15v3M2 10h3M15 10h3"/>' },
      { id: 't3', name: 'Data Filter', color: '#007AFF', iconPath: '<path d="M3 5h14M6 10h8M9 15h2"/>' },
    ],
  },
  {
    label: 'Target',
    nodes: [
      { id: 'd1', name: 'QDrant', color: '#FF3B30', iconPath: '<circle cx="10" cy="10" r="7"/><path d="M7 10h6M10 7v6"/>' },
      { id: 'd2', name: 'Neo4j', color: '#34C759', iconPath: '<circle cx="10" cy="5" r="2"/><circle cx="5" cy="15" r="2"/><circle cx="15" cy="15" r="2"/><path d="M10 7l-5 6M10 7l5 6"/>' },
      { id: 'd3', name: 'Chroma', color: '#5AC8FA', iconPath: '<path d="M4 16l6-12 6 12z"/>' },
    ],
  },
]

const flowNodes = ref([
  { id: 'n1', name: 'S3 Bucket', subtitle: 'raw-data-uploads', category: 'SOURCE', status: 'active', x: 60, y: 120, color: '#FF9500', iconPath: '<path d="M10 2a8 8 0 100 16A8 8 0 0010 2z"/><path d="M2 10h16"/>' },
  { id: 'n2', name: 'Embeddings', subtitle: 'text-embedding-ada-002', category: 'PROCESS', status: 'active', x: 280, y: 120, color: '#AF52DE', iconPath: '<circle cx="10" cy="10" r="4"/><path d="M10 2v3M10 15v3M2 10h3M15 10h3"/>' },
  { id: 'n3', name: 'Chroma DB', subtitle: 'vector-store-primary', category: 'SINK', status: 'persisted', x: 500, y: 60, color: '#5AC8FA', iconPath: '<path d="M4 16l6-12 6 12z"/>' },
  { id: 'n4', name: 'Neo4j', subtitle: 'knowledge-graph-v2', category: 'SINK', status: 'persisted', x: 500, y: 200, color: '#34C759', iconPath: '<circle cx="10" cy="5" r="2"/><circle cx="5" cy="15" r="2"/><circle cx="15" cy="15" r="2"/><path d="M10 7l-5 6M10 7l5 6"/>' },
])

const edges = computed(() => {
  const nodes = flowNodes.value
  const n1 = nodes.find(n => n.id === 'n1')!
  const n2 = nodes.find(n => n.id === 'n2')!
  const n3 = nodes.find(n => n.id === 'n3')!
  const n4 = nodes.find(n => n.id === 'n4')!
  const W = 180, H = 70
  return [
    { id: 'e1', d: `M${n1.x+W},${n1.y+H/2} C${n1.x+W+40},${n1.y+H/2} ${n2.x-40},${n2.y+H/2} ${n2.x},${n2.y+H/2}` },
    { id: 'e2', d: `M${n2.x+W},${n2.y+H/2} C${n2.x+W+40},${n2.y+H/2} ${n3.x-40},${n3.y+H/2} ${n3.x},${n3.y+H/2}` },
    { id: 'e3', d: `M${n2.x+W},${n2.y+H/2} C${n2.x+W+40},${n2.y+H/2} ${n4.x-40},${n4.y+H/2} ${n4.x},${n4.y+H/2}` },
  ]
})

const selectedNodeData = computed(() =>
  selectedNode.value ? flowNodes.value.find(n => n.id === selectedNode.value) : null
)
</script>

<style scoped>
.ingestion-ui {
  display: flex;
  flex-direction: column;
  height: calc(100vh - var(--topbar-h, 56px));
  overflow: hidden;
}

/* ── Toolbar ─────────────────────────────── */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: var(--surface, #fff);
  border-bottom: 1px solid var(--border, #E5E5E7);
  flex-shrink: 0;
  gap: 12px;
}

.toolbar-left { display: flex; align-items: baseline; gap: 10px; }

.flow-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  letter-spacing: -0.01em;
}

.flow-meta { font-size: 12px; color: var(--text-2, #86868B); }

.toolbar-right { display: flex; align-items: center; gap: 8px; }

.btn-ghost-sm {
  display: inline-flex;
  align-items: center;
  gap: 5px;
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
.btn-ghost-sm:hover { background: rgba(0,0,0,0.04); color: var(--text, #1D1D1F); }

.btn-primary-sm {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 7px;
  border: none;
  background: var(--primary, #007AFF);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.12s;
}
.btn-primary-sm:hover { opacity: 0.88; }

.btn-publish {
  background: rgba(0,122,255,0.1);
  color: var(--primary, #007AFF);
}
.btn-publish:hover { background: rgba(0,122,255,0.18); opacity: 1; }

/* ── Editor layout ───────────────────────── */
.editor-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* ── Palette ─────────────────────────────── */
.palette {
  width: 200px;
  border-right: 1px solid var(--border, #E5E5E7);
  background: var(--surface, #fff);
  overflow-y: auto;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.palette-header {
  padding: 12px 16px 8px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-2, #86868B);
  border-bottom: 1px solid var(--border, #E5E5E7);
}

.palette-category { padding: 12px 12px 4px; }

.cat-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-2, #86868B);
  padding: 0 4px;
  display: block;
  margin-bottom: 6px;
}

.palette-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 6px;
  border-radius: 7px;
  cursor: grab;
  transition: background 0.12s;
  margin-bottom: 2px;
}
.palette-node:hover { background: rgba(0,0,0,0.04); }

.node-icon-sm {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.node-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text, #1D1D1F);
}

/* ── Canvas ──────────────────────────────── */
.canvas {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--bg, #F5F5F7);
}

.canvas-bg {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle, #C1C6D7 1px, transparent 1px);
  background-size: 24px 24px;
  opacity: 0.4;
}

.flow {
  position: absolute;
  inset: 0;
}

/* ── Flow node ───────────────────────────── */
.flow-node {
  position: absolute;
  width: 180px;
  background: var(--surface, #fff);
  border: 1.5px solid var(--border, #E5E5E7);
  border-radius: var(--radius, 12px);
  box-shadow: var(--shadow-card, 0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.06));
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
  overflow: hidden;
}
.flow-node:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.10); }
.flow-node--selected { border-color: var(--nc, #007AFF) !important; box-shadow: 0 0 0 3px color-mix(in srgb, var(--nc, #007AFF) 20%, transparent); }

.fn-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
}

.fn-type {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.fn-menu {
  font-size: 14px;
  color: var(--text-2, #86868B);
  cursor: pointer;
  background: none;
  border: none;
  line-height: 1;
}

.fn-body {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
}

.fn-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fn-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }

.fn-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fn-sub {
  font-size: 11px;
  color: var(--text-2, #86868B);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fn-status {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 4px 10px;
  text-align: center;
}
.fn-status--active { background: rgba(52,199,89,0.1); color: #1a7f37; }
.fn-status--persisted { background: rgba(0,122,255,0.1); color: #007AFF; }
.fn-status--error { background: rgba(255,59,48,0.1); color: #FF3B30; }

/* ── Canvas toolbar ──────────────────────── */
.canvas-toolbar {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #E5E5E7);
  border-radius: 10px;
  padding: 4px;
  box-shadow: var(--shadow-float, 0 8px 32px rgba(0,0,0,0.10));
}

.ct-btn {
  width: 32px;
  height: 32px;
  border-radius: 7px;
  background: none;
  border: none;
  font-size: 16px;
  color: var(--text-2, #86868B);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.12s;
}
.ct-btn:hover { background: rgba(0,0,0,0.06); color: var(--text, #1D1D1F); }

/* ── Inspector ───────────────────────────── */
.inspector {
  width: 240px;
  border-left: 1px solid var(--border, #E5E5E7);
  background: var(--surface, #fff);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.inspector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border, #E5E5E7);
}

.inspector-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text, #1D1D1F);
}

.close-btn {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0,0,0,0.06);
  border: none;
  font-size: 11px;
  color: var(--text-2, #86868B);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.inspector-body { padding: 16px; display: flex; flex-direction: column; gap: 14px; }

.insp-field { display: flex; flex-direction: column; gap: 4px; }

.insp-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-2, #86868B);
}

.insp-value {
  font-size: 13px;
  color: var(--text, #1D1D1F);
  font-weight: 500;
}

.badge-sm {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  display: inline-block;
}
.badge-sm--active { background: rgba(52,199,89,0.12); color: #1a7f37; }
.badge-sm--persisted { background: rgba(0,122,255,0.12); color: #007AFF; }
</style>
