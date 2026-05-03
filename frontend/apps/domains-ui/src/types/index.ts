export interface Domain {
  id: string
  name: string
  description: string | null
  owner_id: string
  created_at: string
  updated_at: string
  document_count?: number
  embedding_dimension?: number
}

export interface Document {
  id: string
  domain_id: string
  title: string
  source: string
  document_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
  metadata?: Record<string, any>
}

export interface CreateDomainRequest {
  name: string
  description?: string
}

export interface UpdateDomainRequest {
  name?: string
  description?: string
}
