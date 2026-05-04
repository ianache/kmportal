---
type: summary
name: 7ce3dfb5
sha: 7ce3dfb5dee6f0314eaf5f1c094a96577be92842
created: 2026-05-03T16:47:15Z
updated: 2026-05-03T16:47:15Z
confidence: 1.00
sources: [7ce3dfb5dee6f0314eaf5f1c094a96577be92842]
tier: episodic
---
# Commit 7ce3dfb5

        **docs: Comprehensive pending implementations list

Document all TODOs and missing features across all phases:

Critical (3):
- Rate limiting middleware for API keys
- API key validation in get_current_user_optional
- Domain access check in job status endpoint

High Priority (8):
- MongoDB integration for document content
- Async workers with ARQ
- Dead Letter Queue implementation
- Prometheus + Grafana stack
- Kubernetes manifests
- Helm charts
- Automated backups
- SSL/TLS termination

Medium Priority v2 (9):
- Qdrant/OpenAI/Ollama adapters
- Reranking with cross-encoder
- Webhooks and email notifications
- OpenTelemetry tracing
- Neo4j graph database
- Search analytics
- Suggestions and autocomplete

Low Priority (5):
- Docker Compose overrides
- Build optimizations
- Redis caching in BFF
- CDN for assets
- Audit logging

Also includes recommended sprint planning and production checklist.**

        This commit introduces a new document outlining 25 pending implementations for the Knowledge Management Center project, categorized by priority and including recommended sprint planning and a production checklist.

        ## Changed Files
        - `PENDING_IMPLEMENTATIONS.md`

        ## Entities
        - **Knowledge Management Center** (concept): The project that is being documented regarding its pending implementations.
- **APIKey** (class): A model used in the API that includes a 'rate_limit' field.
- **rate_limit** (field): A field in the APIKey model, defaulting to 1000 requests per hour, that needs enforcement.
- **Rate limiting middleware** (concept): A critical pending implementation to enforce API key rate limits.
- **Redis** (module): A technology required for implementing rate limiting and caching.
- **get_current_user_optional** (function): An existing function in the API core dependencies that requires API key validation.
- **API key validation** (concept): A critical pending implementation within 'get_current_user_optional' for complete dual authentication.
- **Job status endpoint** (function): An endpoint in the API ingestion module that requires domain access checks.
- **Domain access check** (concept): A critical pending implementation for the job status endpoint to prevent information leakage.
- **MongoDB Integration** (decision): A high-priority planned integration for storing document content, currently deferred.
- **ChromaDB** (module): The current database used for storing document content.
- **ingestion_service.py** (module): A Python file related to ingestion, affected by MongoDB integration.
- **Async Workers** (concept): A high-priority planned system for asynchronous ingestion processing.
- **ARQ** (module): A technology planned for implementing asynchronous workers with queues and retry logic.
- **Dead Letter Queue (DLQ)** (concept): A high-priority pending implementation for handling failed asynchronous tasks.
- **Prometheus** (module): A high-priority monitoring system, with its /metrics endpoint already existing.
- **Grafana** (module): A high-priority visualization tool for monitoring, paired with Prometheus.
- **Kubernetes Manifests** (decision): High-priority missing deployment configurations for Kubernetes.
- **Helm Charts** (decision): High-priority missing packaging for reproducible Kubernetes deployments.
- **Automated Backups** (decision): A high-priority planned strategy for backing up various databases, deferred to Phase 10.
- **SSL/TLS Termination** (decision): A high-priority security configuration for HTTPS in production, currently not implemented.
- **QdrantAdapter** (class): A medium-priority planned adapter for Qdrant, intended to replace ChromaDB.
- **OpenAIAdapter** (class): A medium-priority planned adapter to use OpenAI as an embedding provider.
- **OllamaAdapter** (class): A medium-priority planned adapter for local embeddings using Ollama.
- **Cross-Encoder** (concept): A technology planned for medium-priority reranking of search results.
- **Webhooks** (feature): A medium-priority planned feature for configurable HTTP notifications.
- **Email Notifications** (feature): A medium-priority planned feature for email-based event notifications.
- **OpenTelemetry Tracing** (feature): A medium-priority planned system for distributed tracing, with variables defined but not implemented.
- **Neo4j Graph Database** (module): A medium-priority planned graph database for document relationships and search.
- **Search Analytics** (feature): A medium-priority planned feature for logging and tracking search queries and metrics.
- **Suggestions and Autocomplete** (feature): Medium-priority planned features to improve the search experience.
- **Highlighting y Snippets** (feature): A medium-priority feature for search result presentation, partially implemented.
- **Docker Compose Overrides** (decision): Low-priority missing Docker Compose configurations for different environments.
- **Multi-stage Build Optimizations** (decision): Low-priority Dockerfile optimizations for smaller and faster builds.
- **Redis Caching** (feature): A low-priority planned caching mechanism for the BFF, with variables defined but not implemented.
- **BFF** (module): The Backend For Frontend service where Redis caching is planned.
- **CDN for assets** (module): A low-priority planned content delivery network for static frontend assets.
- **Audit Logging** (feature): A low-priority planned feature for specific administrative action logging.
- **api/src/core/dependencies.py** (module): Source file containing the 'get_current_user_optional' function and a TODO for rate limiting middleware.
- **api/src/api/ingestion.py** (module): Source file containing the job status endpoint and a TODO for domain access checks.
- **Endpoint /metrics** (function): An existing endpoint that provides metrics but lacks a full monitoring stack.

        ## Stats
        - Author: ianache <ianache@crossnet.ws>
        - Timestamp: 2026-05-03T11:46:36-05:00
        - Files changed: 1
