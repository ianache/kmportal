<template>
  <div class="diagram-tabs">
    <div class="tabs-bar">
      <button
        v-for="d in store.diagrams"
        :key="d.id"
        class="tab"
        :class="{ active: d.id === store.activeDiagramId }"
        @click="store.selectDiagram(d.id)"
      >
        <span class="tab-name">{{ d.name }}</span>
        <span
          class="tab-close"
          title="Delete diagram"
          @click.stop="requestDelete(d)"
        >✕</span>
      </button>

      <button class="tab tab-add" @click="showNewTab = true" title="New diagram">+</button>
    </div>

    <!-- Inline new-diagram input -->
    <div v-if="showNewTab" class="new-tab-form">
      <input
        ref="newNameInput"
        v-model="newName"
        class="new-name-input"
        placeholder="Diagram name"
        maxlength="80"
        @keydown.enter="addDiagram"
        @keydown.esc="showNewTab = false"
      />
      <button class="btn-ok" @click="addDiagram">OK</button>
      <button class="btn-cancel" @click="showNewTab = false">Cancel</button>
    </div>

    <DeleteDiagramModal
      v-if="pendingDelete"
      :diagram-name="pendingDelete.name"
      @confirm="confirmDelete"
      @cancel="pendingDelete = null"
    />
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { useOntologyStore } from '../../stores/ontology'
import type { Diagram } from '../../types/ontology'
import DeleteDiagramModal from './DeleteDiagramModal.vue'

const store = useOntologyStore()

const showNewTab = ref(false)
const newName = ref('')
const newNameInput = ref<HTMLInputElement | null>(null)
const pendingDelete = ref<Diagram | null>(null)

async function addDiagram() {
  const name = newName.value.trim()
  if (!name) return
  await store.createDiagram(name)
  newName.value = ''
  showNewTab.value = false
}

function requestDelete(d: Diagram) {
  if (store.diagrams.length <= 1) return // spec: at least one diagram must exist
  pendingDelete.value = d
}

async function confirmDelete() {
  if (!pendingDelete.value) return
  await store.deleteDiagram(pendingDelete.value.id)
  pendingDelete.value = null
}

watch(showNewTab, async (v) => {
  if (v) {
    await nextTick()
    newNameInput.value?.focus()
  }
})
</script>

<style scoped>
.diagram-tabs {
  display: flex;
  flex-direction: column;
  background: var(--surface-container, #ecedf9);
  border-bottom: 1px solid var(--outline-variant, #e5e5e7);
}

.tabs-bar {
  display: flex;
  align-items: center;
  overflow-x: auto;
  padding: 0 8px;
  gap: 2px;
  min-height: 40px;
}

.tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: none;
  border-radius: 6px 6px 0 0;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: var(--on-surface-variant, #414755);
  white-space: nowrap;
  transition: background 0.15s;
}

.tab:hover {
  background: rgba(0, 88, 188, 0.08);
}

.tab.active {
  background: var(--surface-container-lowest, #fff);
  color: var(--primary, #0058bc);
  font-weight: 600;
}

.tab-close {
  font-size: 11px;
  opacity: 0.5;
  padding: 1px 2px;
  border-radius: 3px;
  line-height: 1;
}

.tab-close:hover {
  opacity: 1;
  background: rgba(192, 57, 43, 0.15);
  color: #c0392b;
}

.tab-add {
  font-size: 18px;
  font-weight: 300;
  color: var(--primary, #0058bc);
  padding: 4px 10px;
}

.new-tab-form {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-top: 1px solid var(--outline-variant, #e5e5e7);
}

.new-name-input {
  flex: 1;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--primary, #0058bc);
  font-size: 13px;
  outline: none;
}

.btn-ok,
.btn-cancel {
  padding: 5px 12px;
  border-radius: 6px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-ok {
  background: var(--primary, #0058bc);
  color: #fff;
}

.btn-cancel {
  background: transparent;
  color: var(--on-surface-variant, #414755);
  border: 1px solid var(--outline-variant, #e5e5e7);
}
</style>
