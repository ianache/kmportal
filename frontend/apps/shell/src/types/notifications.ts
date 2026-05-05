export type NotificationType = 'success' | 'error' | 'info' | 'warning'
export type NotificationSource = 'ingestion' | 'system'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  source: NotificationSource
  domainId?: string
  metadata?: {
    jobId?: string
    documentId?: string
    route?: string
  }
  read: boolean
  createdAt: string
  expiresAt?: string
}
