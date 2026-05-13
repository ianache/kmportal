<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click="$emit('cancel')">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <div class="warn-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <h3 class="modal-title">Reemplazar ontología</h3>
        </div>

        <div class="modal-body">
          <p class="modal-message">
            Esta acción eliminará todas las clases y propiedades actuales del dominio
            y las reemplazará con el contenido del archivo importado.
          </p>
          <div v-if="classCount > 0 || propCount > 0" class="delete-summary">
            Se eliminarán
            <strong v-if="classCount > 0">{{ classCount }} {{ classCount === 1 ? 'clase' : 'clases' }}</strong>
            <span v-if="classCount > 0 && propCount > 0"> y </span>
            <strong v-if="propCount > 0">{{ propCount }} {{ propCount === 1 ? 'propiedad' : 'propiedades' }}</strong>.
          </div>
          <p class="modal-warning">Esta operación no se puede deshacer.</p>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('cancel')">Cancelar</button>
          <button class="btn btn-danger" @click="$emit('confirm')">Reemplazar todo</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{ isOpen: boolean; classCount: number; propCount: number }>()
defineEmits<{ (e: 'cancel'): void; (e: 'confirm'): void }>()
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1001; animation: fadeIn 0.15s ease-out;
}
.modal-container {
  background: var(--surface-container-lowest, #fff); border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15); max-width: 440px; width: 90%;
  animation: slideIn 0.18s ease-out;
}
.modal-header { display: flex; align-items: center; gap: 12px; padding: 20px 24px 0; }
.warn-icon { color: #f59e0b; display: flex; }
.modal-title { font-size: 17px; font-weight: 600; color: var(--on-surface,#1d1d1f); margin: 0; }
.modal-body { padding: 14px 24px; }
.modal-message { font-size: 14px; color: var(--on-surface-variant,#86868b); line-height: 1.5; margin: 0 0 12px; }
.delete-summary {
  font-size: 13px; background: #fff3cd; border: 1px solid #ffc107;
  border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; color: #856404;
}
.modal-warning { font-size: 13px; font-weight: 600; color: var(--error,#ba1a1a); margin: 0; }
.modal-footer { display: flex; gap: 10px; padding: 4px 24px 20px; justify-content: flex-end; }
.btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 9px 18px; border-radius: 8px; font-size: 14px; font-weight: 500;
  cursor: pointer; transition: all 0.12s ease; border: none; min-width: 90px;
}
.btn-secondary {
  background: transparent; color: var(--on-surface-variant,#86868b);
  border: 1px solid var(--outline-variant,#e5e5e7);
}
.btn-secondary:hover { background: var(--surface-container,#ecedf9); }
.btn-danger { background: var(--error,#ba1a1a); color: white; }
.btn-danger:hover { background: #9b1515; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-16px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)     scale(1);    }
}
</style>
