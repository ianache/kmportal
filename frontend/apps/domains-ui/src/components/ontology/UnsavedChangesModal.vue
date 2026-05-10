<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click="onCancel">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <div class="warning-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <h3 class="modal-title">Unsaved Changes</h3>
        </div>
        
        <div class="modal-body">
          <p class="modal-message">
            You have unsaved changes in the ontology editor. 
            Do you want to save them before leaving?
          </p>
          <div v-if="changeSummary" class="change-summary">
            <p class="summary-title">Pending changes:</p>
            <ul class="summary-list">
              <li v-if="conceptChanges > 0">{{ conceptChanges }} concept {{ conceptChanges === 1 ? 'change' : 'changes' }}</li>
              <li v-if="propertyChanges > 0">{{ propertyChanges }} property {{ propertyChanges === 1 ? 'change' : 'changes' }}</li>
              <li v-if="diagramChanges > 0">{{ diagramChanges }} diagram {{ diagramChanges === 1 ? 'change' : 'changes' }}</li>
            </ul>
          </div>
        </div>
        
        <div class="modal-footer">
          <button 
            class="btn btn-secondary" 
            @click="onCancel"
            :disabled="isSaving"
          >
            Cancel
          </button>
          <button 
            class="btn btn-danger" 
            @click="onDiscard"
            :disabled="isSaving"
          >
            Discard
          </button>
          <button 
            class="btn btn-primary" 
            @click="onSave"
            :disabled="isSaving"
          >
            <span v-if="isSaving" class="spinner-small"></span>
            <span v-else>Save Changes</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  isOpen: boolean
  isSaving: boolean
  conceptOperations?: number
  propertyOperations?: number
  diagramOperations?: number
}>()

const emit = defineEmits<{
  (e: 'save'): void
  (e: 'discard'): void
  (e: 'cancel'): void
}>()

const conceptChanges = computed(() => props.conceptOperations ?? 0)
const propertyChanges = computed(() => props.propertyOperations ?? 0)
const diagramChanges = computed(() => props.diagramOperations ?? 0)

const changeSummary = computed(() => 
  conceptChanges.value + propertyChanges.value + diagramChanges.value > 0
)

function onSave() {
  emit('save')
}

function onDiscard() {
  emit('discard')
}

function onCancel() {
  emit('cancel')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

.modal-container {
  background: var(--surface-container-lowest, #fff);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  max-width: 480px;
  width: 90%;
  animation: slideIn 0.2s ease-out;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px 0;
}

.warning-icon {
  color: var(--warning, #f59e0b);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--on-surface, #1d1d1f);
  margin: 0;
}

.modal-body {
  padding: 16px 24px;
}

.modal-message {
  font-size: 14px;
  color: var(--on-surface-variant, #86868b);
  line-height: 1.5;
  margin: 0 0 16px;
}

.change-summary {
  background: var(--surface-container, #ecedf9);
  border-radius: 8px;
  padding: 12px 16px;
}

.summary-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--on-surface, #1d1d1f);
  margin: 0 0 8px;
}

.summary-list {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 13px;
  color: var(--on-surface-variant, #86868b);
}

.summary-list li {
  padding: 4px 0;
  padding-left: 16px;
  position: relative;
}

.summary-list li::before {
  content: '•';
  position: absolute;
  left: 4px;
  color: var(--primary, #0058bc);
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 0 24px 20px;
  justify-content: flex-end;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: none;
  min-width: 100px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary, #0058bc);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover, #004494);
}

.btn-secondary {
  background: transparent;
  color: var(--on-surface-variant, #86868b);
  border: 1px solid var(--outline-variant, #e5e5e7);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--surface-container, #ecedf9);
}

.btn-danger {
  background: var(--error-container, #ffebee);
  color: var(--error, #d32f2f);
}

.btn-danger:hover:not(:disabled) {
  background: var(--error, #d32f2f);
  color: white;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
