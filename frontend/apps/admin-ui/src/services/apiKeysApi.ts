/**
 * API Key API service
 * Connects to Core API via BFF proxy
 */

import type { APIKey, APIKeyCreate, APIKeyCreateResponse, APIKeyListResponse } from '../types'

const API_BASE = '/api/v1'

export class ApiKeyError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: Response
  ) {
    super(message)
    this.name = 'ApiKeyError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ApiKeyError(
      errorData.detail || `HTTP ${response.status}`,
      response.status,
      response
    )
  }
  return response.json()
}

export const apiKeysApi = {
  /**
   * Create a new API key
   */
  async createApiKey(data: APIKeyCreate): Promise<APIKeyCreateResponse> {
    const response = await fetch(`${API_BASE}/api-keys`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(data),
    })

    return handleResponse<APIKeyCreateResponse>(response)
  },

  /**
   * List all API keys
   */
  async listApiKeys(page: number = 1, pageSize: number = 20): Promise<APIKeyListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })

    const response = await fetch(`${API_BASE}/api-keys?${params}`, {
      method: 'GET',
      credentials: 'include',
    })

    return handleResponse<APIKeyListResponse>(response)
  },

  /**
   * Get a specific API key
   */
  async getApiKey(id: string): Promise<APIKey> {
    const response = await fetch(`${API_BASE}/api-keys/${id}`, {
      method: 'GET',
      credentials: 'include',
    })

    return handleResponse<APIKey>(response)
  },

  /**
   * Revoke (delete) an API key
   */
  async revokeApiKey(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api-keys/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new ApiKeyError(
        errorData.detail || `HTTP ${response.status}`,
        response.status,
        response
      )
    }
  },
}

export default apiKeysApi
