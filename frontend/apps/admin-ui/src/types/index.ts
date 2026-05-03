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

// ==================== Domain Types (for dropdown) ====================

export interface Domain {
  id: string
  name: string
  description: string | null
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
