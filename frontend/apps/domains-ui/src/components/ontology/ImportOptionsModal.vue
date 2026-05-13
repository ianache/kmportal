<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click="$emit('cancel')">
      <div class="modal-container" @click.stop>

        <div class="modal-header">
          <div class="upload-icon">
            <svg width="22" height="22" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10 17V7M6 11l4-4 4 4M3 4h14"/>
            </svg>
          </div>
          <div>
            <h3 class="modal-title">Importar ontología</h3>
            <p class="modal-filename">{{ fileName }}</p>
          </div>
        </div>

        <div class="modal-body">
          <label class="radio-option" :class="{ selected: mode === 'merge' }" @click="mode = 'merge'">
            <input type="radio" v-model="mode" value="merge" />
            <div class="option-content">
              <div class="option-label">
                Merge
                <span class="recommended-badge">recomendado</span>
              </div>
              <div class="option-desc">
                Agrega y actualiza clases por URI sin eliminar las existentes que no estén en el archivo.
              </div>
            </div>
          </label>

          <label class="radio-option" :class="{ selected: mode === 'replace' }" @click="mode = 'replace'">
            <input type="radio" v-model="mode" value="replace" />
            <div class="option-content">
              <div class="option-label">Reemplazar todo</div>
              <div class="option-desc">
                Elimina toda la ontología actual y la sustituye con el contenido del archivo.
              </div>
            </div>
          </label>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('cancel')">Cancelar</button>
          <button class="btn btn-primary" @click="$emit('execute', mode)">Continuar →</button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  isOpen: boolean
  fileName: string
}>()

const emit = defineEmits<{
  (e: 'cancel'): void
  (e: 'execute', mode: 'merge' | 'replace'): void
}>()

const mode = ref<'merge' | 'replace'>('merge')

// Reset to merge each time the modal opens
watch(() => props.isOpen, (open) => { if (open) mode.value = 'merge' })
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
  animation: fadeIn 0.15s ease-out;
}

.modal-container {
  background: var(--surface-container-lowest, #fff);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  max-width: 460px;
  width: 90%;
  animation: slideIn 0.18s ease-out;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 20px 24px 0;
}

.upload-icon {
  color: var(--primary, #0058bc);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(0, 88, 188, 0.08);
  flex-shrink: 0;
  margin-top: 2px;
}

.modal-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--on-surface, #1d1d1f);
  margin: 0 0 2px;
}

.modal-filename {
  font-size: 12px;
  color: var(--on-surface-variant, #86868b);
  margin: 0;
  font-family: monospace;
}

.modal-body {
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 10px;
  border: 1.5px solid var(--outline-variant, #e5e5e7);
  cursor: pointer;
  transition: border-color 0.12s, background 0.12s;
  user-select: none;
}

.radio-option:hover {
  background: var(--surface-container, #ecedf9);
}

.radio-option.selected {
  border-color: var(--primary, #0058bc);
  background: rgba(0, 88, 188, 0.04);
}

.radio-option input[type="radio"] {
  margin-top: 3px;
  accent-color: var(--primary, #0058bc);
  flex-shrink: 0;
}

.option-content { flex: 1; }

.option-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--on-surface, #1d1d1f);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.recommended-badge {
  font-size: 11px;
  font-weight: 500;
  color: var(--primary, #0058bc);
  background: rgba(0, 88, 188, 0.08);
  padding: 1px 7px;
  border-radius: 20px;
}

.option-desc {
  font-size: 13px;
  color: var(--on-surface-variant, #86868b);
  line-height: 1.4;
}

.modal-footer {
  display: flex;
  gap: 10px;
  padding: 4px 24px 20px;
  justify-content: flex-end;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.12s ease;
  border: none;
  min-width: 90px;
}

.btn-secondary {
  background: transparent;
  color: var(--on-surface-variant, #86868b);
  border: 1px solid var(--outline-variant, #e5e5e7);
}

.btn-secondary:hover { background: var(--surface-container, #ecedf9); }

.btn-primary {
  background: var(--primary, #0058bc);
  color: white;
}

.btn-primary:hover { background: var(--primary-hover, #004494); }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-16px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)     scale(1);    }
}
</style>
