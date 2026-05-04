import { bffClient } from 'shell/bffClient'
import type { 
  Domain, 
  DomainListResponse, 
  DocumentListResponse, 
  DocumentFilters 
} from '../types/domains'

class DomainsApiClient {
  async getDomains(page = 1, pageSize = 20): Promise<DomainListResponse> {
    const response = await bffClient.get<DomainListResponse>(
      `/v1/domains?page=${page}&page_size=${pageSize}`
    )
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from domains API')
    }
    
    return response.data
  }

  async getDomain(id: string): Promise<Domain> {
    const response = await bffClient.get<Domain>(`/v1/domains/${id}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from domain API')
    }
    
    return response.data
  }

  async getDomainDocuments(
    domainId: string, 
    page = 1, 
    pageSize = 20,
    filters: DocumentFilters = {}
  ): Promise<DocumentListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString()
    })
    
    if (filters.status) params.append('status', filters.status)
    if (filters.type) params.append('type', filters.type)
    if (filters.query) params.append('q', filters.query)

    const response = await bffClient.get<DocumentListResponse>(
      `/v1/domains/${domainId}/documents?${params.toString()}`
    )
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from documents API')
    }
    
    return response.data
  }
}

export const domainsApi = new DomainsApiClient()
export default domainsApi
