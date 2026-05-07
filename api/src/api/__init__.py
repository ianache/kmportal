"""API routes package."""

from api.api_keys import router as api_keys_router
from api.domains import router as domains_router
from api.health import router as health_router
from api.ingestion import router as ingestion_router
from api.ontology import router as ontology_router
from api.search import router as search_router

__all__ = [
    "domains_router",
    "api_keys_router",
    "ingestion_router",
    "search_router",
    "health_router",
    "ontology_router",
]
