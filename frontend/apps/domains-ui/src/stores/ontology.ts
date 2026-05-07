import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { ontologyApi } from '../services/ontologyApi'
import type {
  Diagram,
  DiagramEdge,
  DiagramNode,
  DiagramViewport,
  OntologyConcept,
  OntologyProperty,
  ConceptCreatePayload,
  PropertyCreatePayload,
} from '../types/ontology'

export const useOntologyStore = defineStore('ontology', () => {
  // ── Domain context ──────────────────────────────────────────────────────────
  const activeDomainId = ref<string | null>(null)

  // ── Semantic state (Neo4j) ──────────────────────────────────────────────────
  const concepts = ref<OntologyConcept[]>([])
  const properties = ref<OntologyProperty[]>([])

  // ── Visual state (PostgreSQL) ───────────────────────────────────────────────
  const diagrams = ref<Diagram[]>([])
  const activeDiagramId = ref<string | null>(null)

  // ── UI state ────────────────────────────────────────────────────────────────
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const selectedElementId = ref<string | null>(null)
  const snapToGrid = ref(false)

  // ── Getters ─────────────────────────────────────────────────────────────────
  const conceptMap = computed(() =>
    Object.fromEntries(concepts.value.map(c => [c.id, c]))
  )

  const propertyMap = computed(() =>
    Object.fromEntries(properties.value.map(p => [p.id, p]))
  )

  const activeDiagram = computed(() =>
    diagrams.value.find(d => d.id === activeDiagramId.value) ?? null
  )

  const selectedConcept = computed(() => {
    if (!selectedElementId.value) return null
    return conceptMap.value[selectedElementId.value] ?? null
  })

  const selectedProperty = computed(() => {
    if (!selectedElementId.value) return null
    const node = activeDiagram.value?.nodes.find(n => n.id === selectedElementId.value)
    if (node) return null
    const edge = activeDiagram.value?.edges.find(e => e.id === selectedElementId.value)
    if (!edge) return null
    return propertyMap.value[edge.property_id] ?? null
  })

  // ── Actions ─────────────────────────────────────────────────────────────────

  async function loadForDomain(domainId: string) {
    if (activeDomainId.value === domainId && concepts.value.length) return
    activeDomainId.value = domainId
    isLoading.value = true
    error.value = null
    try {
      const [ontData, diagData] = await Promise.all([
        ontologyApi.getOntology(domainId),
        ontologyApi.listDiagrams(domainId),
      ])
      concepts.value = ontData.concepts
      properties.value = ontData.properties
      diagrams.value = diagData.items
      if (diagrams.value.length > 0 && !activeDiagramId.value) {
        activeDiagramId.value = diagrams.value[0].id
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load ontology'
    } finally {
      isLoading.value = false
    }
  }

  function selectDiagram(id: string) {
    activeDiagramId.value = id
    selectedElementId.value = null
  }

  async function createDiagram(name: string) {
    if (!activeDomainId.value) return
    const d = await ontologyApi.createDiagram(activeDomainId.value, { name })
    diagrams.value.push(d)
    activeDiagramId.value = d.id
  }

  async function renameDiagram(id: string, name: string) {
    if (!activeDomainId.value) return
    const updated = await ontologyApi.saveDiagram(activeDomainId.value, id, { name })
    const idx = diagrams.value.findIndex(d => d.id === id)
    if (idx >= 0) diagrams.value[idx] = updated
  }

  async function deleteDiagram(id: string) {
    if (!activeDomainId.value) return
    await ontologyApi.deleteDiagram(activeDomainId.value, id)
    diagrams.value = diagrams.value.filter(d => d.id !== id)
    if (activeDiagramId.value === id) {
      activeDiagramId.value = diagrams.value[0]?.id ?? null
    }
  }

  async function addClassToCanvas(concept: OntologyConcept, position: { x: number; y: number }) {
    if (!activeDiagram.value || !activeDomainId.value) return
    const nodeId = `node-${Date.now()}`
    const node: DiagramNode = { id: nodeId, concept_id: concept.id, position }
    const nodes = [...activeDiagram.value.nodes, node]
    const updated = await ontologyApi.saveDiagram(activeDomainId.value, activeDiagram.value.id, { nodes })
    _patchDiagram(updated)
  }

  async function addRelationToCanvas(propertyId: string, sourceNodeId: string, targetNodeId: string) {
    if (!activeDiagram.value || !activeDomainId.value) return
    const prop = propertyMap.value[propertyId]
    if (!prop) return
    const edgeId = `edge-${Date.now()}`
    const edge: DiagramEdge = { id: edgeId, property_id: propertyId, source: sourceNodeId, target: targetNodeId, label: prop.label }
    const edges = [...activeDiagram.value.edges, edge]
    const updated = await ontologyApi.saveDiagram(activeDomainId.value, activeDiagram.value.id, { edges })
    _patchDiagram(updated)
  }

  async function saveLayout(nodes: DiagramNode[], edges: DiagramEdge[], viewport: DiagramViewport) {
    if (!activeDiagram.value || !activeDomainId.value) return
    isSaving.value = true
    try {
      const updated = await ontologyApi.saveDiagram(activeDomainId.value, activeDiagram.value.id, { nodes, edges, viewport })
      _patchDiagram(updated)
    } finally {
      isSaving.value = false
    }
  }

  async function createConcept(payload: ConceptCreatePayload): Promise<OntologyConcept | null> {
    if (!activeDomainId.value) return null
    const concept = await ontologyApi.createConcept(activeDomainId.value, payload)
    concepts.value.push(concept)
    return concept
  }

  async function updateSelectedConcept(payload: Partial<ConceptCreatePayload>) {
    if (!selectedConcept.value || !activeDomainId.value) return
    const updated = await ontologyApi.updateConcept(activeDomainId.value, selectedConcept.value.id, payload)
    const idx = concepts.value.findIndex(c => c.id === updated.id)
    if (idx >= 0) concepts.value[idx] = updated
  }

  async function deleteSelectedConcept() {
    if (!selectedConcept.value || !activeDomainId.value || !activeDiagram.value) return
    const cid = selectedConcept.value.id
    await ontologyApi.deleteConcept(activeDomainId.value, cid)
    concepts.value = concepts.value.filter(c => c.id !== cid)
    properties.value = properties.value.filter(p => p.source_class_id !== cid && p.target_class_id !== cid)
    // Remove nodes and edges referencing this concept
    if (activeDomainId.value) {
      const nodes = activeDiagram.value.nodes.filter(n => n.concept_id !== cid)
      const removedNodeIds = new Set(activeDiagram.value.nodes.filter(n => n.concept_id === cid).map(n => n.id))
      const edges = activeDiagram.value.edges.filter(e => !removedNodeIds.has(e.source) && !removedNodeIds.has(e.target))
      const updated = await ontologyApi.saveDiagram(activeDomainId.value, activeDiagram.value.id, { nodes, edges })
      _patchDiagram(updated)
    }
    selectedElementId.value = null
  }

  async function createProperty(payload: PropertyCreatePayload): Promise<OntologyProperty | null> {
    if (!activeDomainId.value) return null
    const prop = await ontologyApi.createProperty(activeDomainId.value, payload)
    properties.value.push(prop)
    return prop
  }

  function selectElement(id: string | null) {
    selectedElementId.value = id
  }

  function toggleSnapToGrid() {
    snapToGrid.value = !snapToGrid.value
  }

  function _patchDiagram(updated: Diagram) {
    const idx = diagrams.value.findIndex(d => d.id === updated.id)
    if (idx >= 0) diagrams.value[idx] = updated
  }

  function reset() {
    activeDomainId.value = null
    concepts.value = []
    properties.value = []
    diagrams.value = []
    activeDiagramId.value = null
    selectedElementId.value = null
    error.value = null
  }

  return {
    activeDomainId,
    concepts,
    properties,
    diagrams,
    activeDiagramId,
    isLoading,
    isSaving,
    error,
    selectedElementId,
    snapToGrid,
    conceptMap,
    propertyMap,
    activeDiagram,
    selectedConcept,
    selectedProperty,
    loadForDomain,
    selectDiagram,
    createDiagram,
    renameDiagram,
    deleteDiagram,
    addClassToCanvas,
    addRelationToCanvas,
    saveLayout,
    createConcept,
    updateSelectedConcept,
    deleteSelectedConcept,
    createProperty,
    selectElement,
    toggleSnapToGrid,
    reset,
  }
})
