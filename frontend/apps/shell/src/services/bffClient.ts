import type { InjectionKey } from 'vue'

const BFF_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:3000'

export interface ApiError {
  error: string
  message: string
  trace_id?: string
}

export interface ApiResponse<T> {
  data?: T
  error?: ApiError
  status: number
}

class BffClient {
  private baseUrl: string

  constructor() {
    // ALWAYS use relative URLs - requests go through shell's proxy
    this.baseUrl = ''
  }

  private async request<T>(
    method: string,
    path: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${path}`
    
    const config: RequestInit = {
      ...options,
      method,
      credentials: 'include', // CRITICAL: sends cookies
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)
      
      // Handle 401 Unauthorized
      if (response.status === 401) {
        // If we get a 401, it means the session is invalid or expired
        const errorMsg = 'Please log in to continue'
        
        // Notify via custom event so the shell can respond (e.g. redirect to login)
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('bff:unauthorized', { detail: { path } }))
        }

        return {
          status: 401,
          error: {
            error: 'Unauthorized',
            message: errorMsg,
          },
        }
      }

      // Try to parse JSON response — read text first to avoid parse error on empty bodies (e.g. 204 No Content)
      let data: T | undefined
      const contentType = response.headers.get('content-type')

      if (contentType?.includes('application/json')) {
        const text = await response.text()
        if (text) data = JSON.parse(text) as T
      }

      if (!response.ok) {
        const errorData = data as ApiError | undefined
        return {
          status: response.status,
          error: errorData || {
            error: 'Error',
            message: `HTTP ${response.status}`,
          },
        }
      }

      return {
        status: response.status,
        data,
      }
    } catch (err) {
      return {
        status: 0,
        error: {
          error: 'NetworkError',
          message: err instanceof Error ? err.message : 'Network request failed',
        },
      }
    }
  }

  // Auth endpoints
  async getSession() {
    return this.request<{ authenticated: boolean; user: { id: string; email: string; roles: string[] } }>(
      'GET',
      '/auth/session'
    )
  }

  // API proxy endpoints
  async get<T>(path: string, options?: RequestInit) {
    return this.request<T>('GET', `/api${path}`, options)
  }

  async post<T>(path: string, body: any, options?: RequestInit) {
    return this.request<T>('POST', `/api${path}`, {
      ...options,
      body: JSON.stringify(body),
    })
  }

  async put<T>(path: string, body: any, options?: RequestInit) {
    return this.request<T>('PUT', `/api${path}`, {
      ...options,
      body: JSON.stringify(body),
    })
  }

  async delete<T>(path: string, body?: any, options?: RequestInit) {
    if (body) {
      return this.request<T>('DELETE', `/api${path}`, {
        ...options,
        body: JSON.stringify(body),
      })
    }
    return this.request<T>('DELETE', `/api${path}`, options)
  }
}

// Export the class type for TypeScript
export type { BffClient }

// Injection key for provide/inject pattern
export const BffClientKey: InjectionKey<BffClient> = Symbol('BffClient')

export const bffClient = new BffClient()
export default bffClient

// Expose to window for micro-frontends
if (typeof window !== 'undefined') {
  (window as any).__SHELL_BFF_CLIENT__ = bffClient
  console.log('[Shell] BffClient exposed to window.__SHELL_BFF_CLIENT__')
}

// Also export for micro-frontend initialization
export { createLazyApiClient } from './microFrontendApi'
