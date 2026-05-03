<template>
  <div :class="['input-wrapper', { 'input-wrapper--error': error }]">
    <label v-if="label" :for="inputId" class="input-label">
      {{ label }}
      <span v-if="required" class="input-required">*</span>
    </label>
    
    <div class="input-container">
      <span v-if="icon" class="input-icon">{{ icon }}</span>
      
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        class="input-field"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      />
      
      <button
        v-if="clearable && modelValue"
        type="button"
        class="input-clear"
        @click="$emit('update:modelValue', '')"
      >
        ✕
      </button>
    </div>
    
    <span v-if="error" class="input-error">{{ error }}</span>
    <span v-else-if="hint" class="input-hint">{{ hint }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string
  label?: string
  type?: 'text' | 'password' | 'email' | 'search'
  placeholder?: string
  icon?: string
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  clearable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
  clearable: false,
})

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur', event: FocusEvent): void
  (e: 'focus', event: FocusEvent): void
}>()
</script>

<style scoped>
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-label {
  font-family: var(--font-family);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-on-surface);
}

.input-required {
  color: var(--color-error);
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  font-size: 18px;
  color: var(--color-on-surface-variant);
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  font-family: var(--font-family);
  font-size: 16px;
  color: var(--color-on-surface);
  background: var(--color-surface-container-low);
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-input);
  transition: all var(--transition-fast);
}

.input-field:focus {
  outline: none;
  background: var(--color-surface-container-lowest);
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-fixed-dim);
}

.input-field:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-wrapper--error .input-field {
  border-color: var(--color-error);
}

.input-wrapper--error .input-field:focus {
  box-shadow: 0 0 0 3px var(--color-error-container);
}

.input-clear {
  position: absolute;
  right: 12px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--color-on-surface-variant);
  cursor: pointer;
  border-radius: 50%;
  font-size: 14px;
}

.input-clear:hover {
  background: var(--color-surface-container-high);
}

.input-error {
  font-family: var(--font-family);
  font-size: 13px;
  color: var(--color-error);
}

.input-hint {
  font-family: var(--font-family);
  font-size: 13px;
  color: var(--color-on-surface-variant);
}
</style>
