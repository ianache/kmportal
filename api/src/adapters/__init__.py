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
    """
    Factory function to get the configured embedding adapter.

    Provider priority:
    1. Ollama (local) - if EMBEDDING_PROVIDER=ollama or OLLAMA_HOST is set
    2. Gemini (cloud) - if GEMINI_API_KEY is available
    3. Mock (fallback) - for testing without external services

    Args:
        api_key: API key for cloud providers (defaults to GEMINI_API_KEY env var)
        model: Model name (defaults to provider-specific env var or sensible default)

    Returns:
        Configured EmbeddingPort instance

    Environment Variables:
        EMBEDDING_PROVIDER: 'ollama', 'gemini', or 'mock' (default: auto-detect)
        OLLAMA_HOST: Ollama host (default: localhost)
        OLLAMA_PORT: Ollama port (default: 11434)
        OLLAMA_MODEL: Ollama model name (default: embeddinggemma)
        GEMINI_API_KEY: Gemini API key
        GEMINI_EMBEDDING_MODEL: Gemini model (default: text-embedding-004)
    """
    from adapters.embedding.gemini import GeminiAdapter
    from adapters.embedding.mock import MockEmbeddingAdapter
    from adapters.embedding.ollama import OllamaAdapter

    provider = os.getenv("EMBEDDING_PROVIDER", "auto").lower()

    # Determine provider if auto
    if provider == "auto":
        if os.getenv("OLLAMA_HOST") or os.getenv("EMBEDDING_PROVIDER") == "ollama":
            provider = "ollama"
        elif os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        else:
            provider = "mock"

    # Create Ollama adapter (local)
    if provider == "ollama":
        host = os.getenv("OLLAMA_HOST", "localhost")
        port = int(os.getenv("OLLAMA_PORT", "11434"))
        model = model or os.getenv("OLLAMA_MODEL", "embeddinggemma")

        return OllamaAdapter(
            model=model,
            host=host,
            port=port,
            batch_size=10
        )

    # Create Gemini adapter (cloud)
    elif provider == "gemini":
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        model = model or os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")

        if not api_key:
            raise ValueError(
                "Gemini provider selected but GEMINI_API_KEY not set. "
                "Set the API key or choose a different provider."
            )

        return GeminiAdapter(api_key=api_key, model=model)

    # Fall back to mock adapter for testing/development
    else:
        model = model or "mock-embedding"
        dimension = int(os.getenv("MOCK_EMBEDDING_DIMENSION", "768"))
        return MockEmbeddingAdapter(dimension=dimension)

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
