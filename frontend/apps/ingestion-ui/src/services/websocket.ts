import { ref, reactive } from 'vue'
import { io, Socket } from 'socket.io-client'

export interface IngestionJob {
  id: string
  documentId: string
  domainId: string
  filename: string
  status: 'pending' | 'processing' | 'done' | 'failed'
  progress: number
  message: string
  createdAt: string
  updatedAt: string
  error?: string
}

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

class IngestionWebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  
  public isConnected = ref(false)
  public isConnecting = ref(false)
  public jobs = reactive<Map<string, IngestionJob>>(new Map())
  
  private listeners: Map<string, Set<(data: any) => void>> = new Map()

  connect(url: string = 'http://localhost:3000') {
    if (this.socket?.connected || this.isConnecting.value) {
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
      console.log('[Ingestion WS] Connected')
      this.isConnected.value = true
      this.isConnecting.value = false
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', () => {
      console.log('[Ingestion WS] Disconnected')
      this.isConnected.value = false
      this.isConnecting.value = false
    })

    this.socket.on('connect_error', (error) => {
      console.error('[Ingestion WS] Connection error:', error)
      this.isConnecting.value = false
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.socket?.disconnect()
      }
    })

    // Listen for ingestion events
    this.socket.on('ingestion:pending', (event: IngestionEvent) => {
      this.updateJob(event)
      this.emit('job:pending', event)
    })

    this.socket.on('ingestion:processing', (event: IngestionEvent) => {
      this.updateJob(event)
      this.emit('job:processing', event)
    })

    this.socket.on('ingestion:done', (event: IngestionEvent) => {
      this.updateJob(event)
      this.emit('job:done', event)
    })

    this.socket.on('ingestion:failed', (event: IngestionEvent) => {
      this.updateJob(event)
      this.emit('job:failed', event)
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

  private updateJob(event: IngestionEvent) {
    const job: IngestionJob = {
      id: event.job_id,
      documentId: event.document_id,
      domainId: event.domain_id,
      filename: event.document_id, // Will be updated with real filename
      status: event.status,
      progress: event.progress,
      message: event.message,
      createdAt: event.timestamp,
      updatedAt: event.timestamp,
      error: event.error,
    }
    
    this.jobs.set(job.id, job)
  }

  subscribe(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)?.add(callback)
    
    return () => {
      this.listeners.get(event)?.delete(callback)
    }
  }

  private emit(event: string, data: any) {
    this.listeners.get(event)?.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error(`[Ingestion WS] Error in ${event} listener:`, error)
      }
    })
  }

  getJob(jobId: string): IngestionJob | undefined {
    return this.jobs.get(jobId)
  }

  getAllJobs(): IngestionJob[] {
    return Array.from(this.jobs.values()).sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  }

  getActiveJobs(): IngestionJob[] {
    return this.getAllJobs().filter(j => j.status === 'pending' || j.status === 'processing')
  }

  clearCompleted() {
    for (const [id, job] of this.jobs) {
      if (job.status === 'done' || job.status === 'failed') {
        this.jobs.delete(id)
      }
    }
  }
}

export const ingestionWsService = new IngestionWebSocketService()
export default ingestionWsService
