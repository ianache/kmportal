import type { SearchParams, SearchResponse, Domain } from '../types/search'
import { createLazyApiClient } from 'shell/microFrontendApi'

interface DomainListResponse {
  items: Domain[]
  total: number
  page: number
  page_size: number
  pages: number
}

// Cliente API lazy - espera a que el shell esté listo
const apiClient = createLazyApiClient()

class SearchApiClient {
  async search(params: SearchParams): Promise<SearchResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('q', params.q)
    
    if (params.domains?.length) {
      params.domains.forEach(d => queryParams.append('domains', d))
    }
    
    if (params.type) queryParams.append('type', params.type)
    if (params.date_from) queryParams.append('date_from', params.date_from)
    if (params.date_to) queryParams.append('date_to', params.date_to)
    if (params.source) queryParams.append('source', params.source)
    if (params.mode) queryParams.append('mode', params.mode)
    if (params.top_k) queryParams.append('top_k', params.top_k.toString())
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.page_size) queryParams.append('page_size', params.page_size.toString())

    const response = await apiClient.get<SearchResponse>(`/v1/search?${queryParams.toString()}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from search API')
    }
    
    return response.data
  }

  async getDomains(): Promise<Domain[]> {
    const response = await apiClient.get<DomainListResponse>('/v1/domains')
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    return response.data?.items || []
  }

  async getSuggestions(query: string): Promise<string[]> {
    const queryParams = new URLSearchParams({ q: query })
    const response = await apiClient.get<string[]>(`/v1/search/suggest?${queryParams.toString()}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    return response.data || []
  }
}

export const searchApi = new SearchApiClient()
export default searchApi
