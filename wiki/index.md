# Wiki Index

## Concepts

- [Gemini API batch embedding request payload](concepts/gemini_api_batch_embedding_request_payload.md) — The JSON structure sent to the Gemini API's `batchEmbedContents` endpoint, which

- [health checks](concepts/health_checks.md) — An API endpoint or system process responsible for verifying the operational stat

- [Any](concepts/any.md) — A Python type hint from the `typing` module indicating that a value can be of an

- [structlog.contextvars.BoundContextvars](concepts/structlogcontextvarsboundcontextvars.md) — A specific type from the structlog library, previously used as the return type a

- [uvicorn src.main:app](concepts/uvicorn_srcmainapp.md) — An incorrect command pattern for running the API that typically leads to `Module

- [[tool.uv.scripts]](concepts/tooluvscripts.md) — A deprecated section in `pyproject.toml` previously used for `uv` script configu

- [[project.optional-dependencies] dev](concepts/projectoptional-dependencies_dev.md) — A section in `pyproject.toml` where development-specific dependencies are now co

- [uvicorn --app-dir src](concepts/uvicorn_--app-dir_src.md) — A specific command-line argument for uvicorn that designates the `src/` director

- [absolute imports](concepts/absolute_imports.md) — A Python import style (e.g., `from db.database import ...`) that requires the co

- [knowledge-api](concepts/knowledge-api.md) — The Docker image name for the Knowledge Management API.

- [ModuleNotFoundError: No module named 'db'](concepts/modulenotfounderror_no_module_named_db.md) — A common Python error indicating that a module cannot be found, specifically 'db

- [--app-dir src](concepts/--app-dir_src.md) — A uvicorn command-line flag that specifies 'src' as the application directory fo

- [main:app](concepts/mainapp.md) — The entry point for the FastAPI application within the 'src' directory.

- [start.sh](concepts/startsh.md) — A Bash script for starting the Knowledge Management API on Linux/macOS using uvi

- [start.bat](concepts/startbat.md) — A Windows batch script for starting the Knowledge Management API using uvicorn w

- [API startup process](concepts/api_startup_process.md) — The procedure for initiating the Knowledge Management API, now improved with rob

- [local modules](concepts/local_modules.md) — Project-specific Python modules (db, api, mcp, core) located within the applicat

- [ModuleNotFoundError](concepts/modulenotfounderror.md) — A Python error indicating that an imported module could not be found, specifical

- [uvicorn](concepts/uvicorn.md) — An ASGI server used to run FastAPI applications.

- [PYTHONPATH](concepts/pythonpath.md) — An environment variable used by Python to determine the list of directories wher

- [api/Dockerfile](concepts/apidockerfile.md) — The Dockerfile responsible for building the API service's container image.

- [Audit Logging](concepts/audit_logging.md) — A low-priority planned feature for specific administrative action logging.

- [Redis Caching](concepts/redis_caching.md) — A low-priority planned caching mechanism for the BFF, with variables defined but

- [Multi-stage Build Optimizations](concepts/multi-stage_build_optimizations.md) — Low-priority Dockerfile optimizations for smaller and faster builds.

- [Docker Compose Overrides](concepts/docker_compose_overrides.md) — Low-priority missing Docker Compose configurations for different environments.

- [Highlighting y Snippets](concepts/highlighting_y_snippets.md) — A medium-priority feature for search result presentation, partially implemented.

- [OpenTelemetry Tracing](concepts/opentelemetry_tracing.md) — A medium-priority planned system for distributed tracing, with variables defined

- [Cross-Encoder](concepts/cross-encoder.md) — A technology planned for medium-priority reranking of search results.

- [SSL/TLS Termination](concepts/ssltls_termination.md) — A high-priority security configuration for HTTPS in production, currently not im

- [Automated Backups](concepts/automated_backups.md) — A high-priority planned strategy for backing up various databases, deferred to P

- [Kubernetes Manifests](concepts/kubernetes_manifests.md) — High-priority missing deployment configurations for Kubernetes.

- [Async Workers](concepts/async_workers.md) — A high-priority planned system for asynchronous ingestion processing.

- [MongoDB Integration](concepts/mongodb_integration.md) — A high-priority planned integration for storing document content, currently defe

- [Domain access check](concepts/domain_access_check.md) — A critical pending implementation for the job status endpoint to prevent informa

- [API key validation](concepts/api_key_validation.md) — A critical pending implementation within 'get_current_user_optional' for complet

- [Rate limiting middleware](concepts/rate_limiting_middleware.md) — A critical pending implementation to enforce API key rate limits.

- [rate_limit](concepts/rate_limit.md) — A field in the APIKey model, defaulting to 1000 requests per hour, that needs en

- [Prometheus Metrics](concepts/prometheus_metrics.md) — A system for exposing application metrics in a format compatible with Prometheus

- [Version Endpoint](concepts/version_endpoint.md) — An API endpoint that provides information about the application's current versio

- [GZip compression middleware](concepts/gzip_compression_middleware.md) — A middleware component that automatically compresses HTTP responses to reduce ba

- [Production Configuration](concepts/production_configuration.md) — A comprehensive set of environment variables and settings specifically tailored 

- [Health Checks](concepts/health_checks.md) — Endpoints designed to monitor the operational status and dependency health of th

- [Request Logging Middleware](concepts/request_logging_middleware.md) — A middleware component that automatically intercepts and logs details of incomin

- [Structured Logging](concepts/structured_logging.md) — A system for generating machine-readable logs, facilitating easier parsing, quer

- [Observability](concepts/observability.md) — The ability to understand the internal state of the system from its external out

- [Production Hardening](concepts/production_hardening.md) — The overall initiative to enhance the application's resilience, stability, and m

- [get_document_status](concepts/get_document_status.md) — An MCP tool that allows AI agents to inquire about the ingestion and processing 

- [get_domain_info](concepts/get_domain_info.md) — An MCP tool that provides AI agents with detailed metadata and configuration for

- [list_domains](concepts/list_domains.md) — An MCP tool that enables AI agents to retrieve a list of all accessible knowledg

- [search_knowledge](concepts/search_knowledge.md) — An MCP tool that allows AI agents to query the knowledge base using various sear

- [/mcp/messages](concepts/mcpmessages.md) — The message POST endpoint of the FastMCP server, designed for AI agents to send 

- [/mcp/sse](concepts/mcpsse.md) — The Server-Sent Events (SSE) endpoint provided by the FastMCP server, used for r

- [Domain Restrictions](concepts/domain_restrictions.md) — A security mechanism applied to API keys, limiting the API key's access to a pre

- [Scopes](concepts/scopes.md) — Permission identifiers (e.g., 'read', 'write', 'admin') associated with an API k

- [X-API-Key Header](concepts/x-api-key_header.md) — The custom HTTP header (`X-API-Key`) required for authenticating requests to the

- [MCP Tools](concepts/mcp_tools.md) — A conceptual category encompassing the functions and capabilities exposed by the

- [FastMCP Server](concepts/fastmcp_server.md) — An instance of the FastMCP framework serving as the Model Context Protocol serve

- [FE-03](concepts/fe-03.md) — A frontend requirement related to the interactive user experience, particularly 

- [DOM-04](concepts/dom-04.md) — A requirement specifying that search functionality must respect user's domain ac

- [SearchResponse](concepts/searchresponse.md) — An interface defining the structure of the response received from a search query

- [SearchRequest](concepts/searchrequest.md) — An interface defining the parameters for a search query, including query string,

- [Core API /api/v1/search](concepts/core_api_apiv1search.md) — The Core API's REST endpoint for performing search operations, which the BFF pro

- [BFF /api/v1/search](concepts/bff_apiv1search.md) — The Backend For Frontend (BFF) REST API endpoint through which the Search Micro 

- [07-04-PLAN.md](concepts/07-04-planmd.md) — The execution plan document for implementing the Shell Notifications Micro UI.

- [07-03-PLAN.md](concepts/07-03-planmd.md) — The execution plan document for implementing the Ingestion Status Micro UI.

- [07-02-PLAN.md](concepts/07-02-planmd.md) — The execution plan document for implementing the Domain Explorer Micro UI.

- [07-01-PLAN.md](concepts/07-01-planmd.md) — The detailed execution plan document for implementing the Search Micro UI, outli

- [FE-09 requirement](concepts/fe-09_requirement.md) — A frontend requirement resolved by the completion of Phase 6.

- [FE-02 requirement](concepts/fe-02_requirement.md) — A frontend requirement resolved by the completion of Phase 6.

- [FE-01 requirement](concepts/fe-01_requirement.md) — A frontend requirement resolved by the completion of Phase 6.

- [Module Federation Integration](concepts/module_federation_integration.md) — The process of setting up Module Federation for the Frontend Shell to host and c

- [Auth State Management](concepts/auth_state_management.md) — The system responsible for handling user authentication, session validation, log

- [06-03-PLAN.md](concepts/06-03-planmd.md) — A detailed plan for integrating Module Federation in the Frontend Shell, includi

- [06-02-PLAN.md](concepts/06-02-planmd.md) — A detailed plan for implementing the Luminous Knowledge Design System and global

- [06-01-PLAN.md](concepts/06-01-planmd.md) — A detailed plan for implementing authentication state management and BFF integra

- [Frontend Shell Phase 6](concepts/frontend_shell_phase_6.md) — The Module Federation host application that manages authentication, global layou

- [DefaultSettings](concepts/defaultsettings.md) — A comprehensive object defining all the default configuration options and settin

- [DOMManipulationUtilities](concepts/dommanipulationutilities.md) — A collection of helper functions designed for common DOM operations such as addi

- [DiacriticNormalization](concepts/diacriticnormalization.md) — The collective logic and helper functions for processing and normalizing strings

- [filterActive](concepts/filteractive.md) — A boolean flag used to track if the filterHighlight effect is currently active o

- [highlightActive](concepts/highlightactive.md) — A boolean flag used to track if the neighbourhoodHighlight effect is currently a

- [edges](concepts/edges.md) — Represents a DataSet for managing the edges within the network graph, likely fro

- [nodeColors](concepts/nodecolors.md) — An external object or map used to store and retrieve the original colors of node

- [network](concepts/network.md) — Represents the vis.js Network instance, providing methods for interacting with t

- [nodes](concepts/nodes.md) — Represents a DataSet for managing the nodes within the network graph, likely fro

- [scripts](concepts/scripts.md) — A collection of predefined commands used for development and other operations wi

- [Lazy Loading](concepts/lazy_loading.md) — A performance optimization technique where modules or components are loaded only

- [/admin](concepts/admin.md) — A client-side route that dynamically loads the 'adminUi/App' component for the a

- [/ingestion](concepts/ingestion.md) — A client-side route that dynamically loads the 'ingestionUi/App' component for t

- [/search](concepts/search.md) — A client-side route that dynamically loads the 'searchUi/App' component for the 

- [/domains](concepts/domains.md) — A client-side route that dynamically loads the 'domainsUi/App' component for the

- [/](concepts/unnamed.md) — The root route of the application, configured to redirect to the '/search' route

- [router](concepts/router.md) — An initialized instance of Vue Router, configured with HTML5 history mode and ap

- [preview script](concepts/preview_script.md) — An NPM script for locally previewing the production build of the 'shell' applica

- [build script](concepts/build_script.md) — An NPM script for building the 'shell' application for production.

- [dev script](concepts/dev_script.md) — An NPM script for starting the development server of the 'shell' application.

- [Vue.js](concepts/vuejs.md) — The progressive JavaScript framework used for building user interfaces, which po

- [typescript](concepts/typescript.md) — A typed superset of JavaScript, used for developing the domains-ui application.

- [vite](concepts/vite.md) — A next-generation frontend tool that provides a fast development environment and

- [vue](concepts/vue.md) — A progressive JavaScript framework for building user interfaces, used as the cor

- [#app](concepts/app.md) — A DOM element selector (by ID) indicating where the Vue application will be moun

- [vue-router](concepts/vue-router.md) — The official routing library for Vue.js, used to manage navigation within the sh

- [pinia](concepts/pinia.md) — An initialized instance of the Pinia store, used for global state management acr

- [remoteEntry.js](concepts/remoteentryjs.md) — The designated filename for the Module Federation entry point that exposes 'sear

- [Vite](concepts/vite.md) — A fast build tool used for development and bundling of the application.

- [CollectionNotFoundError](concepts/collectionnotfounderror.md) — An exception raised when attempting to access or modify a collection that does n

- [CollectionExistsError](concepts/collectionexistserror.md) — An exception raised when attempting to create a collection that already exists.

- [VectorStoreError](concepts/vectorstoreerror.md) — A base exception class for errors originating from vector store operations.

- [SearchResult](concepts/searchresult.md) — An interface defining the structure of a single search result, encompassing chun

- [ABC](concepts/abc.md) — Python's Abstract Base Class (ABC) mechanism, used to define abstract interfaces

- [mock_user_payload](concepts/mock_user_payload.md) — A pytest fixture providing a mocked JWT payload for a regular user.

- [mock_admin_payload](concepts/mock_admin_payload.md) — A pytest fixture providing a mocked JWT payload for an administrator user.

- [test_domain](concepts/test_domain.md) — A pytest fixture providing a pre-existing domain object for tests requiring an e

- [test_user](concepts/test_user.md) — A pytest fixture representing an authenticated regular user (e.g., reader) for t

- [test_admin](concepts/test_admin.md) — A pytest fixture representing an authenticated administrator user for testing pu

- [client](concepts/client.md) — A pytest fixture providing an asynchronous HTTP test client for making requests 

- [Access Control](concepts/access_control.md) — The system for managing user permissions and roles to determine authorized inter

- [JWT token verification](concepts/jwt_token_verification.md) — The authentication process involving the validation of JSON Web Tokens to author

- [Domain API endpoints](concepts/domain_api_endpoints.md) — The collection of HTTP API endpoints providing CRUD and access management functi

- [pytest](concepts/pytest.md) — A popular Python testing framework used for writing concise and scalable test su

- [core.auth.fetch_jwks](concepts/coreauthfetch_jwks.md) — A mocked asynchronous function from the "core.auth" module, responsible for fetc

- [core.auth.verify_jwt_token](concepts/coreauthverify_jwt_token.md) — A mocked asynchronous function from the "core.auth" module, responsible for veri

- [TestingSessionLocal](concepts/testingsessionlocal.md) — An asynchronous session maker for the test database, configured to produce "Asyn

- [TEST_DATABASE_URL](concepts/test_database_url.md) — A constant string defining the in-memory SQLite database URL used for testing, e

- [Reciprocal Rank Fusion (RRF)](concepts/reciprocal_rank_fusion_rrf.md) — An algorithm for combining and re-ranking search results from multiple independe

- [Keyword Search](concepts/keyword_search.md) — A traditional search paradigm based on matching specific terms in text content.

- [search](concepts/search.md) — The main public interface for initiating a search, dynamically choosing the sear

- [_reciprocal_rank_fusion](concepts/_reciprocal_rank_fusion.md) — A private utility method that implements the Reciprocal Rank Fusion (RRF) algori

- [hybrid_search](concepts/hybrid_search.md) — Combines results from both semantic and keyword searches using Reciprocal Rank F

- [keyword_search](concepts/keyword_search.md) — Performs a full-text search using PostgreSQL on document titles, ranking results

- [semantic_search](concepts/semantic_search.md) — Executes a vector-similarity search by generating query embeddings and retrievin

- [__init__](concepts/__init__.md) — Constructor for SearchService, injecting necessary dependencies: a database sess

- [Embedding Provider](concepts/embedding_provider.md) — A conceptual dependency representing an external service or component responsibl

- [Vector Store](concepts/vector_store.md) — A conceptual dependency representing a database or service specialized in storin

- [Document Processing Pipeline](concepts/document_processing_pipeline.md) — The sequential workflow that a document undergoes within the system, from raw in

- [Eager Loading](concepts/eager_loading.md) — A database optimization technique (using 'selectinload') to load related objects

- [SQLAlchemy AsyncSession](concepts/sqlalchemy_asyncsession.md) — An asynchronous session object used for interacting with the database using SQLA

- [AsyncSession](concepts/asyncsession.md) — An asynchronous database session object, typically from SQLAlchemy, used by serv

- [APIKeyResponse](concepts/apikeyresponse.md) — A Pydantic schema used for structuring output data when returning API key inform

- [APIKeyCreate](concepts/apikeycreate.md) — A Pydantic schema used for validating and structuring input data when creating a

- [APIKey](concepts/apikey.md) — The SQLAlchemy ORM model representing an API key in the database, storing its ha

- [Design Decisions](concepts/design_decisions.md) — Explicitly stated design principles guiding the implementation of the `VectorSto

- [Vector Store Port](concepts/vector_store_port.md) — An architectural pattern representing an abstract interface for interacting with

- [EmbeddingPort.config](concepts/embeddingportconfig.md) — An abstract property within `EmbeddingPort` that returns the `EmbeddingConfig` o

- [EmbeddingPort.model_name](concepts/embeddingportmodel_name.md) — An abstract property within `EmbeddingPort` that returns the string identifier o

- [EmbeddingPort.dimension](concepts/embeddingportdimension.md) — An abstract property within `EmbeddingPort` that returns the integer dimension o

- [separate query embedding](concepts/separate_query_embedding.md) — A design decision to provide a dedicated `embed_query` method in `EmbeddingPort`

- [batch processing](concepts/batch_processing.md) — A design decision to incorporate internal batch processing within the `Embedding

- [dimension as property](concepts/dimension_as_property.md) — A design decision to expose the embedding dimension as an abstract property (`di

- [Embedding Port Pattern](concepts/embedding_port_pattern.md) — A design pattern where an abstract interface (the 'port') is defined for an exte

- [MCP (Model Context Protocol)](concepts/mcp_model_context_protocol.md) — A described feature intended for integrating with AI agent models through a spec

- [Document Ingestion](concepts/document_ingestion.md) — A key feature of the API enabling the uploading, processing, and indexing of doc

- [CORS Middleware](concepts/cors_middleware.md) — A middleware component integrated into the FastAPI application responsible for h

- [app](concepts/app.md) — The main Vue application instance created by `createApp`, to which plugins are a

- [Knowledge Management Center API](concepts/knowledge_management_center_api.md) — The overarching FastAPI application providing REST services for knowledge manage

- [dataclass](concepts/dataclass.md) — A Python decorator and utility module for easily creating classes that are prima

- [SQL_ECHO](concepts/sql_echo.md) — An environment variable that controls whether the SQLAlchemy engine logs SQL sta

- [AsyncSessionLocal](concepts/asyncsessionlocal.md) — A SQLAlchemy asynchronous sessionmaker factory configured to create new `AsyncSe

- [engine](concepts/engine.md) — An asynchronous SQLAlchemy engine configured for the in-memory SQLite database, 

- [DATABASE_URL](concepts/database_url.md) — The environment variable or default connection string used by SQLAlchemy to esta

- [DomainAccessRole Enum](concepts/domainaccessrole_enum.md) — An enumeration defining the possible roles a user can have in relation to a spec

- [DomainAccess Model](concepts/domainaccess_model.md) — An SQLAlchemy model representing the association between a user and a domain, de

- [User Model](concepts/user_model.md) — An SQLAlchemy model representing user entities stored in the application's datab

- [require_domain_admin](concepts/require_domain_admin.md) — An instance of `DomainAccessChecker` configured to check for administrator-level

- [require_domain_access](concepts/require_domain_access.md) — An instance of `DomainAccessChecker` configured to check for any level of access

- [HTTPBearer Security](concepts/httpbearer_security.md) — FastAPI's `HTTPBearer` security scheme used to extract JWT or API Key tokens fro

- [JWKS Caching](concepts/jwks_caching.md) — A mechanism to store fetched JSON Web Key Sets (JWKS) in memory to avoid repeate

- [ALGORITHM](concepts/algorithm.md) — The cryptographic algorithm specified for JWT signature verification, hardcoded 

- [KEYCLOAK_CLIENT_ID](concepts/keycloak_client_id.md) — The client ID registered in Keycloak for this application, used as the audience 

- [KEYCLOAK_REALM](concepts/keycloak_realm.md) — The specific realm within Keycloak to be used for authentication, configurable v

- [KEYCLOAK_URL](concepts/keycloak_url.md) — The base URL for the Keycloak identity provider, configurable via environment va

- [Search Modes](concepts/search_modes.md) — Different strategies for document search: semantic (vector similarity), keyword 

- [Synchronous Ingestion Processing](concepts/synchronous_ingestion_processing.md) — A temporary implementation decision where document processing within the `ingest

- [Ingestion Job](concepts/ingestion_job.md) — A discrete, trackable background task initiated for each content submission, rep

- [Ingestion](concepts/ingestion.md) — The overall process of taking source content (files or text) and integrating it 

- [UserInToken](concepts/userintoken.md) — A Pydantic schema used to encapsulate user details (Keycloak ID, email, roles) e

- [PaginationParams](concepts/paginationparams.md) — A schema defining parameters for pagination, including page number and page size

- [DomainService](concepts/domainservice.md) — An external service responsible for the business logic related to domain managem

- [APIKeyService](concepts/apikeyservice.md) — An external service responsible for the business logic related to API key operat

- [APIRouter](concepts/apirouter.md) — FastAPI component used to group related route handlers with common prefixes and 

- [ChromaDB 0.5+ required](concepts/chromadb_05_required.md) — A compatibility requirement specifying that ChromaDB server version 0.5 or newer

- [Metadata filtering](concepts/metadata_filtering.md) — A design consideration noting the use of ChromaDB's metadata filtering capabilit

- [One collection per domain](concepts/one_collection_per_domain.md) — A design principle stating that each domain should have its own isolated collect

- [httpx.AsyncClient](concepts/httpxasyncclient.md) — An asynchronous HTTP client library used by the ChromaDBAdapter to make non-bloc

- [Authentication](concepts/authentication.md) — The process of verifying the identity of the client making API requests, typical

- [Batch Processing](concepts/batch_processing.md) — An optimization strategy where multiple text inputs are grouped together and sen

- [Text Embeddings](concepts/text_embeddings.md) — Numerical vector representations of text, designed to capture semantic meaning, 

- [httpx](concepts/httpx.md) — An asynchronous HTTP client library used by the `GeminiAdapter` to make non-bloc

- [Google Gemini API](concepts/google_gemini_api.md) — Google's Generative AI API that provides capabilities such as generating text em

- [EmbeddingTaskType](concepts/embeddingtasktype.md) — An enumeration defining different use cases or 'task types' for embeddings, such

- [EmbeddingConfig](concepts/embeddingconfig.md) — A data structure used to encapsulate configuration parameters for an embedding m

- [Contract Testing Strategy](concepts/contract_testing_strategy.md) — A testing approach ensuring that adapter implementations correctly adhere to the

- [Integration Testing Strategy](concepts/integration_testing_strategy.md) — A testing approach that verifies interactions between multiple components, typic

- [Unit Testing Strategy](concepts/unit_testing_strategy.md) — A testing approach focused on isolated testing of individual components, often b

- [API Documentation Endpoints](concepts/api_documentation_endpoints.md) — Automatically generated API documentation available via Swagger UI, ReDoc, and O

- [Docker](concepts/docker.md) — A platform for developing, shipping, and running applications in containers.

- [Structlog](concepts/structlog.md) — A Python library for structured logging.

- [Passlib](concepts/passlib.md) — A password hashing library for Python, including bcrypt support.

- [Python JOSE](concepts/python_jose.md) — A Python library for JSON Object Signing and Encryption (JOSE).

- [Python Multipart](concepts/python_multipart.md) — A Python library for parsing multipart/form-data requests.

- [arq](concepts/arq.md) — An ASGI-compatible asynchronous task queue for Python (Phase 3).

- [Python Magic](concepts/python_magic.md) — A Python wrapper for `libmagic`, used for identifying file types (Phase 3).

- [HTTPX](concepts/httpx.md) — A fully featured HTTP client for Python, supporting HTTP/1.1 and HTTP/2.

- [Pydantic Settings](concepts/pydantic_settings.md) — A library for managing application settings, integrating with Pydantic for valid

- [Pydantic](concepts/pydantic.md) — A data validation and settings management library, used for defining data models

- [Uvicorn](concepts/uvicorn.md) — A lightning-fast ASGI server, used to run the FastAPI application.

- [AsyncPG](concepts/asyncpg.md) — An asynchronous PostgreSQL database driver for Python, used with SQLAlchemy for 

- [SQLAlchemy](concepts/sqlalchemy.md) — An SQL toolkit and Object Relational Mapper (ORM) for Python, used for database 

- [Python 3.13+](concepts/python_313.md) — The required Python version for the project.

- [Hatchling](concepts/hatchling.md) — A modern, standards-compliant Python build backend used by the project.

- [Mypy](concepts/mypy.md) — A static type checker for Python, used to enforce type hints and catch type-rela

- [Adapter Implementations](concepts/adapter_implementations.md) — Concrete implementations of Port Interfaces, using specific technologies (e.g., 

- [Port Interfaces](concepts/port_interfaces.md) — Abstract interfaces defining the contract for interactions with external systems

- [Service Layer](concepts/service_layer.md) — The application layer containing the core business logic and domain entities.

- [API Layer](concepts/api_layer.md) — The outermost layer of the application responsible for handling external request

- [Clean Architecture](concepts/clean_architecture.md) — An architectural principle promoting separation of concerns, making the system i

- [Knowledge Management API Project](concepts/knowledge_management_api_project.md) — The core API for a Knowledge Management Center, built as a Python FastAPI applic

- [Document ingestion](concepts/document_ingestion.md) — Process of taking documents (PDF, plain text, source code), chunking, deduplicat

- [Multi-source ingestion connectors](concepts/multi-source_ingestion_connectors.md) — Connectors enabling ingestion from sources like S3, Kafka, RabbitMQ, folder-watc

- [Production Hardening (Phase 10)](concepts/production_hardening_phase_10.md) — The final phase, focusing on operational readiness, observability, and CI/CD.

- [FastMCP Server (Phase 9)](concepts/fastmcp_server_phase_9.md) — Phase for integrating the AI agent server as the final feature add-on.

- [Admin UI + API Keys (Phase 8)](concepts/admin_ui_api_keys_phase_8.md) — Phase for developing administrative features and API key management.

- [Core Micro UIs (Phase 7)](concepts/core_micro_uis_phase_7.md) — Phase for implementing the daily-use frontend interfaces.

- [Frontend Shell + Shared Packages (Phase 6)](concepts/frontend_shell_shared_packages_phase_6.md) — Phase for establishing the micro-frontend base and shared UI dependencies.

- [BFF + WebSocket (Phase 5)](concepts/bff_websocket_phase_5.md) — Phase for developing the Backend For Frontend and real-time communication featur

- [Search (Phase 4)](concepts/search_phase_4.md) — Phase for implementing the primary user-facing search functionality.

- [Ingestion Pipeline (Phase 3)](concepts/ingestion_pipeline_phase_3.md) — Phase dedicated to building the data processing and indexing pipeline.

- [Core API + Auth (Phase 2)](concepts/core_api_auth_phase_2.md) — Phase focused on establishing the core backend API and cross-cutting authenticat

- [Infrastructure + Scaffolding (Phase 1)](concepts/infrastructure_scaffolding_phase_1.md) — The initial phase of project setup, including environment provisioning and defin

- [pub/sub relay](concepts/pubsub_relay.md) — A messaging pattern used to broadcast events, particularly for real-time notific

- [session management](concepts/session_management.md) — The process of tracking and maintaining user sessions.

- [vector store](concepts/vector_store.md) — The database pattern optimized for storing and querying high-dimensional vector 

- [document content storage](concepts/document_content_storage.md) — The storage pattern for raw text and chunked document content with flexible meta

- [relational metadata storage](concepts/relational_metadata_storage.md) — The storage pattern for structured data like domains, documents, jobs, users, an

- [Structured JSON Logging](concepts/structured_json_logging.md) — A logging standard required for diagnosing production issues effectively.

- [Kubernetes deployment](concepts/kubernetes_deployment.md) — An open-source container orchestration system, a target for production hardening

- [Docker Compose deployment](concepts/docker_compose_deployment.md) — A method for defining and running multi-container Docker applications, required 

- [HttpOnly session cookie](concepts/httponly_session_cookie.md) — A security measure for session management in the BFF, preventing client-side Jav

- [RBAC](concepts/rbac.md) — Role-Based Access Control, defining minimum 'km-admin' and 'km-reader' roles.

- [Micro-frontend architecture](concepts/micro-frontend_architecture.md) — An architectural style enabling independent development and deployment of UI com

- [EmbeddingPort abstraction](concepts/embeddingport_abstraction.md) — An architectural abstraction layer for text embedding providers, allowing swappi

- [VectorStorePort abstraction](concepts/vectorstoreport_abstraction.md) — An architectural abstraction layer for vector database interactions, crucial for

- [AI Agent Integration](concepts/ai_agent_integration.md) — A new system capability allowing external Artificial Intelligence agents to prog

- [Vue Shell](concepts/vue_shell.md) — The main frontend application, built with Vue.js, hosting Micro UIs.

- [Ingestion Worker](concepts/ingestion_worker.md) — A Python service handling asynchronous ingestion jobs, often consuming from mess

- [Phase 1 (project scaffolding)](concepts/phase_1_project_scaffolding.md) — The initial project setup phase, establishing configuration and deployment patte

- [Phase 2 (Ingestion pipeline foundation)](concepts/phase_2_ingestion_pipeline_foundation.md) — The development phase for laying the groundwork of the data ingestion system.

- [Phase 3 (Micro-frontend shell)](concepts/phase_3_micro-frontend_shell.md) — The development phase for the micro-frontend host application.

- [Phase 2 (Auth infrastructure)](concepts/phase_2_auth_infrastructure.md) — The development phase dedicated to establishing robust authentication mechanisms

- [Phase 1 (Core API skeleton)](concepts/phase_1_core_api_skeleton.md) — The initial development phase focusing on the foundational structure of the Core

- [Metadata](concepts/metadata.md) — Descriptive information about documents, stored in PostgreSQL.

- [Content](concepts/content.md) — The raw document data stored in MongoDB.

- [MongoDB + PostgreSQL Dual-Write Inconsistency](concepts/mongodb_postgresql_dual-write_inconsistency.md) — A significant pitfall where non-atomic writes to both MongoDB (for content) and 

- [PersistentVolumeClaim](concepts/persistentvolumeclaim.md) — A request for storage in Kubernetes, replacing host paths used in Docker Compose

- [Service discovery](concepts/service_discovery.md) — The process by which applications and microservices locate network services.

- [Docker Compose Hardcoded Service Discovery Breaking Kubernetes Migration](concepts/docker_compose_hardcoded_service_discovery_breaking_kubernetes_migration.md) — A significant pitfall where services reference each other by Docker Compose serv

- [Embedding service](concepts/embedding_service.md) — The component responsible for generating vector embeddings for documents and que

- [Gemini API](concepts/gemini_api.md) — Google's LLM provider API, specifically identified for its unique parameters pro

- [LLM Provider Lock-In Through Gemini API Shape Leakage](concepts/llm_provider_lock-in_through_gemini_api_shape_leakage.md) — A critical pitfall where the embedding service code becomes tightly coupled to s

- [Keycloak Token Propagation Gap](concepts/keycloak_token_propagation_gap.md) — A critical security pitfall where the BFF validates Keycloak JWTs but fails to f

- [Ingestion pipeline](concepts/ingestion_pipeline.md) — The system responsible for processing and storing incoming documents into the pl

- [Dead Letter Queue (DLQ)](concepts/dead_letter_queue_dlq.md) — A high-priority pending implementation for handling failed asynchronous tasks.

- [Async Ingestion Poison Pills](concepts/async_ingestion_poison_pills.md) — A critical pitfall where malformed or problematic documents halt the asynchronou

- [keycloak-js](concepts/keycloak-js.md) — The JavaScript adapter library for Keycloak, used in the shell application.

- [BFF (Backend-for-Frontend)](concepts/bff_backend-for-frontend.md) — A backend service handling requests from front-ends, responsible for token valid

- [Shell (Host App)](concepts/shell_host_app.md) — The main application responsible for owning the Keycloak instance and managing t

- [Micro-UI](concepts/micro-ui.md) — Independently deployable front-end applications that compose the overall user in

- [Micro-Frontend Auth Token Chaos](concepts/micro-frontend_auth_token_chaos.md) — A critical pitfall where multiple independently deployed micro-UIs attempt to ma

- [ruff](concepts/ruff.md) — A fast Python linter, also proposed for enforcing architectural rules regarding 

- [import-linter](concepts/import-linter.md) — A tool proposed for enforcing architectural rules, such as banning direct databa

- [Python ABC](concepts/python_abc.md) — Python's Abstract Base Classes mechanism, used to define abstract interfaces lik

- [Vector Store Tight Coupling](concepts/vector_store_tight_coupling.md) — A critical pitfall where core application logic becomes dependent on a specific 

- [Pitfalls Research](concepts/pitfalls_research.md) — The activity of identifying potential problems and challenges for the project.

- [Model Context Protocol](concepts/model_context_protocol.md) — A protocol for AI agents to query external knowledge bases as a tool call.

- [LLM embedding provider](concepts/llm_embedding_provider.md) — An external service or model responsible for generating vector embeddings from t

- [Vector Store Portability](concepts/vector_store_portability.md) — The design principle aiming for interchangeability of vector database implementa

- [Knowledge Management Platform](concepts/knowledge_management_platform.md) — An internal enterprise knowledge platform built around semantic search over mult

- [Redis sessions](concepts/redis_sessions.md) — The use of Redis as a scalable and persistent server-side store for managing use

- [HttpOnly session cookies](concepts/httponly_session_cookies.md) — A security mechanism for storing session identifiers in cookies that are inacces

- [Keycloak OAuth2](concepts/keycloak_oauth2.md) — An open-standard protocol for authorization used to secure the BFF layer, handli

- [Express/TypeScript](concepts/expresstypescript.md) — The chosen technology stack for developing the BFF layer, combining the Express.

- [BFF Foundation + OAuth2 Proxy](concepts/bff_foundation_oauth2_proxy.md) — The foundational stage of the BFF layer, encompassing project setup, Keycloak OA

- [SSE](concepts/sse.md) — Server-Sent Events, a transport mechanism for the MCP protocol over HTTP.

- [MCP protocol](concepts/mcp_protocol.md) — Machine-Composable Protocol, used by FastMCP to expose tools to AI agents.

- [ASGI](concepts/asgi.md) — Asynchronous Server Gateway Interface, a standard for Python async web servers, 

- [WebSocket](concepts/websocket.md) — A communication protocol providing full-duplex communication channels over a sin

- [REST](concepts/rest.md) — Architectural style for networked applications, used for communication between c

- [boto3](concepts/boto3.md) — AWS SDK for Python, used for S3 polling by Ingestion Worker.

- [pdfminer](concepts/pdfminer.md) — Python library for PDF document parsing.

- [NodeJS](concepts/nodejs.md) — JavaScript runtime environment used for the BFF.

- [JWT](concepts/jwt.md) — JSON Web Token, used for authenticating requests after OAuth2/OIDC flow.

- [3rd Party / AI Agents](concepts/3rd_party_ai_agents.md) — External systems or AI agents interacting with the platform via API Keys or the 

- [MICRO UIs](concepts/micro_uis.md) — Independent Vue 3 projects deployed as remotes via Module Federation, providing 

- [Edición colaborativa de documentos](concepts/edición_colaborativa_de_documentos.md) — Feature explicitly out of scope, as the KM platform is for reading/consulting, n

- [Generación de contenido por LLM (RAG synthesis)](concepts/generación_de_contenido_por_llm_rag_synthesis.md) — Feature explicitly out of scope, as the platform focuses on indexing and queryin

- [D004](concepts/d004.md) — Decision to treat Vue, Pinia, and Vue Router as singletons in Module Federation 

- [D003](concepts/d003.md) — Decision that the BFF uses HttpOnly session cookies for JWT security, preventing

- [D002](concepts/d002.md) — Decision to integrate FastMCP as an ASGI sub-app within the Core API to reduce o

- [D001](concepts/d001.md) — Decision to implement VectorStorePort and EmbeddingPort abstractions in Phase 1 

- [Phase 7: Core micro UIs](concepts/phase_7_core_micro_uis.md) — A project phase focused on implementing core user interface components as indepe

- [Phase 6: Frontend shell](concepts/phase_6_frontend_shell.md) — Phase establishing the Vue 3 Module Federation host and integrating the design s

- [Phase 5: BFF layer](concepts/phase_5_bff_layer.md) — A Node.js Backend-for-Frontend (BFF) layer designed to proxy Keycloak authentica

- [Ingestión Async con Job Tracking](concepts/ingestión_async_con_job_tracking.md) — Architectural pattern for handling large document processing asynchronously, pro

- [Module Federation con Singletons](concepts/module_federation_con_singletons.md) — Micro-frontend pattern ensuring single instances of core libraries (Vue, Pinia, 

- [BFF con HttpOnly Session Cookies](concepts/bff_con_httponly_session_cookies.md) — Architectural pattern where the BFF handles session cookies, keeping JWTs secure

- [Sistemas terceros](concepts/sistemas_terceros.md) — Target user role for systems integrating via REST API with API Key authenticatio

- [Agentes AI externos](concepts/agentes_ai_externos.md) — Target user role that accesses the knowledge base via FastMCP.

- [Usuarios finales](concepts/usuarios_finales.md) — Target user role responsible for searching and consulting documents.

- [Administradores](concepts/administradores.md) — Target user role responsible for managing knowledge domains, users, and API keys

- [Vue 3](concepts/vue_3.md) — JavaScript frontend framework used for the Frontend Shell and Micro UIs.

- [Fastify](concepts/fastify.md) — Web framework used for the BFF.

- [Python](concepts/python.md) — The primary language runtime for the Core API and Ingestion Worker components.

- [Milestone v0.1](concepts/milestone_v01.md) — Represents the complete planning phase for Project Initialization & Roadmap, wit

- [Phase 5](concepts/phase_5.md) — The next project phase, focusing on the BFF Layer (Node.js proxy with WebSocket)

- [PostgreSQL Full-Text Search](concepts/postgresql_full-text_search.md) — The underlying database technology used for implementing the BM25 Keyword Search

- [Metadata Filtering](concepts/metadata_filtering.md) — The capability to filter search results based on specific metadata attributes li

- [RRF Fusion](concepts/rrf_fusion.md) — Reciprocal Rank Fusion algorithm used to combine and re-rank results from multip

- [BM25 Keyword Search](concepts/bm25_keyword_search.md) — A search mode implemented using PostgreSQL full-text search for exact term and p

- [Search Engine](concepts/search_engine.md) — The overarching system built in Phase 4, providing various search functionalitie

- [Phase 4](concepts/phase_4.md) — The project phase dedicated to building the Search Engine module.

- [Phase 3](concepts/phase_3.md) — The preceding project phase, which Phase 4 depends on.

- [Ranking Feature](concepts/ranking_feature.md) — The system's ability to order search results by relevance and provide pagination

- [Domain Scoping Feature](concepts/domain_scoping_feature.md) — The capability to limit search results exclusively to documents belonging to spe

- [Filtered Search Feature](concepts/filtered_search_feature.md) — The ability to narrow down search results using specific metadata criteria (e.g.

- [Hybrid Search Feature](concepts/hybrid_search_feature.md) — The ability to combine the strengths of both semantic and keyword search methods

- [Semantic Search Feature](concepts/semantic_search_feature.md) — The ability of the search engine to find information based on conceptual meaning

- [PostgreSQL Database](concepts/postgresql_database.md) — The relational database used for storing document metadata and performing full-t

- [Search Analytics](concepts/search_analytics.md) — A medium-priority planned feature for logging and tracking search queries and me

- [Suggestions and Autocomplete](concepts/suggestions_and_autocomplete.md) — Medium-priority planned features to improve the search experience.

- [Highlighting and Snippets](concepts/highlighting_and_snippets.md) — A feature to highlight matching terms and generate contextual text snippets in s

- [Domain Access Enforcement](concepts/domain_access_enforcement.md) — A security mechanism validating user access to specific domains, returning a 403

- [Search Response](concepts/search_response.md) — The output structure containing ranked, paginated search results with relevance 

- [Search Request](concepts/search_request.md) — The input structure containing query, domain IDs, and filters for a search opera

- [Phase 4 Search Engine](concepts/phase_4_search_engine.md) — The overall project phase dedicated to building the search engine.

- [Phase 4 (Search Engine)](concepts/phase_4_search_engine.md) — The subsequent phase of the project, which will leverage the ingested documents 

- [Chunk](concepts/chunk.md) — A data structure representing a piece of text with an associated vector embeddin

- [Domain-Based Collections](concepts/domain-based_collections.md) — The architectural decision to organize data within ChromaDB into separate collec

- [Semantic Chunking Default](concepts/semantic_chunking_default.md) — The architectural decision to use semantic chunking as the primary strategy due 

- [Synchronous Processing (MVP)](concepts/synchronous_processing_mvp.md) — The initial architectural choice for the Minimum Viable Product (MVP) to process

- [Async Workers (ARQ)](concepts/async_workers_arq.md) — An asynchronous task queue system planned for future implementation to handle qu

- [Job Progress](concepts/job_progress.md) — A metric (0-100%) used to track the completion percentage of an ingestion job as

- [Document Status](concepts/document_status.md) — A set of predefined states ('pending', 'processing', 'done', 'failed') that repr

- [Embeddings (Gemini)](concepts/embeddings_gemini.md) — The process of generating vector representations (embeddings) of document chunks

- [Task 3.8: Vector Store Integration](concepts/task_38_vector_store_integration.md) — The component responsible for interacting with a vector database to store docume

- [Task 3.7: MongoDB Integration](concepts/task_37_mongodb_integration.md) — The planned integration with MongoDB for persistent storage of raw document cont

- [Task 3.6: Error Handling & DLQ](concepts/task_36_error_handling_dlq.md) — The system components designed to manage, track, and recover from errors during 

- [GET /v1/ingest/document/{id}/status](concepts/get_v1ingestdocumentidstatus.md) — A specific REST API endpoint to retrieve the status of a specific document withi

- [GET /v1/ingest/{job_id}](concepts/get_v1ingestjob_id.md) — A specific REST API endpoint to retrieve the current status and progress of an o

- [POST /v1/ingest/text](concepts/post_v1ingesttext.md) — A specific REST API endpoint for submitting raw text content for ingestion, acce

- [POST /v1/ingest](concepts/post_v1ingest.md) — A specific REST API endpoint for uploading files (e.g., PDF) to initiate the doc

- [Task 3.5: REST API Endpoints](concepts/task_35_rest_api_endpoints.md) — The set of HTTP endpoints exposed by the ingestion pipeline for external systems

- [Task 3.4: Ingestion Service](concepts/task_34_ingestion_service.md) — The core business logic component of the pipeline, responsible for orchestrating

- [ChunkingConfig](concepts/chunkingconfig.md) — A configuration object used to define parameters for document chunking, includin

- [Fixed-Size Chunking](concepts/fixed-size_chunking.md) — A document chunking strategy that divides content into chunks of a predefined ch

- [Task 3.3: Document Chunking](concepts/task_33_document_chunking.md) — The sub-process of dividing extracted document content into smaller, manageable 

- [Task 3.2: Text Extraction](concepts/task_32_text_extraction.md) — The sub-process within the ingestion pipeline responsible for extracting textual

- [Task 3.1: Planning & Architecture](concepts/task_31_planning_architecture.md) — The initial stage of Phase 3, involving the creation of plans, data flow diagram

- [Phase 3 — Document Ingestion Pipeline](concepts/phase_3_document_ingestion_pipeline.md) — The third phase of the project, focused on building a robust system for extracti

- [Semantic Chunking](concepts/semantic_chunking.md) — A document chunking strategy that prioritizes respecting natural linguistic boun

- [Embedding Dimension](concepts/embedding_dimension.md) — A numerical value representing the dimensionality of the generated vector embedd

- [IngestionJob](concepts/ingestionjob.md) — A record representing the state and progress of a single document ingestion task

- [Motor](concepts/motor.md) — An asynchronous MongoDB driver for Python, used to facilitate interaction with M

- [python-docx](concepts/python-docx.md) — An external Python library used for creating, reading, and updating Microsoft Wo

- [PyMuPDF](concepts/pymupdf.md) — An external high-performance Python library (used via the 'fitz' module) for PDF

- [ARQ Worker](concepts/arq_worker.md) — An asynchronous task processing system that picks up and executes document inges

- [Local Folder Watcher](concepts/local_folder_watcher.md) — A component responsible for monitoring a local file system folder and automatica

- [S3](concepts/s3.md) — An ingestion source from which documents can be submitted via S3 prefix events.

- [Phase 3 Document Ingestion Pipeline](concepts/phase_3_document_ingestion_pipeline.md) — The third phase of the project, dedicated to implementing the full pipeline for 

- [Domain-Based Access Control Decision](concepts/domain-based_access_control_decision.md) — The architectural decision to implement granular permissions at the domain level

- [Dual Auth Strategy Decision](concepts/dual_auth_strategy_decision.md) — The architectural decision to implement both JWT-based authentication for web us

- [Repository/Service Pattern Decision](concepts/repositoryservice_pattern_decision.md) — The architectural decision to separate business logic into service layers and da

- [SQLAlchemy 2.0 Async Decision](concepts/sqlalchemy_20_async_decision.md) — The architectural decision to use SQLAlchemy 2.0 with its native async support f

- [JWT Flow](concepts/jwt_flow.md) — The process by which JSON Web Tokens are validated and used to authenticate user

- [Authentication & Authorization System](concepts/authentication_authorization_system.md) — The overall system responsible for verifying user identities and controlling acc

- [API Endpoints](concepts/api_endpoints.md) — The various HTTP interfaces exposed by the Core API for interacting with system 

- [Paginated Responses](concepts/paginated_responses.md) — A standardized response format for list endpoints that includes pagination metad

- [Swagger UI Documentation](concepts/swagger_ui_documentation.md) — Interactive API documentation available at the /docs endpoint, detailing all API

- [Token Refresh](concepts/token_refresh.md) — A security requirement for maintaining user sessions transparently without re-lo

- [Domain CRUD with JWT Auth](concepts/domain_crud_with_jwt_auth.md) — A core feature allowing administrators to perform Create, Read, Update, and Dele

- [Phase 3: Document Ingestion Pipeline](concepts/phase_3_document_ingestion_pipeline.md) — The subsequent project phase after Phase 2, focusing on document ingestion capab

- [Alembic](concepts/alembic.md) — A database migration tool for SQLAlchemy.

- [Domain-Based Access Control](concepts/domain-based_access_control.md) — An architectural decision to implement granular permissions per domain, allowing

- [Dual Auth Strategy](concepts/dual_auth_strategy.md) — An architectural decision to support both JWT for web sessions (via Keycloak) an

- [Dependency Injection](concepts/dependency_injection.md) — An architectural pattern used with FastAPI for managing and providing dependenci

- [Repository Pattern](concepts/repository_pattern.md) — An architectural decision to encapsulate data access and business logic within s

- [Tests](concepts/tests.md) — Unit and integration tests to ensure code quality and correctness, targeting hig

- [Pydantic v2 schemas](concepts/pydantic_v2_schemas.md) — The version 2 Pydantic schemas used for data modeling and validation, including 

- [Request/Response Schemas](concepts/requestresponse_schemas.md) — Pydantic models used for input validation and output serialization for all API e

- [Pagination Utilities](concepts/pagination_utilities.md) — Helper functions and schemas for handling paginated list responses across API en

- [API Key validation](concepts/api_key_validation.md) — The process of verifying API keys presented by external integrations.

- [SHA-256 hashing](concepts/sha-256_hashing.md) — The cryptographic hashing algorithm used for storing API keys securely.

- [API Key generation](concepts/api_key_generation.md) — The process of creating secure random API keys.

- [API Key Framework](concepts/api_key_framework.md) — A system for generating, validating, and managing API keys for external integrat

- [Domain CRUD Endpoints](concepts/domain_crud_endpoints.md) — API endpoints for creating, reading, updating, and deleting domain resources, in

- [PermissionDenied exception handling](concepts/permissiondenied_exception_handling.md) — Mechanism for handling unauthorized access attempts by raising a specific except

- [Role-Based Access Control](concepts/role-based_access_control.md) — A security mechanism ensuring that access to API endpoints is governed by the us

- [JWT token validation](concepts/jwt_token_validation.md) — The process of verifying the authenticity and integrity of JWT tokens.

- [JWKS fetching](concepts/jwks_fetching.md) — The process of retrieving JSON Web Key Sets from Keycloak for JWT validation.

- [JWT Middleware](concepts/jwt_middleware.md) — Middleware responsible for handling JWT authentication.

- [Async session management](concepts/async_session_management.md) — The system for handling asynchronous database sessions.

- [SQLAlchemy async engine](concepts/sqlalchemy_async_engine.md) — The asynchronous engine for SQLAlchemy database connections.

- [Database Configuration](concepts/database_configuration.md) — The setup for connecting to and managing the PostgreSQL database.

- [UUID primary keys](concepts/uuid_primary_keys.md) — A design choice to use UUIDs as primary keys for models.

- [SQLAlchemy 2.0](concepts/sqlalchemy_20.md) — The ORM version used for database interactions, supporting async operations.

- [Database Models](concepts/database_models.md) — The collection of SQLAlchemy 2.0 async models representing the core entities sto

- [Phase 2 — Core API Foundation](concepts/phase_2_core_api_foundation.md) — A project phase focused on establishing the core API infrastructure.

- [Phase 1](concepts/phase_1.md) — The preceding phase of the project, which Phase 2 depends on.

- [Knowledge Domain](concepts/knowledge_domain.md) — A logical container or scope within the system where ingested documents are cate

- [Pagination](concepts/pagination.md) — A method to retrieve lists of items in smaller, structured pages using parameter

- [Automatic Documentation](concepts/automatic_documentation.md) — The process of auto-generating API documentation using Swagger UI with correct s

- [Domain Management](concepts/domain_management.md) — A key feature of the API for creating, viewing, updating, and deleting knowledge

- [Role-Based Access Control (RBAC)](concepts/role-based_access_control_rbac.md) — System for controlling access to resources based on assigned user roles like km-

- [JWT Authentication](concepts/jwt_authentication.md) — The primary authentication method, involving the verification of JSON Web Tokens

- [Dual Authentication](concepts/dual_authentication.md) — An authentication system combining JWT for web users and API Keys for integratio

- [REST API](concepts/rest_api.md) — A primary interface for document ingestion, supporting file uploads and inline t

- [Core API Foundation](concepts/core_api_foundation.md) — The primary goal of Phase 2, establishing the fundamental REST API with authenti

- [Phase 2](concepts/phase_2.md) — The current phase of the project, titled 'Core API Foundation', aimed at buildin

- [MyPy](concepts/mypy.md) — The static type checker configured for code quality checks.

- [Ruff](concepts/ruff.md) — An extremely fast Python linter and formatter, used for code quality and style e

- [Pytest](concepts/pytest.md) — A testing framework for Python, used for running unit and integration tests.

- [Phase 2: Core API Foundation](concepts/phase_2_core_api_foundation.md) — The subsequent project phase focusing on database models, JWT middleware, domain

- [Code Quality](concepts/code_quality.md) — Adherence to code quality standards, including type hints, comprehensive docstri

- [Unit Tests](concepts/unit_tests.md) — A set of 30 unit tests specifically validating the `VectorStorePort` and `Embedd

- [Environment Configuration](concepts/environment_configuration.md) — The practice of externalizing all URLs and credentials as environment variables 

- [Docker Compose Infrastructure](concepts/docker_compose_infrastructure.md) — The setup and configuration of core services using Docker Compose to ensure a re

- [Phase 1: Bootstrap Infrastructure](concepts/phase_1_bootstrap_infrastructure.md) — The initial project phase focused on establishing foundational infrastructure an

- [Phase 1 Verification Report](concepts/phase_1_verification_report.md) — The report summarizing the successful completion and verification of Phase 1: Bo

- [.env.example](concepts/envexample.md) — A template file containing example environment variables for project configurati

- [Batch Processing (Embeddings)](concepts/batch_processing_embeddings.md) — An architectural decision that embedding generation should handle batching inter

- [One Collection Per Domain](concepts/one_collection_per_domain.md) — An architectural decision for the vector store to maintain separate collections 

- [Async Everything](concepts/async_everything.md) — An architectural decision to use asynchronous operations for all I/O, improving 

- [Phase 1 Infrastructure](concepts/phase_1_infrastructure.md) — The initial phase of the Knowledge Management Center project, focused on setting

- [Phase 2 Core API Foundation](concepts/phase_2_core_api_foundation.md) — The current phase of the project, establishing the foundational elements of the 

- [Use monorepo structure](concepts/use_monorepo_structure.md) — A structural decision to organize the codebase into a monorepo for better collab

- [Use abstract ports for vector store and embedding](concepts/use_abstract_ports_for_vector_store_and_embedding.md) — A critical architectural decision to define abstract interfaces for vector store

- [Externalize configuration with environment variables](concepts/externalize_configuration_with_environment_variables.md) — A core decision to manage all configurable parameters via environment variables 

- [Use Docker Compose for infrastructure](concepts/use_docker_compose_for_infrastructure.md) — A core decision to use Docker Compose to define and manage all local infrastruct

- [Adapter Pattern](concepts/adapter_pattern.md) — A design pattern employed to provide a unified interface for disparate systems (

- [Health Check Endpoints](concepts/health_check_endpoints.md) — Standardized `/health` endpoints for services to report their operational status

- [Definition of Done](concepts/definition_of_done.md) — A checklist of deliverables and conditions that must be met for Phase 1 to be co

- [Risks](concepts/risks.md) — Identified potential issues for Phase 1, along with their impact and mitigation 

- [Dependencies](concepts/dependencies.md) — External requirements and prerequisites for the completion of Phase 1.

- [Tasks](concepts/tasks.md) — Specific, actionable items required to achieve the goals of Phase 1.

- [Success Criteria](concepts/success_criteria.md) — Measurable conditions that define the successful completion of Phase 1.

- [Abstractions](concepts/abstractions.md) — Critical interfaces like VectorStorePort and EmbeddingPort implemented to preven

- [Infrastructure as Code](concepts/infrastructure_as_code.md) — The practice of defining and managing infrastructure components using code, spec

- [Monorepo Structure](concepts/monorepo_structure.md) — The project's organizational structure as a monorepo, comprising independent pac

- [Local Development Environment](concepts/local_development_environment.md) — The goal state where all services run with one command and are reachable, with p

- [Phase 1 Bootstrap Infrastructure](concepts/phase_1_bootstrap_infrastructure.md) — The initial phase of the project, focused on setting up the core development env

- [Backup Strategies](concepts/backup_strategies.md) — Plans for data backup and recovery, deferred to Phase 10.

- [Advanced Monitoring](concepts/advanced_monitoring.md) — Advanced system monitoring using tools like Prometheus/Grafana, deferred to Phas

- [CI/CD Pipeline](concepts/cicd_pipeline.md) — An automated process for continuous integration and continuous deployment, encom

- [Contract Testing](concepts/contract_testing.md) — A testing strategy to ensure that concrete adapters correctly adhere to the inte

- [Integration Testing](concepts/integration_testing.md) — A testing strategy that verifies the interactions between services within a Dock

- [Unit Testing](concepts/unit_testing.md) — A testing strategy that isolates and tests individual components using mocks for

- [Collection (VectorDB)](concepts/collection_vectordb.md) — An isolated data storage unit within vector databases, used to separate domain-s

- [OpenAIAdapter](concepts/openaiadapter.md) — An adapter implementing EmbeddingPort for OpenAI.

- [GeminiAdapter](concepts/geminiadapter.md) — An adapter implementing EmbeddingPort for Gemini.

- [QdrantAdapter](concepts/qdrantadapter.md) — A planned concrete implementation of the `VectorStorePort` using Qdrant, intende

- [ChromaDBAdapter](concepts/chromadbadapter.md) — A concrete implementation of the `VectorStorePort` using ChromaDB, intended for 

- [Core API / Ingestion](concepts/core_api_ingestion.md) — The central domain logic layer that interacts with external services through def

- [Ollama](concepts/ollama.md) — A local LLM provider mentioned as a potential target for switching embedding mod

- [OpenAI](concepts/openai.md) — An alternative LLM provider mentioned as a potential target for switching embedd

- [D5: Redis Explicitly Added](concepts/d5_redis_explicitly_added.md) — A technical decision to include Redis as a core infrastructure component in Phas

- [D4: Docker Compose for MVP](concepts/d4_docker_compose_for_mvp.md) — A technical decision to use Docker Compose for the Minimum Viable Product (MVP) 

- [D3: EmbeddingPort Dimension Property](concepts/d3_embeddingport_dimension_property.md) — A technical decision to define 'dimension' as an abstract property within Embedd

- [D2: One-to-one Collection-Domain](concepts/d2_one-to-one_collection-domain.md) — A technical decision to map each logical domain to a unique collection (or index

- [D1: Async VectorStorePort](concepts/d1_async_vectorstoreport.md) — A technical decision to make all methods of the VectorStorePort asynchronous due

- [Externalized Configuration](concepts/externalized_configuration.md) — The principle of managing all configuration (URLs, credentials) via environment 

- [Docker Compose Unified Environment](concepts/docker_compose_unified_environment.md) — A standardized development and integration testing environment built on Docker C

- [Ports & Adapters Architecture](concepts/ports_adapters_architecture.md) — An architectural pattern ensuring the domain layer remains decoupled from extern

- [Phase 1 - Bootstrap Infrastructure](concepts/phase_1_-_bootstrap_infrastructure.md) — The initial phase of the project focused on establishing foundational infrastruc

- [Concern: Pin FastMCP exact version](concepts/concern_pin_fastmcp_exact_version.md) — A pre-Phase 9 concern to pin the exact version of FastMCP and verify its API aga

- [Concern: Evaluate Module Federation plugins](concepts/concern_evaluate_module_federation_plugins.md) — A pre-Phase 6 concern to evaluate and pin a specific version of a Vite Module Fe

- [Concern: Verify ChromaDB 0.5 collection API](concepts/concern_verify_chromadb_05_collection_api.md) — A pre-Phase 3 concern to check for breaking changes in ChromaDB's 0.5 API.

- [Concern: Verify Gemini text-embedding-004 batch size limits](concepts/concern_verify_gemini_text-embedding-004_batch_size_limits.md) — A pre-Phase 3 concern to confirm batch size and rate limits for the embedding se

- [Concern: Deployment hostnames needed](concepts/concern_deployment_hostnames_needed.md) — A pre-Phase 2 concern about requiring specific hostnames for CORS and Keycloak r

- [Concern: Keycloak `kmplatform` client readiness](concepts/concern_keycloak_kmplatform_client_readiness.md) — A pre-Phase 2 concern regarding the configuration and readiness of the Keycloak 

- [@module-federation/vite](concepts/module-federationvite.md) — Another plugin for Vite enabling Module Federation, under evaluation for maturit

- [@originjs/vite-plugin-federation](concepts/originjsvite-plugin-federation.md) — A Vite plugin that implements Module Federation, allowing the shell application 

- [Gemini text-embedding-004](concepts/gemini_text-embedding-004.md) — A text embedding model from Google, with pending concerns regarding batch size a

- [Decision: Vue, Pinia, Vue Router declared singleton:true](concepts/decision_vue_pinia_vue_router_declared_singletontrue.md) — A decision to ensure these frontend libraries are shared as singletons across Mo

- [Vue Router](concepts/vue_router.md) — The official routing library for Vue.js, managing client-side navigation and map

- [Pinia](concepts/pinia.md) — A lightweight state management library integrated into the Vue application.

- [Vue](concepts/vue.md) — The JavaScript framework used to build the single-page application user interfac

- [Decision: BFF uses HttpOnly session cookies](concepts/decision_bff_uses_httponly_session_cookies.md) — A security decision to prevent JWT exposure to browser JavaScript.

- [BFF](concepts/bff.md) — Backend-for-Frontend, implemented using Node.js.

- [Decision: FastMCP mounts as ASGI sub-app on Core API](concepts/decision_fastmcp_mounts_as_asgi_sub-app_on_core_api.md) — A decision to integrate FastMCP directly into the Core API process.

- [Core API](concepts/core_api.md) — A Python service responsible for the core business logic and API endpoints.

- [Decision: VectorStorePort and EmbeddingPort abstractions must be defined in Phase 1](concepts/decision_vectorstoreport_and_embeddingport_abstractions_must_be_defined_in_phase_1.md) — A key architectural decision to establish core port abstractions early to preven

- [Postgres](concepts/postgres.md) — A relational database service used in the project's Docker Compose setup.

- [Documentation](concepts/documentation.md) — The ongoing process of creating and updating project documentation, including AP

- [Health endpoints](concepts/health_endpoints.md) — API endpoints (e.g., `/health`) used to monitor the status and readiness of serv

- [Environment config](concepts/environment_config.md) — The configuration system for environment variables, exemplified by a `.env.examp

- [Monorepo structure](concepts/monorepo_structure.md) — The chosen repository organization for the project, encompassing multiple servic

- [Phase 1 – Bootstrap infrastructure](concepts/phase_1_bootstrap_infrastructure.md) — The initial phase of the project, focused on setting up foundational infrastruct

- [Core value](concepts/core_value.md) — The fundamental principle guiding the project: authenticated users finding knowl

- [Project State](concepts/project_state.md) — The overall status and direction of the project, including progress, metrics, an

- [API Key](concepts/api_key.md) — Authentication token used by 3rd Party/AI Agents and for specific administrative

- [EmbeddingPort](concepts/embeddingport.md) — An interface (port) defining the contract for embedding operations, implemented 

- [VectorStorePort](concepts/vectorstoreport.md) — An interface (port) defining the contract for vector store operations, implement

- [Swagger UI](concepts/swagger_ui.md) — An interactive API documentation tool automatically generated from OpenAPI speci

- [Luminous Knowledge design system](concepts/luminous_knowledge_design_system.md) — The defined design system whose principles and components are implemented in the

- [Monorepo](concepts/monorepo.md) — A software development strategy where code for multiple projects is stored in a 

- [Phase 10: Production hardening](concepts/phase_10_production_hardening.md) — Final phase focused on Docker Compose finalization, logging, and observability.

- [Phase 9: MCP integration](concepts/phase_9_mcp_integration.md) — Phase integrating the FastMCP server to expose search tools to AI agents.

- [Phase 8: Admin and API keys](concepts/phase_8_admin_and_api_keys.md) — Phase implementing admin micro UIs, API key lifecycle management, and rate limit

- [Phase 4: Search engine](concepts/phase_4_search_engine.md) — Phase implementing semantic, hybrid, and filtered search functionalities.

- [Phase 3: Document ingestion pipeline](concepts/phase_3_document_ingestion_pipeline.md) — Phase covering multi-source ingestion, chunking, and embedding generation for do

- [Phase 2: Core API foundation](concepts/phase_2_core_api_foundation.md) — Phase focused on building the FastAPI core API with Keycloak authentication and 

- [Phase 1: Bootstrap infrastructure](concepts/phase_1_bootstrap_infrastructure.md) — The initial phase focusing on setting up the monorepo, Docker Compose, port abst

- [Horizontal Pod Autoscaler (HPA)](concepts/horizontal_pod_autoscaler_hpa.md) — Used in Kubernetes to automatically scale the number of pods based on resource u

- [AI Agent Tools](concepts/ai_agent_tools.md) — Specific functions exposed by the MCP Server for AI agents to interact with the 

- [Rate Limiting](concepts/rate_limiting.md) — A mechanism implemented by APIs to control the number of requests a client can m

- [Paginating Search Results](concepts/paginating_search_results.md) — Functionality to retrieve search results in paginated format.

- [Search Metadata Filters](concepts/search_metadata_filters.md) — Ability to filter search results by document metadata such as type, date, source

- [Embedding Dimension Metadata](concepts/embedding_dimension_metadata.md) — Storing the dimension of embeddings as collection metadata in the vector store.

- [Ingestion Job Status API](concepts/ingestion_job_status_api.md) — An API endpoint to query the status of document ingestion jobs (pending/processi

- [Document Processing](concepts/document_processing.md) — The internal workflow of parsing, extracting content, chunking, and indexing an 

- [Session Persistence](concepts/session_persistence.md) — User session persistence across browser reloads.

- [Environment Variables](concepts/environment_variables.md) — Configuration settings externalized from the codebase and loaded from the enviro

- [Health Endpoints](concepts/health_endpoints.md) — A requirement for each service to expose a `/health` endpoint returning a 200 st

- [Webhooks](concepts/webhooks.md) — A medium-priority planned feature for configurable HTTP notifications.

- [Email Notifications](concepts/email_notifications.md) — A medium-priority planned feature for email-based event notifications.

- [Real-time Ingestion Notifications](concepts/real-time_ingestion_notifications.md) — WebSocket-based notifications provided by the BFF to the frontend about document

- [Luminous Knowledge Design System](concepts/luminous_knowledge_design_system.md) — The design guidelines and aesthetic principles for the frontend, including Glass

- [OpenAPI Documentation (Swagger UI)](concepts/openapi_documentation_swagger_ui.md) — Automatically generated interactive documentation for the Core API endpoints.

- [User Role](concepts/user_role.md) — Defines access levels within the system, such as 'km-admin' and 'km-reader'.

- [Admin Role](concepts/admin_role.md) — A user role with elevated permissions for administrative tasks like domain manag

- [Knowledge Domains Management](concepts/knowledge_domains_management.md) — Functionality for administrators to create, edit, delete, and manage user/role a

- [Reranking (Cross-encoder)](concepts/reranking_cross-encoder.md) — A post-search process to re-order search results for improved relevance using a 

- [Chunking](concepts/chunking.md) — The process of splitting documents into smaller, overlapping segments before gen

- [Embeddings Generation](concepts/embeddings_generation.md) — The process of converting document chunks into numerical vector representations.

- [Document Ingestion Pipeline](concepts/document_ingestion_pipeline.md) — The system responsible for ingesting, processing, chunking, and indexing documen

- [Dead Letter Queue](concepts/dead_letter_queue.md) — A queue for messages that could not be processed after a specified number of ret

- [Prometheus](concepts/prometheus.md) — Used for monitoring and alerting, typically integrated with Grafana (v2 requirem

- [Grafana](concepts/grafana.md) — Used for creating dashboards and visualizing observability data (v2 requirement)

- [OpenTelemetry](concepts/opentelemetry.md) — Used for distributed tracing across services (v2 requirement).

- [Helm Charts](concepts/helm_charts.md) — High-priority missing packaging for reproducible Kubernetes deployments.

- [Ollama LLM Provider](concepts/ollama_llm_provider.md) — Planned support for using local Ollama models as an alternative LLM provider (v2

- [OpenAI LLM Provider](concepts/openai_llm_provider.md) — Planned support for using OpenAI models as an alternative LLM provider (v2 requi

- [FastMCP Framework](concepts/fastmcp_framework.md) — The framework used to integrate AI agent tools into the Core API.

- [Module Federation](concepts/module_federation.md) — A webpack feature utilized to allow the Frontend Shell to host and dynamically l

- [NodeJS Runtime](concepts/nodejs_runtime.md) — The runtime environment used for the BFF service.

- [FastAPI Framework](concepts/fastapi_framework.md) — The web framework used to build the Core API.

- [Gemini Embeddings](concepts/gemini_embeddings.md) — The default model used for generating document embeddings.

- [EmbeddingPort Abstraction](concepts/embeddingport_abstraction.md) — An abstraction layer for generating embeddings, ensuring flexibility in choosing

- [VectorStorePort Abstraction](concepts/vectorstoreport_abstraction.md) — An abstraction layer for interacting with vector databases, ensuring portability

- [Micro UIs](concepts/micro_uis.md) — Smaller, independent user interface components hosted within the Vue Shell.

- [JWT (JSON Web Token)](concepts/jwt_json_web_token.md) — The token format used by Keycloak for authentication and authorization.

- [Keycloak (OAuth2/OIDC)](concepts/keycloak_oauth2oidc.md) — Identity provider used for web user authentication.

- [Docker Compose Environment](concepts/docker_compose_environment.md) — Used for local development to run all services, including databases and messagin

- [Monorepo Architecture](concepts/monorepo_architecture.md) — The project will be structured as a monorepo containing independent services lik

- [granularity](concepts/granularity.md) — Configuration setting for granularity.

- [mode](concepts/mode.md) — Configuration setting for operation mode.

- [resolve_model_ids](concepts/resolve_model_ids.md) — Configuration setting for resolving model IDs.

- [agent_skills_config](concepts/agent_skills_config.md) — Category for agent skills configuration.

- [context_warnings](concepts/context_warnings.md) — Hook configuration setting for context warnings.

- [hooks_config](concepts/hooks_config.md) — Category for hook-related configuration settings.

- [skip_discuss](concepts/skip_discuss.md) — Workflow configuration setting for skipping discussion.

- [discuss_mode](concepts/discuss_mode.md) — Workflow configuration setting for the discussion mode.

- [research_before_questions](concepts/research_before_questions.md) — Workflow configuration setting for research before questions.

- [text_mode](concepts/text_mode.md) — Workflow configuration setting for enabling text mode.

- [ui_safety_gate](concepts/ui_safety_gate.md) — Workflow configuration setting for enabling UI safety gate.

- [ui_phase](concepts/ui_phase.md) — Workflow configuration setting for enabling UI phase.

- [node_repair_budget](concepts/node_repair_budget.md) — Workflow configuration setting for the budget for node repair.

- [node_repair](concepts/node_repair.md) — Workflow configuration setting for enabling node repair.

- [auto_advance](concepts/auto_advance.md) — Workflow configuration setting for enabling auto-advancement.

- [nyquist_validation](concepts/nyquist_validation.md) — Workflow configuration setting for enabling Nyquist validation.

- [verifier](concepts/verifier.md) — Workflow configuration setting for enabling verification.

- [plan_check](concepts/plan_check.md) — Workflow configuration setting for enabling plan checks.

- [research](concepts/research.md) — Workflow configuration setting for enabling research.

- [workflow_config](concepts/workflow_config.md) — Category for workflow-related configuration settings.

- [quick_branch_template](concepts/quick_branch_template.md) — Git configuration setting for quick branch naming template.

- [milestone_branch_template](concepts/milestone_branch_template.md) — Git configuration setting for milestone branch naming template.

- [phase_branch_template](concepts/phase_branch_template.md) — Git configuration setting for phase branch naming template.

- [branching_strategy](concepts/branching_strategy.md) — Git configuration setting for the branching strategy.

- [git_config](concepts/git_config.md) — Category for Git-related configuration settings.

- [exa_search](concepts/exa_search.md) — Configuration setting for using Exa Search.

- [firecrawl](concepts/firecrawl.md) — Configuration setting for using Firecrawl.

- [brave_search](concepts/brave_search.md) — Configuration setting for using Brave Search.

- [search_gitignored](concepts/search_gitignored.md) — Configuration setting for searching gitignored files.

- [parallelization](concepts/parallelization.md) — Configuration setting for parallel execution.

- [commit_docs](concepts/commit_docs.md) — Configuration setting indicating whether to commit generated documentation.

- [model_profile](concepts/model_profile.md) — Configuration setting for an unnamed model's profile.

- [uv como gestor de paquetes Python](concepts/uv_como_gestor_de_paquetes_python.md) — Decision to use uv as the Python package manager for superior speed and reproduc

- [BFF en NodeJS separado del Core API](concepts/bff_en_nodejs_separado_del_core_api.md) — Decision to separate the BFF (Node.js) from the Core API to decouple presentatio

- [API Keys en PostgreSQL](concepts/api_keys_en_postgresql.md) — Decision to store API Keys in PostgreSQL for consistency with existing relationa

- [Design system 'Luminous Knowledge' (DESIGN.md)](concepts/design_system_luminous_knowledge_designmd.md) — Decision to implement the 'Luminous Knowledge' design system (minimalism + glass

- [Micro-frontend (shell + micro UIs)](concepts/micro-frontend_shell_micro_uis.md) — Decision to adopt a micro-frontend architecture to allow independent evolution a

- [FastMCP para integración AI](concepts/fastmcp_para_integración_ai.md) — Decision to use FastMCP as the standard for AI integration, compatible with emer

- [FAISS descartado en favor de ChromaDB](concepts/faiss_descartado_en_favor_de_chromadb.md) — Decision to discard FAISS because ChromaDB offers real persistence and a more co

- [ChromaDB para MVP vectorial](concepts/chromadb_para_mvp_vectorial.md) — Decision to use ChromaDB for the MVP vector store due to its lower operational c

- [Minimalismo + Glassmorfismo](concepts/minimalismo_glassmorfismo.md) — The aesthetic principles, Minimalism and Glassmorphism, that define the 'Luminou

- [Micro-frontend](concepts/micro-frontend.md) — An architectural pattern for the frontend, consisting of a central shell integra

- [uv](concepts/uv.md) — A fast Python package installer and dependency resolver, also used here to run d

- [FastMCP server](concepts/fastmcp_server.md) — A server component that exposes the knowledge base to external AI agents via the

- [Frontend Vue + Pinia](concepts/frontend_vue_pinia.md) — The user interface application developed with Vue 3 and Pinia, featuring a micro

- [BFF NodeJS](concepts/bff_nodejs.md) — The Backend for Frontend service, providing REST and bidirectional WebSocket com

- [Core API Python](concepts/core_api_python.md) — The central backend service providing all core business logic and data access vi

- [Documentos (PDF, texto plano, código fuente)](concepts/documentos_pdf_texto_plano_código_fuente.md) — Various types of content, including PDF, plain text, and source code, ingested b

- [Dominios de conocimiento](concepts/dominios_de_conocimiento.md) — Defined logical containers for organizing knowledge within the platform, managed

- [Administrador](concepts/administrador.md) — A user role responsible for centrally creating, editing, and deleting knowledge 

- [package.json](concepts/packagejson.md) — A configuration file that defines project metadata and lists external dependenci

- [api/README.md](concepts/apireadmemd.md) — A documentation file providing specific guidance and details for the Core API mo

- [DESIGN.md](concepts/designmd.md) — A documentation file specifying the complete 'Luminous Knowledge' design system 

- [REQUIREMENTS.md](concepts/requirementsmd.md) — A planning documentation file listing the 54 version 1 project requirements.

- [ROADMAP.md](concepts/roadmapmd.md) — A planning documentation file outlining the 10-phase project roadmap with succes

- [PROJECT.md](concepts/projectmd.md) — A planning documentation file detailing the project vision, constraints, and key

- [README.md](concepts/readmemd.md) — Documentation file providing quick start guides, common issues, and API usage in

- [wiki.html](concepts/wikihtml.md) — An HTML file generated by `show_wiki.py` that displays the interactive wiki grap

- [wiki/graph.json](concepts/wikigraphjson.md) — A JSON file containing the node-link data representation of the project's wiki g

- [Ports & Adapters Pattern](concepts/ports_adapters_pattern.md) — An architectural pattern (also known as Hexagonal Architecture) that isolates th

- [API Keys](concepts/api_keys.md) — A key feature of the API for securely managing and authenticating access tokens 

- [OAuth2/OIDC](concepts/oauth2oidc.md) — The standard for authentication and authorization, implemented via Keycloak.

- [Node.js](concepts/nodejs.md) — The primary language runtime for the BFF (Backend-for-Frontend) component.

- [FastAPI](concepts/fastapi.md) — A modern, fast (high-performance) web framework for building APIs with Python 3.

- [RabbitMQ](concepts/rabbitmq.md) — A message broker, also used in the ingestion pipeline for message queuing.

- [Kafka](concepts/kafka.md) — A distributed streaming platform used in the ingestion pipeline for message queu

- [ZooKeeper](concepts/zookeeper.md) — A centralized service for maintaining configuration information, naming, providi

- [Redis](concepts/redis.md) — In-memory data store used for BFF sessions, pub/sub, and rate limiting.

- [with-app](concepts/with-app.md) — A Docker Compose profile used to selectively start the application-specific serv

- [rabbitmq_data](concepts/rabbitmq_data.md) — A local Docker volume for persisting RabbitMQ data.

- [kafka_data](concepts/kafka_data.md) — A local Docker volume for persisting Kafka data.

- [zookeeper_logs](concepts/zookeeper_logs.md) — A local Docker volume for persisting ZooKeeper logs.

- [zookeeper_data](concepts/zookeeper_data.md) — A local Docker volume for persisting ZooKeeper data.

- [redis_data](concepts/redis_data.md) — A local Docker volume for persisting Redis data.

- [chromadb_data](concepts/chromadb_data.md) — A local Docker volume for persisting ChromaDB data.

- [mongodb_data](concepts/mongodb_data.md) — A local Docker volume for persisting MongoDB data.

- [postgres_data](concepts/postgres_data.md) — A local Docker volume for persisting PostgreSQL data.

- [bff](concepts/bff.md) — A Backend for Frontend (BFF) service, implemented in Node.js, to serve the front

- [ingestion](concepts/ingestion.md) — An Ingestion Worker service, a Python asynchronous worker for processing data.

- [api](concepts/api.md) — The Core API service, a Python FastAPI application that serves as the backend fo

- [rabbitmq](concepts/rabbitmq.md) — A RabbitMQ message broker service, including a management UI, for asynchronous m

- [kafka](concepts/kafka.md) — An Apache Kafka message broker service for distributed stream processing.

- [zookeeper](concepts/zookeeper.md) — An Apache ZooKeeper service, a prerequisite for running Kafka.

- [redis](concepts/redis.md) — A Redis instance serving as a session store and pub/sub message broker.

- [chromadb](concepts/chromadb.md) — A ChromaDB vector store service, designated for MVP functionality.

- [mongodb](concepts/mongodb.md) — A MongoDB database service intended for storing document content.

- [postgres](concepts/postgres.md) — A PostgreSQL database service used as a relational metadata store for the applic

- [knowledge_network](concepts/knowledge_network.md) — A custom Docker bridge network facilitating communication between all services i

- [Research Nodes](concepts/research_nodes.md) — Custom, feature-rich card components specific to this design system, including i

- [Progress Indicators](concepts/progress_indicators.md) — Visual elements representing task completion, styled as thin bars with a desatur

- [Sidebars](concepts/sidebars.md) — Navigation panels styled as high-blur glassmorphic elements with fixed widths.

- [Chips](concepts/chips.md) — Compact, pill-shaped indicators for categorization or status, with specific back

- [Floating Elements (Level 3)](concepts/floating_elements_level_3.md) — The highest layer for popovers and tooltips, indicated by a lighter grey surface

- [The Content (Level 2)](concepts/the_content_level_2.md) — The layer for main cards and modals, using a slightly warmer near-black surface 

- [The Frame (Level 1)](concepts/the_frame_level_1.md) — The layer for sidebars and headers, utilizing a semi-transparent blur and low-op

- [The Canvas (Level 0)](concepts/the_canvas_level_0.md) — The base background layer of the UI, typically using a deep charcoal color (#121

- [Fluid Grid](concepts/fluid_grid.md) — The layout model employed, featuring a 12-column system that adapts to screen wi

- [Corporate Modern](concepts/corporate_modern.md) — One of the aesthetic influences for the design system, contributing to an author

- [Illuminated Intellect](concepts/illuminated_intellect.md) — The core brand concept and personality driving the design system, targeting rese

- [Spacing](concepts/spacing.md) — The system for defining distances and proportions, based on an 8px base unit and

- [Rounded Shapes](concepts/rounded_shapes.md) — The consistent use of rounded corners for UI components and structural elements,

- [Luminous Knowledge Dark](concepts/luminous_knowledge_dark.md) — The name of the dark theme design system described in the document, focused on p

- [Breadcrumbs](concepts/breadcrumbs.md) — Minimalist text links providing navigation context, styled in body-sm.

- [Segmented Controls](concepts/segmented_controls.md) — A sliding toggle style control for switching views.

- [Chips & Tags](concepts/chips_tags.md) — Pill-shaped elements used for categorization and metadata, with a light gray fil

- [Glass Sidebars](concepts/glass_sidebars.md) — Full-height container elements that leverage Glassmorphism for their visual effe

- [Input Fields](concepts/input_fields.md) — UI components for user input, styled with a darker background and an illuminatin

- [Cards](concepts/cards.md) — Content containers defined by their fill color against the background rather tha

- [Buttons](concepts/buttons.md) — UI components for user interaction, styled with solid fills or ghost borders dep

- [Fluid Layout](concepts/fluid_layout.md) — A layout principle used for the workspace editor, allowing for adaptable content

- [Fixed Grid](concepts/fixed_grid.md) — A layout principle used for content consumption to ensure structural alignment.

- [Inter](concepts/inter.md) — The sole font family utilized across the entire design system for maximum clarit

- [Shapes](concepts/shapes.md) — The defined shape language, emphasizing rounded corners for a modern, approachab

- [Elevation & Depth](concepts/elevation_depth.md) — The method for conveying hierarchy and physical space through Glassmorphism and 

- [Layout & Spacing](concepts/layout_spacing.md) — Principles and rules governing the arrangement of elements, including grid syste

- [Typography](concepts/typography.md) — The typographic guidelines, including font families, sizes, weights, line height

- [Colors](concepts/colors.md) — The defined color palette for the design system, including surface, primary, sec

- [Glassmorphism](concepts/glassmorphism.md) — A design aesthetic and technique used for communicating depth, characterized by 

- [Minimalism](concepts/minimalism.md) — A core aesthetic philosophy emphasizing clarity, focus, and reduction of cogniti

- [Design System](concepts/design_system.md) — The set of design tokens, components, and guidelines (Luminous Knowledge) for co

- [Luminous Knowledge](concepts/luminous_knowledge.md) — Design system defined by minimalism and glassmorphism, ensuring a unified visual

- [Knowledge Domains](concepts/knowledge_domains.md) — The categories used to organize knowledge content, which will be centrally defin

- [Knowledge Types](concepts/knowledge_types.md) — The formats of knowledge ingested into the platform, including PDF, plain text, 

- [Hybrid Search](concepts/hybrid_search.md) — A search strategy that integrates multiple search methods (e.g., semantic and ke

- [Semantic Search](concepts/semantic_search.md) — A search paradigm based on understanding meaning and context through vector embe

- [API Key Authentication](concepts/api_key_authentication.md) — An alternative authentication method using hashed API keys, though its validatio

- [Kubernetes](concepts/kubernetes.md) — An open-source container-orchestration system, the target deployment environment

- [Docker Compose](concepts/docker_compose.md) — A tool for defining and running multi-container Docker applications.

- [ChromaDB](concepts/chromadb.md) — A vector database identified as a potential source of tight coupling if used imp

- [MongoDB](concepts/mongodb.md) — A NoSQL database used for storing raw document content.

- [PostgreSQL](concepts/postgresql.md) — A relational database used for storing document metadata and configuration.

- [Neo4J](concepts/neo4j.md) — The planned graph database for managing relations between documents and graph-ba

- [Qdrant](concepts/qdrant.md) — An alternative vector database mentioned as a target for potential migration.

- [FAISS](concepts/faiss.md) — An initial vector database technology chosen for the Minimum Viable Product (MVP

- [Embeddings](concepts/embeddings.md) — Vector representations of knowledge content used for processing, indexing, and e

- [Gemini](concepts/gemini.md) — Default provider for embedding generation (text-embedding-004).

- [Large Language Models (LLMs)](concepts/large_language_models_llms.md) — General category of AI models to be used for processing, indexing, and querying 

- [FastMCP](concepts/fastmcp.md) — A third-party dependency (package) used to implement the Model Context Protocol,

- [Model Context Protocol (MCP)](concepts/model_context_protocol_mcp.md) — A protocol enabling tools like Google Stitch and allowing third-party AI agents 

- [Google Stitch](concepts/google_stitch.md) — A tool used for obtaining current design schematics via MCP before generating UI

- [UX/UI Rules](concepts/uxui_rules.md) — Specific guidelines for AI agents regarding UX/UI design, including the use of G

- [Working Rules](concepts/working_rules.md) — General operational rules for AI agents, emphasizing research, planning, avoidin

- [AI Agent Guidelines](concepts/ai_agent_guidelines.md) — A set of rules and instructions provided to AI agents (e.g., Claude Code) for in

- [Grafos](concepts/grafos.md) — A search method based on relationships and graphs, used as a component of the Hy

- [Vectores](concepts/vectores.md) — A semantic search method based on vector embeddings, used as a component of the 

- [BM25](concepts/bm25.md) — A lexical search algorithm used as a component of the Hybrid Search System.

- [Keycloak](concepts/keycloak.md) — The identity and access management solution used for authentication, proxied by 

- [Python APIs](concepts/python_apis.md) — Planned backend services developed with Python 1.13+, using uv, FastAPI, and Fas

- [BFF (Backend For Frontend)](concepts/bff_backend_for_frontend.md) — A planned NodeJS component acting as an API Rest and Websocket server, bridging 

- [Web Interface](concepts/web_interface.md) — The planned user interface for the 'Knowledge Management Center', to be built us

- [Knowledge Ingestion](concepts/knowledge_ingestion.md) — The planned functionality for bringing knowledge into the system from various so

- [Claude Code](concepts/claude_code.md) — An AI assistant (claude.ai/code) provided with specific working rules for intera

- [Hybrid Search System](concepts/hybrid_search_system.md) — An advanced search mechanism combining lexical (BM25), semantic (Vectors), and g

- [Confidence System](concepts/confidence_system.md) — A feature within `llmwikidoc` that manages the reliability score of information 

- [wiki/](concepts/wiki.md) — The root directory where the knowledge base information is organized, including 

- [gemini-2.5-flash](concepts/gemini-25-flash.md) — The specific LLM model configured to be used by the `llmwikidoc` system.

- [llmwikidoc](concepts/llmwikidoc.md) — The core system for structuring and maintaining a knowledge repository, configur

- [Knowledge Management Center](concepts/knowledge_management_center.md) — The project that is being documented regarding its pending implementations.

## Modules

- [adapters/__init__.py](entities/adapters__init__py.md) — The initialization module for the adapters package, now providing factory functi

- [mcp_server](entities/mcp_server.md) — The new name for the Model Context Protocol (MCP) module located at `api/src/mcp

- [src/](entities/src.md) — The primary source code directory of the API, which needs to be correctly recogn

- [api/pyproject.toml](entities/apipyprojecttoml.md) — Project configuration file, updated to remove deprecated UV settings and move de

- [api/README.md](entities/apireadmemd.md) — Documentation file for the Knowledge Management API, now significantly updated w

- [api/src/core](entities/apisrccore.md) — A Python sub-package within 'api/src' for core utilities and middleware.

- [api/src](entities/apisrc.md) — The root Python package for the Knowledge Management API, containing the main ap

- [src.main:app](entities/srcmainapp.md) — The specific entry point within the API's `src` directory that the uvicorn serve

- [start.py](entities/startpy.md) — A recommended Python script serving as the entry point to run the API, encapsula

- [start.bat](entities/startbat.md) — A new Batch script designed to launch the Knowledge Management API, specifically

- [start.sh](entities/startsh.md) — A new Bash script designed to launch the Knowledge Management API, specifically 

- [store](entities/store.md) — A global state management module (e.g., Vuex or Pinia store) responsible for han

- [api/src/api/ingestion.py](entities/apisrcapiingestionpy.md) — Source file containing the job status endpoint and a TODO for domain access chec

- [CDN for assets](entities/cdn_for_assets.md) — A low-priority planned content delivery network for static frontend assets.

- [Neo4j Graph Database](entities/neo4j_graph_database.md) — A medium-priority planned graph database for document relationships and search.

- [Grafana](entities/grafana.md) — A high-priority visualization tool for monitoring, paired with Prometheus.

- [Prometheus](entities/prometheus.md) — A high-priority monitoring system, with its /metrics endpoint already existing.

- [ARQ](entities/arq.md) — A technology planned for implementing asynchronous workers with queues and retry

- [ingestion_service.py](entities/ingestion_servicepy.md) — A Python file related to ingestion, affected by MongoDB integration.

- [.env.production.example](entities/envproductionexample.md) — An example file documenting all required environment variables for a production 

- [ci-cd.yml](entities/ci-cdyml.md) — A GitHub Actions workflow definition for the CI/CD pipeline, orchestrating testi

- [health.py](entities/healthpy.md) — A Python module that defines various health check endpoints (/health, /health/de

- [logging_middleware.py](entities/logging_middlewarepy.md) — A Python module implementing a middleware for automatic HTTP request logging, ge

- [logging_config.py](entities/logging_configpy.md) — The Python module responsible for configuring structured logging using structlog

- [api/src/mcp/server.py](entities/apisrcmcpserverpy.md) — A new module housing the core logic for the FastMCP server, including its defini

- [api/src/mcp/auth.py](entities/apisrcmcpauthpy.md) — A new module dedicated to handling API key-based authentication for the MCP serv

- [api/src/mcp/__init__.py](entities/apisrcmcp__init__py.md) — The package initialization file for the `mcp` module, defining what symbols are 

- [api/src/main.py](entities/apisrcmainpy.md) — The primary application file for the Knowledge Management Center API, updated to

- [frontend/apps/search-ui/src/types/search.ts](entities/frontendappssearch-uisrctypessearchts.md) — TypeScript interfaces defining the data structures for search requests, response

- [frontend/apps/search-ui/src/components/SearchResultCard.vue](entities/frontendappssearch-uisrccomponentssearchresultcardvue.md) — A Vue component designed to display an individual search result, including highl

- [frontend/apps/search-ui/src/components/SearchFilters.vue](entities/frontendappssearch-uisrccomponentssearchfiltersvue.md) — A Vue component implementing the user interface for filtering search results by 

- [frontend/apps/search-ui/src/services/searchApi.ts](entities/frontendappssearch-uisrcservicessearchapits.md) — A service module providing the API client for interacting with the Backend For F

- [frontend/apps/search-ui/src/stores/search.ts](entities/frontendappssearch-uisrcstoressearchts.md) — A Pinia store responsible for managing the state and handling API calls related 

- [frontend/apps/search-ui](entities/frontendappssearch-ui.md) — The dedicated Vue.js application that will host the Search Micro UI, intended to

- [Shell Notifications Micro UI](entities/shell_notifications_micro_ui.md) — A micro-UI for displaying real-time toast notifications and updating a notificat

- [Ingestion Status Micro UI](entities/ingestion_status_micro_ui.md) — A micro-UI providing real-time updates for ingestion jobs via WebSocket, includi

- [Domain Explorer Micro UI](entities/domain_explorer_micro_ui.md) — A micro-UI for listing domains with document counts, browsing documents, and vie

- [Search Micro UI](entities/search_micro_ui.md) — A micro-UI responsible for semantic and filtered search, displaying highlighted 

- [searchUi micro-UI](entities/searchui_micro-ui.md) — One of the micro-frontend applications updated to be a Module Federation remote 

- [ingestionUi micro-UI](entities/ingestionui_micro-ui.md) — One of the micro-frontend applications updated to be a Module Federation remote 

- [domainsUi micro-UI](entities/domainsui_micro-ui.md) — One of the micro-frontend applications updated to be a Module Federation remote 

- [adminUi micro-UI](entities/adminui_micro-ui.md) — One of the micro-frontend applications updated to be a Module Federation remote 

- [Design tokens CSS](entities/design_tokens_css.md) — A CSS file at `src/styles/design-tokens.css` defining global design variables fo

- [BFF API client](entities/bff_api_client.md) — An HTTP client at `src/services/bffClient.ts` for proxying requests to the Core 

- [Pinia auth store](entities/pinia_auth_store.md) — A Pinia store at `src/stores/auth.ts` managing user session, login/logout action

- [frontend/apps/shell/src/types/auth.ts](entities/frontendappsshellsrctypesauthts.md) — TypeScript type definitions for authentication-related data structures used acro

- [frontend/apps/shell/src/services/bffClient.ts](entities/frontendappsshellsrcservicesbffclientts.md) — A client module for interacting with the BFF API, specifically for authenticatio

- [frontend/apps/shell/src/middleware/auth.ts](entities/frontendappsshellsrcmiddlewareauthts.md) — Vue Router navigation guards for enforcing authentication rules and redirects in

- [frontend/apps/shell/src/stores/auth.ts](entities/frontendappsshellsrcstoresauthts.md) — The Pinia store module managing authentication state in the Frontend Shell, prov

- [TomSelect](entities/tomselect.md) — The main module providing the comprehensive functionality for the Tom Select com

- [concurrently](entities/concurrently.md) — A utility to run multiple commands concurrently, used here to start several fron

- [knowledge-management-frontend](entities/knowledge-management-frontend.md) — The root frontend module for a knowledge management system, likely part of a mon

- [adminUi/App](entities/adminuiapp.md) — A dynamically imported Vue component that serves as the root for the administrat

- [ingestionUi/App](entities/ingestionuiapp.md) — A dynamically imported Vue component that serves as the root for the data ingest

- [searchUi/App](entities/searchuiapp.md) — A dynamically imported Vue component that serves as the root for the search user

- [domainsUi/App](entities/domainsuiapp.md) — A dynamically imported Vue component that serves as the root for the domains use

- [frontend/apps/shell/src/main.ts](entities/frontendappsshellsrcmaints.md) — The primary entry point for the Vue application, responsible for initializing th

- [ingestionUi](entities/ingestionui.md) — A remote micro-frontend application consumed by the shell application via Module

- [searchUi](entities/searchui.md) — A remote micro-frontend application consumed by the shell application via Module

- [domainsUi](entities/domainsui.md) — A remote micro-frontend application consumed by the shell application via Module

- [shell](entities/shell.md) — A UI component or sub-package within the frontend monorepo, likely the main appl

- [frontend/apps/search-ui/src/main.ts](entities/frontendappssearch-uisrcmaints.md) — The primary entry point file for the search-ui Vue.js application, responsible f

- [App.vue](entities/appvue.md) — The main Vue component for the domains user interface, responsible for displayin

- [Vue](entities/vue.md) — The JavaScript framework utilized for building the user interface of the domains

- [./src/App.vue](entities/srcappvue.md) — The main Vue component of the 'search-ui' application, exposed as './App' for co

- [@vitejs/plugin-vue](entities/vitejsplugin-vue.md) — A Vite plugin that provides Vue.js support for the 'search-ui' application.

- [main.ts](entities/maints.md) — The primary entry point file for the ingestion-ui Vue application.

- [./App](entities/app.md) — The main Vue application component (`./src/App.vue`) exposed by `adminUi` via Mo

- [adminUi](entities/adminui.md) — A remote micro-frontend application consumed by the shell application via Module

- [@originjs/vite-plugin-federation](entities/originjsvite-plugin-federation.md) — A Vite plugin specifically for enabling Module Federation within the 'search-ui'

- [test_vector_store.py](entities/test_vector_storepy.md) — The main module containing unit tests for the vector store port and related comp

- [core.auth](entities/coreauth.md) — Module responsible for authentication, including JWT token verification and JWKS

- [schemas](entities/schemas.md) — Presumed module containing Pydantic schemas, such as DomainCreate and DomainUpda

- [uuid](entities/uuid.md) — Module for generating Universally Unique Identifiers (UUIDs).

- [unittest.mock](entities/unittestmock.md) — Standard library module for creating mock objects to replace parts of the system

- [pytest](entities/pytest.md) — A testing framework used for writing scalable tests, providing fixtures and mark

- [api/tests/test_domains.py](entities/apiteststest_domainspy.md) — The Python module containing all tests for the domain API endpoints.

- [test_auth.py](entities/test_authpy.md) — The main test file for the authentication utilities, ensuring their correct func

- [api/tests/test_api_keys.py](entities/apiteststest_api_keyspy.md) — Contains end-to-end tests specifically for the API key management endpoints, cov

- [api/tests/conftest.py](entities/apitestsconftestpy.md) — Contains shared test configurations, fixtures, and utilities for the API test su

- [api/tests/__init__.py](entities/apitests__init__py.md) — Marks the directory as a Python package for API tests.

- [Search Service Module](entities/search_service_module.md) — Centralizes document search operations, supporting various strategies like seman

- [domain_service](entities/domain_service.md) — Provides the core business logic for managing domains and their associated acces

- [services](entities/services.md) — The main services package, serving as an entry point for various business logic 

- [api/src/ports/__init__.py](entities/apisrcports__init__py.md) — The `__init__.py` file for the `ports` package, serving as a central point to im

- [api/src/models/base](entities/apisrcmodelsbase.md) — Defines the SQLAlchemy database models for the Knowledge Management Center, incl

- [api/src/models](entities/apisrcmodels.md) — The Python package for database models, exposing core models from 'base.py'.

- [main](entities/main.md) — The primary module defining and running the Knowledge Management Center API appl

- [extractors](entities/extractors.md) — The Python module containing functions and classes for document text extraction 

- [re](entities/re.md) — Python's built-in module for regular expression operations, used here for text s

- [ingestion.chunking](entities/ingestionchunking.md) — This module provides various strategies and data structures for breaking down la

- [api/src/db/__init__.py](entities/apisrcdb__init__py.md) — The initialization file for the database package, responsible for exposing core 

- [Dependencies Module](entities/dependencies_module.md) — Provides FastAPI dependency functions for integrating authentication and authori

- [Auth Module](entities/auth_module.md) — Core module responsible for handling JWT token verification with Keycloak, cachi

- [search.py](entities/searchpy.md) — The main module defining the Search API endpoints for a knowledge management sys

- [ingestion.py](entities/ingestionpy.md) — The main module defining API endpoints related to document ingestion and status 

- [domains](entities/domains.md) — Contains API endpoints for managing knowledge domains, including creation, listi

- [api_keys](entities/api_keys.md) — Contains API endpoints for managing API keys, allowing users to create, list, re

- [api/src/adapters/vector_store/__init__.py](entities/apisrcadaptersvector_store__init__py.md) — Initializes the vector store adapters package, indicating its purpose as a conta

- [api.src.adapters.embedding.gemini](entities/apisrcadaptersembeddinggemini.md) — The module containing the `GeminiAdapter` class, which serves as a concrete adap

- [api.src.adapters.embedding](entities/apisrcadaptersembedding.md) — The Python package responsible for housing various implementations of the `Embed

- [adapters](entities/adapters.md) — The 'api/src/adapters' Python package. Its stated purpose is to provide concrete

- [Env Example File](entities/env_example_file.md) — The `../.env.example` file, which provides a template for required environment v

- [Dockerfile](entities/dockerfile.md) — A file containing instructions for building a Docker image for the application.

- [Tests Directory](entities/tests_directory.md) — The `tests/` directory, which contains the project's test suite.

- [Services Directory](entities/services_directory.md) — The `src/services/` directory, which contains business logic implementations.

- [Models Directory](entities/models_directory.md) — The `src/models/` directory, which contains Pydantic data models.

- [Routers Directory](entities/routers_directory.md) — The `src/routers/` directory, which contains API route handlers.

- [Adapters Directory](entities/adapters_directory.md) — The `src/adapters/` directory, which contains concrete implementations of Port I

- [Ports Directory](entities/ports_directory.md) — The `src/ports/` directory, which contains abstract interface definitions (Ports

- [README.md](entities/readmemd.md) — The main documentation file providing an overview, architectural principles, pro

- [pyproject.toml](entities/pyprojecttoml.md) — The project configuration file, specifying metadata, dependencies, build system,

- [Core Micro UIs](entities/core_micro_uis.md) — The daily-use frontend interfaces including search, domains, and ingestion.

- [Admin UI](entities/admin_ui.md) — A micro-UI for administrative tasks like domain management and API key issuance.

- [Search Component](entities/search_component.md) — Handles semantic and hybrid search queries with access control and pagination.

- [Ingestion Pipeline](entities/ingestion_pipeline.md) — Responsible for processing documents from various sources, chunking, deduplicati

- [Frontend Shell UI](entities/frontend_shell_ui.md) — The main entry point for the micro-frontend architecture, defining shared depend

- [BFF (Backend For Frontend) service](entities/bff_backend_for_frontend_service.md) — The Node.js service handling frontend requests, OAuth2, session management, and 

- [Core API service](entities/core_api_service.md) — The central Python-based backend service handling domain CRUD, authentication, a

- [PyMuPDF](entities/pymupdf.md) — A Python library for PDF document parsing, used in the ingestion pipeline.

- [Gemini text-embedding-004](entities/gemini_text-embedding-004.md) — The default text embedding provider, producing 768-dimensional vectors.

- [vite-plugin-federation](entities/vite-plugin-federation.md) — The Vite plugin enabling Module Federation for Vue 3 micro-frontends.

- [openid-client](entities/openid-client.md) — A Node.js library for OpenID Connect client implementation, used in the BFF for 

- [Fastify](entities/fastify.md) — The Node.js web framework used for the Backend For Frontend (BFF).

- [arq task queue](entities/arq_task_queue.md) — An asyncio-native async task queue for the platform, preferred over Celery for s

- [Pydantic v2](entities/pydantic_v2.md) — A data validation and parsing library, a hard dependency for FastAPI 0.100+.

- [uv package manager](entities/uv_package_manager.md) — The recommended package manager for Python dependencies.

- [Python 3.13](entities/python_313.md) — The core programming language for the Core API and ingestion worker.

- [FastMCP server](entities/fastmcp_server.md) — A Python component enabling external AI agents to interact with the platform thr

- [pre-commit](entities/pre-commit.md) — A framework for managing and running Git hooks, executing code quality checks be

- [import-linter](entities/import-linter.md) — A tool to enforce architectural import boundaries within the codebase.

- [mypy](entities/mypy.md) — A static type checker for Python, used in strict mode.

- [ruff](entities/ruff.md) — A fast Python linter and formatter, replacing multiple older tools like flake8, 

- [arq](entities/arq.md) — A lightweight asynchronous task queue using Redis (option B), recommended for it

- [celery](entities/celery.md) — A task queue for asynchronous ingestion jobs (option A), using Redis as a broker

- [aioboto3](entities/aioboto3.md) — An asynchronous wrapper around boto3, preferred for async S3 polling.

- [boto3](entities/boto3.md) — The synchronous AWS SDK for Python, used for S3 source connectors.

- [aio-pika](entities/aio-pika.md) — An asynchronous RabbitMQ client (AMQP), used for ingestion trigger events.

- [aiokafka](entities/aiokafka.md) — An asynchronous Kafka consumer/producer client, used for ingestion trigger event

- [tiktoken](entities/tiktoken.md) — A library for token counting with OpenAI models, useful for chunking logic.

- [openai](entities/openai.md) — The client library for interacting with the OpenAI embedding API (planned for fu

- [google-generativeai](entities/google-generativeai.md) — The client library for interacting with the Gemini embedding API.

- [tree-sitter](entities/tree-sitter.md) — An AST-based code parsing library for optional semantic code chunking.

- [pygments](entities/pygments.md) — A library for source code language detection and tokenization, used in code inge

- [chardet](entities/chardet.md) — A library for character encoding detection in text files.

- [pdfminer.six](entities/pdfminersix.md) — An alternative PDF parser, used as a fallback for complex layouts.

- [pymupdf](entities/pymupdf.md) — A PDF text extraction library, preferred for its balance of accuracy and speed.

- [redis](entities/redis.md) — A client for Redis, used for pub/sub messaging and session caching.

- [qdrant-client](entities/qdrant-client.md) — A vector store client designated for a future v2 migration.

- [chromadb](entities/chromadb.md) — A vector store client used for the Minimum Viable Product (MVP).

- [pymongo](entities/pymongo.md) — A synchronous MongoDB driver, used internally by `motor`.

- [motor](entities/motor.md) — An asynchronous MongoDB driver, built on top of `pymongo`.

- [alembic](entities/alembic.md) — A database migration tool for PostgreSQL, generating scripts from SQLAlchemy mod

- [sqlalchemy](entities/sqlalchemy.md) — An ORM and query builder for PostgreSQL, used with its asyncio extension.

- [asyncpg](entities/asyncpg.md) — A fast asynchronous PostgreSQL driver for Python.

- [cryptography](entities/cryptography.md) — A library providing cryptographic primitives, a transitive dependency for `pytho

- [httpx](entities/httpx.md) — An async HTTP client preferred for internal calls and JWKS fetching in FastAPI c

- [python-jose](entities/python-jose.md) — A library for JWT validation, specifically for RS256 tokens from Keycloak.

- [mcp](entities/mcp.md) — The former name of the Model Context Protocol module that caused a naming confli

- [fastmcp](entities/fastmcp.md) — A server implementation for the Model Context Protocol, designed to be mounted a

- [starlette](entities/starlette.md) — An ASGI toolkit that FastAPI builds upon; its version is controlled by FastAPI.

- [python-multipart](entities/python-multipart.md) — A library providing file upload support within FastAPI.

- [pydantic-settings](entities/pydantic-settings.md) — A library for managing application settings, replacing Pydantic's BaseSettings i

- [pydantic](entities/pydantic.md) — A data validation and settings management library, a hard dependency of FastAPI.

- [uvicorn](entities/uvicorn.md) — The ASGI server used to run FastAPI applications.

- [fastapi](entities/fastapi.md) — The HTTP web framework used for the Python Core API.

- [pnpm](entities/pnpm.md) — A fast, disk space efficient package manager used for monorepos, utilized here t

- [npm](entities/npm.md) — A package manager for Node.js, an option for managing Node.js dependencies.

- [uv](entities/uv.md) — The recommended package manager for Python, managing virtual environments and in

- [config.ts](entities/configts.md) — A TypeScript configuration file proposed for centralizing environment variable r

- [config.py](entities/configpy.md) — A Python configuration file proposed for centralizing environment variable readi

- [google.generativeai](entities/googlegenerativeai.md) — The Python client library for the Google Gemini API.

- [Multi-LLM Embedding Architecture](entities/multi-llm_embedding_architecture.md) — A flexible architecture allowing abstraction and configuration of different LLM 

- [MCP Server for AI Agent Integration](entities/mcp_server_for_ai_agent_integration.md) — A server exposing the knowledge base to external AI agents using the Model Conte

- [Multi-Source Ingestion Pipeline](entities/multi-source_ingestion_pipeline.md) — An advanced ingestion system supporting various connectors (S3, Kafka, RabbitMQ)

- [Infrastructure and Operations](entities/infrastructure_and_operations.md) — Encompasses deployment, environment configuration, and logging practices for the

- [Frontend (Web UI)](entities/frontend_web_ui.md) — The user-facing web application for accessing, searching, and managing knowledge

- [Authentication and Authorization](entities/authentication_and_authorization.md) — Manages user login, role-based access control, API key issuance, and session man

- [Search](entities/search.md) — Provides capabilities for finding relevant knowledge, including semantic, hybrid

- [Document Ingestion and Processing](entities/document_ingestion_and_processing.md) — Handles the intake, parsing, chunking, embedding, and storage of documents from 

- [Domain Management](entities/domain_management.md) — Functionality for creating, organizing, and controlling access to knowledge doma

- [05-03-PLAN.md](entities/05-03-planmd.md) — The third detailed plan for Phase 5, focusing on real-time WebSocket events for 

- [05-02-PLAN.md](entities/05-02-planmd.md) — The second detailed plan for Phase 5, outlining the implementation of the Core A

- [05-01-PLAN.md](entities/05-01-planmd.md) — The first detailed plan for Phase 5, focusing on establishing the BFF foundation

- [ROADMAP.md](entities/roadmapmd.md) — The primary document outlining the phased development plan for the Knowledge Man

- [Gemini](entities/gemini.md) — AI model used as the default for embedding generation.

- [Redis pub/sub](entities/redis_pubsub.md) — Publish/subscribe messaging paradigm, recommended for BFF-worker event relay.

- [Qdrant](entities/qdrant.md) — The target vector store for a v2 migration, implemented as an adapter swap.

- [admin-ui](entities/admin-ui.md) — A UI component or sub-package within the frontend monorepo, likely related to ad

- [search-ui](entities/search-ui.md) — A UI component or sub-package within the frontend monorepo, likely related to se

- [ingestion-ui](entities/ingestion-ui.md) — A UI component or sub-package within the frontend monorepo, likely related to da

- [domains-ui](entities/domains-ui.md) — The frontend application responsible for the user interface related to knowledge

- [MCP Server (FastMCP)](entities/mcp_server_fastmcp.md) — Component exposing knowledge base as MCP-compliant tools for AI agents.

- [INGESTION WORKER (Python/async)](entities/ingestion_worker_pythonasync.md) — Asynchronous Python service responsible for processing ingestion jobs, parsing d

- [MESSAGE BROKER](entities/message_broker.md) — Asynchronous messaging system (Kafka or RabbitMQ) used for ingestion job orchest

- [CORE API (Python/FastAPI)](entities/core_api_pythonfastapi.md) — Python FastAPI service owning all business logic, data persistence interactions,

- [BFF (NodeJS)](entities/bff_nodejs.md) — NodeJS Backend-for-Frontend service handling session management, OAuth2/OIDC flo

- [FRONTEND SHELL](entities/frontend_shell.md) — Vue 3 host application managing app-level routing, global state, and Module Fede

- [KEYCLOAK](entities/keycloak.md) — External Identity Provider for OAuth2/OIDC authentication.

- [api/search.py](entities/apisearchpy.md) — The Python file defining the REST API endpoints for search functionalities.

- [services/search_service.py](entities/servicessearch_servicepy.md) — The Python file containing the main search service logic and RRF fusion implemen

- [Search API Endpoints](entities/search_api_endpoints.md) — The collection of RESTful API endpoints (`api/search.py`) providing access to se

- [SearchService](entities/searchservice.md) — Orchestrates and performs different types of document searches, combining result

- [Documentation Module](entities/documentation_module.md) — Covers the creation of API documentation, search examples, and ranking explanati

- [Tests Module](entities/tests_module.md) — Encompasses various tests including unit, integration, permission, and performan

- [Filter and Rank Module](entities/filter_and_rank_module.md) — Responsible for applying metadata filters, permissions checks, and final relevan

- [Search Pipeline](entities/search_pipeline.md) — The orchestrated sequence of operations that processes a search request to produ

- [api/ingestion.py](entities/apiingestionpy.md) — A Python module defining the RESTful API endpoints related to document ingestion

- [services/ingestion_service.py](entities/servicesingestion_servicepy.md) — A Python module encapsulating the business logic for managing the document inges

- [ingestion/chunking.py](entities/ingestionchunkingpy.md) — A Python module implementing different strategies for dividing document text int

- [ingestion/extractors.py](entities/ingestionextractorspy.md) — A Python module containing functions for extracting text from various file forma

- [main.py](entities/mainpy.md) — The main FastAPI application entry point that now imports and mounts the `mcp_se

- [api/api_keys.py](entities/apiapi_keyspy.md) — A Python module containing the FastAPI route definitions for API key management 

- [api/domains.py](entities/apidomainspy.md) — A Python module containing the FastAPI route definitions for domain-related API 

- [api/src/api/api_keys.py](entities/apisrcapiapi_keyspy.md) — Module containing FastAPI endpoints for API key creation, listing, retrieval, an

- [api/src/api/domains.py](entities/apisrcapidomainspy.md) — Module containing FastAPI endpoints specifically for domain-related CRUD and acc

- [api/src/services/api_key_service.py](entities/apisrcservicesapi_key_servicepy.md) — Module containing the business logic and repository operations for API key manag

- [api/src/services/domain_service.py](entities/apisrcservicesdomain_servicepy.md) — Module containing the business logic and repository operations for domain manage

- [api/src/core/dependencies.py](entities/apisrccoredependenciespy.md) — Source file containing the 'get_current_user_optional' function and a TODO for r

- [api/src/core/auth.py](entities/apisrccoreauthpy.md) — A Python module containing utilities for JWT validation and user authentication.

- [api/src/schemas/__init__.py](entities/apisrcschemas__init__py.md) — Module containing all Pydantic schemas for API requests and responses.

- [api/src/db/database.py](entities/apisrcdbdatabasepy.md) — Contains the configuration for the asynchronous database engine, session managem

- [api/src/models/__init__.py](entities/apisrcmodels__init__py.md) — Module containing all SQLAlchemy model definitions for the project.

- [API Key Endpoints](entities/api_key_endpoints.md) — REST endpoints for creating, listing, and revoking API keys.

- [Domain CRUD Endpoints](entities/domain_crud_endpoints.md) — REST endpoints for creating, listing, retrieving, updating, and deleting knowled

- [Swagger UI](entities/swagger_ui.md) — A tool for rendering auto-generated API documentation visually at the /docs endp

- [Alembic](entities/alembic.md) — The lightweight database migration tool used with SQLAlchemy.

- [SQLAlchemy](entities/sqlalchemy.md) — The Python SQL toolkit and Object-Relational Mapper (ORM) used for database inte

- [.env.example](entities/envexample.md) — An example file listing all required environment variables for various services 

- [shared/](entities/shared.md) — A placeholder directory for shared packages and utilities across the monorepo.

- [frontend/apps/admin-ui/](entities/frontendappsadmin-ui.md) — A micro UI application for administrative tasks, running on port 5104.

- [frontend/apps/ingestion-ui/](entities/frontendappsingestion-ui.md) — A micro UI application for ingestion functionality, running on port 5102.

- [frontend/apps/search-ui/](entities/frontendappssearch-ui.md) — A micro UI application for search functionality, running on port 5103.

- [frontend/apps/domains-ui/](entities/frontendappsdomains-ui.md) — A micro UI application for managing domains, running on port 5101.

- [frontend/apps/shell/](entities/frontendappsshell.md) — The Module Federation host application for the frontend, running on port 5100.

- [frontend/](entities/frontend.md) — The directory containing Vue 3 and Module Federation based frontend applications

- [bff/](entities/bff.md) — A placeholder directory for the Backend For Frontend service, planned for Phase 

- [ingestion/](entities/ingestion.md) — A placeholder directory for the ingestion service, planned for Phase 3.

- [api/](entities/api.md) — The directory containing the Core API Python (FastAPI) application.

- [FastAPI API](entities/fastapi_api.md) — The core Python API service built with FastAPI, including a health endpoint.

- [Core API (Python/FastAPI)](entities/core_api_pythonfastapi.md) — The main backend API for the project, implemented in Python using FastAPI, inclu

- [25-KnowledgeManagement/](entities/25-knowledgemanagement.md) — The root directory of the monorepo, containing all project services and shared c

- [api/src/adapters/embedding/gemini.py](entities/apisrcadaptersembeddinggeminipy.md) — The Python module containing the implementation of the GeminiAdapter.

- [api/src/adapters/vector_store/chroma_db.py](entities/apisrcadaptersvector_storechroma_dbpy.md) — Contains the ChromaDBAdapter, a concrete implementation of the VectorStorePort u

- [api/src/ports/embedding.py](entities/apisrcportsembeddingpy.md) — Defines the abstract interface and related components for text embedding generat

- [api/src/ports/vector_store.py](entities/apisrcportsvector_storepy.md) — The module defining the abstract interface and data models for vector store oper

- [shared](entities/shared.md) — A directory for shared packages like TypeScript types and Vue components, part o

- [micro-uis](entities/micro-uis.md) — A directory containing independent micro-UIs (domains-ui, search-ui, ingestion-u

- [frontend/shell](entities/frontendshell.md) — The Module Federation host for the frontend, part of the monorepo structure.

- [bff](entities/bff.md) — The Node.js Backend for Frontend service, part of the monorepo structure.

- [ingestion](entities/ingestion.md) — The top-level Python package for document ingestion, exposing core functionaliti

- [api](entities/api.md) — The main package for API routes, serving as an aggregation point for various sub

- [Google Generative AI API](entities/google_generative_ai_api.md) — The specific API used by the Gemini adapter for generating text embeddings.

- [Docker Compose](entities/docker_compose.md) — A tool used for defining and running multi-container Docker applications, centra

- [Gemini API](entities/gemini_api.md) — Google's API for generative artificial intelligence, utilized for embedding gene

- [ABC](entities/abc.md) — Python's Abstract Base Class module, used as a base class to define abstract int

- [Admin micro UI](entities/admin_micro_ui.md) — A dedicated micro UI for administrative tasks like domain and user management.

- [FastMCP](entities/fastmcp.md) — A server for exposing tools to AI agents, integrated in Phase 9.

- [Vue Router](entities/vue_router.md) — The application's routing system configured at `src/router/index.ts` with auth g

- [Pinia](entities/pinia.md) — A state management library for Vue.js, specified for use in the authentication s

- [Vue 3](entities/vue_3.md) — The JavaScript framework for the platform's micro-frontend UIs.

- [Node.js BFF](entities/nodejs_bff.md) — The Backend-for-Frontend component implemented using Node.js.

- [RabbitMQ](entities/rabbitmq.md) — Open-source message broker, an option for the Message Broker.

- [Kafka](entities/kafka.md) — Distributed streaming platform, an option for the Message Broker.

- [Redis](entities/redis.md) — A technology required for implementing rate limiting and caching.

- [ChromaDB](entities/chromadb.md) — The current database used for storing document content.

- [MongoDB](entities/mongodb.md) — The document store used for raw text and chunk content with flexible metadata.

- [PostgreSQL](entities/postgresql.md) — The relational database used for structured metadata.

- [Keycloak](entities/keycloak.md) — The OAuth2/OIDC provider for authentication and authorization.

- [FastAPI](entities/fastapi.md) — The Python HTTP framework used for the Core API.

- [Phase 7: Core micro UIs](entities/phase_7_core_micro_uis.md) — Implements core user interface micro-applications for search, domain exploration

- [Phase 6: Frontend shell](entities/phase_6_frontend_shell.md) — Develops the Vue 3 Module Federation host application responsible for authentica

- [Phase 5: BFF layer](entities/phase_5_bff_layer.md) — Builds a Node.js Backend-for-Frontend (BFF) responsible for OAuth2 proxying, RES

- [MCP Server](entities/mcp_server.md) — An ASGI sub-app within the Core API, providing tools for AI agents to interact w

- [Frontend Shell](entities/frontend_shell.md) — The main host application for the frontend, built with Vue 3 and Module Federati

- [BFF (Backend for Frontend)](entities/bff_backend_for_frontend.md) — NodeJS REST API that consumes the Core API, exposes endpoints to the frontend, m

- [@opencode-ai/plugin](entities/opencode-aiplugin.md) — A third-party plugin module that this project depends on.

- [pyvis.network](entities/pyvisnetwork.md) — A Python library for creating interactive network visualizations, used by `show_

- [networkx](entities/networkx.md) — A Python library for the creation, manipulation, and study of complex networks, 

- [json (module)](entities/json_module.md) — Python's standard library for working with JSON data, used by `show_wiki.py` to 

- [show_wiki.py](entities/show_wikipy.md) — A Python script designed to visualize the project's wiki graph structure using n

- [Frontend](entities/frontend.md) — The user interface for the platform, built with Vue 3, Pinia, and designed with 

- [BFF](entities/bff.md) — The Backend For Frontend service where Redis caching is planned.

- [Core API](entities/core_api.md) — The primary programmatic interface for interacting with the platform, offering e

- [AI Component](entities/ai_component.md) — The part of the system responsible for processing, indexing, and querying knowle

- [llmwikidoc Configuration](entities/llmwikidoc_configuration.md) — Configuration settings for the llmwikidoc tool, defining model, directory, conte

## Classs

- [MCPAuthMiddleware](entities/mcpauthmiddleware.md) — An authentication middleware for MCP endpoints that validates API keys provided 

- [ToastContainer component](entities/toastcontainer_component.md) — A reusable UI component at `src/components/ui/ToastContainer.vue` that implement

- [BaseInput component](entities/baseinput_component.md) — A reusable UI component at `src/components/ui/BaseInput.vue` for text input fiel

- [BaseCard component](entities/basecard_component.md) — A reusable UI component at `src/components/ui/BaseCard.vue` providing card conta

- [BaseButton component](entities/basebutton_component.md) — A reusable UI component at `src/components/ui/BaseButton.vue` supporting primary

- [ShellLayout component](entities/shelllayout_component.md) — A global layout component at `src/components/layout/ShellLayout.vue` featuring a

- [LoginRequired view](entities/loginrequired_view.md) — A Vue view component at `src/views/LoginRequired.vue` prompting users to log in 

- [AuthCallback view](entities/authcallback_view.md) — A Vue view component at `src/views/AuthCallback.vue` dedicated to handling OAuth

- [ItemSearchEngine](entities/itemsearchengine.md) — A class that provides advanced search, filtering, and sorting capabilities for i

- [EventEmitter](entities/eventemitter.md) — A utility class responsible for managing custom events within the Tom Select com

- [App](entities/app.md) — The root Vue component of the application, imported from './App.vue', serving as

- [TestSearchResult](entities/testsearchresult.md) — A test suite for verifying the creation and field handling of the SearchResult d

- [TestChunk](entities/testchunk.md) — A test suite for verifying the creation and field handling of the Chunk dataclas

- [TestVectorStorePort](entities/testvectorstoreport.md) — A test suite for verifying the core functionality and error handling of the Vect

- [MockVectorStoreAdapter](entities/mockvectorstoreadapter.md) — A concrete mock implementation of the VectorStorePort for testing purposes, simu

- [TestExceptions](entities/testexceptions.md) — A test suite for verifying the behavior and inheritance of the custom exception 

- [TestEmbeddingTaskType](entities/testembeddingtasktype.md) — A test suite for verifying the enumeration values and behavior of the `Embedding

- [TestEmbeddingConfig](entities/testembeddingconfig.md) — A test suite for verifying the creation and default parameter values of the `Emb

- [TestEmbeddingPort](entities/testembeddingport.md) — A test suite focused on verifying the core functionality and properties of the `

- [MockEmbeddingAdapter](entities/mockembeddingadapter.md) — A mock implementation of the `EmbeddingPort` interface, designed for testing to 

- [AsyncMock](entities/asyncmock.md) — A mock object from `unittest.mock` that can be awaited, suitable for mocking asy

- [TestDomainAccess](entities/testdomainaccess.md) — A test class grouping tests related to managing user access (grant/revoke) to do

- [TestDomainDelete](entities/testdomaindelete.md) — A test class grouping tests related to deleting domains via the API.

- [TestDomainUpdate](entities/testdomainupdate.md) — A test class grouping tests related to updating existing domains via the API.

- [TestDomainGet](entities/testdomainget.md) — A test class grouping tests related to retrieving a specific domain by ID from t

- [TestDomainList](entities/testdomainlist.md) — A test class grouping tests related to listing domains from the API.

- [TestDomainCreation](entities/testdomaincreation.md) — A test class grouping tests related to the creation of new domains via the API.

- [JWTError](entities/jwterror.md) — An exception class from the `jose` library, signaling issues during JWT processi

- [TestAPIKeyUtils](entities/testapikeyutils.md) — A test suite for API key utilities including generation, hashing, and verificati

- [TestUserExtraction](entities/testuserextraction.md) — A test suite focusing on the `extract_user_from_token` function, ensuring accura

- [TestJWTVerification](entities/testjwtverification.md) — A test suite dedicated to verifying the functionality of `verify_jwt_token`, cov

- [TestAPIKeyRevoke](entities/testapikeyrevoke.md) — A test class grouping tests related to the revocation (deletion) of API keys via

- [TestAPIKeyList](entities/testapikeylist.md) — A test class grouping tests related to listing API keys via the "/v1/api-keys" e

- [TestAPICKeyCreation](entities/testapickeycreation.md) — A test class grouping tests related to the creation of API keys via the "/v1/api

- [Exception](entities/exception.md) — The base class for all non-exit exceptions in Python, which IngestionError exten

- [AsyncSession](entities/asyncsession.md) — An asynchronous database session provided by SQLAlchemy for database interaction

- [VectorChunk](entities/vectorchunk.md) — A data class representing a chunk of text with its embedding and metadata, used 

- [ErrorResponse](entities/errorresponse.md) — Pydantic schema for standardizing API error responses, providing a detailed mess

- [IngestionStatusResponse](entities/ingestionstatusresponse.md) — A Pydantic schema used for responding to requests that query the status of an in

- [IngestionResponse](entities/ingestionresponse.md) — A Pydantic schema used for responding to requests that initiate an ingestion job

- [IngestionRequest](entities/ingestionrequest.md) — Pydantic schema for requesting document ingestion, specifying the target domain,

- [APIKeyListResponse](entities/apikeylistresponse.md) — Pydantic schema for a paginated list of API key responses.

- [APIKeyCreateResponse](entities/apikeycreateresponse.md) — Pydantic schema for the response after creating an API key, extending APIKeyResp

- [APIKeyResponse](entities/apikeyresponse.md) — Pydantic schema for responding with API key metadata, excluding the actual key, 

- [APIKeyCreate](entities/apikeycreate.md) — Pydantic schema for creating a new API key, specifying its name, scopes, allowed

- [DocumentListResponse](entities/documentlistresponse.md) — Pydantic schema for a paginated list of document responses.

- [DocumentResponse](entities/documentresponse.md) — Pydantic schema for responding with document details, extending DocumentBase wit

- [DocumentCreate](entities/documentcreate.md) — Pydantic schema for creating a new document, extending DocumentBase with domain 

- [DocumentBase](entities/documentbase.md) — Base Pydantic schema for a document, defining its title and optional metadata.

- [DomainAccessResponse](entities/domainaccessresponse.md) — A Pydantic schema for serializing and structuring domain access grant data for A

- [DomainAccessRevoke](entities/domainaccessrevoke.md) — Pydantic schema for revoking access to a domain for a specific user.

- [DomainAccessGrant](entities/domainaccessgrant.md) — A Pydantic schema for validating and structuring data when granting domain acces

- [DomainUpdate](entities/domainupdate.md) — A schema (likely Pydantic) defining the data structure for updating an existing 

- [DomainCreate](entities/domaincreate.md) — A schema (likely Pydantic) defining the data structure for creating a new domain

- [DomainBase](entities/domainbase.md) — Base Pydantic schema for a domain, defining its name and an optional description

- [UserResponse](entities/userresponse.md) — A Pydantic schema for serializing and structuring user data for API responses.

- [UserCreate](entities/usercreate.md) — Pydantic schema for creating a new user, extending UserBase with required Keyclo

- [UserBase](entities/userbase.md) — Base Pydantic schema for user information, including email and optional full nam

- [CollectionNotFoundError](entities/collectionnotfounderror.md) — A specific exception raised when an operation targets a vector collection that d

- [CollectionExistsError](entities/collectionexistserror.md) — A specific exception raised when an attempt is made to create a vector collectio

- [VectorStoreError](entities/vectorstoreerror.md) — The base exception class for all custom errors that can occur during vector stor

- [CollectionInfo](entities/collectioninfo.md) — A dataclass providing descriptive information about a specific vector collection

- [EmbeddingTaskType](entities/embeddingtasktype.md) — An enumeration defining various task types for embedding models, such as semanti

- [IngestionJob](entities/ingestionjob.md) — A database model representing a specific job to ingest a document, tracking its 

- [APIKey](entities/apikey.md) — A model used in the API that includes a 'rate_limit' field.

- [Domain](entities/domain.md) — A data model representing a domain in the application's database.

- [User](entities/user.md) — Represents the SQLAlchemy ORM model for a user entity.

- [DomainAccessRole](entities/domainaccessrole.md) — An enumeration defining the possible roles a user can have within a domain (e.g.

- [DocumentStatus](entities/documentstatus.md) — An enumeration defining the possible states for a document or an ingestion job, 

- [Config](entities/config.md) — A utility class for loading application configuration parameters such as environ

- [HealthResponse](entities/healthresponse.md) — Pydantic schema for a health check response, detailing service name, overall sta

- [TextExtractionError](entities/textextractionerror.md) — An exception class indicating a failure during the text extraction process from 

- [UnsupportedFormatError](entities/unsupportedformaterror.md) — An exception class indicating that the provided file format for text extraction 

- [ChunkingError](entities/chunkingerror.md) — An exception raised when an error occurs during the document chunking process.

- [Base](entities/base.md) — The SQLAlchemy declarative base class that all ORM models should inherit from to

- [DomainAccessChecker](entities/domainaccesschecker.md) — A class that provides a customizable FastAPI dependency for checking a user's ac

- [Document](entities/document.md) — A data model representing a document in the application's database.

- [DomainAccess](entities/domainaccess.md) — Represents the SQLAlchemy ORM model for a user's access grant to a specific doma

- [UserInToken](entities/userintoken.md) — A Pydantic schema or model used to represent the structure of user information e

- [SearchResponse](entities/searchresponse.md) — A data transfer object (DTO) schema for the overall search operation response, c

- [SearchRequest](entities/searchrequest.md) — A data transfer object (DTO) schema for incoming search query parameters.

- [APIRouter](entities/apirouter.md) — A class from FastAPI used to define modular API routes.

- [IngestionError](entities/ingestionerror.md) — Custom exception raised for errors encountered during the document ingestion pro

- [IngestionService](entities/ingestionservice.md) — A service class responsible for managing the lifecycle of document ingestion, fr

- [router](entities/router.md) — An instance of APIRouter, configured with the prefix '/v1/ingest' and tag 'Inges

- [InvalidModelError](entities/invalidmodelerror.md) — A specific exception indicating that an invalid or unsupported model was specifi

- [AuthenticationError](entities/authenticationerror.md) — A specific exception indicating that an authentication failure occurred during a

- [RateLimitError](entities/ratelimiterror.md) — A specific exception indicating that a rate limit has been exceeded when attempt

- [EmbeddingError](entities/embeddingerror.md) — The base exception class for all errors that can occur during embedding operatio

- [OllamaAdapter](entities/ollamaadapter.md) — A medium-priority planned adapter for local embeddings using Ollama.

- [OpenAIAdapter](entities/openaiadapter.md) — A medium-priority planned adapter to use OpenAI as an embedding provider.

- [QdrantAdapter](entities/qdrantadapter.md) — A medium-priority planned adapter for Qdrant, intended to replace ChromaDB.

- [SearchService Class](entities/searchservice_class.md) — A Python class that encapsulates the core business logic for different search mo

- [DeadLetterQueue](entities/deadletterqueue.md) — A mechanism for storing information about ingestion jobs that have permanently f

- [ChunkingConfig](entities/chunkingconfig.md) — A configuration class that specifies parameters for how documents should be chun

- [Ingestion Service](entities/ingestion_service.md) — The core business logic service responsible for validating documents, creating i

- [PaginatedResponse](entities/paginatedresponse.md) — Pydantic model for standardized paginated API response metadata, including the l

- [PaginationParams](entities/paginationparams.md) — Pydantic model defining parameters for pagination queries, including page number

- [DomainListResponse](entities/domainlistresponse.md) — Pydantic schema for a paginated list of domain responses.

- [DomainResponse](entities/domainresponse.md) — A Pydantic schema for serializing and structuring domain data for API responses.

- [APIKeyService](entities/apikeyservice.md) — A service responsible for validating API keys, utilized by `MCPAuthMiddleware` t

- [DomainService](entities/domainservice.md) — A service class responsible for orchestrating CRUD operations on domains and man

- [IngestionJob Model](entities/ingestionjob_model.md) — A database model for tracking document ingestion jobs, including document ID, st

- [APIKey Model](entities/apikey_model.md) — A database model for managing API keys used for external integrations, storing k

- [DomainAccess Model](entities/domainaccess_model.md) — A many-to-many database model linking users to domains with specific roles, enab

- [Document Model](entities/document_model.md) — A database model representing document metadata, including title, status, and ch

- [Domain Model](entities/domain_model.md) — A database model representing a knowledge domain, with fields such as name, embe

- [User Model](entities/user_model.md) — A database model representing a user, synced from Keycloak with fields like keyc

- [PaginatedResponse schema](entities/paginatedresponse_schema.md) — A Pydantic schema for structuring paginated API responses, including total items

- [PaginationParams schema](entities/paginationparams_schema.md) — A Pydantic schema for defining pagination request parameters like page number an

- [IngestionJob model](entities/ingestionjob_model.md) — A SQLAlchemy model for tracking data ingestion jobs.

- [APIKey model](entities/apikey_model.md) — A SQLAlchemy model for managing API keys used by external integrations.

- [DomainAccess model](entities/domainaccess_model.md) — A SQLAlchemy model for many-to-many relationships defining user access to domain

- [Document model](entities/document_model.md) — A SQLAlchemy model for document metadata stored in PostgreSQL.

- [Domain model](entities/domain_model.md) — A SQLAlchemy model representing knowledge domains.

- [User model](entities/user_model.md) — A SQLAlchemy model representing users, synced from Keycloak.

- [APIKeyModel](entities/apikeymodel.md) — SQLAlchemy model storing API key details, including hashed keys and scopes.

- [DomainAccessModel](entities/domainaccessmodel.md) — SQLAlchemy model managing many-to-many relationships between users and domains w

- [UserModel](entities/usermodel.md) — SQLAlchemy model representing a user, synced from Keycloak.

- [DocumentModel](entities/documentmodel.md) — SQLAlchemy model representing document metadata, linked to a domain.

- [DomainModel](entities/domainmodel.md) — SQLAlchemy model representing a knowledge domain with attributes like id, name, 

- [GeminiAdapter](entities/geminiadapter.md) — An adapter class that implements the EmbeddingPort interface, using Google's Gem

- [ChromaDBAdapter](entities/chromadbadapter.md) — A concrete implementation of the VectorStorePort interface, used for interacting

- [SearchService (Example)](entities/searchservice_example.md) — An example domain service demonstrating the usage of the VectorStorePort interfa

- [Gemini Embedding Adapter](entities/gemini_embedding_adapter.md) — A concrete implementation of the EmbeddingPort interface, using the Gemini model

- [ChromaDB Vector Store Adapter](entities/chromadb_vector_store_adapter.md) — A concrete implementation of the VectorStorePort interface, specifically for int

- [EmbeddingConfig](entities/embeddingconfig.md) — A dataclass used to configure an embedding model, specifying properties like mod

- [SearchResult](entities/searchresult.md) — A data transfer object (DTO) schema for a single search result item.

- [Chunk](entities/chunk.md) — A dataclass representing a text chunk, including its unique ID, content, optiona

- [EmbeddingPort](entities/embeddingport.md) — An abstract base class (interface) defining the contract for embedding providers

- [VectorStorePort](entities/vectorstoreport.md) — An abstract port defining the interface for interacting with any vector database

- [Network](entities/network.md) — A class from the `pyvis.network` module used to build and display interactive ne

## Functions

- [_embed_batch](entities/_embed_batch.md) — A private method within GeminiAdapter responsible for constructing and sending a

- [get_embedding_adapter](entities/get_embedding_adapter.md) — An asynchronous factory function that returns a configured EmbeddingPort impleme

- [get_vector_store_adapter](entities/get_vector_store_adapter.md) — An asynchronous factory function that returns a configured VectorStorePort imple

- [bind_request_context](entities/bind_request_context.md) — A function within `logging_config.py` designed to bind request-specific context 

- [knowledge-api (script)](entities/knowledge-api_script.md) — The command-line entry point defined in `pyproject.toml` for the API.

- [loadDomains](entities/loaddomains.md) — An incorrectly named method that was previously called to retrieve domain data, 

- [fetchDomains](entities/fetchdomains.md) — The correct method name in the 'store' module used to retrieve domain data.

- [onMounted](entities/onmounted.md) — A Vue lifecycle hook that runs after the component has been mounted to the DOM.

- [Endpoint /metrics](entities/endpoint_metrics.md) — An existing endpoint that provides metrics but lacks a full monitoring stack.

- [Job status endpoint](entities/job_status_endpoint.md) — An endpoint in the API ingestion module that requires domain access checks.

- [check_domain_access](entities/check_domain_access.md) — A utility function that verifies if an authenticated API key is authorized to ac

- [require_scope](entities/require_scope.md) — A utility function that checks if an authenticated API key has the necessary sco

- [get_mcp_app](entities/get_mcp_app.md) — A function within the `mcp_server` module that returns the ASGI application inst

- [useBreakpoint composable](entities/usebreakpoint_composable.md) — A Vue composable at `useBreakpoint.ts` used for detecting responsive breakpoints

- [NestedPropertyAccess](entities/nestedpropertyaccess.md) — A utility function for safely retrieving values from deeply nested object proper

- [ValueSerialization](entities/valueserialization.md) — A utility function for consistently converting various data types (e.g., boolean

- [Debounce](entities/debounce.md) — A utility function used to limit the rate at which another function can execute,

- [TextNormalization](entities/textnormalization.md) — A utility function that normalizes a string by converting it to NFKD form, remov

- [ConfigurationParser](entities/configurationparser.md) — A function responsible for extracting initial settings and data (options, optgro

- [HighlightText](entities/highlighttext.md) — A utility function that visually highlights occurrences of a specified search te

- [highlightFilter](entities/highlightfilter.md) — Filters nodes based on a specified property and value. It can filter either node

- [selectNodes](entities/selectnodes.md) — A convenience function that selects a given array of nodes in the network and th

- [selectNode](entities/selectnode.md) — A convenience function that selects a given array of nodes in the network and th

- [filterHighlight](entities/filterhighlight.md) — Filters (hides and shows) nodes in the network. When nodes are selected, all oth

- [neighbourhoodHighlight](entities/neighbourhoodhighlight.md) — Highlights a selected node and its connections up to two degrees of separation. 

- [dev:all](entities/devall.md) — A development script that concurrently starts all main UI components: shell, dom

- [dev](entities/dev.md) — A development script that starts the 'shell' UI component using pnpm's filter me

- [createWebHistory](entities/createwebhistory.md) — A Vue Router function that creates an HTML5 history mode instance, providing cle

- [createRouter](entities/createrouter.md) — A Vue Router function used to create a new router instance with specified histor

- [createPinia](entities/createpinia.md) — A Pinia function used to create a new Pinia store instance.

- [build script](entities/build_script.md) — A script to compile and bundle the 'search-ui' application for production.

- [dev script](entities/dev_script.md) — A development script that starts the Vite development server for 'search-ui' on 

- [createApp](entities/createapp.md) — A Vue function used to create a new application instance based on a root compone

- [federation](entities/federation.md) — The primary function from `@originjs/vite-plugin-federation` used to configure M

- [vue](entities/vue.md) — The core Vue.js library providing functionalities for building user interfaces, 

- [defineConfig](entities/defineconfig.md) — A utility function from Vite that helps define a configuration object, providing

- [uuid4](entities/uuid4.md) — A function from the `uuid` module used to generate a random UUID.

- [patch](entities/patch.md) — A decorator/context manager from `unittest.mock` used to temporarily replace obj

- [test_revoke_domain_access](entities/test_revoke_domain_access.md) — Tests that an administrator can successfully revoke a user's access to a domain.

- [test_grant_domain_access](entities/test_grant_domain_access.md) — Tests that an administrator can successfully grant access to a domain for a spec

- [test_delete_nonexistent_domain](entities/test_delete_nonexistent_domain.md) — Tests that attempting to delete a non-existent domain returns a 404 Not Found er

- [test_delete_domain](entities/test_delete_domain.md) — Tests that an administrator can successfully delete an existing domain.

- [test_update_domain](entities/test_update_domain.md) — Tests that an administrator can successfully update the details of an existing d

- [test_get_nonexistent_domain](entities/test_get_nonexistent_domain.md) — Tests that attempting to retrieve a domain with a non-existent ID returns a 404 

- [test_get_domain_by_id](entities/test_get_domain_by_id.md) — Tests that a domain can be successfully retrieved using its unique identifier.

- [test_list_domains_pagination](entities/test_list_domains_pagination.md) — Tests that the domain listing endpoint correctly handles pagination parameters.

- [test_list_domains_as_admin](entities/test_list_domains_as_admin.md) — Tests that an administrator can retrieve a list of all domains.

- [test_create_domain_as_reader](entities/test_create_domain_as_reader.md) — Tests that a user with a reader role is unauthorized to create a new domain.

- [test_create_domain_as_admin](entities/test_create_domain_as_admin.md) — Tests that an administrator role can successfully create a new domain.

- [test_verify_api_key](entities/test_verify_api_key.md) — Tests that `verify_api_key` accurately checks an API key against its stored hash

- [test_hash_api_key](entities/test_hash_api_key.md) — Tests that `hash_api_key` consistently generates a 64-character SHA-256 hash for

- [test_generate_api_key](entities/test_generate_api_key.md) — Tests that `generate_api_key` produces unique, secure, and sufficiently long API

- [test_extract_user_without_realm_access](entities/test_extract_user_without_realm_access.md) — Tests that `extract_user_from_token` gracefully handles payloads missing the `re

- [test_extract_user_with_client_roles](entities/test_extract_user_with_client_roles.md) — Tests that `extract_user_from_token` aggregates both realm-level and client-spec

- [test_extract_user_from_token](entities/test_extract_user_from_token.md) — Tests that `extract_user_from_token` correctly populates a `UserInToken` object 

- [test_verify_expired_jwt_token](entities/test_verify_expired_jwt_token.md) — Tests that `verify_jwt_token` returns `None` when it encounters an expired JWT t

- [test_verify_invalid_jwt_token](entities/test_verify_invalid_jwt_token.md) — Tests that `verify_jwt_token` returns `None` when provided with a token that is 

- [test_verify_valid_jwt_token](entities/test_verify_valid_jwt_token.md) — Tests that `verify_jwt_token` successfully processes a valid JWT token, returnin

- [test_revoke_api_key](entities/test_revoke_api_key.md) — Tests the successful revocation of an API key, verifying the HTTP status code an

- [test_list_api_keys](entities/test_list_api_keys.md) — Tests the listing of API keys, verifying the list structure, total count, and en

- [test_create_api_key](entities/test_create_api_key.md) — Tests the successful creation of an API key, verifying the HTTP status code, res

- [mock_admin_payload](entities/mock_admin_payload.md) — A pytest fixture returning a dictionary representing a mock JWT payload for an '

- [mock_user_payload](entities/mock_user_payload.md) — A pytest fixture returning a dictionary representing a mock JWT payload for a st

- [mock_jwt_token](entities/mock_jwt_token.md) — A pytest fixture returning a static, mock JWT token string for use in authentica

- [test_domain](entities/test_domain.md) — A pytest-asyncio fixture that creates and commits a test domain associated with 

- [test_admin](entities/test_admin.md) — A pytest-asyncio fixture that creates and commits a 'km-admin' test user to the 

- [test_user](entities/test_user.md) — A pytest-asyncio fixture that creates and commits a standard 'km-reader' test us

- [db_session](entities/db_session.md) — A pytest-asyncio fixture providing a fresh, isolated database session for each t

- [event_loop](entities/event_loop.md) — A pytest-asyncio fixture that provides a new event loop for the test session, en

- [get_job_status](entities/get_job_status.md) — Retrieves the current status of a specific IngestionJob by its ID from the datab

- [_fail_job](entities/_fail_job.md) — A private helper method to mark both a Document and its corresponding IngestionJ

- [process_document](entities/process_document.md) — The core method that executes the full document processing pipeline: text extrac

- [create_ingestion_job](entities/create_ingestion_job.md) — Asynchronously creates a new Document record and an associated IngestionJob, ini

- [to_domain_access_response](entities/to_domain_access_response.md) — A utility function that converts a 'DomainAccess' model object into a 'DomainAcc

- [DomainService.list_access_grants](entities/domainservicelist_access_grants.md) — Lists all access records associated with a particular domain, eagerly loading us

- [DomainService.revoke_access](entities/domainservicerevoke_access.md) — Deletes a specific user's access record for a given domain, effectively removing

- [DomainService.grant_access](entities/domainservicegrant_access.md) — Establishes or updates a user's access role for a specified domain, handling bot

- [DomainService.delete_domain](entities/domainservicedelete_domain.md) — Removes a domain entity from the database.

- [DomainService.update_domain](entities/domainserviceupdate_domain.md) — Modifies the 'name' and/or 'description' of an existing domain.

- [DomainService.list_domains](entities/domainservicelist_domains.md) — Retrieves a paginated list of domains, filtering them based on user permissions 

- [DomainService.get_domain](entities/domainserviceget_domain.md) — Fetches a single domain record from the database using its unique identifier.

- [DomainService.create_domain](entities/domainservicecreate_domain.md) — Creates a new domain entity in the database and automatically assigns the creati

- [validate_api_key](entities/validate_api_key.md) — An asynchronous method of `APIKeyService` that validates a plain API key string 

- [to_api_key_response](entities/to_api_key_response.md) — A utility function responsible for converting an `APIKey` database model instanc

- [to_domain_response](entities/to_domain_response.md) — A utility function that transforms a database 'Domain' model object into a 'Doma

- [EmbeddingPort.health_check](entities/embeddingporthealth_check.md) — An abstract method in `EmbeddingPort` to perform a lightweight check to verify t

- [EmbeddingPort.embed_document](entities/embeddingportembed_document.md) — An abstract method in `EmbeddingPort` for generating a single embedding vector s

- [EmbeddingPort.embed_query](entities/embeddingportembed_query.md) — An abstract method in `EmbeddingPort` for generating a single embedding vector s

- [EmbeddingPort.embed](entities/embeddingportembed.md) — An abstract method in `EmbeddingPort` responsible for generating embedding vecto

- [generate_uuid](entities/generate_uuid.md) — Generates a new UUID string, typically used as a default for ID columns in model

- [root](entities/root.md) — An API endpoint serving as the application's base path, providing basic API info

- [lifespan](entities/lifespan.md) — An asynchronous context manager that orchestrates the application's lifecycle, h

- [detect_file_type](entities/detect_file_type.md) — Determines and returns the standard MIME type string associated with a given fil

- [extract_text_from_txt](entities/extract_text_from_txt.md) — Decodes and extracts text from a plain text file, attempting UTF-8 decoding firs

- [extract_text_from_docx](entities/extract_text_from_docx.md) — Extracts text content from a Microsoft Word DOCX document by processing its para

- [extract_text_from_pdf](entities/extract_text_from_pdf.md) — Extracts human-readable text content from a Portable Document Format (PDF) file 

- [extract_text](entities/extract_text.md) — A utility function imported from `ingestion.extractors` responsible for extracti

- [chunk_document](entities/chunk_document.md) — A utility function imported from `ingestion.chunking` that divides a document's 

- [fixed_size_chunking](entities/fixed_size_chunking.md) — Chunks text into segments of a relatively fixed character length, with configura

- [semantic_chunking](entities/semantic_chunking.md) — Chunks text by attempting to preserve semantic units, primarily paragraphs and s

- [chunk_by_sentences](entities/chunk_by_sentences.md) — Splits an input text string into a list of sentences, using common sentence-endi

- [chunk_by_paragraphs](entities/chunk_by_paragraphs.md) — Splits an input text string into a list of individual paragraphs, using multiple

- [close_db](entities/close_db.md) — An asynchronous function responsible for properly closing and disposing of the d

- [init_db](entities/init_db.md) — An asynchronous function that connects to the database and creates all tables de

- [get_current_user_optional](entities/get_current_user_optional.md) — An existing function in the API core dependencies that requires API key validati

- [verify_api_key](entities/verify_api_key.md) — A function from `core.auth` that compares a plaintext API key with a stored hash

- [hash_api_key](entities/hash_api_key.md) — A function from `core.auth` that securely hashes an API key using SHA-256.

- [generate_api_key](entities/generate_api_key.md) — A function from `core.auth` that generates a new, secure API key string.

- [extract_user_from_token](entities/extract_user_from_token.md) — A function from `core.auth` that parses a JWT token's payload to extract user-re

- [verify_jwt_token](entities/verify_jwt_token.md) — An asynchronous function from `core.auth` responsible for verifying the authenti

- [rsa_key_to_pem](entities/rsa_key_to_pem.md) — A simplified utility that ostensibly converts an RSA key from JWK format to PEM.

- [get_signing_key](entities/get_signing_key.md) — Searches the retrieved JWKS for a specific signing key matching a given Key ID (

- [fetch_jwks](entities/fetch_jwks.md) — An asynchronous function from `core.auth` responsible for fetching JSON Web Key 

- [get_search_suggestions](entities/get_search_suggestions.md) — Provides search autocomplete suggestions based on a partial query, primarily by 

- [search_documents_post](entities/search_documents_post.md) — Handles POST requests for advanced document search, accepting a SearchRequest ob

- [search_documents](entities/search_documents.md) — Handles GET requests for document search, supporting query parameters for search

- [get_search_service](entities/get_search_service.md) — A FastAPI dependency function that configures and provides an instance of the Se

- [to_ingestion_status_response](entities/to_ingestion_status_response.md) — Converts an IngestionJob object into the IngestionStatusResponse schema for API 

- [to_ingestion_response](entities/to_ingestion_response.md) — Converts Document and IngestionJob objects into the IngestionResponse schema for

- [get_document_status](entities/get_document_status.md) — Retrieves the current processing status of a specific Document by its ID from th

- [get_ingestion_status](entities/get_ingestion_status.md) — API endpoint (GET /v1/ingest/{job_id}) for retrieving the current processing sta

- [ingest_text](entities/ingest_text.md) — API endpoint (POST /v1/ingest/text) for directly ingesting raw text content with

- [get_db](entities/get_db.md) — An asynchronous dependency function that provides a database session (`AsyncSess

- [list_domain_access](entities/list_domain_access.md) — Lists all users with access grants for a specific domain; requires domain admini

- [revoke_domain_access](entities/revoke_domain_access.md) — Revokes a user's access to a specified domain; requires domain administrator pri

- [grant_domain_access](entities/grant_domain_access.md) — Grants a specified user access to a particular domain; requires domain administr

- [delete_domain](entities/delete_domain.md) — Deletes a knowledge domain; requires domain administrator privileges.

- [update_domain](entities/update_domain.md) — Modifies an existing knowledge domain's details; requires domain administrator p

- [get_domain](entities/get_domain.md) — Retrieves details for a specific domain by its ID; requires the user to have acc

- [list_domains](entities/list_domains.md) — Lists all knowledge domains accessible to the current user, with pagination supp

- [create_domain](entities/create_domain.md) — Creates a new knowledge domain; requires the 'km-admin' role.

- [revoke_api_key](entities/revoke_api_key.md) — An asynchronous method of `APIKeyService` that deactivates an existing API key b

- [get_api_key](entities/get_api_key.md) — An asynchronous method of `APIKeyService` that retrieves an `APIKey` object from

- [list_api_keys](entities/list_api_keys.md) — An asynchronous method of `APIKeyService` that retrieves a paginated list of API

- [create_api_key](entities/create_api_key.md) — An asynchronous method of `APIKeyService` that generates a new API key, hashes i

- [health_check](entities/health_check.md) — An abstract method within `VectorStorePort` to ascertain the operational status 

- [get_collection_count](entities/get_collection_count.md) — An abstract method within `VectorStorePort` to retrieve the total number of vect

- [delete](entities/delete.md) — An abstract method within `VectorStorePort` to remove specific chunks from a col

- [search](entities/search.md) — An abstract method within `VectorStorePort` to perform a semantic similarity sea

- [upsert](entities/upsert.md) — An abstract method within `VectorStorePort` to insert new chunks or update exist

- [list_collections](entities/list_collections.md) — An abstract method within `VectorStorePort` to retrieve a list of all existing c

- [delete_collection](entities/delete_collection.md) — An abstract method within `VectorStorePort` to permanently delete a collection a

- [create_collection](entities/create_collection.md) — An abstract method within `VectorStorePort` to create a new vector collection wi

- [close](entities/close.md) — Asynchronously closes the underlying httpx.AsyncClient connections, releasing re

- [client](entities/client.md) — A pytest-asyncio fixture providing an asynchronous HTTP client ("httpx.AsyncClie

- [__init__](entities/__init__.md) — The constructor for the `APIKeyService` class, responsible for injecting the asy

- [test_search_service](entities/test_search_service.md) — An example test function illustrating how to unit test a service by mocking its 

- [Suggestions Endpoint](entities/suggestions_endpoint.md) — A GET endpoint (`/v1/search/suggest`) providing autocomplete query suggestions.

- [Advanced Search Endpoint](entities/advanced_search_endpoint.md) — A POST endpoint (`/v1/search`) for performing searches with a JSON request body,

- [Main Search Endpoint](entities/main_search_endpoint.md) — The primary GET endpoint (`/v1/search`) for performing searches with query param

- [Search API Endpoint](entities/search_api_endpoint.md) — The public HTTP GET endpoint (`/v1/search`) that exposes the search functionalit

- [keyword_search Function](entities/keyword_search_function.md) — A function specifically for performing BM25 keyword search using PostgreSQL full

- [hybrid_search Method](entities/hybrid_search_method.md) — A method within SearchService for combining semantic and keyword search results 

- [semantic_search Method](entities/semantic_search_method.md) — A method within SearchService for performing vector-based semantic search.

- [Reciprocal Rank Fusion (RRF)](entities/reciprocal_rank_fusion_rrf.md) — An algorithm used to combine and re-rank results from multiple search algorithms

- [BM25 Keyword Search](entities/bm25_keyword_search.md) — Retrieves documents based on keyword matching with BM25-like relevance scoring, 

- [Vector Store Search](entities/vector_store_search.md) — Retrieves documents or chunks based on vector similarity in a vector database.

- [Query Embedding](entities/query_embedding.md) — The process of converting a natural language query into a vector representation 

- [vector_store.upsert](entities/vector_storeupsert.md) — A function call used to store or update chunks, along with their embeddings and 

- [embedding_provider.embed](entities/embedding_providerembed.md) — A function call used within the ingestion pipeline responsible for generating em

- [process_document_job](entities/process_document_job.md) — A background task function decorated with `@job` for ARQ, responsible for execut

- [process_job](entities/process_job.md) — An asynchronous method within the IngestionService responsible for the core proc

- [ingest_document](entities/ingest_document.md) — API endpoint (POST /v1/ingest) responsible for uploading a document file and ini

- [require_domain_admin](entities/require_domain_admin.md) — A dependency that ensures the authenticated user has administrative privileges f

- [require_domain_access](entities/require_domain_access.md) — A dependency injection function (imported) that authenticates the user and verif

- [require_reader](entities/require_reader.md) — FastAPI dependency that ensures the authenticated user possesses either the 'km-

- [require_admin](entities/require_admin.md) — FastAPI dependency that ensures the authenticated user possesses the 'km-admin' 

- [get_current_user](entities/get_current_user.md) — FastAPI dependency that enforces authentication. It depends on `get_current_user

- [DELETE /v1/api-keys/{id}](entities/delete_v1api-keysid.md) — Endpoint to revoke an API key.

- [GET /v1/api-keys/{id}](entities/get_v1api-keysid.md) — Endpoint to retrieve a specific API key by its ID.

- [GET /v1/api-keys](entities/get_v1api-keys.md) — Endpoint to list existing API keys.

- [POST /v1/api-keys](entities/post_v1api-keys.md) — Endpoint to create a new API key.

- [GET /v1/domains/{id}/access](entities/get_v1domainsidaccess.md) — Endpoint to list access grants for a specific domain, restricted to domain admin

- [DELETE /v1/domains/{id}/access](entities/delete_v1domainsidaccess.md) — Endpoint to revoke access to a domain for a user, restricted to domain administr

- [POST /v1/domains/{id}/access](entities/post_v1domainsidaccess.md) — Endpoint to grant access to a domain for a user, restricted to domain administra

- [DELETE /v1/domains/{id}](entities/delete_v1domainsid.md) — Endpoint to delete a domain, restricted to domain administrators.

- [PUT /v1/domains/{id}](entities/put_v1domainsid.md) — Endpoint to update an existing domain, restricted to domain administrators.

- [GET /v1/domains/{id}](entities/get_v1domainsid.md) — Endpoint to retrieve a specific domain by its ID.

- [GET /v1/domains](entities/get_v1domains.md) — Endpoint to list domains, supporting pagination and filtering by user access.

- [POST /v1/domains](entities/post_v1domains.md) — Endpoint to create a new domain, restricted to administrators.

- [require_domain_admin()](entities/require_domain_admin.md) — A FastAPI dependency function to enforce domain administrator access.

- [require_domain_access()](entities/require_domain_access.md) — A FastAPI dependency function to enforce access based on domain permissions.

- [require_reader()](entities/require_reader.md) — A FastAPI dependency function to enforce reader-only access.

- [require_admin()](entities/require_admin.md) — A FastAPI dependency function to enforce administrator-only access.

- [get_current_user()](entities/get_current_user.md) — A FastAPI dependency function for extracting and syncing user information from a

- [close_db()](entities/close_db.md) — A function for gracefully shutting down database connections.

- [init_db()](entities/init_db.md) — A function for creating database tables on startup.

- [get_db()](entities/get_db.md) — A FastAPI dependency function for providing database sessions.

- [`require_domain_access` RBAC Dependency](entities/require_domain_access_rbac_dependency.md) — FastAPI dependency checking if the current user has access to a specific knowled

- [`require_reader` RBAC Dependency](entities/require_reader_rbac_dependency.md) — FastAPI dependency enforcing that the current user has either 'km-reader' or 'km

- [`require_admin` RBAC Dependency](entities/require_admin_rbac_dependency.md) — FastAPI dependency enforcing that the current user has the 'km-admin' role.

- [`get_current_user` FastAPI Dependency](entities/get_current_user_fastapi_dependency.md) — FastAPI dependency responsible for validating JWT tokens and extracting user cla

- [/health Endpoint](entities/health_endpoint.md) — A FastAPI endpoint designed for health probes, returning service name, status, v
