/**
 * API Key API service
 * Connects to Core API via BFF proxy
 */

import { createLazyApiClient } from 'shell/microFrontendApi'
import type { APIKey, APIKeyCreate, APIKeyCreateResponse, APIKeyListResponse } from '../types'

// Lazy API client - waits for shell to be ready
const apiClient = createLazyApiClient()

export const apiKeysApi = {
  /**
   * Create a new API key
   */
  async createApiKey(data: APIKeyCreate): Promise<APIKeyCreateResponse> {
    const response = await apiClient.post<APIKeyCreateResponse>('/v1/api-keys', data)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from API Key creation')
    }
    
    return response.data
  },

  /**
   * List all API keys
   */
  async listApiKeys(page: number = 1, pageSize: number = 20): Promise<APIKeyListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })

    const response = await apiClient.get<APIKeyListResponse>(`/v1/api-keys?${params}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from API Key list')
    }
    
    return response.data
  },

  /**
   * Get a specific API key
   */
  async getApiKey(id: string): Promise<APIKey> {
    const response = await apiClient.get<APIKey>(`/v1/api-keys/${id}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('No data received from API Key details')
    }
    
    return response.data
  },

  /**
   * Revoke (delete) an API key
   */
  async revokeApiKey(id: string): Promise<void> {
    const response = await apiClient.delete<void>(`/v1/api-keys/${id}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
  },
}

export default apiKeysApi
