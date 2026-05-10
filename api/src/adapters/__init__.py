"""Adapters package - Concrete implementations of ports.

This module provides factory functions to get instances of the adapters.
All adapters implement their respective Port interfaces, allowing for
easy swapping of implementations without changing business logic.
"""

import os
from typing import Optional

# Lazy imports to avoid circular dependencies


async def get_vector_store_adapter(
    host: str | None = None,
    port: int | None = None
) -> "VectorStorePort":
    """
    Factory function to get the configured vector store adapter.

    Currently returns ChromaDBAdapter. In v2, this can be configured
    to return QdrantAdapter based on environment settings.

    Args:
        host: ChromaDB host (defaults to CHROMA_HOST env var or localhost)
        port: ChromaDB port (defaults to CHROMA_PORT env var or 8000)

    Returns:
        Configured VectorStorePort instance

    Example:
        adapter = await get_vector_store_adapter()
        await adapter.create_collection("domain-123", dimension=768)
    """
    from adapters.vector_store.chroma_db import ChromaDBAdapter

    host = host or os.getenv("CHROMA_HOST", "localhost")
    port = port or int(os.getenv("CHROMA_PORT", "8000"))

    return ChromaDBAdapter(host=host, port=port)


async def get_embedding_adapter(
    api_key: str | None = None,
    model: str | None = None
) -> "EmbeddingPort":
    # ... (omitted for brevity in replace call, but I will provide full implementation)
    pass

async def get_graph_adapter(
    uri: str | None = None,
    user: str | None = None,
    password: str | None = None
) -> "GraphPort":
    """
    Factory function to get the configured graph database adapter.

    Returns Neo4jAdapter configured with environment variables.

    Args:
        uri: Connection URI (defaults to NEO4J_BOLT_URL or bolt://localhost:7687)
        user: Username (defaults to NEO4J_USER or neo4j)
        password: Password (defaults to NEO4J_PASSWORD)

    Returns:
        Configured GraphPort instance
    """
    from adapters.graph.neo4j_adapter import Neo4jAdapter
    from core.config import settings

    uri = uri or settings.neo4j_bolt_url
    user = user or settings.neo4j_user
    password = password or settings.neo4j_password

    return Neo4jAdapter(uri=uri, user=user, password=password)


# Type imports for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ports.embedding import EmbeddingPort
    from ports.vector_store import VectorStorePort
    from ports.graph import GraphPort
