"""Adapters package - Concrete implementations of ports.

This module provides factory functions to get instances of the adapters.
All adapters implement their respective Port interfaces, allowing for
easy swapping of implementations without changing business logic.
"""

import os
from typing import Optional

# Lazy imports to avoid circular dependencies


async def get_vector_store_adapter(
    host: Optional[str] = None,
    port: Optional[int] = None
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
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> "EmbeddingPort":
    """
    Factory function to get the configured embedding adapter.
    
    Priority:
    1. OLLAMA_EMBEDDING_MODEL - Use local Ollama instance
    2. Gemini API - Use Google AI Studio API
    3. Mock - Fall back to deterministic hash-based embeddings
    
    Args:
        api_key: API key for the embedding service (defaults to GEMINI_API_KEY env var)
        model: Model name (defaults to OLLAMA_EMBEDDING_MODEL or GEMINI_EMBEDDING_MODEL)
    
    Returns:
        Configured EmbeddingPort instance
    
    Example:
        adapter = await get_embedding_adapter()
        embeddings = await adapter.embed(["text to embed"])
    """
    # Check if Ollama is explicitly requested
    ollama_model = os.getenv("OLLAMA_EMBEDDING_MODEL")
    if ollama_model:
        from adapters.embedding.ollama import OllamaAdapter
        ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
        return OllamaAdapter(
            model=ollama_model,
            host=ollama_host,
            port=ollama_port
        )
    
    # Check if mock embedding is explicitly requested
    if os.getenv("MOCK_EMBEDDING", "false").lower() == "true":
        from adapters.embedding.mock import MockEmbeddingAdapter
        return MockEmbeddingAdapter()
    
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    model = model or os.getenv("GEMINI_EMBEDDING_MODEL", "embedding-001")
    
    if not api_key:
        # Fall back to mock adapter for testing
        from adapters.embedding.mock import MockEmbeddingAdapter
        return MockEmbeddingAdapter()
    
    # Use Gemini adapter (will fall back to hash embeddings if API fails)
    from adapters.embedding.gemini import GeminiAdapter
    return GeminiAdapter(api_key=api_key, model=model)


# Type imports for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ports.vector_store import VectorStorePort
    from ports.embedding import EmbeddingPort
