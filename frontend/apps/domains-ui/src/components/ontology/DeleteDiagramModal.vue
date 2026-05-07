<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('cancel')">
      <div class="modal" role="dialog" aria-modal="true">
        <h3 class="modal-title">Delete Diagram</h3>
        <p class="modal-body">
          This will permanently delete <strong>{{ diagramName }}</strong>. Type
          <code>delete</code> to confirm.
        </p>
        <input
          v-model="confirmText"
          class="confirm-input"
          placeholder="delete"
          autocomplete="off"
          @keydown.enter="confirm"
        />
        <div class="modal-actions">
          <button class="btn-cancel" @click="$emit('cancel')">Cancel</button>
          <button class="btn-delete" :disabled="confirmText !== 'delete'" @click="confirm">
            Delete
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ diagramName: string }>()
const emit = defineEmits<{ (e: 'confirm'): void; (e: 'cancel'): void }>()

const confirmText = ref('')

function confirm() {
  if (confirmText.value === 'delete') emit('confirm')
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--surface-container-lowest, #fff);
  border-radius: 12px;
  padding: 28px 32px;
  min-width: 360px;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--on-surface, #1d1d1f);
  margin: 0 0 12px;
}

.modal-body {
  font-size: 14px;
  color: var(--on-surface-variant, #414755);
  line-height: 1.6;
  margin: 0 0 16px;
}

code {
  background: var(--surface-container, #ecedf9);
  padding: 1px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.confirm-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--outline, #c6c6c8);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  margin-bottom: 20px;
  transition: border-color 0.2s;
}

.confirm-input:focus {
  border-color: var(--primary, #0058bc);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel {
  padding: 8px 18px;
  border-radius: 8px;
  border: 1px solid var(--outline-variant, #e5e5e7);
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  color: var(--on-surface, #1d1d1f);
}

.btn-delete {
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  background: #c0392b;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-delete:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
