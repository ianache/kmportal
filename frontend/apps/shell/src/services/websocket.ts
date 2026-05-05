import { io, Socket } from 'socket.io-client'
import { ref, type InjectionKey, type Ref } from 'vue'

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:3000'

export interface WebSocketService {
  isConnected: Ref<boolean>
  status: Ref<'connecting' | 'connected' | 'disconnected' | 'error'>
  authFailed: Ref<boolean>
  connect(url?: string): void
  disconnect(): void
  on(event: string, callback: (data: any) => void): void
  off(event: string, callback: (data: any) => void): void
  emit(event: string, data: any): void
}

export const WebSocketKey: InjectionKey<WebSocketService> = Symbol('WebSocket')

class ShellWebSocketClient implements WebSocketService {
  private socket: Socket | null = null
  private connectUrl: string | undefined = undefined
  private invalidSessionRetries = 0
  public status = ref<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  public isConnected = ref(false)
  public authFailed = ref(false)

  connect(url?: string) {
    if (this.socket?.connected) return

    this.connectUrl = url
    this.authFailed.value = false
    this.invalidSessionRetries = 0
    this.status.value = 'connecting'
    this._createSocket(url)
  }

  private _createSocket(url?: string, forceNew = false) {
    this.socket = io(url || WS_URL, {
      path: '/ws',
      withCredentials: true,
      transports: ['websocket', 'polling'],
      reconnection: false, // we handle reconnection manually
      forceNew,
    })

    this.socket.on('connect', () => {
      this.invalidSessionRetries = 0
      this.status.value = 'connected'
      this.isConnected.value = true
      console.log('Shell WS Connected')
      this.socket?.emit('subscribe', { room: 'notifications' })
    })

    this.socket.on('disconnect', () => {
      this.status.value = 'disconnected'
      this.isConnected.value = false
      console.log('Shell WS Disconnected')
    })

    this.socket.on('connect_error', (error) => {
      this.status.value = 'error'
      this.isConnected.value = false

      if (error.message === 'Invalid session') {
        this.socket?.disconnect()
        this.socket = null

        // Retry once with a fresh socket to cover the server-restart case where
        // the Socket.IO session is stale but the HTTP session cookie is still valid.
        // A second failure means the HTTP session itself is expired → stop and
        // signal the app so it can redirect to login.
        if (this.invalidSessionRetries === 0) {
          this.invalidSessionRetries++
          this._createSocket(this.connectUrl, true)
        } else {
          this.authFailed.value = true
          console.warn('Shell WS: session expired — re-authentication required')
        }
        return
      }

      console.error('Shell WS Connection Error:', error)
    })
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
    this.status.value = 'disconnected'
    this.isConnected.value = false
  }

  on(event: string, callback: (data: any) => void) {
    this.socket?.on(event, callback)
  }

  off(event: string, callback: (data: any) => void) {
    this.socket?.off(event, callback)
  }

  emit(event: string, data: any) {
    this.socket?.emit(event, data)
  }
}

export const wsService = new ShellWebSocketClient()

export function useShellWebSocket() {
  return {
    wsService,
    status: wsService.status,
    isConnected: wsService.isConnected,
    authFailed: wsService.authFailed,
  }
}
