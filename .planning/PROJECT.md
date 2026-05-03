# Knowledge Management Center

## What This Is

Plataforma completa de gestión del conocimiento organizado en dominios definidos por administradores. Ingesta documentos (PDF, texto plano, código fuente) desde múltiples fuentes (carpeta local, S3, REST async, Kafka, RabbitMQ), los indexa con embeddings vectoriales y los expone vía APIs RESTful seguras. Diseñada para uso interno vía Web y para integración de terceros vía API Keys y agentes AI vía MCP.

## Core Value

Cualquier usuario autenticado puede encontrar conocimiento relevante dentro de los dominios autorizados en segundos, usando búsqueda semántica o híbrida sobre documentos indexados.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Administrador puede crear, editar y eliminar dominios de conocimiento de forma centralizada
- [ ] Sistema ingesta documentos PDF, texto plano y código fuente desde carpeta local y REST API async
- [ ] Sistema ingesta documentos desde S3, tópico Kafka y cola RabbitMQ
- [ ] Documentos procesados se almacenan en PostgreSQL (metadata), MongoDB (contenido raw) y ChromaDB (embeddings)
- [ ] Búsqueda semántica (vectorial), híbrida y por filtros de dominio/metadatos disponible
- [ ] Core API Python expone todos los endpoints al BFF y a terceros
- [ ] BFF NodeJS provee REST y WebSocket bidireccional al frontend
- [ ] Frontend Vue + Pinia con arquitectura micro-frontend (shell central + múltiples micro UIs)
- [ ] Autenticación OAuth2/OIDC vía Keycloak (realm=Apps, client_id=kmplatform) para Web
- [ ] Acceso de terceros autenticado con API Keys gestionadas en PostgreSQL
- [ ] FastMCP server expone base de conocimiento a agentes AI externos
- [ ] Embeddings generados con Gemini (default), arquitectura multi-LLM extensible
- [ ] Despliegue inicial en Docker Compose, target Kubernetes
- [ ] Migración de ChromaDB → Qdrant sin cambio de interfaz
- [ ] Migración hacia Neo4J para relaciones entre documentos (post-MVP)

### Out of Scope

- Autenticación por usuario final directo (sin Keycloak) — seguridad centralizada en Keycloak
- Edición colaborativa de documentos — plataforma es de lectura/consulta, no editor
- Generación de nuevo contenido por LLM — solo indexación y consulta
- App móvil nativa — web-first
- Chat conversacional en tiempo real — WebSocket se usa para notificaciones y estado de ingesta, no chat
- Facturación / billing multi-tenant — plataforma interna

## Context

- Proyecto nuevo (greenfield), sin código existente.
- Keycloak disponible en `https://oauth2.qa.comsatel.com.pe` v26+, realm `Apps`, client_id `kmplatform`.
- El frontend usará arquitectura **micro-frontend**: un shell central (host app) integra múltiples micro UIs independientes (Module Federation o similar).
- El sistema de diseño está definido en `DESIGN.md` bajo el nombre **"Luminous Knowledge"**: estética Minimalismo + Glassmorfismo, inspiración Apple. Paleta: primary `#007AFF` / `#0058BC`, surface `#F5F5F7`, tipografía Inter 17px. Glassmorphism: `backdrop-filter: blur(20-30px)`, sombras difusas. Bordes redondeados (10px botones, 12-16px cards). Todas las micro UIs deben adherir a este design system.
- Stack de embeddings arranca con ChromaDB y Gemini; el diseño debe permitir swap a Qdrant sin reescritura de servicios.
- FastMCP (Model Context Protocol) permite a agentes AI externos (Claude, GPT, etc.) consultar la base de conocimiento como tool.
- No hay escala definida aún — diseñar para escalar horizontalmente sin optimizaciones prematuras.

## Constraints

- **Tech Stack**: Python 3.13+ con uv, FastAPI, FastMCP — no cambiar gestor de paquetes
- **Tech Stack**: NodeJS para BFF, Vue 3 + Pinia para frontend
- **Tech Stack**: PostgreSQL + MongoDB + ChromaDB (MVP) → Qdrant (v2)
- **Security**: OAuth2/OIDC Keycloak obligatorio para web; API Keys para terceros
- **Infra**: Docker Compose (MVP) → Kubernetes (producción)
- **LLM**: Gemini como default; diseño debe soportar múltiples proveedores sin refactor mayor
- **Micro-frontend**: Shell central + micro UIs independientes; cada micro UI es deployable por separado
- **Design System**: `DESIGN.md` es la fuente de verdad para todos los componentes visuales; no se desvía sin modificar DESIGN.md primero

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| ChromaDB para MVP vectorial | Menor complejidad operacional que Qdrant para arrancar | — Pending |
| FAISS descartado en favor de ChromaDB | ChromaDB ofrece persistencia real y API más completa | — Pending |
| FastMCP para integración AI | Estándar MCP emergente, compatible con Claude/GPT agents | — Pending |
| Micro-frontend (shell + micro UIs) | Permite evolución y deploy independiente de cada sección UI | — Pending |
| Design system "Luminous Knowledge" (DESIGN.md) | Minimalismo + Glassmorfismo define identidad visual unificada entre micro UIs | — Pending |
| API Keys en PostgreSQL | Consistencia con almacenamiento relacional ya presente | — Pending |
| BFF en NodeJS separado del Core API | Desacopla lógica de presentación de lógica de negocio; BFF maneja WebSocket | — Pending |
| uv como gestor de paquetes Python | Velocidad y reproducibilidad superior a pip/poetry | — Pending |

## Evolution

Este documento evoluciona en transiciones de fase y milestones.

**Tras cada fase** (vía `/gsd:transition`):
1. ¿Requisitos invalidados? → Mover a Out of Scope con razón
2. ¿Requisitos validados? → Mover a Validated con referencia de fase
3. ¿Nuevos requisitos emergidos? → Añadir a Active
4. ¿Decisiones a registrar? → Añadir a Key Decisions
5. ¿"What This Is" sigue siendo preciso? → Actualizar si hay desvío

**Tras cada milestone** (vía `/gsd:complete-milestone`):
1. Revisión completa de todas las secciones
2. Check de Core Value — ¿sigue siendo la prioridad correcta?
3. Auditar Out of Scope — ¿las razones siguen siendo válidas?
4. Actualizar Context con estado actual

---
*Last updated: 2026-05-02 after initialization*
