<template>
  <div :class="['card', `card--${elevation}`]">
    <div v-if="$slots.header || title" class="card__header">
      <slot name="header">
        <h3 v-if="title" class="card__title">{{ title }}</h3>
        <p v-if="subtitle" class="card__subtitle">{{ subtitle }}</p>
      </slot>
    </div>
    
    <div class="card__body">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
  elevation?: 'low' | 'medium' | 'high'
}

withDefaults(defineProps<Props>(), {
  elevation: 'low',
})
</script>

<style scoped>
.card {
  background: var(--color-surface-container-lowest);
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-card);
  overflow: hidden;
}

.card--low {
  box-shadow: var(--shadow-card);
}

.card--medium {
  box-shadow: var(--shadow-md);
}

.card--high {
  box-shadow: var(--shadow-lg);
}

.card__header {
  padding: 24px 24px 0;
}

.card__title {
  font-family: var(--font-family);
  font-size: 20px;
  font-weight: 600;
  color: var(--color-on-surface);
  margin: 0;
}

.card__subtitle {
  font-family: var(--font-family);
  font-size: 14px;
  color: var(--color-on-surface-variant);
  margin: 4px 0 0;
}

.card__body {
  padding: 24px;
}

.card__footer {
  padding: 16px 24px;
  background: var(--color-surface-container-low);
  border-top: 1px solid var(--color-outline-variant);
}
</style>
