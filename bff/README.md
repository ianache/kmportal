# Knowledge Management Center - BFF (Backend-for-Frontend)

Node.js Express-based BFF layer that proxies authentication via Keycloak OAuth2, exposes REST endpoints to the frontend, handles WebSocket communication, and provides Redis caching.

## Architecture

```
Frontend (Vue 3) <--HttpOnly Cookie--> BFF (Node.js/Express) <--JWT--> Core API (FastAPI)
                                           |
                                           v
                                      Redis (Sessions)
                                           |
                                           v
                                      Keycloak (OAuth2)
```

## Security Model

- **HttpOnly Session Cookies**: Frontend receives only a session cookie, never the JWT
- **Server-Side Token Storage**: Access and refresh tokens stored in Redis, accessible only server-side
- **Automatic Token Refresh**: BFF handles token refresh transparently when access tokens expire
- **CSRF Protection**: OAuth2 state parameter validates callback requests

## Quick Start

### Prerequisites

- Node.js 22 LTS
- Redis running (via Docker Compose)
- Keycloak configured with a client

### Installation

```bash
cd bff
npm install
```

### Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `KEYCLOAK_URL` - Keycloak server URL
- `KEYCLOAK_REALM` - Keycloak realm name
- `KEYCLOAK_CLIENT_ID` - Client ID
- `KEYCLOAK_CLIENT_SECRET` - Client secret
- `SESSION_SECRET` - Random secret for session encryption (generate with `openssl rand -base64 32`)

### Development

```bash
npm run dev
```

Server starts on http://localhost:3000

### Production Build

```bash
npm run build
npm start
```

### Docker Build

```bash
docker build -t knowledge-management-bff .
docker run -p 3000:3000 --env-file .env knowledge-management-bff
```

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Authentication
- `GET /auth/login` - Redirect to Keycloak login
- `GET /auth/callback` - OAuth2 callback handler
- `GET /auth/logout` - Logout and destroy session
- `GET /auth/session` - Get current session info (authenticated)

### API Proxy (Protected)
- All `/api/*` routes require valid session
- Proxies requests to Core API with JWT authorization

## Authentication Flow

1. Frontend redirects to `/auth/login`
2. BFF redirects to Keycloak with OAuth2 authorization request
3. User authenticates with Keycloak
4. Keycloak redirects back to `/auth/callback` with authorization code
5. BFF exchanges code for tokens (access, refresh, ID)
6. Tokens stored in Redis session (server-side)
7. HttpOnly session cookie set in browser response
8. Frontend redirected back to application

## Session Management

- Sessions stored in Redis with 7-day TTL
- Session cookie is HttpOnly, Secure (in production), SameSite=lax
- Sessions automatically extended on activity
- Logout destroys session in Redis and clears cookie

## Keycloak Configuration

Required client settings:
- **Client ID**: `kmplatform` (or as configured)
- **Client Authenticator**: `Client ID and Secret`
- **Valid Redirect URIs**: `http://localhost:3000/auth/callback`
- **Web Origins**: `http://localhost:5173` (frontend URL)
- **Standard Flow Enabled**: Yes
- **Direct Access Grants Enabled**: No (use authorization code flow)

## Development Notes

- TypeScript strict mode enabled
- Hot reload with `ts-node-dev` in development
- Source maps generated for debugging
- All secrets must come from environment variables

## License

MIT
