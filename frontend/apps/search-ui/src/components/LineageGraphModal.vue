<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click="$emit('close')">
      <div class="modal-container" @click.stop>

        <!-- Modal header -->
        <div class="modal-header">
          <div class="modal-title-group">
            <!-- Network icon -->
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="5" r="3"/><circle cx="19" cy="19" r="3"/><circle cx="5" cy="19" r="3"/>
              <line x1="12" y1="8" x2="12" y2="14"/><line x1="12" y1="17" x2="19" y2="17"/>
              <line x1="12" y1="17" x2="5" y2="17"/>
            </svg>
            <h2 class="modal-title">Semantic Lineage</h2>
          </div>

          <div class="modal-meta" v-if="resultData">
            <span class="meta-badge meta-badge--owl">{{ resultData.provenance.owl_class }}</span>
            <span class="meta-badge" :class="isoBadgeClass">{{ resultData.provenance.iso_compliance }}</span>
          </div>

          <button class="close-btn" @click="$emit('close')" aria-label="Close">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Graph area or empty state -->
        <div class="modal-body">
          <div v-if="isEmpty" class="empty-state">
            <!-- ShieldCheck icon -->
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
                 style="color: var(--on-surface-variant, #86868b)">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              <polyline points="9 12 11 14 15 10"/>
            </svg>
            <p class="empty-text">
              No se encontraron relaciones estructurales en la Ontología para este resultado.
            </p>
          </div>

          <div v-else ref="cyContainer" class="cy-container"></div>
        </div>

        <!-- Source file footer -->
        <div class="modal-footer" v-if="resultData">
          <span class="source-label">Source:</span>
          <span class="source-value">{{ resultData.source_file || 'Unknown' }}</span>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'
import type { HybridSearchResult } from '../types/semantic'

const props = defineProps<{
  isOpen: boolean
  resultData: HybridSearchResult | null
}>()

defineEmits<{ (e: 'close'): void }>()

const cyContainer = ref<HTMLElement | null>(null)
let cyInstance: any = null

// ── Helpers ──────────────────────────────────────────────────────────────────

const isEmpty = computed(() =>
  !props.resultData || props.resultData.provenance.nodes.length === 0
)

const isoBadgeClass = computed(() => {
  const c = props.resultData?.provenance.iso_compliance?.toUpperCase() ?? ''
  if (c === 'PÚBLICO' || c === 'PUBLICO' || c === 'PUBLIC') return 'meta-badge--public'
  if (c === 'CONFIDENCIAL' || c === 'CONFIDENTIAL') return 'meta-badge--confidential'
  return ''
})

// ── Cytoscape lifecycle ───────────────────────────────────────────────────────

function destroyCy() {
  if (cyInstance) {
    cyInstance.destroy()
    cyInstance = null
  }
}

async function initCy() {
  if (isEmpty.value || !cyContainer.value) return
  destroyCy()

  const cytoscape = (await import('cytoscape')).default
  const data = props.resultData!

  // Build elements: root node + provenance nodes + edges to root + inter-node edges
  const elements: any[] = [
    { data: { id: 'root', label: 'Resultado', classType: 'Root' } },
    ...data.provenance.nodes.map(n => ({
      data: { id: n.id, label: n.name || n.label, classType: n.label },
    })),
    // Connect every provenance node to root when no explicit edge covers it
    ...data.provenance.nodes.map(n => ({
      data: { source: 'root', target: n.id, label: data.provenance.owl_class },
    })),
    // Explicit edges from provenance
    ...data.provenance.edges.map((e, i) => ({
      data: {
        id: `edge-${i}`,
        source: e.source || 'root',
        target: e.target,
        label: e.relation_type,
      },
    })),
  ]

  cyInstance = cytoscape({
    container: cyContainer.value,
    elements,
    style: [
      // Default node
      {
        selector: 'node',
        style: {
          'background-color': '#d1d5db',
          'label': 'data(label)',
          'color': '#1d1d1f',
          'font-size': '11px',
          'text-valign': 'center',
          'text-halign': 'center',
          'width': 60,
          'height': 60,
          'text-wrap': 'wrap',
          'text-max-width': '55px',
        },
      },
      // Root node — hexagon, amber
      {
        selector: 'node[classType="Root"]',
        style: {
          'shape': 'hexagon',
          'background-color': '#f59e0b',
          'color': '#1d1d1f',
          'font-weight': 700,
          'width': 72,
          'height': 72,
        },
      },
      // Control / ISO nodes — rounded-rectangle, blue
      {
        selector: 'node[classType *= "Control"], node[classType *= "ISO"]',
        style: {
          'shape': 'round-rectangle',
          'background-color': '#3b82f6',
          'color': '#ffffff',
          'width': 80,
          'height': 44,
        },
      },
      // Edges
      {
        selector: 'edge',
        style: {
          'width': 1.5,
          'line-color': '#cbd5e1',
          'target-arrow-color': '#94a3b8',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'label': 'data(label)',
          'font-size': '9px',
          'color': '#6b7280',
          'text-background-color': '#ffffff',
          'text-background-opacity': 0.85,
          'text-background-padding': '2px',
        },
      },
    ],
    layout: {
      name: 'breadthfirst',
      directed: true,
      padding: 20,
      spacingFactor: 1.4,
    },
  })
}

// Re-render when modal opens or data changes
watch(
  () => [props.isOpen, props.resultData] as const,
  async ([open]) => {
    if (open && !isEmpty.value) {
      await nextTick()
      await initCy()
    } else {
      destroyCy()
    }
  }
)

onUnmounted(destroyCy)
</script>

<style scoped>
/* Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fade-in 0.18s ease-out;
}

/* Container */
.modal-container {
  background: var(--surface-container-lowest, #ffffff);
  border-radius: 16px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18);
  width: min(720px, 94vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slide-up 0.2s ease-out;
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--outline-variant, #e5e5e7);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary, #0058bc);
}

.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--on-surface, #1d1d1f);
  margin: 0;
}

.modal-meta {
  display: flex;
  gap: 6px;
  flex: 1;
  flex-wrap: wrap;
}

.meta-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--surface-container, #ecedf9);
  color: var(--on-surface-variant, #414755);
}

.meta-badge--owl {
  background: rgba(0, 88, 188, 0.1);
  color: var(--primary, #0058bc);
}

.meta-badge--public {
  background: rgba(22, 163, 74, 0.1);
  color: #16a34a;
}

.meta-badge--confidential {
  background: rgba(234, 88, 12, 0.1);
  color: #ea580c;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--on-surface-variant, #86868b);
  cursor: pointer;
  margin-left: auto;
  transition: background 0.15s;
  flex-shrink: 0;
}

.close-btn:hover {
  background: var(--surface-container, #ecedf9);
}

/* Body */
.modal-body {
  flex: 1;
  min-height: 360px;
  overflow: hidden;
}

.cy-container {
  width: 100%;
  height: 380px;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 360px;
  gap: 16px;
  padding: 40px;
  text-align: center;
}

.empty-text {
  font-size: 14px;
  color: var(--on-surface-variant, #86868b);
  line-height: 1.6;
  max-width: 360px;
  margin: 0;
}

/* Footer */
.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--surface-container, #ecedf9);
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.source-label {
  font-weight: 600;
  color: var(--on-surface, #1d1d1f);
}

.source-value {
  color: var(--on-surface-variant, #86868b);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Animations */
@keyframes fade-in {
  from { opacity: 0 }
  to   { opacity: 1 }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(16px) scale(0.97) }
  to   { opacity: 1; transform: translateY(0)    scale(1)    }
}
</style>
