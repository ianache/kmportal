"""Ports package - Abstract interfaces for external services."""

from .embedding import (
    AuthenticationError,
    EmbeddingConfig,
    EmbeddingError,
    EmbeddingPort,
    EmbeddingTaskType,
    InvalidModelError,
    RateLimitError,
)
from .vector_store import (
    Chunk,
    CollectionExistsError,
    CollectionInfo,
    CollectionNotFoundError,
    SearchResult,
    VectorStoreError,
    VectorStorePort,
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
