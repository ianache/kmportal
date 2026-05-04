export interface SearchResult {
  chunk_id: string
  score: number
  text: string
  document_id: string
  document_title: string
  domain_id: string
  metadata: {
    type?: string
    source?: string
    created_at?: string
    [key: string]: any
  }
}

export interface SearchFilters {
  types?: string[]
  date_from?: string
  date_to?: string
  sources?: string[]
}

export interface SearchParams {
  q: string
  domains?: string[]
  mode?: 'semantic' | 'keyword' | 'hybrid'
  top_k?: number
  type?: string
  date_from?: string
  date_to?: string
  source?: string
  page?: number
  page_size?: number
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total: number
  search_time_ms: number
  page: number
  page_size: number
}

export interface Domain {
  id: string
  name: string
  description?: string
  document_count: number
}

export interface HighlightRange {
  start: number
  end: number
  term: string
}

export interface SearchState {
  query: string
  results: SearchResult[]
  filters: SearchFilters & { selectedDomains: string[] }
  loading: boolean
  error: string | null
  total: number
  searchTimeMs: number
  availableDomains: Domain[]
}
