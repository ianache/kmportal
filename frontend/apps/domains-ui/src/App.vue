<template>
  <div class="domains-app">
    <!-- Ontology editor takes full focus when active -->
    <OntologyEditor
      v-if="ontologyDomain"
      :domain-id="ontologyDomain.id"
      :domain-name="ontologyDomain.name"
      @close="ontologyDomain = null"
    />

    <template v-else>
      <transition name="fade" mode="out-in">
        <DomainList
          v-if="!domainsStore.hasSelectedDomain"
          @open-ontology="openOntology"
        />
        <DomainDetail v-else />
      </transition>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDomainsStore } from './stores/domains'
import { useOntologyStore } from './stores/ontology'
import DomainList from './components/DomainList.vue'
import DomainDetail from './components/DomainDetail.vue'
import OntologyEditor from './components/ontology/OntologyEditor.vue'
import type { Domain } from './types/domains'

const domainsStore = useDomainsStore()
const ontologyStore = useOntologyStore()

const ontologyDomain = ref<Domain | null>(null)

function openOntology(domain: Domain) {
  ontologyStore.reset()
  ontologyDomain.value = domain
}
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
