"""Ports package - Abstract interfaces for external services."""

from .vector_store import (
    VectorStorePort,
    Chunk,
    SearchResult,
    CollectionInfo,
    VectorStoreError,
    CollectionExistsError,
    CollectionNotFoundError,
)

from .embedding import (
    EmbeddingPort,
    EmbeddingConfig,
    EmbeddingTaskType,
    EmbeddingError,
    RateLimitError,
    AuthenticationError,
    InvalidModelError,
)

__all__ = [
    # Vector Store
    "VectorStorePort",
    "Chunk",
    "SearchResult",
    "CollectionInfo",
    "VectorStoreError",
    "CollectionExistsError",
    "CollectionNotFoundError",
    # Embedding
    "EmbeddingPort",
    "EmbeddingConfig",
    "EmbeddingTaskType",
    "EmbeddingError",
    "RateLimitError",
    "AuthenticationError",
    "InvalidModelError",
]
