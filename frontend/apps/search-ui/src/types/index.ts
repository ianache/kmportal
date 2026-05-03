export interface SearchResult {
  id: string
  document_id: string
  chunk_text: string
  score: number
  domain: string
  document_title: string
  document_type: string
  source: string
  created_at: string
  metadata?: Record<string, any>
}

export interface SearchFilters {
  domains?: string[]
  types?: string[]
  date_from?: string
  date_to?: string
  sources?: string[]
}

export interface SearchRequest {
  query: string
  domains?: string[]
  filters?: SearchFilters
  page?: number
  page_size?: number
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
  page: number
  page_size: number
  query: string
}

export interface Domain {
  id: string
  name: string
  description?: string
  document_count?: number
}
