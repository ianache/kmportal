/**
 * Type definitions for Admin UI
 */

// ==================== API Key Types ====================

export interface APIKey {
  id: string
  name: string
  scopes: string[]
  domain_ids: string[]
  rate_limit: number
  created_at: string
  expires_at: string | null
  last_used_at: string | null
  is_active: boolean
}

export interface APIKeyCreate {
  name: string
  scopes: string[]
  domain_ids: string[]
  rate_limit: number
  expires_at?: string | null
}

export interface APIKeyCreateResponse extends APIKey {
  key: string // Only shown once on creation
}

export interface APIKeyListResponse {
  items: APIKey[]
  total: number
  page: number
  page_size: number
  pages: number
}

// ==================== Domain Types ====================

export interface Domain {
  id: string
  name: string
  description: string | null
  owner_id: string
  created_at: string
  updated_at: string
  document_count?: number
}

export interface DomainCreate {
  name: string
  description: string | null
}

export interface DomainUpdate {
  name?: string
  description?: string | null
}

export interface DomainListResponse {
  items: Domain[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface DomainAccess {
  id: string
  domain_id: string
  user_id: string
  role: 'admin' | 'reader'
  granted_at: string
}

export interface DomainAccessGrant {
  user_id: string
  role: 'admin' | 'reader'
}

export interface DomainAccessResponse extends DomainAccess {
  user?: { id: string; email: string; full_name?: string | null }
}

// ==================== Stats Types ====================

export interface AdminStats {
  active_users: number
  api_keys: number
  storage_used: string
  uptime: string
}

// ==================== UI Types ====================

export interface SettingItem {
  key: string
  name: string
  description: string
  type: 'toggle' | 'select' | 'text' | 'number'
  value: any
  options?: string[]
}

export interface SettingSection {
  id: string
  title: string
  description: string
  color: string
  items: number
  badge: string | null
  iconPath: string
  settingItems: SettingItem[]
}
