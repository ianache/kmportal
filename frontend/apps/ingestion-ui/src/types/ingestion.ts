export interface IngestionJob {
  id: string
  document_id: string
  domain_id: string
  status: 'pending' | 'processing' | 'done' | 'failed'
  progress: number
  started_at?: string
  completed_at?: string
  error_message?: string
  created_at: string
}

export interface JobListResponse {
  items: IngestionJob[]
  total: number
}

export interface IngestionResponse {
  job_id: string
  document_id: string
  status: string
}

export interface JobFilters {
  domain_id?: string
  status?: string
}

export type JobStatus = IngestionJob['status']

export interface WebSocketEvent {
  type: string
  jobId: string
  documentId?: string
  domainId?: string
  status?: JobStatus
  progress?: number
  message?: string
  error?: string
}
