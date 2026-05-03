<template>
  <button
    :class="[
      'btn',
      `btn--${variant}`,
      `btn--${size}`,
      { 'btn--loading': loading },
      { 'btn--block': block },
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="btn__spinner"></span>
    <span :class="{ 'btn__text--hidden': loading }">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  block?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  block: false,
})

defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-family);
  font-weight: 500;
  border: none;
  border-radius: var(--radius-button);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  white-space: nowrap;
}

/* Sizes */
.btn--sm {
  padding: 8px 16px;
  font-size: 14px;
}

.btn--md {
  padding: 12px 24px;
  font-size: 16px;
}

.btn--lg {
  padding: 16px 32px;
  font-size: 17px;
}

/* Variants */
.btn--primary {
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.btn--primary:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn--secondary {
  background: var(--color-surface-container);
  color: var(--color-primary);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--color-surface-container-high);
}

.btn--tertiary {
  background: transparent;
  color: var(--color-primary);
}

.btn--tertiary:hover:not(:disabled) {
  background: var(--color-surface-container-low);
}

.btn--danger {
  background: var(--color-error);
  color: var(--color-on-error);
}

.btn--danger:hover:not(:disabled) {
  opacity: 0.9;
}

/* States */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.btn--block {
  width: 100%;
}

.btn--loading {
  cursor: wait;
}

/* Spinner */
.btn__spinner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.btn__text--hidden {
  opacity: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
