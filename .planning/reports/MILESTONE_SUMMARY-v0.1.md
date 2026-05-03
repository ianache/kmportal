# Milestone v0.1 — Project Initialization & Roadmap

**Generated:** 2026-05-02
**Purpose:** Team onboarding and project review
**Status:** Roadmap Complete → Ready for Phase 1 Execution

---

## 1. Project Overview

**Knowledge Management Center** es una plataforma greenfield de gestión del conocimiento empresarial diseñada para usuarios internos. El objetivo central es que cualquier usuario autenticado pueda encontrar conocimiento relevante dentro de dominios autorizados en segundos, utilizando búsqueda semántica o híbrida sobre documentos indexados.

### Core Value Proposition

> *"Cualquier usuario autenticado puede encontrar conocimiento relevante dentro de los dominios autorizados en segundos, usando búsqueda semántica o híbrida sobre documentos indexados."*

### ¿Qué se ha construido hasta ahora?

**Este milestone NO contiene código ejecutable.** Representa la fase de **planificación completa** donde se ha:

- ✅ Definido el alcance del proyecto (54 requisitos v1 mapeados)
- ✅ Creado un roadmap de 10 fases secuenciales
- ✅ Investigado la arquitectura y stack tecnológico
- ✅ Documentado el sistema de diseño "Luminous Knowledge"
- ✅ Identificado riesgos técnicos y decisiones críticas
- ✅ Establecido el monorepo y estructura de planificación

### Target Users

- **Administradores:** Gestionan dominios de conocimiento, usuarios y API keys
- **Usuarios finales:** Buscan y consultan documentos en dominios autorizados
- **Agentes AI externos:** Acceden vía FastMCP para consultar la base de conocimiento
- **Sistemas terceros:** Integración vía API REST con autenticación por API Key

---

## 2. Architecture & Technical Decisions

### Stack Tecnológico Definido

| Capa | Tecnología | Versión | Rationale |
|------|-----------|---------|-----------|
| **Core API** | Python + FastAPI | 3.13+ + 0.115+ | Project constraint; FastMCP mounting nativo |
| **BFF** | Node.js + Fastify | 22 LTS + 4.x | HttpOnly cookies, WebSocket relay, OAuth2 proxy |
| **Frontend** | Vue 3 + Pinia | 3.4+ + 2.1+ | Module Federation, design system Glassmorphism |
| **Vector Store (MVP)** | ChromaDB | 0.5+ | Menor complejidad operacional que Qdrant |
| **Vector Store (v2)** | Qdrant | 1.9+ | Target de migración sin cambios de código |
| **Metadata** | PostgreSQL | 16 | Relaciones complejas, dominios, usuarios |
| **Document Store** | MongoDB | 7+ | Contenido raw y chunks con schema flexible |
| **Embeddings** | Gemini | text-embedding-004 | Default provider; 768 dims |
| **Message Broker** | Kafka + RabbitMQ | 7+ / 4+ | Multi-source ingestion (S3, colas, tópicos) |
| **Auth** | Keycloak | 26+ | OAuth2/OIDC obligatorio, realm=Apps |
| **Cache/Sessions** | Redis | 7+ | BFF sessions, pub/sub, rate limiting |

### Decisiones Clave Registradas

| Decisión | Rationale | Outcome |
|----------|-----------|---------|
| **ChromaDB para MVP vectorial** | Menor complejidad operacional que Qdrant para arrancar | — Pending |
| **FAISS descartado en favor de ChromaDB** | ChromaDB ofrece persistencia real y API más completa | — Pending |
| **FastMCP para integración AI** | Estándar MCP emergente, compatible con Claude/GPT agents | — Pending |
| **Micro-frontend (shell + micro UIs)** | Permite evolución y deploy independiente de cada sección UI | — Pending |
| **Design system "Luminous Knowledge" (DESIGN.md)** | Minimalismo + Glassmorfismo define identidad visual unificada entre micro UIs | — Pending |
| **API Keys en PostgreSQL** | Consistencia con almacenamiento relacional ya presente | — Pending |
| **BFF en NodeJS separado del Core API** | Desacopla lógica de presentación de lógica de negocio; BFF maneja WebSocket | — Pending |
| **uv como gestor de paquetes Python** | Velocidad y reproducibilidad superior a pip/poetry | — Pending |

### Patrones de Arquitectura Críticos

1. **VectorStorePort + EmbeddingPort (Abstracciones)**
   - *Por qué:* Prevenir tight coupling con ChromaDB o Gemini
   - *Fase:* Phase 1 (antes de escribir código de ingesta)
   - *Riesgo si no se hace:* Migración a Qdrant u otro provider requiere rewrite completo

2. **BFF con HttpOnly Session Cookies**
   - *Por qué:* JWT nunca expuesto a browser JavaScript (OWASP)
   - *Fase:* Phase 5
   - *Implementación:* BFF almacena tokens server-side, frontend solo ve cookie de sesión

3. **Module Federation con Singletons**
   - *Por qué:* Vue, Pinia, Vue Router deben ser instancias únicas entre shell y micro UIs
   - *Fase:* Phase 6
   - *Riesgo:* Version mismatch causa silencioso dual instances → Pinia stores no comparten estado

4. **Ingestión Async con Job Tracking**
   - *Por qué:* Documentos grandes requieren tiempo de procesamiento; UI necesita feedback
   - *Fase:* Phase 3
   - *Flujo:* Upload → job_id → polling/WebSocket → estado (pending/processing/done/failed)

---

## 3. Phases Delivered

**Estado actual:** Ninguna fase ha sido ejecutada todavía. El proyecto está en **Phase 1: Bootstrap infrastructure** con estado "Ready to plan".

| Phase | Name | Status | One-Liner | Requisitos |
|-------|------|--------|-----------|------------|
| 1 | Bootstrap infrastructure | **Ready to plan** | Monorepo, Docker Compose, port abstractions, env configuration | INFRA-01..05 |
| 2 | Core API foundation | Planned | FastAPI + auth (Keycloak JWT), domain CRUD, OpenAPI docs | AUTH-01..05, DOM-01..02, API-01..05 |
| 3 | Document ingestion pipeline | Planned | Multi-source ingestion, chunking, embedding generation | ING-01..10, EMB-01..05 |
| 4 | Search engine | Planned | Semantic, hybrid, filtered search over domain-scoped embeddings | SRCH-01..05, DOM-03 |
| 5 | BFF layer | Planned | Node.js BFF + OAuth2 proxy + WebSocket + Redis cache | BFF-01..04 |
| 6 | Frontend shell | Planned | Vue 3 Module Federation host + design system | FE-01..02, FE-09 |
| 7 | Core micro UIs | Planned | Search, domain explorer, ingestion status micro UIs | FE-03..05, FE-08, DOM-04 |
| 8 | Admin and API keys | Planned | Admin micro UIs + API key lifecycle + rate limiting | FE-06..07, AUTH-04, API-04 |
| 9 | MCP integration | Planned | FastMCP server exposing search tools to AI agents | MCP-01..05 |
| 10 | Production hardening | Planned | Docker Compose finalization, logging, observability | System validation |

### Ruta Crítica (Critical Path)

```
P1 → P2 → P3 → P4 → P5 → P6 → P7
(Backend crítico)    (Frontend)
```

**Nada visible para usuarios funciona hasta que P1-P4 estén completas.**
El frontend (P5-P7) puede desarrollarse en paralelo con P3-P4 usando mock data si hay equipos separados.

---

## 4. Requirements Coverage

### v1 Requirements (54 total)

**Cobertura:** 54/54 mapeados a fases ✓

#### Infraestructura & Configuración (5)
- ⏳ **INFRA-01**: Monorepo con servicios independientes → Phase 1
- ⏳ **INFRA-02**: Docker Compose con todos los servicios → Phase 1
- ⏳ **INFRA-03**: VectorStorePort y EmbeddingPort abstracciones → Phase 1
- ⏳ **INFRA-04**: Variables de entorno para configuración sensible → Phase 1
- ⏳ **INFRA-05**: Health endpoints en todos los servicios → Phase 1

#### Autenticación & Seguridad (5)
- ⏳ **AUTH-01**: OAuth2/OIDC Keycloak (realm=Apps, client_id=kmplatform) → Phase 2
- ⏳ **AUTH-02**: JWT propagado BFF → Core API → Phase 2
- ⏳ **AUTH-03**: Roles admin/user → Phase 2
- ⏳ **AUTH-04**: API Keys para terceros → Phase 8
- ⏳ **AUTH-05**: Sesión persiste entre recargas → Phase 2

#### Dominios de Conocimiento (4)
- ⏳ **DOM-01**: CRUD de dominios → Phase 2
- ⏳ **DOM-02**: Asignación de usuarios/roles a dominios → Phase 2
- ⏳ **DOM-03**: Búsqueda scoped por dominio → Phase 4
- ⏳ **DOM-04**: Visualización de dominios con conteos → Phase 7

#### Ingesta de Documentos (10)
- ⏳ **ING-01..05**: Ingesta desde carpeta local, REST async, S3, Kafka, RabbitMQ → Phase 3
- ⏳ **ING-06..07**: Procesamiento de PDF, texto plano, código fuente → Phase 3
- ⏳ **ING-08**: Chunking configurable con overlap → Phase 3
- ⏳ **ING-09**: Dead Letter Queue para fallos → Phase 3
- ⏳ **ING-10**: Estado de job accesible vía API → Phase 3

#### Embeddings & Almacenamiento (5)
- ⏳ **EMB-01**: Embeddings con Gemini vía EmbeddingPort → Phase 3
- ⏳ **EMB-02**: Embeddings en ChromaDB (collection por dominio) → Phase 3
- ⏳ **EMB-03**: Metadata de documento en PostgreSQL → Phase 3
- ⏳ **EMB-04**: Documento raw en MongoDB → Phase 3
- ⏳ **EMB-05**: Dimensión de embedding como metadata → Phase 3

#### Búsqueda (5)
- ⏳ **SRCH-01**: Búsqueda semántica vectorial → Phase 4
- ⏳ **SRCH-02**: Búsqueda híbrida (vectorial + BM25) → Phase 4
- ⏳ **SRCH-03**: Filtros por metadatos → Phase 4
- ⏳ **SRCH-04**: Resultados con chunks + metadata + score → Phase 4
- ⏳ **SRCH-05**: Paginación de resultados → Phase 4

#### Core API (5), BFF (4), Frontend (9), MCP (5)
- ⏳ Todos mapeados a fases 2, 5, 6-7, 8 respectivamente

### Out of Scope (Explícitamente excluido)

| Feature | Reason |
|---------|--------|
| Generación de contenido por LLM (RAG synthesis) | Plataforma es de indexación y consulta, no generación |
| Edición colaborativa de documentos | KM de lectura/consulta, no editor |
| App móvil nativa | Web-first; mobile en futuro si hay demanda |
| Chat conversacional en tiempo real | WebSocket es para estado de ingesta, no chat |
| Billing / multi-tenancy | Plataforma interna |
| Autenticación sin Keycloak (local users) | Seguridad centralizada en IdP existente |

---

## 5. Key Decisions Log

### Decisiones de Arquitectura

| ID | Decisión | Contexto | Rationale |
|----|----------|----------|-----------|
| **D001** | VectorStorePort y EmbeddingPort abstracciones en Phase 1 | Prevenir tight coupling | Deben definirse antes de cualquier código de ingesta para evitar rewrite en migración a Qdrant |
| **D002** | FastMCP como ASGI sub-app en Core API | Integración AI agents | No requiere proceso separado para MVP; reduce operacional complexity |
| **D003** | BFF usa HttpOnly session cookies | Seguridad JWT | JWT nunca expuesto a browser JS; BFF maneja refresh transparente |
| **D004** | Vue/Pinia/Vue Router como singletons en Module Federation | Micro-frontend integrity | Version mismatch causa instancias duales silenciosas; CI debe verificar versiones alineadas |

### Top 5 Riesgos Técnicos Identificados

| # | Riesgo | Mitigación | Fase Crítica |
|---|--------|------------|--------------|
| 1 | **VectorStorePort tight coupling** | Definir ABC antes de ingestion code; import-linter banning chromadb fuera de adapters/ | Phase 1 |
| 2 | **EmbeddingPort tight coupling** | EmbeddingPort ABC con dimension property; guardar embedding_model + dimension por dominio | Phase 1 |
| 3 | **Keycloak token propagation gap** | BFF forwards Authorization: Bearer; Core API valida JWT independientemente; domain ACL desde claims | Phase 2 |
| 4 | **Async ingestion poison pills** | try/except + exponential backoff + max 5 retries + DLQ; idempotency key previene double-processing | Phase 3 |
| 5 | **Module Federation version hell** | Shell: singleton:true, eager:true; todos remotes: singleton:true; matching requiredVersion; CI check | Phase 6 |

---

## 6. Tech Debt & Deferred Items

### Bloqueadores Actuales (Pre-Phase 2)

- [ ] **Keycloak `kmplatform` client readiness**: Confirmar que existe cliente confidential en realm=Apps con roles km-admin/km-reader y redirect URIs correctos
- [ ] **Deployment hostnames**: Definir bff.kmp.local, shell.kmp.local, api.kmp.local antes de configurar CORS y Keycloak
- [ ] **Gemini API limits**: Verificar batch size limits y rate limits de text-embedding-004 antes de implementar batching (Phase 3)
- [ ] **ChromaDB version**: Confirmar si hay datos existentes de v0.4 que requieran migración

### Tech Debt Técnico

- **Migración ChromaDB → Qdrant**: Arquitectura preparada (VectorStorePort), pero migración real es trabajo de v2
- **Neo4J para relaciones**: Post-MVP; no requiere cambios en diseño actual
- **Multi-LLM providers**: Gemini es default; arquitectura permite swap pero no implementado en v1
- **Kubernetes manifests**: Docker Compose es MVP; K8s es target de producción

### Lecciones Aprendidas (Pre-ejecución)

- **Adapter pattern es crítico**: Sin VectorStorePort/EmbeddingPort, migraciones son rewrites caros
- **Module Federation requiere disciplina de versiones**: Un mismatch de Vue/Pinia rompe reactivity silenciosamente
- **BFF pattern separa concerns limpiamente**: Auth, WebSocket, caching no deben estar en Core API
- **FastMCP es last**: Esperar a que search y API keys estén estables antes de exponer a AI agents

---

## 7. Getting Started

### ¿Qué necesitas saber para contribuir?

#### Estructura de Directorios

```
25-KnowledgeManagement/
├── .planning/                  ← Documentación de planificación (aquí estás)
│   ├── PROJECT.md             ← Definición del proyecto, constraints, decisions
│   ├── ROADMAP.md             ← 10 fases con criterios de éxito
│   ├── REQUIREMENTS.md        ← 54 requisitos v1 mapeados
│   ├── STATE.md               ← Estado actual, blockers, velocity
│   ├── DESIGN.md              ← Sistema de diseño "Luminous Knowledge"
│   ├── DESIGN_dark.md         ← Variante dark mode
│   └── research/              ← Investigación de arquitectura
│       ├── SUMMARY.md         ← Resumen de investigación
│       ├── ARCHITECTURE.md    ← Diagramas y flujos
│       ├── STACK.md           ← Stack tecnológico
│       ├── PITFALLS.md        ← Riesgos y mitigaciones
│       └── FEATURES.md        ← Feature analysis
│
├── api/                       ← Core API Python (Phase 2+)
├── ingestion/                 ← Ingestion worker (Phase 3+)
├── bff/                       ← Backend for Frontend Node.js (Phase 5+)
├── frontend/
│   ├── shell/                 ← Module Federation host (Phase 6)
│   └── micro-uis/             ← Micro UIs independientes (Phase 7-8)
├── docker-compose.yml         ← Infra completa (Phase 1)
└── README.md                  ← Overview del proyecto
```

### Cómo empezar (Primeros pasos)

#### Para desarrolladores backend (Python):

1. **Familiarízate con el roadmap**: Lee `.planning/ROADMAP.md` completo
2. **Entiende las abstracciones**: `.planning/research/ARCHITECTURE.md` sección "Storage Layer"
3. **Comprende el flujo de ingesta**: Mismo doc, sección "Ingestion Flow"
4. **Revisa decisiones críticas**: `.planning/PROJECT.md` sección "Key Decisions"
5. **Empieza con Phase 1**: Infraestructura Docker Compose y abstracciones VectorStorePort/EmbeddingPort

#### Para desarrolladores frontend (Vue):

1. **Design system primero**: Lee `.planning/DESIGN.md` completamente
2. **Entiende Module Federation**: `.planning/research/ARCHITECTURE.md` sección "Micro-Frontend Architecture"
3. **Singleton contract es crítico**: Vue/Pinia/Vue Router deben ser singletons
4. **Espera a Phase 6**: Frontend shell depende de BFF (Phase 5)
5. **Puedes prototipar**: Usa mock data para explorar componentes con design system

#### Para DevOps/Infra:

1. **Keycloak setup**: Confirmar cliente kmplatform en realm=Apps
2. **Hostnames**: Definir dominios para bff, shell, api
3. **Docker Compose**: Phase 1 requiere PostgreSQL, MongoDB, ChromaDB, Redis, Kafka, RabbitMQ
4. **Preparar para K8s**: Phase 10 requiere manifests; puedes empezar templates temprano

### Puntos de entrada clave

#### API Contracts (BFF → Core API)

```
POST /api/v1/search
{
  "query": "string",
  "domain_id": "uuid | null",
  "search_type": "semantic | hybrid | keyword",
  "filters": { "source_type"?: string, "date_from"?: ISO8601 },
  "top_k": 10
}

POST /api/v1/ingest
{
  "source_type": "upload | s3 | folder | rest",
  "domain_id": "uuid",
  "file"?: binary | "s3_key"?: string,
  "metadata"?: { "author"?: string, "tags"?: string[] }
}
Response: { "job_id": "uuid", "status": "queued" }
```

#### MCP Tools (FastMCP → AI Agents)

```
search_knowledge(query, domain_id?, top_k=5)
list_domains()
get_document(doc_id)
get_document_chunks(doc_id)
```

### Documentos de referencia obligatorios

| Documento | Qué contiene | Cuándo leer |
|-----------|--------------|-------------|
| `.planning/PROJECT.md` | Scope, value prop, constraints, decisions | **Antes de cualquier código** |
| `.planning/ROADMAP.md` | 10 fases, success criteria, dependencies | Antes de empezar cada fase |
| `.planning/REQUIREMENTS.md` | 54 requisitos v1 con traceability | Cuando implementas un requisito |
| `.planning/DESIGN.md` | Sistema de diseño completo | Antes de cualquier UI |
| `.planning/research/ARCHITECTURE.md` | Diagramas, flujos, API contracts | Cuando diseñas un componente |
| `.planning/research/SUMMARY.md` | Recomendaciones de stack, pitfalls | Al inicio del proyecto |

---

## Stats

- **Timeline:** 2026-05-02 (roadmap creation) → **En progreso**
- **Phases:** 0 / 10 completadas (0%)
- **Requirements:** 54 v1 requirements mapeados, 0 implementados
- **Commits:** 6 (todos docs/planning)
- **Contributors:** 1
- **Estado:** Ready to plan Phase 1

---

## Resumen Ejecutivo

**Este proyecto está en fase de planificación completa.** Todo el trabajo de diseño, arquitectura, investigación y roadmap ha sido documentado exhaustivamente. No hay código de aplicación todavía.

**Próximo paso:** Ejecutar **Phase 1: Bootstrap infrastructure** — Docker Compose con todas las bases de datos, monorepo estructurado, y las abstracciones críticas VectorStorePort + EmbeddingPort definidas antes de escribir cualquier código de ingesta.

**Riesgo principal:** Las abstracciones de Phase 1 (VectorStorePort, EmbeddingPort) son críticas. Si no se definen correctamente, todas las fases subsecuentes acumulan deuda técnica que hace imposible migrar a Qdrant u otros providers sin rewrite completo.

**Equipo recomendado:**
- 1-2 desarrolladores backend (Python/FastAPI) para P1-P4
- 1 desarrollador backend (Node.js) para P5
- 1-2 desarrolladores frontend (Vue) para P6-P8
- 1 DevOps para Keycloak, Docker, K8s (P1, P10)

**Tiempo estimado:** 3-4 meses para v1 completo (10 fases) con equipo de 4-5 personas.

---

*Documento generado para onboarding del equipo. Para preguntas específicas sobre fases, requisitos o decisiones de arquitectura, consultar los documentos referenciados en `.planning/`.*
