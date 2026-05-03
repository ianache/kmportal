# Context: Phase 1 — Bootstrap Infrastructure

**Phase:** 1  
**Status:** In Progress  
**Created:** 2026-05-02

---

## Technical Context

### Why This Phase is Critical

Phase 1 is la fundación sobre la cual se construye todo el proyecto. Sin las abstracciones correctas aquí, las fases 2-10 acumularían deuda técnica irreparable. Específicamente:

1. **VectorStorePort/EmbeddingPort** son "puntos de inversión de dependencia" que permiten:
   - Cambiar ChromaDB → Qdrant en v2 sin tocar lógica de negocio
   - Cambiar Gemini → OpenAI/Ollama sin reescribir código de ingesta
   - Testear con mocks/fakes en CI sin servicios externos

2. **Docker Compose unificado** elimina "works on my machine" y permite:
   - Onboarding de nuevos desarrolladores en minutos, no horas
   - Tests de integración reproducibles
   - Paridad entre dev y producción (con overrides)

3. **Configuración externalizada** previene:
   - Secrets en repositorios (seguridad)
   - Cambios de código para cambiar de ambiente (flexibilidad)
   - Acoplamiento a URLs específicas (portabilidad)

### Arquitectura de Puertos y Adaptadores (Ports & Adapters)

```
┌─────────────────────────────────────────────┐
│           Core API / Ingestion              │
│  ┌──────────────────────────────────────┐  │
│  │    Domain Service (business logic)   │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│         uses (dependency)                  │
│                 │                           │
│  ┌──────────────▼───────────────────────┐  │
│  │      VectorStorePort (ABC)           │  │
│  │      EmbeddingPort (ABC)             │  │
│  └──────────────┬───────────────────────┘  │
└─────────────────┼───────────────────────────┘
                  │ implements
┌─────────────────▼───────────────────────────┐
│           Adapters Layer                    │
│  ┌──────────────────────────────────────┐  │
│  │  ChromaDBAdapter  │  GeminiAdapter   │  │
│  │  QdrantAdapter    │  OpenAIAdapter   │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**Regla de oro:** El dominio (Core API) solo conoce los Ports (interfaces). Nunca conoce ChromaDB, Qdrant, Gemini, ni OpenAI. Los Adapters implementan los Ports y traducen a APIs específicas.

### Decisiones Técnicas

<decisions>

#### D1: VectorStorePort debe ser async
**Context:** Bases de datos vectoriales son I/O bound. Llamadas bloqueantes matarían la performance de FastAPI.  
**Decision:** Todos los métodos de VectorStorePort son `async def`.  
**Consequences:** Implementaciones deben usar async clients (httpx para ChromaDB HTTP, qdrant-client async). Testear con `pytest-asyncio`.

#### D2: Uno-to-uno Collection-Domain
**Context:** ChromaDB y Qdrant usan "collections" (o índices). Necesitamos aislamiento de datos por dominio.  
**Decision:** Un collection = un dominio. Nombre del collection = domain_id (UUID).  
**Consequences:** Búsqueda siempre filtra por collection; no hay riesgo de cross-domain data leakage en vector store. Migración: cada dominio se migra independientemente.

#### D3: EmbeddingPort dimension como propiedad
**Context:** Diferentes modelos tienen diferentes dimensiones (Gemini 768, OpenAI text-embedding-3 1536).  
**Decision:** `dimension` es una property abstracta que cada implementación define.  
**Consequences:** Dominio debe almacenar `embedding_dimension` en PostgreSQL. Validación: embeddings generados deben coincidir con dimensión del dominio.

#### D4: Docker Compose sobre Kubernetes para MVP
**Context:** Kubernetes añade complejidad operacional. Para MVP local, Docker Compose es suficiente.  
**Decision:** Docker Compose para dev/MVP; K8s manifests en Phase 10.  
**Consequences:** Parcial: mismos contenedores, diferente orquestación. Variables de entorno son idénticas.

#### D5: Redis agregado explícitamente
**Context:** Originalmente no estaba en el stack listado, pero es necesario para BFF WebSocket relay.  
**Decision:** Redis es infraestructura de Phase 1, no Phase 5.  
**Consequences:** BFF puede usar Redis desde el día 1; no hay refactor doloroso más tarde.

</decisions>

### Stack Versions

| Component | Version | Reason |
|-----------|---------|--------|
| PostgreSQL | 16 | LTS, gen_random_uuid() nativo |
| MongoDB | 7 | Document store moderno, flexible schema |
| ChromaDB | 0.5.x | HTTP API estable; verify for breaking changes |
| Redis | 7 | Streams para event sourcing si se necesita |
| Kafka | 7.x | KRaft mode (no Zookeeper) preferido |
| RabbitMQ | 4.x | Management UI útil para debugging |

### Configuración de Puertos (Host → Container)

| Service | Host Port | Container Port | Notes |
|---------|-----------|----------------|-------|
| PostgreSQL | 5432 | 5432 | Standard |
| MongoDB | 27017 | 27017 | Standard |
| ChromaDB | 8000 | 8000 | HTTP API |
| Redis | 6379 | 6379 | Standard |
| Kafka | 9092 | 9092 | External listener |
| RabbitMQ | 5672 / 15672 | 5672 / 15672 | AMQP / Management UI |

### Convenciones de Nomenclatura

- **Collections:** `{domain_id}` (UUID v4, lowercase)
- **Environment variables:** UPPER_SNAKE_CASE
- **Python packages:** lowercase_with_underscores
- **Adapters:** `{Service}Adapter` (e.g., `ChromaDBAdapter`, `GeminiAdapter`)

### Health Check Strategy

Cada servicio expone `/health` que verifica:

1. **Liveness:** ¿El proceso responde?
2. **Readiness:** ¿Las dependencias (DBs) están accesibles?

Para Docker Compose health checks:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Testing Strategy

- **Unit tests:** Mocks de Ports para testear lógica de dominio sin servicios
- **Integration tests:** Docker Compose con test database (parallel to dev)
- **Contract tests:** Verificar que adapters implementan Ports correctamente

### Pre-commit Checklist

Antes de commit en Phase 1:
- [ ] No hay imports de `chromadb` fuera de `adapters/vector_store/`
- [ ] No hay imports de `google.generativeai` fuera de `adapters/embedding/`
- [ ] Todas las URLs están en variables de entorno
- [ ] `.env.example` está actualizado
- [ ] `docker compose config` valida sin errores

### Deferred (Post-Phase 1)

<deferred>

- Optimización de imágenes Docker (multi-stage builds) → Phase 10
- Kubernetes manifests → Phase 10
- CI/CD pipeline → Phase 10
- Monitoreo avanzado (Prometheus/Grafana) → Phase 10
- Backup strategies → Phase 10

</deferred>

### Open Questions

1. **ChromaDB persistence:** ¿Datos persistentes entre reinicios? (Sí, volumen Docker)
2. **Kafka persistence:** ¿Retención por tiempo o tamaño? (Configurar en v2 si es necesario)
3. **RabbitMQ persistence:** ¿Colas durable? (Sí, para jobs de ingesta)

### References

- `.planning/PROJECT.md` — Constraints y Key Decisions
- `.planning/REQUIREMENTS.md` — INFRA-01..05
- `.planning/research/ARCHITECTURE.md` — Storage layer rationale
- `.planning/research/SUMMARY.md` — Stack recommendations

---

**Updated:** 2026-05-02 — Phase 1 initialization
