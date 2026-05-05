import { bffClient } from 'shell/bffClient'
import type { 
  IngestionJob, 
  JobListResponse, 
  IngestionResponse,
  JobFilters 
} from '../types/ingestion'

class IngestionApiClient {
  async getJobs(filters: JobFilters = {}): Promise<JobListResponse> {
    const params = new URLSearchParams()
    if (filters.domain_id) params.append('domain_id', filters.domain_id)
    if (filters.status) params.append('status', filters.status)

    const response = await bffClient.get<JobListResponse>(`/v1/ingest/jobs?${params.toString()}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    return response.data || { items: [], total: 0 }
  }

  async getJob(jobId: string): Promise<IngestionJob> {
    const response = await bffClient.get<IngestionJob>(`/v1/ingest/${jobId}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    if (!response.data) {
      throw new Error('Job not found')
    }
    
    return response.data
  }

  async uploadDocument(domainId: string, file: File): Promise<IngestionResponse> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('domain_id', domainId)

    // Using fetch directly because bffClient.post stringifies body
    const response = await fetch(`${import.meta.env.VITE_BFF_URL || 'http://localhost:3000'}/api/v1/ingest`, {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })

    if (!response.ok) {
      // FastAPI error shape: { detail: string } — fall back to generic message
      const body = await response.json().catch(() => ({}))
      const msg = body.detail || body.message || `Upload failed (${response.status})`
      throw new Error(msg)
    }

    return response.json()
  }

  async retryJob(jobId: string): Promise<void> {
    const response = await bffClient.post<void>(`/v1/ingest/${jobId}/retry`, {})
    if (response.error) {
      throw new Error(response.error.message)
    }
  }

  async getDomains(): Promise<any[]> {
    const response = await bffClient.get<any>('/v1/domains')
    if (response.error) {
      throw new Error(response.error.message)
    }
    return response.data?.items || []
  }
}

export const ingestionApi = new IngestionApiClient()
export default ingestionApi
