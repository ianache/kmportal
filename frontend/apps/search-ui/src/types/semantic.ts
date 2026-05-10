export interface GraphNode {
  id: string
  label: string // OWL class name (e.g. Control_Seguridad)
  name: string
}

export interface GraphEdge {
  source: string
  target: string
  relation_type: string
}

export interface SemanticProvenance {
  owl_class: string
  iso_compliance: string
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface HybridSearchResult {
  link_id: string // UUID
  content: string
  score: number
  source_file: string
  provenance: SemanticProvenance
}
