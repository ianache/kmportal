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

export const XSD_TYPES = [
  { label: 'string',   uri: 'http://www.w3.org/2001/XMLSchema#string' },
  { label: 'integer',  uri: 'http://www.w3.org/2001/XMLSchema#integer' },
  { label: 'decimal',  uri: 'http://www.w3.org/2001/XMLSchema#decimal' },
  { label: 'float',    uri: 'http://www.w3.org/2001/XMLSchema#float' },
  { label: 'boolean',  uri: 'http://www.w3.org/2001/XMLSchema#boolean' },
  { label: 'date',     uri: 'http://www.w3.org/2001/XMLSchema#date' },
  { label: 'dateTime', uri: 'http://www.w3.org/2001/XMLSchema#dateTime' },
  { label: 'anyURI',   uri: 'http://www.w3.org/2001/XMLSchema#anyURI' },
] as const

export type XsdTypeUri = typeof XSD_TYPES[number]['uri']

export function xsdLabel(uri: string): string {
  return uri.replace('http://www.w3.org/2001/XMLSchema#', 'xsd:')
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

export interface PropertyUpdatePayload {
  label?: string
  target_class_id?: string
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
