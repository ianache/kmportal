---
type: concept
name: 08-01-PLAN.md
created: 2026-05-03T11:15:00Z
updated: 2026-05-03T11:15:00Z
confidence: 0.90
---

# Plan 08-01: Admin UI with API Key Management

## Goal
Implement the Admin micro-UI with real API key lifecycle management, connecting to the Core API endpoints.

## Background
The Core API already has API key endpoints (`/v1/api-keys`) implemented with full CRUD operations. The admin-ui currently uses mock data and needs to be connected to the real API.

## Implementation Steps

### 1. Types (`types/index.ts`)
Define TypeScript interfaces matching the API schemas:
- `APIKey` - API key metadata (without the plain key)
- `APIKeyCreate` - Creation request payload
- `APIKeyCreateResponse` - Response with the plain key (shown once)
- `APIKeyListResponse` - Paginated list response
- `SettingSection`, `SettingItem` - UI types for settings panels

### 2. API Service (`services/apiKeysApi.ts`)
Create API client for BFF endpoints:
- `createApiKey(data)` - POST /api/v1/api-keys
- `listApiKeys(page, pageSize)` - GET /api/v1/api-keys
- `getApiKey(id)` - GET /api/v1/api-keys/{id}
- `revokeApiKey(id)` - DELETE /api/v1/api-keys/{id}
- Error handling with `ApiKeyError` class

### 3. Pinia Store (`stores/admin.ts`)
State management for admin features:
- State: `apiKeys`, `totalApiKeys`, `isLoading`, `error`, `newlyCreatedKey`
- Getters: `activeApiKeys`, `revokedApiKeys`, `totalPages`
- Actions: `loadApiKeys`, `createApiKey`, `revokeApiKey`
- Track newly created key for one-time display

### 4. UI Components in App.vue
Full-featured API key management interface:
- Stats cards showing active/total API keys
- API Keys section in settings grid with live badge count
- List view with pagination
- Create key modal with form (name, scopes, rate limit, expiry)
- One-time key display with copy button after creation
- Revoke confirmation modal
- Skeleton loading states
- Error handling with retry

## API Endpoints

```
POST   /api/v1/api-keys          - Create API key
GET    /api/v1/api-keys          - List API keys (paginated)
GET    /api/v1/api-keys/{id}     - Get API key details
DELETE /api/v1/api-keys/{id}     - Revoke API key
```

## UI Features

### Stats Row
- Active API Keys (count from store)
- Total API Keys (count from store)
- Storage Used (placeholder)
- Uptime (placeholder)

### API Keys Panel
- Create Key button
- Table/list of keys with:
  - Name, status badge (Active/Revoked)
  - Scopes, rate limit, creation date
  - Last used timestamp
  - Revoke button for active keys
- Pagination controls
- Empty state with illustration

### Create Key Modal
- Name input (required)
- Scopes checkboxes (read, write, admin)
- Rate limit dropdown (100/hr, 1K/hr, 10K/hr)
- Optional expiration datetime
- Submit/Cancel buttons

### Key Created View
- Warning banner: "Copy this key now. It won't be shown again!"
- Key displayed in monospace with copy button
- Done button to close

## Dependencies
- Pinia (already in package.json)
- Design tokens (copied from shell)

## Testing
- Build: `npm run build`
- Dev: `npm run dev` (port 5104)

## Success Criteria
- [x] Admin UI builds successfully
- [x] Can list API keys from backend
- [x] Can create new API keys
- [x] Plain key shown only once after creation
- [x] Can revoke API keys
- [x] Proper loading and error states
- [x] Responsive design matching Luminous Knowledge system
