<template>
  <div class="domains-app">
    <transition name="fade" mode="out-in">
      <DomainList v-if="!domainsStore.hasSelectedDomain" />
      <DomainDetail v-else />
    </transition>
  </div>
</template>

<script setup lang="ts">
import { useDomainsStore } from './stores/domains'
import DomainList from './components/DomainList.vue'
import DomainDetail from './components/DomainDetail.vue'

const domainsStore = useDomainsStore()
</script>

<style scoped>
.domains-app {
  min-height: 100%;
  background: var(--background, #f9f9ff);
  color: var(--on-background, #181c23);
  font-family: Inter, sans-serif;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
