import type { SearchRequest, SearchResponse, Domain } from '../types'

const BFF_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:3000'

interface DomainListResponse {
  items: Domain[]
  total: number
  page: number
  page_size: number
  pages: number
}

class SearchApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = BFF_URL
  }

  private async request<T>(
    method: string,
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`

    const response = await fetch(url, {
      method,
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }))
      throw new Error(error.message || error.error || `HTTP ${response.status}`)
    }

    return response.json()
  }

  async search(request: SearchRequest): Promise<SearchResponse> {
    const params = new URLSearchParams()
    params.append('q', request.query)
    
    if (request.domains?.length) {
      request.domains.forEach(d => params.append('domains', d))
    }
    
    if (request.filters?.types?.length) {
      request.filters.types.forEach(t => params.append('types', t))
    }
    
    if (request.filters?.date_from) {
      params.append('date_from', request.filters.date_from)
    }
    
    if (request.filters?.date_to) {
      params.append('date_to', request.filters.date_to)
    }
    
    if (request.page) {
      params.append('page', request.page.toString())
    }
    
    if (request.page_size) {
      params.append('page_size', request.page_size.toString())
    }

    return this.request<SearchResponse>('GET', `/api/v1/search?${params.toString()}`)
  }

  async getDomains(): Promise<Domain[]> {
    const data = await this.request<DomainListResponse>('GET', '/api/v1/domains')
    return data.items
  }

  async getSuggestions(query: string): Promise<string[]> {
    const params = new URLSearchParams({ q: query })
    return this.request<string[]>('GET', `/api/v1/search/suggest?${params.toString()}`)
  }
}

export const searchApi = new SearchApiClient()
export default searchApi
