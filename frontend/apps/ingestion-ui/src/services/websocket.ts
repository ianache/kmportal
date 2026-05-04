import { io, Socket } from 'socket.io-client'
import { ref } from 'vue'
import type { WebSocketEvent } from '../types/ingestion'

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:3000'

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
}

export const wsClient = new WebSocketClient()

export function useWebSocket() {
  return {
    wsClient,
    status: wsClient.status
  }
}
