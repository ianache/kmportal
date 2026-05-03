import { ref, reactive } from 'vue'
import { io, Socket } from 'socket.io-client'
import type { InjectionKey } from 'vue'

export interface IngestionEvent {
  type: 'ingestion.pending' | 'ingestion.processing' | 'ingestion.done' | 'ingestion.failed'
  job_id: string
  document_id: string
  domain_id: string
  status: 'pending' | 'processing' | 'done' | 'failed'
  progress: number
  message: string
  timestamp: string
  error?: string
}

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: Date
  read: boolean
}

class WebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  
  public isConnected = ref(false)
  public isConnecting = ref(false)
  public notifications = reactive<Notification[]>([])
  public unreadCount = ref(0)
  
  private listeners: Map<string, Set<(data: any) => void>> = new Map()

  connect(url: string = 'http://localhost:3000') {
    if (this.socket?.connected) {
      console.log('WebSocket already connected')
      return
    }
    
    if (this.isConnecting.value) {
      console.log('WebSocket already connecting')
      return
    }
    
    this.isConnecting.value = true
    
    this.socket = io(url, {
      path: '/ws',
      transports: ['websocket', 'polling'],
      withCredentials: true,
      autoConnect: true,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.isConnected.value = true
      this.isConnecting.value = false
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.isConnected.value = false
      this.isConnecting.value = false
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.isConnecting.value = false
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached')
        this.socket?.disconnect()
      }
    })

    // Listen for ingestion events
    this.socket.on('ingestion:update', (event: IngestionEvent) => {
      this.handleIngestionEvent(event)
      this.emit('ingestion:update', event)
    })

    this.socket.on('ingestion:complete', (event: IngestionEvent) => {
      this.addNotification({
        id: `ingestion-${event.job_id}`,
        type: 'success',
        title: 'Ingestion Complete',
        message: `Document "${event.document_id}" has been successfully ingested`,
        timestamp: new Date(),
        read: false,
      })
      this.emit('ingestion:complete', event)
    })

    this.socket.on('ingestion:error', (event: IngestionEvent) => {
      this.addNotification({
        id: `ingestion-${event.job_id}`,
        type: 'error',
        title: 'Ingestion Failed',
        message: event.error || `Failed to ingest document "${event.document_id}"`,
        timestamp: new Date(),
        read: false,
      })
      this.emit('ingestion:error', event)
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.isConnected.value = false
      this.isConnecting.value = false
    }
  }

  subscribe(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)?.add(callback)
    
    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback)
    }
  }

  private emit(event: string, data: any) {
    this.listeners.get(event)?.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error(`Error in ${event} listener:`, error)
      }
    })
  }

  private handleIngestionEvent(event: IngestionEvent) {
    // Could add progress indicators here
    console.log('Ingestion event:', event)
  }

  private addNotification(notification: Notification) {
    this.notifications.unshift(notification)
    this.unreadCount.value++
    
    // Keep only last 50 notifications
    if (this.notifications.length > 50) {
      this.notifications.pop()
    }
  }

  markAllAsRead() {
    this.notifications.forEach(n => n.read = true)
    this.unreadCount.value = 0
  }

  markAsRead(notificationId: string) {
    const notification = this.notifications.find(n => n.id === notificationId)
    if (notification && !notification.read) {
      notification.read = true
      this.unreadCount.value = Math.max(0, this.unreadCount.value - 1)
    }
  }

  clearNotifications() {
    this.notifications.length = 0
    this.unreadCount.value = 0
  }

  // Subscribe to a specific domain room
  subscribeToDomain(domainId: string) {
    if (this.socket?.connected) {
      this.socket.emit('subscribe', { room: `domain:${domainId}` })
    }
  }

  unsubscribeFromDomain(domainId: string) {
    if (this.socket?.connected) {
      this.socket.emit('unsubscribe', { room: `domain:${domainId}` })
    }
  }
}

export const wsService = new WebSocketService()
export const WebSocketKey: InjectionKey<WebSocketService> = Symbol('websocket')
export default wsService
