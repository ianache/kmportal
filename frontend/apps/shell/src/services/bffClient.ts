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
    this.baseUrl = BFF_URL
  }

  private async request<T>(
    method: string,
    path: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${path}`
    
    const config: RequestInit = {
      method,
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      // Handle 401 Unauthorized
      if (response.status === 401) {
        return {
          status: 401,
          error: {
            error: 'Unauthorized',
            message: 'Please log in to continue',
          },
        }
      }

      // Try to parse JSON response
      let data: T | undefined
      const contentType = response.headers.get('content-type')
      
      if (contentType?.includes('application/json')) {
        data = await response.json()
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

  async delete<T>(path: string, options?: RequestInit) {
    return this.request<T>('DELETE', `/api${path}`, options)
  }
}

export const bffClient = new BffClient()
export default bffClient
