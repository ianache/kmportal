# Knowledge Management Center

Plataforma completa de gestión del conocimiento organizado en dominios definidos por administradores.

## 🎯 Objetivo

Cualquier usuario autenticado puede encontrar conocimiento relevante dentro de los dominios autorizados en segundos, usando búsqueda semántica o híbrida sobre documentos indexados.

## 🏗️ Arquitectura

**Stack Tecnológico:**
- **Core API**: Python 3.13 + FastAPI + FastMCP
- **BFF**: Node.js + Fastify + WebSocket
- **Frontend**: Vue 3 + Pinia + Module Federation
- **Datos**: PostgreSQL + MongoDB + ChromaDB → Qdrant
- **Auth**: Keycloak (OAuth2/OIDC)
- **Infra**: Docker Compose → Kubernetes

## 📋 Roadmap

| Fase | Nombre | Estado |
|------|--------|--------|
| 1 | Bootstrap infrastructure | 🟡 **In Progress** |
| 2 | Core API foundation | 🔵 Planned |
| 3 | Document ingestion pipeline | 🔵 Planned |
| 4 | Search engine | 🔵 Planned |
| 5-10 | BFF, Frontend, MCP, Production | 🔵 Planned |

## 🚀 Empezar

### Requisitos

- Docker & Docker Compose
- Python 3.13+ (para desarrollo local)
- Node.js 22+ (para frontend)

### Inicio Rápido

1. **Clonar y configurar**:
```bash
git clone <repository>
cd 25-KnowledgeManagement
cp .env.example .env
# Editar .env con tus valores
```

2. **Iniciar infraestructura**:
```bash
# Solo servicios de base de datos (Phase 1)
docker compose up -d postgres mongodb chromadb redis kafka rabbitmq

# Verificar estado
docker compose ps
```

3. **Verificar health checks**:
```bash
# PostgreSQL
docker compose exec postgres pg_isready -U knowledge

# MongoDB
docker compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Redis
docker compose exec redis redis-cli ping

# Kafka
docker compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# RabbitMQ
curl http://localhost:15672/api/overview -u knowledge:change_me_in_production
```

## 📁 Estructura del Proyecto

```
25-KnowledgeManagement/
├── .planning/                 # Documentación y planificación
│   ├── PROJECT.md            # Definición del proyecto
│   ├── ROADMAP.md            # Roadmap de 10 fases
│   ├── REQUIREMENTS.md       # 54 requisitos v1
│   ├── DESIGN.md             # Sistema de diseño
│   └── phases/               # Documentación por fase
│       └── 01-bootstrap-infrastructure/
│
├── api/                       # Core API Python (FastAPI)
│   ├── src/
│   │   ├── ports/            # Interfaces abstractas
│   │   ├── adapters/         # Implementaciones
│   │   └── main.py           # App FastAPI
│   └── pyproject.toml
│
├── ingestion/                 # Worker de ingesta Python
├── bff/                       # Backend for Frontend Node.js
├── frontend/
│   ├── shell/                # Module Federation host
│   └── micro-uis/            # Micro UIs independientes
├── shared/                    # Paquetes compartidos
│
├── docker-compose.yml         # Infraestructura completa
├── .env.example              # Variables de entorno
└── README.md                 # Este archivo
```

## 🎨 Sistema de Diseño

**"Luminous Knowledge"** - Minimalismo + Glassmorphism, inspirado en Apple.

- **Color primario**: `#007AFF` (Apple Blue)
- **Fondo**: `#F9F9FF` (gris frío)
- **Tipografía**: Inter (17px base)
- **Glassmorphism**: `backdrop-filter: blur(20-30px)`

Ver `DESIGN.md` para especificaciones completas.

## 🔐 Autenticación

- **Web**: OAuth2/OIDC via Keycloak (realm=Apps, client_id=kmplatform)
- **API**: API Keys en header `X-API-Key`
- **MCP**: API Keys para agentes AI

## 📚 Documentación

- [PROJECT.md](.planning/PROJECT.md) - Visión, constraints, decisiones
- [ROADMAP.md](.planning/ROADMAP.md) - 10 fases con criterios de éxito
- [REQUIREMENTS.md](.planning/REQUIREMENTS.md) - 54 requisitos v1
- [DESIGN.md](DESIGN.md) - Sistema de diseño completo
- [api/README.md](api/README.md) - Guía del Core API

## 🧪 Testing

```bash
# Tests de API
cd api
uv run pytest

# Tests de infraestructura
docker compose config  # Validar docker-compose.yml
```

## 🚢 Deployment

### Desarrollo Local
```bash
docker compose up -d
```

### Up local

```
uvicorn main:app --app-dir src --reload --host 0.0.0.0 --port 8000 --env-file .env
```

### Producción (Phase 10)
- Kubernetes manifests
- Helm charts
- CI/CD pipeline

## 🤝 Contribuir

1. Revisar [ROADMAP.md](.planning/ROADMAP.md) para entender la fase actual
2. Seguir [DESIGN.md](DESIGN.md) para UI/UX
3. Usar Ports & Adapters pattern (ver [api/README.md](api/README.md))
4. Commit con mensajes claros: `feat(phase1): add VectorStorePort`

## 📝 Licencia

MIT

## 🆘 Soporte

- Documentación: Ver `.planning/` directory
- Issues: GitHub Issues
- Roadmap: Ver [ROADMAP.md](.planning/ROADMAP.md)

---

**Estado Actual**: Phase 1 - Bootstrap infrastructure (In Progress)

**Última actualización**: 2026-05-02
