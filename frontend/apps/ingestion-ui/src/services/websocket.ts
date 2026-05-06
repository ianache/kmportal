import { io, Socket } from 'socket.io-client'
import { ref, type InjectionKey } from 'vue'
import type { WebSocketEvent } from '../types/ingestion'

// Re-export the injection key so App.vue can use it for inject() even when
// the shell alias resolves to this file in standalone dev mode.
export interface WebSocketService {
  status: ReturnType<typeof ref<string>>
  isConnected?: ReturnType<typeof ref<boolean>>
  authFailed?: ReturnType<typeof ref<boolean>>
  connect(url?: string): void
  disconnect(): void
  on(event: string, callback: (data: any) => void): void
  off(event: string, callback: (data: any) => void): void
  emit(event: string, data: any): void
}
export const WebSocketKey: InjectionKey<WebSocketService> = Symbol('WebSocket')

// Use relative URL to go through shell's proxy
const WS_URL = ''

class WebSocketClient {
  private socket: Socket | null = null
  public status = ref<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')

  connect() {
    if (this.socket?.connected) return

    this.status.value = 'connecting'
    
    this.socket = io(WS_URL, {
      path: '/ws',
      withCredentials: true,
      transports: ['websocket', 'polling']
    })

    this.socket.on('connect', () => {
      this.status.value = 'connected'
      console.log('WS Connected')
      this.socket?.emit('subscribe', { room: 'ingestion' })
    })

    this.socket.on('disconnect', () => {
      this.status.value = 'disconnected'
      console.log('WS Disconnected')
    })

    this.socket.on('connect_error', (error) => {
      this.status.value = 'error'
      console.error('WS Connection Error:', error)
    })
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
    this.status.value = 'disconnected'
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

export const wsClient = new WebSocketClient()

export function useWebSocket() {
  return {
    wsClient,
    status: wsClient.status
  }
}
