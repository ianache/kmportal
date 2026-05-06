# REPORTE DE PRUEBAS FUNCIONALES - SISTEMA DE AUTENTICACIÓN

**Fecha:** 2026-05-05  
**Usuario de Prueba:** kmuser@comsatel.com.pe  
**Password:** welcome1  
**Estado:** ✅ CONFIGURACIÓN COMPLETADA - LISTO PARA PRUEBAS

---

## 📊 RESUMEN EJECUTIVO

Se han realizado correcciones exhaustivas en el sistema de autenticación para resolver el problema de redirección continua a login después de autenticar correctamente en Keycloak.

### ✅ Correcciones Aplicadas

#### 1. Backend (BFF) - Configuración de Cookies
**Archivo:** `bff/src/middleware/session.ts`

```typescript
cookie: {
  secure: false,        // ✅ HTTP en desarrollo
  domain: undefined,    // ✅ Dominio actual (localhost)
  sameSite: 'lax',      // ✅ Permite cross-port
  httpOnly: true,
  maxAge: 604800000
}
```

**Impacto:** Permite que las cookies de sesión funcionen correctamente entre diferentes puertos (3000, 5100-5104) en localhost.

#### 2. Frontend (Shell) - URLs Relativas
**Archivos modificados:**
- `apps/shell/src/services/bffClient.ts` - Usa `baseUrl = ''`
- `apps/shell/src/stores/auth.ts` - Usa `fetch('/auth/session')`
- `apps/shell/src/services/websocket.ts` - URL relativa
- `apps/shell/src/main.ts` - WebSocket con URL vacía

**Impacto:** Todas las peticiones pasan por el proxy de Vite, manteniendo cookies de mismo origen.

#### 3. Micro-frontends - Fallback de bffClient
**Archivos modificados:**
- `apps/search-ui/src/services/searchApi.ts`
- `apps/domains-ui/src/services/domainsApi.ts`
- `apps/ingestion-ui/src/services/ingestionApi.ts`

**Impacto:** Si `window.__SHELL_BFF_CLIENT__` no está disponible, usan fetch directo con URLs relativas.

#### 4. CORS Configurado
**Archivos:** Todos los `vite.config.ts` de micro-frontends

```typescript
server: {
  cors: {
    origin: ['http://localhost:5100'],
    credentials: true
  }
}
```

**Impacto:** Permite que el shell cargue los micro-frontends desde diferentes puertos.

#### 5. WebSocket - Parseo de Cookie
**Archivo:** `bff/src/websocket/server.ts`

Corregido el parseo del session ID de cookies firmadas (formato `s:<sessionId>.<signature>`).

---

## 🧪 PLAN DE PRUEBAS

### Pre-requisitos
1. Redis ejecutándose en `localhost:6379`
2. BFF configurado con variables de entorno correctas
3. Todos los servicios iniciados

### Instrucciones de Ejecución

#### Paso 1: Limpiar Cookies
- Chrome DevTools (F12) → Application → Cookies → localhost → Clear All
- O ejecutar: `document.cookie.split(";").forEach(c => document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"))`

#### Paso 2: Iniciar Servicios
**Terminal 1 - BFF (3000):**
```bash
cd bff
npm run dev
```

**Terminal 2 - Shell (5100):**
```bash
cd frontend/apps/shell
npm run dev
```

**Terminal 3 - Search UI (5103):**
```bash
cd frontend/apps/search-ui
npm run dev
```

**Terminal 4 - Domains UI (5101):**
```bash
cd frontend/apps/domains-ui
npm run dev
```

**Terminal 5 - Ingestion UI (5102):**
```bash
cd frontend/apps/ingestion-ui
npm run dev
```

**Terminal 6 - Admin UI (5104):**
```bash
cd frontend/apps/admin-ui
npm run dev
```

#### Paso 3: Ejecutar Pruebas Playwright
```bash
cd frontend
npm install
npx playwright install chromium
npx playwright test
```

---

## 📋 CASOS DE PRUEBA

### TC-001: Login Exitoso
**Pasos:**
1. Navegar a `http://localhost:5100`
2. Click en "Sign In"
3. Ingresar `kmuser@comsatel.com.pe` / `welcome1`
4. Click en Sign In de Keycloak

**Resultado Esperado:**
- Redirige a `/auth/callback?success=true`
- Muestra "Welcome! Authentication successful. Redirecting..."
- Redirige a `/search`
- Muestra email del usuario en sidebar

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

---

### TC-002: Persistencia de Sesión
**Pasos:**
1. Realizar login exitoso
2. Navegar a `/domains`
3. Navegar a `/ingestion`
4. Navegar a `/search`

**Resultado Esperado:**
- Todas las páginas cargan sin error 401
- Usuario permanece autenticado
- Cookie `bff.sid` presente en todas las peticiones

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

---

### TC-003: Control de Acceso por Rol
**Pasos:**
1. Realizar login con usuario KM_ADMIN
2. Intentar acceder a `/admin`

**Resultado Esperado:**
- Si tiene rol KM_ADMIN: Carga página Admin
- Si no tiene rol: Redirige a `/search`

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

---

### TC-004: APIs Protegidas
**Pasos:**
1. Sin iniciar sesión, navegar a `http://localhost:5100`
2. Intentar acceder a `/api/v1/domains`

**Resultado Esperado:**
- Retorna HTTP 401 Unauthorized
- Mensaje: "Please log in to continue"

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

---

### TC-005: Logout
**Pasos:**
1. Realizar login exitoso
2. Click en logout (user row en sidebar)
3. Intentar acceder a `/search`

**Resultado Esperado:**
- Redirige a página de login
- Cookie `bff.sid` eliminada
- Acceso denegado a rutas protegidas

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

---

### TC-006: Cookie de Sesión
**Pasos:**
1. Realizar login exitoso
2. Verificar cookies en DevTools

**Resultado Esperado:**
- Cookie `bff.sid` presente
- `httpOnly: true`
- `domain: localhost`
- `path: /`
- `sameSite: Lax`

**Estado:** ⏳ PENDIENTE DE EJECUCIÓN

---

## 🔧 CONFIGURACIÓN VERIFICADA

### BFF (.env)
```env
NODE_ENV=development
PORT=3000
FRONTEND_URL=http://localhost:5100
CORS_ORIGINS=http://localhost:5100
COOKIE_DOMAIN=localhost
COOKIE_SECURE=false
SESSION_SECRET=dev-session-secret-knowledge-mgmt-2025-local
REDIS_URL=redis://localhost:6379
KEYCLOAK_URL=https://oauth2.qa.comsatel.com.pe
KEYCLOAK_REALM=Apps
KEYCLOAK_CLIENT_ID=kmplatform
```

### Shell (vite.config.ts)
```typescript
proxy: {
  '/api': { target: 'http://localhost:3000', changeOrigin: true },
  '/auth': { target: 'http://localhost:3000', changeOrigin: true },
  '/ws': { target: 'http://localhost:3000', ws: true, changeOrigin: true }
}
```

---

## 📈 RESULTADOS ESPERADOS

### Métricas de Éxito
- ✅ Login exitoso: < 5 segundos
- ✅ Navegación post-login: Sin errores 401
- ✅ Persistencia de sesión: > 30 minutos
- ✅ Logout: Limpieza completa de cookies

### Criterios de Aceptación
1. Usuario puede autenticar en Keycloak
2. Sesión se establece correctamente
3. Usuario navega entre todas las páginas según su rol
4. APIs protegidas retornan 401 sin sesión
5. WebSocket conecta con sesión válida

---

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar Pruebas Manuales:**
   - Seguir instrucciones del archivo `EJECUTAR_PRUEBAS.bat`
   - Documentar resultados

2. **Ejecutar Pruebas Automatizadas:**
   ```bash
   cd frontend
   npx playwright test
   ```

3. **Verificar Reporte:**
   - Abrir `frontend/playwright-report/index.html`

---

## 📞 NOTAS

- Las correcciones están basadas en el análisis del flujo de autenticación OAuth2 + Session Cookies
- El problema principal era la configuración de cookies que impedía el funcionamiento cross-port
- Se implementó fallback en micro-frontends para mayor robustez

**Reporte generado por:** OpenCode Agent  
**Fecha de generación:** 2026-05-05
