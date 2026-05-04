import type { Domain, Document, CreateDomainRequest, UpdateDomainRequest } from '../types'

const BFF_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:3000'

interface DomainListResponse {
  items: Domain[]
  total: number
  page: number
  page_size: number
  pages: number
}

class DomainsApiClient {
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

  async getDomains(): Promise<Domain[]> {
    const data = await this.request<DomainListResponse>('GET', '/api/v1/domains')
    return data.items
  }

  async getDomain(id: string): Promise<Domain> {
    return this.request<Domain>('GET', `/api/v1/domains/${id}`)
  }

  async createDomain(data: CreateDomainRequest): Promise<Domain> {
    return this.request<Domain>('POST', '/api/v1/domains', {
      body: JSON.stringify(data)
    })
  }

  async updateDomain(id: string, data: UpdateDomainRequest): Promise<Domain> {
    return this.request<Domain>('PUT', `/api/v1/domains/${id}`, {
      body: JSON.stringify(data)
    })
  }

  async deleteDomain(id: string): Promise<void> {
    return this.request<void>('DELETE', `/api/v1/domains/${id}`)
  }

  async getDomainDocuments(domainId: string): Promise<Document[]> {
    return this.request<Document[]>('GET', `/api/v1/domains/${domainId}/documents`)
  }
}

export const domainsApi = new DomainsApiClient()
export default domainsApi
