import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ingestionApi } from '../services/ingestionApi'
import type { IngestionJob, JobFilters, WebSocketEvent } from '../types/ingestion'

interface WsEventSource {
  on(event: string, cb: (data: any) => void): void
  off(event: string, cb: (data: any) => void): void
}

export const useIngestionStore = defineStore('ingestion', () => {
  // State
  const jobs = ref<IngestionJob[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const filters = ref<JobFilters>({
    domain_id: undefined,
    status: undefined
  })

  // Getters
  const activeJobs = computed(() => jobs.value.filter(j => j.status === 'processing'))
  const recentJobs = computed(() => [...jobs.value].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ))
  
  const stats = computed(() => {
    const s = { total: jobs.value.length, pending: 0, processing: 0, done: 0, failed: 0 }
    jobs.value.forEach(j => {
      if (j.status in s) (s as any)[j.status]++
    })
    return s
  })

  // Actions
  async function loadJobs() {
    isLoading.value = true
    error.value = null
    try {
      const response = await ingestionApi.getJobs(filters.value)
      jobs.value = response.items
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load jobs'
    } finally {
      isLoading.value = false
    }
  }

  function _onJobCreated(event: WebSocketEvent) {
    jobs.value.unshift({
      id: event.jobId,
      document_id: event.documentId || '',
      domain_id: event.domainId || '',
      status: event.status || 'pending',
      progress: 0,
      created_at: new Date().toISOString()
    })
  }

  function _onJobUpdated(event: WebSocketEvent) {
    const index = jobs.value.findIndex(j => j.id === event.jobId)
    if (index !== -1) {
      if (event.status) jobs.value[index].status = event.status
      if (event.progress !== undefined) jobs.value[index].progress = event.progress
      if (event.message) jobs.value[index].error_message = event.message
    }
  }

  function _onJobCompleted(event: WebSocketEvent) {
    const index = jobs.value.findIndex(j => j.id === event.jobId)
    if (index !== -1) {
      jobs.value[index].status = 'done'
      jobs.value[index].progress = 100
      jobs.value[index].completed_at = new Date().toISOString()
    }
  }

  function _onJobFailed(event: WebSocketEvent) {
    const index = jobs.value.findIndex(j => j.id === event.jobId)
    if (index !== -1) {
      jobs.value[index].status = 'failed'
      jobs.value[index].error_message = event.error || event.message || 'Unknown error'
    }
  }

  function setupWebSocket(ws: WsEventSource) {
    ws.on('job:created', _onJobCreated)
    ws.on('job:updated', _onJobUpdated)
    ws.on('job:completed', _onJobCompleted)
    ws.on('job:failed', _onJobFailed)
  }

  function teardownWebSocket(ws: WsEventSource) {
    ws.off('job:created', _onJobCreated)
    ws.off('job:updated', _onJobUpdated)
    ws.off('job:completed', _onJobCompleted)
    ws.off('job:failed', _onJobFailed)
  }

  async function retryJob(jobId: string) {
    try {
      await ingestionApi.retryJob(jobId)
      // Status will update via WS
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Retry failed'
    }
  }

  function setFilter(key: keyof JobFilters, value: any) {
    filters.value[key] = value
    loadJobs()
  }

  return {
    jobs,
    isLoading,
    error,
    filters,
    activeJobs,
    recentJobs,
    stats,
    loadJobs,
    setupWebSocket,
    teardownWebSocket,
    retryJob,
    setFilter
  }
})
