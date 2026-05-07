/**
 * Domains API service
 * Connects to Core API via BFF proxy
 */

import { createLazyApiClient } from 'shell/microFrontendApi'
import type { 
  Domain, 
  DomainCreate, 
  DomainUpdate, 
  DomainListResponse,
  DomainAccessGrant,
  DomainAccessResponse
} from '../types'

// Lazy API client - waits for shell to be ready
const apiClient = createLazyApiClient()

export const domainsApi = {
  /**
   * Create a new domain
   */
  async createDomain(data: DomainCreate): Promise<Domain> {
    const response = await apiClient.post<Domain>('/v1/domains', data)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from domain creation')
    }
    
    return response.data
  },

  /**
   * List all domains
   */
  async listDomains(page: number = 1, pageSize: number = 20): Promise<DomainListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })

    const response = await apiClient.get<DomainListResponse>(`/v1/domains?${params}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from domain list')
    }
    
    return response.data
  },

  /**
   * Get a specific domain
   */
  async getDomain(id: string): Promise<Domain> {
    const response = await apiClient.get<Domain>(`/v1/domains/${id}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from domain details')
    }
    
    return response.data
  },

  /**
   * Update a domain
   */
  async updateDomain(id: string, data: DomainUpdate): Promise<Domain> {
    const response = await apiClient.put<Domain>(`/v1/domains/${id}`, data)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from domain update')
    }
    
    return response.data
  },

  /**
   * Delete a domain
   */
  async deleteDomain(id: string): Promise<void> {
    const response = await apiClient.delete<void>(`/v1/domains/${id}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
  },

  /**
   * Grant access to a domain
   */
  async grantAccess(domainId: string, data: DomainAccessGrant): Promise<DomainAccessResponse> {
    const response = await apiClient.post<DomainAccessResponse>(`/v1/domains/${domainId}/access`, data)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from access grant')
    }
    
    return response.data
  },

  /**
   * Revoke access from a domain
   */
  async revokeAccess(domainId: string, userId: string): Promise<void> {
    const response = await apiClient.delete<void>(`/v1/domains/${domainId}/access`, { user_id: userId } as any)
    // Note: The apiClient.delete might need adjustment if it doesn't support body.
    // The backend DELETE /v1/domains/{domain_id}/access expects DomainAccessRevoke schema in body.
    
    if (response.error) {
      throw new Error(response.error.message)
    }
  },

  /**
   * List all access grants for a domain
   */
  async listAccess(domainId: string): Promise<DomainAccessResponse[]> {
    const response = await apiClient.get<DomainAccessResponse[]>(`/v1/domains/${domainId}/access`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from access list')
    }
    
    return response.data
  }
}

export default domainsApi
