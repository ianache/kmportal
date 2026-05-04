export interface Domain {
  id: string
  name: string
  description?: string
  embedding_model: string
  embedding_dimension: number
  document_count: number
  created_by: string
  created_at: string
  updated_at: string
}

export interface Document {
  id: string
  title: string
  domain_id: string
  source_type: string
  source_uri?: string
  status: 'pending' | 'processing' | 'done' | 'failed'
  chunk_count: number
  error_message?: string
  created_at: string
  updated_at: string
  metadata: {
    content_type?: string
    original_filename?: string
    size_bytes?: number
    [key: string]: any
  }
}

export interface DomainListResponse {
  items: Domain[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface DocumentListResponse {
  items: Document[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface DocumentFilters {
  status?: string
  type?: string
  query?: string
}
