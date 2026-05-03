# Requirements: Knowledge Management Center

**Defined:** 2026-05-02
**Core Value:** Cualquier usuario autenticado puede encontrar conocimiento relevante dentro de los dominios autorizados en segundos, usando búsqueda semántica o híbrida sobre documentos indexados.

## v1 Requirements

### Infraestructura & Configuración

- [ ] **INFRA-01**: Monorepo con servicios independientes (api, ingestion, bff, frontend/shell, micro-uis)
- [ ] **INFRA-02**: Docker Compose con todos los servicios (PostgreSQL, MongoDB, ChromaDB, Redis, Kafka, RabbitMQ)
- [ ] **INFRA-03**: VectorStorePort y EmbeddingPort abstracciones definidas antes de cualquier código de ingesta
- [ ] **INFRA-04**: Variables de entorno para toda configuración sensible (sin hardcoding)
- [ ] **INFRA-05**: Health endpoints en todos los servicios

### Autenticación & Seguridad

- [ ] **AUTH-01**: Usuario web se autentica vía OAuth2/OIDC Keycloak (realm=Apps, client_id=kmplatform)
- [ ] **AUTH-02**: JWT propagado desde BFF → Core API con validación en cada servicio
- [ ] **AUTH-03**: Roles: admin y user con permisos diferenciados
- [ ] **AUTH-04**: API Keys para terceros: CRUD por admin, almacenadas hasheadas en PostgreSQL
- [ ] **AUTH-05**: Sesión persiste entre recargas del navegador

### Dominios de Conocimiento

- [ ] **DOM-01**: Admin puede crear/editar/eliminar dominios con nombre, descripción y metadatos
- [ ] **DOM-02**: Admin puede asignar usuarios/roles a dominios
- [ ] **DOM-03**: Búsqueda de documentos siempre scoped al dominio autorizado del usuario
- [ ] **DOM-04**: Admin visualiza lista de dominios con conteo de documentos

### Ingesta de Documentos

- [ ] **ING-01**: Ingesta desde carpeta local (watch + upload manual)
- [ ] **ING-02**: Ingesta vía REST API async (POST documento → job_id → status polling)
- [ ] **ING-03**: Ingesta desde S3 (bucket + prefix configurable por dominio)
- [ ] **ING-04**: Ingesta desde tópico Kafka (consumer group por dominio)
- [ ] **ING-05**: Ingesta desde cola RabbitMQ (exchange/queue configurable)
- [ ] **ING-06**: Procesamiento de PDF (extracción de texto y metadata)
- [ ] **ING-07**: Procesamiento de texto plano y código fuente con detección de lenguaje
- [ ] **ING-08**: Chunking configurable con overlap; chunks almacenados en MongoDB
- [ ] **ING-09**: Dead Letter Queue para documentos que fallan tras N reintentos
- [ ] **ING-10**: Estado de job de ingesta accesible vía API (pending/processing/done/failed)

### Embeddings & Almacenamiento

- [ ] **EMB-01**: Generación de embeddings con Gemini (default) vía EmbeddingPort
- [ ] **EMB-02**: Embeddings almacenados en ChromaDB con collection por dominio
- [ ] **EMB-03**: Metadata de documento indexada en PostgreSQL (fuente, dominio, fecha, tipo, hash)
- [ ] **EMB-04**: Documento raw almacenado en MongoDB
- [ ] **EMB-05**: Dimensión de embedding almacenada como metadata de colección

### Búsqueda

- [ ] **SRCH-01**: Búsqueda semántica (vectorial) sobre colección del dominio autorizado
- [ ] **SRCH-02**: Búsqueda híbrida (vectorial + BM25 lexical) con score combinado
- [ ] **SRCH-03**: Filtros por metadatos: tipo de documento, fecha, fuente, dominio
- [ ] **SRCH-04**: Resultados incluyen chunk relevante + metadata + score de relevancia
- [ ] **SRCH-05**: Paginación de resultados de búsqueda

### Core API (Python / FastAPI)

- [ ] **API-01**: Endpoints para dominios, documentos, búsqueda, ingesta y administración
- [ ] **API-02**: Documentación OpenAPI auto-generada (Swagger UI)
- [ ] **API-03**: Autenticación dual: JWT (usuarios web) + API Key (terceros)
- [ ] **API-04**: Rate limiting por API Key
- [ ] **API-05**: Respuestas paginadas con formato estándar

### BFF (NodeJS)

- [ ] **BFF-01**: REST API que consume Core API y expone endpoints al frontend
- [ ] **BFF-02**: WebSocket bidireccional para notificaciones de estado de ingesta en tiempo real
- [ ] **BFF-03**: Proxy de autenticación Keycloak (gestión de tokens, refresh)
- [ ] **BFF-04**: Caché de respuestas frecuentes (Redis)

### Frontend — Shell & Micro UIs

- [ ] **FE-01**: Shell principal (Module Federation host) con navegación, auth state y layout global
- [ ] **FE-02**: Diseño adherido a DESIGN.md "Luminous Knowledge" (Glassmorphism, Inter, primary #007AFF)
- [ ] **FE-03**: Micro UI: Búsqueda (query input, resultados con highlights, filtros)
- [ ] **FE-04**: Micro UI: Explorador de dominios (lista, detalle, documentos del dominio)
- [ ] **FE-05**: Micro UI: Estado de ingesta (jobs activos, historial, errores)
- [ ] **FE-06**: Micro UI: Admin — gestión de dominios y usuarios
- [ ] **FE-07**: Micro UI: Admin — gestión de API Keys
- [ ] **FE-08**: Notificaciones en tiempo real vía WebSocket (estado de ingesta)
- [ ] **FE-09**: Responsive: desktop y tablet

### MCP Server

- [ ] **MCP-01**: FastMCP montado como ASGI sub-app en Core API
- [ ] **MCP-02**: Tool `search_knowledge(query, domain, filters)` accesible a agentes AI
- [ ] **MCP-03**: Tool `list_domains()` para descubrir dominios disponibles
- [ ] **MCP-04**: Autenticación MCP vía API Key
- [ ] **MCP-05**: Scoping: agente solo accede a dominios autorizados por su API Key

## v2 Requirements

### Vector Store Migration

- **VS-01**: Migración de ChromaDB → Qdrant sin cambio de interfaz (VectorStorePort)
- **VS-02**: Neo4J para relaciones entre documentos y búsqueda por grafo

### LLM & Embeddings

- **LLM-01**: Soporte de múltiples proveedores LLM (OpenAI, local via Ollama)
- **LLM-02**: Reranking cross-encoder post búsqueda vectorial
- **LLM-03**: Modelo de embedding configurable por dominio

### Infraestructura

- **K8S-01**: Kubernetes manifests completos con HPA
- **K8S-02**: Helm charts para deployment reproducible
- **OBS-01**: Distributed tracing (OpenTelemetry)
- **OBS-02**: Dashboards Grafana/Prometheus

### Notificaciones

- **NOTF-01**: Notificaciones por email en eventos de ingesta (errores, completado)
- **NOTF-02**: Webhooks configurables por dominio

## Out of Scope

| Feature | Reason |
|---------|--------|
| Generación de contenido por LLM (RAG answer synthesis) | Plataforma es de indexación y consulta, no generación |
| Edición colaborativa de documentos | KM de lectura/consulta, no editor |
| App móvil nativa | Web-first; mobile en futuro si hay demanda |
| Chat conversacional en tiempo real | WebSocket es para estado de ingesta, no chat |
| Billing / multi-tenancy | Plataforma interna |
| Autenticación sin Keycloak (local users) | Seguridad centralizada en IdP existente |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | Pending |
| INFRA-02 | Phase 1 | Pending |
| INFRA-03 | Phase 1 | Pending |
| INFRA-04 | Phase 1 | Pending |
| INFRA-05 | Phase 1 | Pending |
| AUTH-01 | Phase 2 | Pending |
| AUTH-02 | Phase 2 | Pending |
| AUTH-03 | Phase 2 | Pending |
| AUTH-04 | Phase 8 | Pending |
| AUTH-05 | Phase 2 | Pending |
| DOM-01 | Phase 2 | Pending |
| DOM-02 | Phase 2 | Pending |
| DOM-03 | Phase 4 | Pending |
| DOM-04 | Phase 7 | Pending |
| ING-01 | Phase 3 | Pending |
| ING-02 | Phase 3 | Pending |
| ING-03 | Phase 3 | Pending |
| ING-04 | Phase 3 | Pending |
| ING-05 | Phase 3 | Pending |
| ING-06 | Phase 3 | Pending |
| ING-07 | Phase 3 | Pending |
| ING-08 | Phase 3 | Pending |
| ING-09 | Phase 3 | Pending |
| ING-10 | Phase 3 | Pending |
| EMB-01 | Phase 3 | Pending |
| EMB-02 | Phase 3 | Pending |
| EMB-03 | Phase 3 | Pending |
| EMB-04 | Phase 3 | Pending |
| EMB-05 | Phase 3 | Pending |
| SRCH-01 | Phase 4 | Pending |
| SRCH-02 | Phase 4 | Pending |
| SRCH-03 | Phase 4 | Pending |
| SRCH-04 | Phase 4 | Pending |
| SRCH-05 | Phase 4 | Pending |
| API-01 | Phase 2 | Pending |
| API-02 | Phase 2 | Pending |
| API-03 | Phase 2 | Pending |
| API-04 | Phase 8 | Pending |
| API-05 | Phase 2 | Pending |
| BFF-01 | Phase 5 | Pending |
| BFF-02 | Phase 5 | Pending |
| BFF-03 | Phase 5 | Pending |
| BFF-04 | Phase 5 | Pending |
| FE-01 | Phase 6 | Pending |
| FE-02 | Phase 6 | Pending |
| FE-03 | Phase 7 | Pending |
| FE-04 | Phase 7 | Pending |
| FE-05 | Phase 7 | Pending |
| FE-06 | Phase 8 | Pending |
| FE-07 | Phase 8 | Pending |
| FE-08 | Phase 7 | Pending |
| FE-09 | Phase 6 | Pending |
| MCP-01 | Phase 9 | Pending |
| MCP-02 | Phase 9 | Pending |
| MCP-03 | Phase 9 | Pending |
| MCP-04 | Phase 9 | Pending |
| MCP-05 | Phase 9 | Pending |

**Coverage:**
- v1 requirements: 54 total
- Mapped to phases: 54
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-02*
*Last updated: 2026-05-02 after initial definition*
