import type {
  IngestionJob,
  JobListResponse,
  IngestionResponse,
  JobFilters
} from '../types/ingestion'
import { createLazyApiClient } from 'shell/microFrontendApi'

const apiClient = createLazyApiClient()

export interface OWLClass {
  id: string
  label: string
  uri: string
}

export interface SemanticPayload {
  content: string
  metadata: {
    owl_class: string
    governance_level: string
    source_ref: string
  }
  graph_properties: Record<string, string>
}

export interface SemanticIngestionResponse {
  success: boolean
  link_id: string
}

class IngestionApiClient {
  async getJobs(filters: JobFilters = {}): Promise<JobListResponse> {
    const params = new URLSearchParams()
    if (filters.domain_id) params.append('domain_id', filters.domain_id)
    if (filters.status) params.append('status', filters.status)

    const response = await apiClient.get<JobListResponse>(`/v1/ingest/jobs?${params.toString()}`)
    
    if (response.error) {
      throw new Error(response.error.message)
    }
    
    return response.data || { items: [], total: 0 }
  }

  async getJob(jobId: string): Promise<IngestionJob> {
    const response = await apiClient.get<IngestionJob>(`/v1/ingest/${jobId}`)
    
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

    const response = await fetch('/api/v1/ingest', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })

    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      const msg = body.detail || body.message || `Upload failed (${response.status})`
      throw new Error(msg)
    }

    return response.json()
  }

  async retryJob(jobId: string): Promise<void> {
    const response = await apiClient.post<void>(`/v1/ingest/${jobId}/retry`, {})
    if (response.error) {
      throw new Error(response.error.message)
    }
  }

  async getDomains(): Promise<any[]> {
    const response = await apiClient.get<any>('/v1/domains')
    if (response.error) {
      throw new Error(response.error.message)
    }
    return response.data?.items || []
  }

  async extractFile(file: File): Promise<{ content: string; filename: string }> {
    const form = new FormData()
    form.append('file', file)
    const response = await fetch('/api/v1/ingest/extract', {
      method: 'POST',
      body: form,
      credentials: 'include'
    })
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      throw new Error(body.detail || `Extraction failed (${response.status})`)
    }
    return response.json()
  }

  async ingestVector(
    domainId: string,
    content: string,
    source: string
  ): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post<{ success: boolean; message: string }>(
      `/v1/ingest/vector?domain_id=${domainId}`,
      { content, metadata: { source, type: 'quick_rag' } }
    )
    if (response.error) throw new Error(response.error.message)
    return response.data!
  }

  async ingestSemantic(
    domainId: string,
    payload: SemanticPayload
  ): Promise<SemanticIngestionResponse> {
    const response = await apiClient.post<SemanticIngestionResponse>(
      `/v1/ingest/semantic?domain_id=${domainId}`,
      payload
    )
    if (response.error) throw new Error(response.error.message)
    return response.data!
  }

  async getOWLClasses(domainId: string): Promise<OWLClass[]> {
    const response = await apiClient.get<{ concepts: OWLClass[] }>(
      `/v1/domains/${domainId}/ontology`
    )
    if (response.error) throw new Error(response.error.message)
    return response.data?.concepts || []
  }
}

export const ingestionApi = new IngestionApiClient()
export default ingestionApi
