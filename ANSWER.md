Siguiendo las Working Rules, antes de planificar necesito entender bien el proyecto. Tengo varias preguntas clave para evitar
  suposiciones:

  ---
  1. Tipo de conocimiento
  ¿Qué formato tiene el "conocimiento" que ingresa a la plataforma? ¿Documentos (PDF, Word, texto plano), páginas web, datos
  estructurados (JSON/CSV), código fuente, o una combinación?

  2. Dominios de conocimiento
  ¿Cómo se definen los dominios? ¿Son categorías predefinidas por el administrador, creadas dinámicamente por el usuario, o inferidas
   automáticamente del contenido?

  3. FastMCP y componente AI
  El uso de FastMCP (Model Context Protocol) sugiere integración con modelos de lenguaje (LLMs). ¿Hay un componente de IA para
  procesar, indexar o consultar el conocimiento (embeddings, búsqueda semántica, RAG)? ¿Qué LLM o proveedor se usa?

  4. Base de datos
  ¿Hay preferencia de tecnología de almacenamiento? Por ejemplo:
  - Relacional: PostgreSQL
  - Documental: MongoDB
  - Búsqueda full-text/vectorial: Elasticsearch, Qdrant, Weaviate, ChromaDB
  - ¿O una combinación?

  5. Búsqueda
  ¿Qué tipo de búsqueda se espera? ¿Full-text clásica, semántica (vectorial), híbrida, o filtros por dominio/metadatos?

  6. Infraestructura y despliegue
  ¿Cuál es el target de despliegue? ¿Docker Compose local, Kubernetes, cloud (AWS/GCP/Azure)? ¿Hay servicios ya existentes de Kafka,
  RabbitMQ, S3, Keycloak que se reutilicen?

  7. APIs para terceros
  ¿Las APIs públicas de búsqueda para terceros requieren autenticación vía Keycloak también, o usan otro mecanismo (API keys, JWT
  propio)?

  8. Escala aproximada
  ¿Hay expectativas de volumen? (número de documentos, usuarios concurrentes, frecuencia de ingesta)

  ---
  Con estas respuestas podré producir un plan de arquitectura completo para tu aprobación antes de escribir cualquier código.

✻ Worked for 28s

※ recap: Designing a full-stack Knowledge Management Platform. Waiting for answers to 8 clarifying questions about knowledge types,
  domains, AI/FastMCP role, database preferences, search strategy, deployment target, third-party auth, and scale before creating the
   architecture plan. (disable recaps in /config)

> 1. PDF, Texto plano y codigo fuente. 2. los dominios serán definidos por un administrador de forma centralizada. 3. debe haber
  componente para indexar y consultar documentos usando embeddings sobre 2 tipos de base de datos (Neo4J y QDrant) - para el 1er MVP
   usar FAISS a reemplazar luego por QDrant y usaremos diferentes LLMs donde inicialmente se usara Gemini (default) y el uso de MCP
  es para permitir a Agentes AI de terceros integrarse a la base de conocimiento. 4. Relacional: PostgreSQL, Documental: MongoDB,
  Búsqueda full-text/vectorial: ChromaDB (para el MVP inicial) y posteriormente cambiar a QDrant. 5. espero realizar busquedas
  semántica (vectorial), híbrida, o filtros por dominio/metadatos. 6. docker compose inicial y kubernetes, considerar servicio
  inicial disponible Keycloak (https://oauth2.qa.comsatel.com.pe) v26+. 7. autenticacion usando API Key. 8. no tengo una escala aun
  definida.