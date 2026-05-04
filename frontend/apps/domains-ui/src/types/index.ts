export interface Domain {
  id: string
  name: string
  description: string | null
  name_en?: string | null
  description_en?: string | null
  tags?: string[]
  visibility?: 'public' | 'private'
  cover_image?: string | null
  embedding_model?: string
  embedding_dimension?: number
  created_by?: string
  created_at: string
  updated_at: string
  document_count?: number
}

export interface Document {
  id: string
  domain_id: string
  title: string
  source_type: string
  document_type?: string
  status: 'pending' | 'processing' | 'done' | 'failed'
  chunk_count?: number
  created_at: string
  updated_at: string
  metadata?: Record<string, any>
}

export interface CreateDomainRequest {
  name: string
  description?: string
  name_en?: string
  description_en?: string
  tags?: string[]
  visibility?: 'public' | 'private'
  cover_image?: string
  ingestion_flow?: string
}

export interface UpdateDomainRequest {
  name?: string
  description?: string
  name_en?: string
  description_en?: string
  tags?: string[]
  visibility?: 'public' | 'private'
  cover_image?: string
}
