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

  // DatatypeProperties (attributes) belonging to the currently selected class
  const selectedConceptAttributes = computed(() => {
    if (!selectedConcept.value) return []
    return properties.value.filter(
      p => p.property_type === 'DatatypeProperty' && p.source_class_id === selectedConcept.value!.id
    )
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

    // Auto-add edges for ObjectProperties between this concept and already-present classes
    const presentNodes = activeDiagram.value.nodes
    const existingPropIds = new Set(activeDiagram.value.edges.map(e => e.property_id))
    const autoEdges: DiagramEdge[] = []

    properties.value
      .filter(p => p.property_type === 'ObjectProperty' && !existingPropIds.has(p.id))
      .forEach((p, idx) => {
        const isSource = p.source_class_id === concept.id
        const isTarget = p.target_class_id === concept.id
        if (!isSource && !isTarget) return

        const otherConceptId = isSource ? p.target_class_id : p.source_class_id
        const otherNode = presentNodes.find(n => n.concept_id === otherConceptId)
        if (!otherNode) return

        autoEdges.push({
          id: `edge-${Date.now()}-${idx}`,
          property_id: p.id,
          source: isSource ? nodeId : otherNode.id,
          target: isSource ? otherNode.id : nodeId,
          label: p.label,
        })
      })

    const nodes = [...activeDiagram.value.nodes, node]
    const edges = [...activeDiagram.value.edges, ...autoEdges]
    const updated = await ontologyApi.saveDiagram(activeDomainId.value, activeDiagram.value.id, { nodes, edges })
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
    if (!selectedConcept.value || !activeDomainId.value) return
    const cid = selectedConcept.value.id
    const domainId = activeDomainId.value
    await ontologyApi.deleteConcept(domainId, cid)
    concepts.value = concepts.value.filter(c => c.id !== cid)
    properties.value = properties.value.filter(p => p.source_class_id !== cid && p.target_class_id !== cid)
    // Remove from ALL diagrams that reference this concept
    await Promise.all(
      diagrams.value
        .filter(d => d.nodes.some(n => n.concept_id === cid))
        .map(async (d) => {
          const removedIds = new Set(d.nodes.filter(n => n.concept_id === cid).map(n => n.id))
          const nodes = d.nodes.filter(n => n.concept_id !== cid)
          const edges = d.edges.filter(e => !removedIds.has(e.source) && !removedIds.has(e.target))
          const updated = await ontologyApi.saveDiagram(domainId, d.id, { nodes, edges })
          _patchDiagram(updated)
        })
    )
    selectedElementId.value = null
  }

  async function deleteSelectedProperty() {
    if (!selectedProperty.value || !activeDomainId.value) return
    const pid = selectedProperty.value.id
    const domainId = activeDomainId.value
    await ontologyApi.deleteProperty(domainId, pid)
    properties.value = properties.value.filter(p => p.id !== pid)
    // Remove edges referencing this property from ALL diagrams
    await Promise.all(
      diagrams.value
        .filter(d => d.edges.some(e => e.property_id === pid))
        .map(async (d) => {
          const edges = d.edges.filter(e => e.property_id !== pid)
          const updated = await ontologyApi.saveDiagram(domainId, d.id, { edges })
          _patchDiagram(updated)
        })
    )
    selectedElementId.value = null
  }

  async function removeNodesFromCanvas(nodeIds: string[]) {
    if (!activeDiagram.value || !activeDomainId.value) return
    const removeSet = new Set(nodeIds)
    const removedConceptIds = new Set(
      activeDiagram.value.nodes.filter(n => removeSet.has(n.id)).map(n => n.concept_id)
    )
    const nodes = activeDiagram.value.nodes.filter(n => !removeSet.has(n.id))
    const edges = activeDiagram.value.edges.filter(e => !removeSet.has(e.source) && !removeSet.has(e.target))
    const updated = await ontologyApi.saveDiagram(activeDomainId.value, activeDiagram.value.id, { nodes, edges })
    _patchDiagram(updated)
    if (selectedElementId.value && removedConceptIds.has(selectedElementId.value)) {
      selectedElementId.value = null
    }
  }

  async function removeEdgesFromCanvas(edgeIds: string[]) {
    if (!activeDiagram.value || !activeDomainId.value) return
    const removeSet = new Set(edgeIds)
    const edges = activeDiagram.value.edges.filter(e => !removeSet.has(e.id))
    const updated = await ontologyApi.saveDiagram(activeDomainId.value, activeDiagram.value.id, { edges })
    _patchDiagram(updated)
    if (selectedElementId.value && removeSet.has(selectedElementId.value)) {
      selectedElementId.value = null
    }
  }

  async function createDatatypeAttribute(label: string, xsdUri: string, comment?: string): Promise<void> {
    if (!selectedConcept.value || !activeDomainId.value) return
    const concept = selectedConcept.value
    const base = concept.uri.includes('#')
      ? concept.uri.substring(0, concept.uri.lastIndexOf('#') + 1)
      : concept.uri + '#'
    const prop = await ontologyApi.createProperty(activeDomainId.value, {
      uri: `${base}${label.replace(/\s+/g, '_')}`,
      label,
      property_type: 'DatatypeProperty',
      source_class_id: concept.id,
      target_class_id: xsdUri,
      comment,
    })
    properties.value.push(prop)
  }

  async function deleteDatatypeAttribute(propertyId: string): Promise<void> {
    if (!activeDomainId.value) return
    await ontologyApi.deleteProperty(activeDomainId.value, propertyId)
    properties.value = properties.value.filter(p => p.id !== propertyId)
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
    selectedConceptAttributes,
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
    deleteSelectedProperty,
    createDatatypeAttribute,
    deleteDatatypeAttribute,
    removeNodesFromCanvas,
    removeEdgesFromCanvas,
    createProperty,
    selectElement,
    toggleSnapToGrid,
    reset,
  }
})
