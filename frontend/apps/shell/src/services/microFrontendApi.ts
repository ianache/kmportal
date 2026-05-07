// Sistema de inicialización para micro-frontends
// Asegura que el bffClient del shell esté disponible antes de hacer peticiones

interface BffClient {
  get<T>(path: string): Promise<{ status: number; data?: T; error?: { error: string; message: string } }>
  post<T>(path: string, body: any): Promise<{ status: number; data?: T; error?: { error: string; message: string } }>
  put<T>(path: string, body: any): Promise<{ status: number; data?: T; error?: { error: string; message: string } }>
  delete<T>(path: string, body?: any): Promise<{ status: number; data?: T; error?: { error: string; message: string } }>
}

// Esperar a que el shell exponga el bffClient
export async function waitForBffClient(maxAttempts = 50, interval = 100): Promise<BffClient> {
  return new Promise((resolve, reject) => {
    let attempts = 0
    
    const check = () => {
      attempts++
      
      if (typeof window !== 'undefined' && (window as any).__SHELL_BFF_CLIENT__) {
        console.log('[MicroFrontend] BffClient found after', attempts, 'attempts')
        resolve((window as any).__SHELL_BFF_CLIENT__)
        return
      }
      
      if (attempts >= maxAttempts) {
        reject(new Error('BffClient not available. Shell may not be loaded correctly.'))
        return
      }
      
      setTimeout(check, interval)
    }
    
    check()
  })
}

// Cliente API con inicialización lazy
export function createLazyApiClient() {
  let bffClient: BffClient | null = null
  let initPromise: Promise<BffClient> | null = null
  
  async function getClient(): Promise<BffClient> {
    if (bffClient) return bffClient
    
    if (!initPromise) {
      initPromise = waitForBffClient().then(client => {
        bffClient = client
        return client
      })
    }
    
    return initPromise
  }
  
  return {
    async get<T>(path: string): Promise<{ status: number; data?: T; error?: { error: string; message: string } }> {
      const client = await getClient()
      return client.get(path)
    },
    async post<T>(path: string, body: any): Promise<{ status: number; data?: T; error?: { error: string; message: string } }> {
      const client = await getClient()
      return client.post(path, body)
    },
    async put<T>(path: string, body: any): Promise<{ status: number; data?: T; error?: { error: string; message: string } }> {
      const client = await getClient()
      return client.put(path, body)
    },
    async delete<T>(path: string, body?: any): Promise<{ status: number; data?: T; error?: { error: string; message: string } }> {
      const client = await getClient()
      return client.delete(path, body)
    }
  }
}
