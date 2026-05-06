// Servicio centralizado para comunicación entre shell y micro-frontends
// Expone el bffClient a través de postMessage para evitar problemas de CORS/cookies

import { bffClient } from './bffClient'

// Canal de comunicación seguro
const CHANNEL = 'km-shell-bridge'

// Inicializar listener para recibir peticiones de micro-frontends
export function initShellBridge() {
  if (typeof window === 'undefined') return

  window.addEventListener('message', async (event) => {
    // Verificar origen (solo aceptar de localhost)
    if (!event.origin.match(/^http://localhost:/​(510[1-9]|51[0-9][0-9])​$/)) {
      return
    }

    const { channel, id, type, path, body } = event.data
    
    if (channel !== CHANNEL) return

    try {
      let response
      
      switch (type) {
        case 'GET':
          response = await bffClient.get(path)
          break
        case 'POST':
          response = await bffClient.post(path, body)
          break
        case 'PUT':
          response = await bffClient.put(path, body)
          break
        case 'DELETE':
          response = await bffClient.delete(path)
          break
        default:
          throw new Error(`Unknown type: ${type}`)
      }

      // Responder al micro-frontend
      event.source?.postMessage({
        channel: CHANNEL,
        id,
        success: true,
        data: response
      }, { targetOrigin: event.origin })

    } catch (error) {
      event.source?.postMessage({
        channel: CHANNEL,
        id,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }, { targetOrigin: event.origin })
    }
  })

  console.log('[ShellBridge] Initialized')
}

// Para micro-frontends: Cliente que usa postMessage
export function createShellBridgeClient() {
  if (typeof window === 'undefined') {
    throw new Error('Shell bridge only works in browser')
  }

  const parent = window.parent
  if (parent === window) {
    throw new Error('Not running inside shell iframe')
  }

  let requestId = 0
  const pendingRequests = new Map()

  // Escuchar respuestas
  window.addEventListener('message', (event) => {
    if (event.data.channel !== CHANNEL) return
    
    const { id, success, data, error } = event.data
    const request = pendingRequests.get(id)
    
    if (request) {
      pendingRequests.delete(id)
      if (success) {
        request.resolve(data)
      } else {
        request.reject(new Error(error))
      }
    }
  })

  // Crear métodos del cliente
  const request = (type: string, path: string, body?: any): Promise<any> => {
    return new Promise((resolve, reject) => {
      const id = ++requestId
      pendingRequests.set(id, { resolve, reject })

      parent.postMessage({
        channel: CHANNEL,
        id,
        type,
        path,
        body
      }, '*')

      // Timeout de 10 segundos
      setTimeout(() => {
        if (pendingRequests.has(id)) {
          pendingRequests.delete(id)
          reject(new Error('Request timeout'))
        }
      }, 10000)
    })
  }

  return {
    get: (path: string) => request('GET', path),
    post: (path: string, body: any) => request('POST', path, body),
    put: (path: string, body: any) => request('PUT', path, body),
    delete: (path: string) => request('DELETE', path)
  }
}
