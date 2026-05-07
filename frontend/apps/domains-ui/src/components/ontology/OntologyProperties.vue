<template>
  <aside class="props-panel" :class="{ open: isOpen }">
    <button class="toggle-btn" @click="isOpen = !isOpen" :title="isOpen ? 'Collapse' : 'Expand'">
      {{ isOpen ? '▶' : '◀' }}
    </button>

    <div v-if="isOpen" class="panel-content">
      <h4 class="panel-title">Properties</h4>

      <template v-if="selectedConcept">
        <label class="field-label">Label</label>
        <input class="field-input" v-model="editLabel" @blur="save" />
        <label class="field-label">URI</label>
        <input class="field-input" v-model="editUri" @blur="save" />
        <label class="field-label">Comment</label>
        <textarea class="field-input" rows="3" v-model="editComment" @blur="save" />
        <button class="btn-danger" @click="store.deleteSelectedConcept()">Delete Class</button>
      </template>

      <template v-else-if="selectedProperty">
        <label class="field-label">Label</label>
        <p class="field-value">{{ selectedProperty!.label }}</p>
        <label class="field-label">Type</label>
        <p class="field-value">{{ selectedProperty!.property_type }}</p>
        <label class="field-label">URI</label>
        <p class="field-value mono">{{ selectedProperty!.uri }}</p>
      </template>

      <p v-else class="empty-msg">Select a class or relation on the canvas.</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useOntologyStore } from '../../stores/ontology'

const store = useOntologyStore()
const { selectedConcept, selectedProperty } = storeToRefs(store)
const isOpen = ref(true)

const editLabel = ref('')
const editUri = ref('')
const editComment = ref('')

watch(
  selectedConcept,
  (c) => {
    editLabel.value = c?.label ?? ''
    editUri.value = c?.uri ?? ''
    editComment.value = c?.comment ?? ''
  },
  { immediate: true }
)

async function save() {
  if (!selectedConcept.value) return
  const current = selectedConcept.value
  if (
    editLabel.value === current.label &&
    editUri.value === current.uri &&
    editComment.value === (current.comment ?? '')
  ) return
  await store.updateSelectedConcept({
    label: editLabel.value,
    uri: editUri.value,
    comment: editComment.value || undefined,
  })
}
</script>

<style scoped>
.props-panel {
  position: relative;
  background: var(--surface-container-lowest, #fff);
  border-left: 1px solid var(--outline-variant, #e5e5e7);
  display: flex;
  flex-direction: row;
  transition: width 0.2s;
  width: 44px;
  overflow: hidden;
}

.props-panel.open {
  width: 240px;
}

.toggle-btn {
  position: absolute;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  width: 22px;
  height: 48px;
  border: none;
  background: var(--surface-container, #ecedf9);
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  font-size: 10px;
  color: var(--on-surface-variant, #414755);
  z-index: 5;
}

.panel-content {
  padding: 16px 16px 16px 28px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  overflow-y: auto;
}

.panel-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--on-surface-variant, #86868b);
  margin: 0 0 8px;
}

.field-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--on-surface-variant, #86868b);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field-input {
  padding: 6px 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  resize: vertical;
  width: 100%;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: var(--primary, #0058bc);
}

.field-value {
  font-size: 13px;
  color: var(--on-surface, #1d1d1f);
  margin: 0;
}

.mono {
  font-family: monospace;
  font-size: 11px;
  word-break: break-all;
}

.empty-msg {
  font-size: 13px;
  color: var(--on-surface-variant, #86868b);
  font-style: italic;
  margin: 0;
  text-align: center;
  padding-top: 24px;
}

.btn-danger {
  padding: 7px 12px;
  border-radius: 8px;
  border: none;
  background: #c0392b;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
}
</style>
