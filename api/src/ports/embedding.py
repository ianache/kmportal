"""
Embedding Port - Abstract interface for text embedding generation.

This module defines the contract that all embedding providers must follow.
It enables swapping between different embedding services (Gemini, OpenAI,
Ollama, etc.) without changing business logic.

Usage:
    # In domain service - only depends on the port
    from ports.embedding import EmbeddingPort
    
    class EmbeddingService:
        def __init__(self, embedder: EmbeddingPort):
            self.embedder = embedder
        
        async def embed_document(self, chunks: List[str]) -> List[List[float]]:
            return await self.embedder.embed(chunks)

Implementations:
    - GeminiAdapter: Google Gemini embedding models
    - OpenAIAdapter: OpenAI text-embedding models (for v2)
    - OllamaAdapter: Local embeddings via Ollama (for v2)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class EmbeddingTaskType(str, Enum):
    """
    Types of embedding tasks for semantic search optimization.
    
    Some models (like Gemini) support task-specific embeddings that
    optimize for different use cases.
    """
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
    CLASSIFICATION = "CLASSIFICATION"
    CLUSTERING = "CLUSTERING"
    RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT"
    RETRIEVAL_QUERY = "RETRIEVAL_QUERY"


@dataclass
class EmbeddingConfig:
    """
    Configuration for embedding generation.
    
    Attributes:
        model: Model identifier (e.g., 'text-embedding-004')
        dimension: Output embedding dimension
        batch_size: Maximum texts per API call
        task_type: Optional task type for optimization
    """
    model: str
    dimension: int
    batch_size: int = 100
    task_type: Optional[EmbeddingTaskType] = None


class EmbeddingPort(ABC):
    """
    Abstract port for embedding generation.
    
    This interface abstracts all interactions with embedding providers.
    Business logic should only interact with this interface, never
    directly with Gemini, OpenAI, or any other concrete implementation.
    
    Implementations:
        - GeminiAdapter: Google Generative AI API
        - OpenAIAdapter: OpenAI API (for v2)
        - OllamaAdapter: Local Ollama server (for v2)
    
    Design Decisions:
        1. dimension as property - different models have different dimensions
        2. batch processing - API rate limits require batching
        3. separate query embedding - some models optimize queries differently
    """
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Return the embedding dimension for this provider.
        
        This is a property (not a method) because it's a static
        characteristic of the model.
        
        Examples:
            - Gemini text-embedding-004: 768
            - OpenAI text-embedding-3-small: 1536
            - OpenAI text-embedding-3-large: 3072
            
        Returns:
            Integer dimension of embeddings produced by this provider
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Return the model identifier string.
        
        Returns:
            Model name (e.g., 'text-embedding-004', 'text-embedding-3-small')
        """
        pass
    
    @property
    @abstractmethod
    def config(self) -> EmbeddingConfig:
        """
        Return the full configuration for this provider.
        
        Returns:
            EmbeddingConfig with all settings
        """
        pass
    
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        This method handles batching internally based on the configured
        batch_size. Callers can pass large lists without worrying about
        API limits.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors, one per input text.
            Each vector has length equal to self.dimension.
            
        Raises:
            EmbeddingError: If the API call fails
            RateLimitError: If rate limit is exceeded
            
        Example:
            texts = ["First document", "Second document", "Third document"]
            embeddings = await embedder.embed(texts)
            # embeddings is [[0.1, 0.2, ...], [0.3, 0.4, ...], [0.5, 0.6, ...]]
        """
        pass
    
    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding optimized for search queries.
        
        Some models (like Gemini with task_type) can optimize embeddings
        differently for queries vs documents. This method should be used
        for search queries, while embed() is for documents.
        
        Args:
            text: Single search query text
            
        Returns:
            Embedding vector of length self.dimension
            
        Raises:
            EmbeddingError: If the API call fails
            RateLimitError: If rate limit is exceeded
        """
        pass
    
    @abstractmethod
    async def embed_document(self, text: str) -> List[float]:
        """
        Generate embedding optimized for documents.
        
        This is a convenience method for single documents.
        Equivalent to embed([text])[0] but may apply document-specific
        optimizations.
        
        Args:
            text: Single document text
            
        Returns:
            Embedding vector of length self.dimension
            
        Raises:
            EmbeddingError: If the API call fails
            RateLimitError: If rate limit is exceeded
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the embedding provider is accessible.
        
        This should make a lightweight call to verify the API key
        is valid and the service is reachable.
        
        Returns:
            True if healthy, False otherwise
        """
        pass


class EmbeddingError(Exception):
    """Base exception for embedding errors."""
    pass


class RateLimitError(EmbeddingError):
    """Raised when API rate limit is exceeded."""
    pass


class AuthenticationError(EmbeddingError):
    """Raised when API authentication fails."""
    pass


class InvalidModelError(EmbeddingError):
    """Raised when an invalid model is specified."""
    pass
