# Puntos Pendientes de Implementación - Knowledge Management Center

## Resumen Ejecutivo
**Estado Actual**: Fases 1-10 completadas (MVP funcional)
**Total Pendientes**: 25 items categorizados por prioridad

---

## 🔴 CRÍTICOS (Bloqueantes para Producción)

### 1. Rate Limiting para API Keys
**Ubicación**: `api/src/core/dependencies.py:56`
**Estado**: TODO en código
**Descripción**: El campo `rate_limit` existe en el modelo APIKey (default 1000 req/hr) pero no hay middleware que lo imponga.
**Impacto**: Sin protección contra abuso de API
**Implementación necesaria**:
- Middleware de rate limiting con Redis
- Tracking por API key
- Respuesta 429 con header Retry-After

```python
# Pseudocódigo
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    api_key = request.headers.get("X-API-Key")
    current_count = await redis.get(f"rate_limit:{api_key}")
    if current_count > rate_limit:
        return Response(status_code=429, headers={"Retry-After": "3600"})
```

### 2. Validación de API Keys en get_current_user_optional
**Ubicación**: `api/src/core/dependencies.py:56`
**Estado**: TODO en código
**Descripción**: El código tiene un placeholder para validación de API keys pero no está implementado
**Impacto**: Autenticación dual (JWT + API Key) incompleta

### 3. Domain Access Check en Job Status
**Ubicación**: `api/src/api/ingestion.py:180`
**Estado**: TODO en código
**Descripción**: No se verifica si el usuario tiene acceso al dominio del job de ingestión
**Impacto**: Potencial filtración de información entre dominios

---

## 🟡 ALTOS (Funcionalidad Importante)

### 4. MongoDB Integration (Task 3.7)
**Estado**: Deferred/Mencionado en wiki
**Descripción**: El contenido de documentos debería almacenarse en MongoDB, actualmente solo está en ChromaDB
**Archivos afectados**: `ingestion_service.py`, documentos grandes
**Nota**: Marcado como "planned" en fase 3 pero no implementado

### 5. Async Workers con ARQ
**Estado**: Deferred a v2
**Descripción**: Procesamiento de ingestión asíncrono con colas y retry logic
**Actual**: Procesamiento síncrono en MVP
**Requiere**: Workers ARQ, Dead Letter Queue, retry logic con backoff

### 6. DLQ (Dead Letter Queue) Completa
**Estado**: Parcial
**Descripción**: El concepto existe pero falta implementación completa de reintentos y manejo de poison pills
**Archivos**: `task_36_error_handling_dlq.md`

### 7. Prometheus + Grafana Monitoring Stack
**Estado**: Endpoint existe (/metrics) pero sin stack de monitoreo
**Descripción**: 
- Endpoint /metrics implementado ✅
- Falta: Prometheus scraper
- Falta: Grafana dashboards
- Falta: Alertas configuradas

### 8. Kubernetes Manifests
**Estado**: No existe
**Descripción**: Solo hay Docker Compose, faltan:
- Deployments
- Services
- ConfigMaps/Secrets
- Ingress
- HPA (Horizontal Pod Autoscaler)

### 9. Helm Charts
**Estado**: No existe (marcado como v2 requirement)
**Descripción**: Instalación reproducible en K8s

### 10. Backups Automatizados
**Estado**: Deferred a Phase 10
**Descripción**: Estrategia de backup para PostgreSQL, MongoDB, ChromaDB

### 11. SSL/TLS Termination
**Estado**: No implementado
**Descripción**: Configuración de HTTPS en producción
**Nota**: Dockerfile expone puerto 8000 sin SSL

---

## 🟢 MEDIOS (Mejoras y Features v2)

### 12. Adapters Adicionales (v2)
**QdrantAdapter**:
- Estado: Planificado para migración v2
- Archivo: `concepts/qdrantadapter.md`
- Reemplazaría ChromaDB

**OpenAIAdapter**:
- Estado: Planificado v2
- Permitiría usar OpenAI como provider de embeddings

**OllamaAdapter**:
- Estado: Planificado v2
- Embeddings locales con Ollama

### 13. Reranking con Cross-Encoder
**Estado**: v2 requirement
**Descripción**: Post-procesamiento de resultados de búsqueda para mejor relevancia

### 14. Webhooks
**Estado**: v2 requirement
**Descripción**: Notificaciones HTTP configurables por dominio para eventos de ingestión

### 15. Email Notifications
**Estado**: v2 requirement
**Descripción**: Notificaciones por email de eventos (errores, completación)

### 16. OpenTelemetry Tracing
**Estado**: v2 requirement
**Descripción**: Distributed tracing entre servicios
- Variables ya definidas en .env.production.example
- No implementado

### 17. Neo4j Graph Database
**Estado**: v2 requirement
**Descripción**: Relaciones entre documentos y graph-based search

### 18. Search Analytics
**Estado**: Mencionado en wiki
**Descripción**: Logging y tracking de queries, resultados, métricas de performance

### 19. Suggestions y Autocomplete
**Estado**: Mencionado en wiki
**Descripción**: Sugerencias de queries y autocompletado

### 20. Highlighting y Snippets
**Estado**: Parcial
**Descripción**: Resaltado de términos en resultados de búsqueda

---

## 🔵 BAJOS (Optimizaciones y Polish)

### 21. Docker Compose Overrides
**Estado**: No existe
**Descripción**: 
- `docker-compose.override.yml` para desarrollo
- `docker-compose.staging.yml` para staging
- `docker-compose.prod.yml` para producción optimizada

### 22. Multi-stage Build Optimizations
**Estado**: Básico
**Descripción**: 
- Dockerfile actual funcional pero puede optimizarse
- Cache de dependencias
- Smaller final images

### 23. Redis Caching en BFF
**Estado**: Variables definidas pero no implementado
**Descripción**: Cache de respuestas en BFF mencionado en requerimientos

### 24. CDN para Assets Frontend
**Estado**: No implementado
**Descripción**: Servir assets estáticos desde CDN en producción

### 25. Audit Logging
**Estado**: No implementado
**Descripción**: Logging específico de acciones administrativas

---

## 📋 Checklist de Producción (Pendientes)

### Seguridad
- [ ] Rate limiting middleware implementado
- [ ] API key validation completo
- [ ] Domain access checks en todos los endpoints
- [ ] SSL/TLS configurado
- [ ] Security headers (helmet ya en BFF ✅)
- [ ] Secrets management (Docker/K8s secrets)

### Observabilidad
- [x] Structured logging ✅
- [x] Health checks ✅
- [x] Prometheus metrics endpoint ✅
- [ ] Prometheus scraper configurado
- [ ] Grafana dashboards creados
- [ ] Alertas configuradas (PagerDuty/Opsgenie)
- [ ] Log aggregation (ELK/Loki)

### Operaciones
- [ ] Kubernetes manifests
- [ ] Helm charts
- [ ] Backup automatizado
- [ ] Disaster recovery procedures
- [ ] Runbooks documentados

### Performance
- [ ] Load testing realizado
- [ ] Connection pooling tuning
- [ ] Redis caching implementado
- [ ] CDN configurado

---

## 🎯 Prioridades Recomendadas

### Sprint 1 (Críticos)
1. Rate limiting middleware
2. API key validation completo
3. Domain access checks

### Sprint 2 (Producción)
4. Kubernetes manifests básicos
5. Prometheus + Grafana stack
6. SSL/TLS configuration

### Sprint 3 (v2 Features)
7. MongoDB integration
8. Async workers con ARQ
9. Webhooks

### Futuro (v2)
10. Qdrant/OpenAI/Ollama adapters
11. Neo4j graph database
12. Advanced analytics

---

## 📊 Estadísticas

| Prioridad | Cantidad | % Total |
|-----------|----------|---------|
| 🔴 Críticos | 3 | 12% |
| 🟡 Altos | 8 | 32% |
| 🟢 Medios | 9 | 36% |
| 🔵 Bajos | 5 | 20% |
| **Total** | **25** | **100%** |

---

## 📁 Archivos con TODOs Explícitos

1. `api/src/core/dependencies.py:56` - API key validation
2. `api/src/api/ingestion.py:180` - Domain access check

---

## 🔗 Referencias

- **Wiki v2 Requirements**: `wiki/concepts/` (grafana, prometheus, opentelemetry, etc.)
- **Deferred Features**: `concepts/backup_strategies.md`, `concepts/advanced_monitoring.md`
- **Roadmap**: `.planning/ROADMAP.md`
- **Phase 10 Plan**: `wiki/concepts/10-01-planmd.md`
