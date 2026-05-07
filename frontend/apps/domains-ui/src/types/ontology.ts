export interface OntologyConcept {
  id: string
  domain_id: string
  uri: string
  label: string
  comment?: string
}

export interface OntologyProperty {
  id: string
  domain_id: string
  uri: string
  label: string
  property_type: 'ObjectProperty' | 'DatatypeProperty'
  source_class_id: string
  target_class_id: string
  comment?: string
}

export interface OntologyData {
  domain_id: string
  concepts: OntologyConcept[]
  properties: OntologyProperty[]
}

export interface DiagramNodePosition {
  x: number
  y: number
}

export interface DiagramNode {
  id: string
  concept_id: string
  position: DiagramNodePosition
  style?: Record<string, string>
}

export interface DiagramEdge {
  id: string
  property_id: string
  source: string
  target: string
  label?: string
  style?: Record<string, string>
}

export interface DiagramViewport {
  x: number
  y: number
  zoom: number
}

export interface Diagram {
  id: string
  domain_id: string
  name: string
  nodes: DiagramNode[]
  edges: DiagramEdge[]
  viewport: DiagramViewport
  created_at: string
  updated_at: string
}

export interface DiagramListResponse {
  items: Diagram[]
  total: number
}

export interface ConceptCreatePayload {
  uri: string
  label: string
  comment?: string
}

export interface PropertyCreatePayload {
  uri: string
  label: string
  property_type: 'ObjectProperty' | 'DatatypeProperty'
  source_class_id: string
  target_class_id: string
  comment?: string
}

export interface DiagramCreatePayload {
  name: string
}

export interface DiagramUpdatePayload {
  name?: string
  nodes?: DiagramNode[]
  edges?: DiagramEdge[]
  viewport?: DiagramViewport
}
