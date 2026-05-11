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
  OntologyBatchPayload,
  ConceptBatchOperation,
  PropertyBatchOperation,
  DiagramBatchOperation,
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
  const panelMode = ref<'create' | 'edit' | null>(null)
  const pendingClassPosition = ref<{ x: number; y: number } | null>(null)

  // ── Pending changes state (batch operations) ────────────────────────────────
  const hasUnsavedChanges = ref(false)
  const pendingConceptOperations = ref<ConceptBatchOperation[]>([])
  const pendingPropertyOperations = ref<PropertyBatchOperation[]>([])
  const pendingDiagramOperations = ref<DiagramBatchOperation[]>([])

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
    const tempId = `temp-diagram-${Date.now()}`
    queueDiagramOperation({ operation: 'create', id: tempId, data: { name } })
    // Optimistic update
    const d: Diagram = {
      id: tempId,
      domain_id: activeDomainId.value,
      name,
      nodes: [],
      edges: [],
      viewport: { x: 0, y: 0, zoom: 1 },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    diagrams.value.push(d)
    activeDiagramId.value = d.id
  }

  async function renameDiagram(id: string, name: string) {
    if (!activeDomainId.value) return
    queueDiagramOperation({ operation: 'update', id, data: { name } })
    // Optimistic update
    const idx = diagrams.value.findIndex(d => d.id === id)
    if (idx >= 0) {
      diagrams.value[idx] = { ...diagrams.value[idx], name, updated_at: new Date().toISOString() }
    }
  }

  async function deleteDiagram(id: string) {
    if (!activeDomainId.value) return
    queueDiagramOperation({ operation: 'delete', id })
    // Optimistic update
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
    
    // Queue diagram update
    queueDiagramOperation({ 
      operation: 'update', 
      id: activeDiagram.value.id, 
      data: { nodes, edges } 
    })
    
    // Optimistic update
    const idx = diagrams.value.findIndex(d => d.id === activeDiagram.value!.id)
    if (idx >= 0) {
      diagrams.value[idx] = { 
        ...diagrams.value[idx], 
        nodes, 
        edges, 
        updated_at: new Date().toISOString() 
      }
    }
  }

  async function addRelationToCanvas(propertyId: string, sourceNodeId: string, targetNodeId: string) {
    if (!activeDiagram.value || !activeDomainId.value) return
    const prop = propertyMap.value[propertyId]
    if (!prop) return
    const edgeId = `edge-${Date.now()}`
    const edge: DiagramEdge = { id: edgeId, property_id: propertyId, source: sourceNodeId, target: targetNodeId, label: prop.label }
    const edges = [...activeDiagram.value.edges, edge]
    
    // Queue the change
    queueDiagramOperation({
      operation: 'update',
      id: activeDiagram.value.id,
      data: { edges }
    })
    
    // Optimistic update
    const idx = diagrams.value.findIndex(d => d.id === activeDiagram.value!.id)
    if (idx >= 0) {
      diagrams.value[idx] = {
        ...diagrams.value[idx],
        edges,
        updated_at: new Date().toISOString()
      }
    }
  }

  async function saveLayout(
    previousNodes: DiagramNode[], 
    previousEdges: DiagramEdge[], 
    viewport: DiagramViewport,
    markAsUnsaved: boolean = true
  ) {
    if (!activeDiagram.value || !activeDomainId.value) return
    
    // Get current state from store (which has been updated by the canvas)
    const currentNodes = activeDiagram.value.nodes
    const currentEdges = activeDiagram.value.edges
    
    // Compare previous state against current state to detect changes
    const hasNodeChanges = JSON.stringify(previousNodes) !== JSON.stringify(currentNodes)
    const hasEdgeChanges = JSON.stringify(previousEdges) !== JSON.stringify(currentEdges)
    
    if ((hasNodeChanges || hasEdgeChanges) && markAsUnsaved) {
      // Queue the operation with current state for saving
      queueDiagramOperation({ 
        operation: 'update', 
        id: activeDiagram.value.id, 
        data: { nodes: currentNodes, edges: currentEdges, viewport } 
      })
    }
    
    // Update viewport in local state
    const idx = diagrams.value.findIndex(d => d.id === activeDiagram.value!.id)
    if (idx >= 0) {
      diagrams.value[idx] = { 
        ...diagrams.value[idx], 
        viewport,
        updated_at: new Date().toISOString() 
      }
    }
  }

  async function createConcept(payload: ConceptCreatePayload): Promise<OntologyConcept | null> {
    if (!activeDomainId.value) return null
    const concept = await ontologyApi.createConcept(activeDomainId.value, payload)
    concepts.value.push(concept)
    queueConceptOperation({ operation: 'create', id: concept.id, data: payload })
    return concept
  }

  async function updateSelectedConcept(payload: Partial<ConceptCreatePayload>) {
    if (!selectedConcept.value || !activeDomainId.value) return
    queueConceptOperation({ operation: 'update', id: selectedConcept.value.id, data: payload as ConceptCreatePayload })
    // Optimistic update
    const idx = concepts.value.findIndex(c => c.id === selectedConcept.value!.id)
    if (idx >= 0) {
      concepts.value[idx] = { ...concepts.value[idx], ...payload }
    }
  }

  async function deleteSelectedConcept() {
    if (!selectedConcept.value || !activeDomainId.value) return
    const cid = selectedConcept.value.id
    queueConceptOperation({ operation: 'delete', id: cid })
    // Optimistic update - remove from local state
    concepts.value = concepts.value.filter(c => c.id !== cid)
    properties.value = properties.value.filter(p => p.source_class_id !== cid && p.target_class_id !== cid)
    // Remove from ALL diagrams in local state
    diagrams.value.forEach(d => {
      const removedIds = new Set(d.nodes.filter(n => n.concept_id === cid).map(n => n.id))
      d.nodes = d.nodes.filter(n => n.concept_id !== cid)
      d.edges = d.edges.filter(e => !removedIds.has(e.source) && !removedIds.has(e.target))
    })
    selectedElementId.value = null
  }

  async function deleteSelectedProperty() {
    if (!selectedProperty.value || !activeDomainId.value) return
    const pid = selectedProperty.value.id
    queuePropertyOperation({ operation: 'delete', id: pid })
    // Optimistic update
    properties.value = properties.value.filter(p => p.id !== pid)
    // Remove edges referencing this property from ALL diagrams in local state
    diagrams.value.forEach(d => {
      d.edges = d.edges.filter(e => e.property_id !== pid)
    })
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
    
    // Queue the change
    queueDiagramOperation({
      operation: 'update',
      id: activeDiagram.value.id,
      data: { nodes, edges }
    })
    
    // Optimistic update
    const idx = diagrams.value.findIndex(d => d.id === activeDiagram.value!.id)
    if (idx >= 0) {
      diagrams.value[idx] = {
        ...diagrams.value[idx],
        nodes,
        edges,
        updated_at: new Date().toISOString()
      }
    }
    
    if (selectedElementId.value && removedConceptIds.has(selectedElementId.value)) {
      selectedElementId.value = null
    }
  }

  async function removeEdgesFromCanvas(edgeIds: string[]) {
    if (!activeDiagram.value || !activeDomainId.value) return
    const removeSet = new Set(edgeIds)
    const edges = activeDiagram.value.edges.filter(e => !removeSet.has(e.id))
    
    // Queue the change
    queueDiagramOperation({
      operation: 'update',
      id: activeDiagram.value.id,
      data: { edges }
    })
    
    // Optimistic update
    const idx = diagrams.value.findIndex(d => d.id === activeDiagram.value!.id)
    if (idx >= 0) {
      diagrams.value[idx] = {
        ...diagrams.value[idx],
        edges,
        updated_at: new Date().toISOString()
      }
    }
    
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
    const tempId = `temp-attr-${Date.now()}`
    const payload: PropertyCreatePayload = {
      uri: `${base}${label.replace(/\s+/g, '_')}`,
      label,
      property_type: 'DatatypeProperty',
      source_class_id: concept.id,
      target_class_id: xsdUri,
      comment,
    }
    queuePropertyOperation({ operation: 'create', id: tempId, data: payload })
    // Optimistic update
    const prop: OntologyProperty = {
      id: tempId,
      domain_id: activeDomainId.value,
      ...payload,
    }
    properties.value.push(prop)
  }

  async function updateDatatypeAttribute(propertyId: string, label: string, xsdUri: string, comment?: string): Promise<void> {
    if (!activeDomainId.value) return
    const payload: PropertyCreatePayload = {
      uri: '', // Will be preserved by backend
      label,
      property_type: 'DatatypeProperty',
      source_class_id: '', // Will be preserved by backend
      target_class_id: xsdUri,
      comment,
    }
    queuePropertyOperation({ operation: 'update', id: propertyId, data: payload })
    // Optimistic update
    const idx = properties.value.findIndex(p => p.id === propertyId)
    if (idx >= 0) {
      properties.value[idx] = { 
        ...properties.value[idx], 
        label, 
        target_class_id: xsdUri, 
        comment: comment ?? '' 
      }
    }
  }

  async function deleteDatatypeAttribute(propertyId: string): Promise<void> {
    if (!activeDomainId.value) return
    queuePropertyOperation({ operation: 'delete', id: propertyId })
    // Optimistic update
    properties.value = properties.value.filter(p => p.id !== propertyId)
  }

  async function createProperty(payload: PropertyCreatePayload): Promise<OntologyProperty | null> {
    if (!activeDomainId.value) return null
    const tempId = `temp-prop-${Date.now()}`
    queuePropertyOperation({ operation: 'create', id: tempId, data: payload })
    // Optimistic update
    const prop: OntologyProperty = {
      id: tempId,
      domain_id: activeDomainId.value,
      ...payload,
    }
    properties.value.push(prop)
    return prop
  }

  function selectElement(id: string | null) {
    selectedElementId.value = id
    if (!id) {
      panelMode.value = null
    } else if (conceptMap.value[id]) {
      panelMode.value = 'edit'
    } else {
      panelMode.value = null
    }
  }

  function openCreatePanel(position: { x: number; y: number }) {
    pendingClassPosition.value = position
    selectedElementId.value = null
    panelMode.value = 'create'
  }

  function closePanel() {
    panelMode.value = null
    pendingClassPosition.value = null
  }

  function toggleSnapToGrid() {
    snapToGrid.value = !snapToGrid.value
  }

  // ── Pending changes tracking ────────────────────────────────────────────────

  function markUnsaved() {
    hasUnsavedChanges.value = true
  }

  function clearPendingChanges() {
    hasUnsavedChanges.value = false
    pendingConceptOperations.value = []
    pendingPropertyOperations.value = []
    pendingDiagramOperations.value = []
  }

  function queueConceptOperation(op: ConceptBatchOperation) {
    // Remove any existing operation for the same ID to avoid duplicates
    pendingConceptOperations.value = pendingConceptOperations.value.filter(
      existing => existing.id !== op.id
    )
    pendingConceptOperations.value.push(op)
    markUnsaved()
  }

  function queuePropertyOperation(op: PropertyBatchOperation) {
    pendingPropertyOperations.value = pendingPropertyOperations.value.filter(
      existing => existing.id !== op.id
    )
    pendingPropertyOperations.value.push(op)
    markUnsaved()
  }

  function queueDiagramOperation(op: DiagramBatchOperation) {
    pendingDiagramOperations.value = pendingDiagramOperations.value.filter(
      existing => existing.id !== op.id
    )
    pendingDiagramOperations.value.push(op)
    markUnsaved()
  }

  async function saveAllChanges(): Promise<boolean> {
    if (!activeDomainId.value) return false
    if (!hasUnsavedChanges.value) return true

    isSaving.value = true
    error.value = null

    try {
      const payload: OntologyBatchPayload = {
        concepts: pendingConceptOperations.value,
        properties: pendingPropertyOperations.value,
        diagrams: pendingDiagramOperations.value,
      }

      const result = await ontologyApi.saveOntologyBatch(activeDomainId.value, payload)

      if (result.success) {
        clearPendingChanges()
        // Reload to ensure consistency
        await loadForDomain(activeDomainId.value)
        return true
      } else {
        error.value = result.errors.join(', ')
        return false
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to save changes'
      return false
    } finally {
      isSaving.value = false
    }
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
    hasUnsavedChanges,
    pendingConceptOperations,
    pendingPropertyOperations,
    pendingDiagramOperations,
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
    updateDatatypeAttribute,
    deleteDatatypeAttribute,
    removeNodesFromCanvas,
    removeEdgesFromCanvas,
    createProperty,
    selectElement,
    openCreatePanel,
    closePanel,
    panelMode,
    pendingClassPosition,
    toggleSnapToGrid,
    saveAllChanges,
    clearPendingChanges,
    markUnsaved,
    reset,
  }
})
