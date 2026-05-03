"""
Vector Store Port - Abstract interface for vector database operations.

This module defines the contract that all vector store implementations must follow.
It enables swapping between different vector databases (ChromaDB, Qdrant, etc.)
without changing business logic.

Usage:
    # In domain service - only depends on the port
    from ports.vector_store import VectorStorePort
    
    class SearchService:
        def __init__(self, vector_store: VectorStorePort):
            self.vector_store = vector_store
        
        async def search(self, query_embedding: List[float], domain_id: str):
            return await self.vector_store.search(
                collection=domain_id,
                query_vector=query_embedding,
                top_k=10
            )

Implementations:
    - ChromaDBAdapter: ChromaDB implementation for MVP
    - QdrantAdapter: Qdrant implementation for v2
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Chunk:
    """
    Represents a text chunk with its embedding and metadata.
    
    Attributes:
        id: Unique identifier for the chunk (usually UUID)
        text: The actual text content of the chunk
        embedding: Vector representation of the text (optional for insertion)
        metadata: Additional metadata (doc_id, page_num, chunk_index, etc.)
    """
    id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SearchResult:
    """
    Represents a single search result from vector store.
    
    Attributes:
        chunk_id: ID of the matching chunk
        score: Similarity score (0.0 to 1.0, higher is better)
        text: Text content of the chunk
        metadata: Associated metadata
    """
    chunk_id: str
    score: float
    text: str
    metadata: Dict[str, Any]


@dataclass
class CollectionInfo:
    """
    Information about a vector collection.
    
    Attributes:
        name: Collection identifier (usually domain_id)
        dimension: Embedding dimension
        count: Number of vectors in collection
        created_at: Creation timestamp
    """
    name: str
    dimension: int
    count: int
    created_at: Optional[datetime] = None


class VectorStorePort(ABC):
    """
    Abstract port for vector store operations.
    
    This interface abstracts all interactions with vector databases.
    Business logic should only interact with this interface, never
    directly with ChromaDB, Qdrant, or any other concrete implementation.
    
    Implementations:
        - ChromaDBAdapter: Uses ChromaDB HTTP client
        - QdrantAdapter: Uses Qdrant client (for v2 migration)
    
    Design Decisions:
        1. All methods are async - vector DB operations are I/O bound
        2. One collection per domain - provides data isolation
        3. Chunks carry their own embeddings - allows pre-computed embeddings
    """
    
    @abstractmethod
    async def create_collection(
        self, 
        name: str, 
        dimension: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a new collection with specified embedding dimension.
        
        In domain-driven terms: one collection = one knowledge domain.
        
        Args:
            name: Collection identifier (recommendation: use domain_id UUID)
            dimension: Embedding dimension (e.g., 768 for Gemini)
            metadata: Optional metadata about the collection
            
        Raises:
            CollectionExistsError: If collection already exists
            VectorStoreError: For other errors
        """
        pass
    
    @abstractmethod
    async def delete_collection(self, name: str) -> None:
        """
        Delete a collection and all its vectors.
        
        WARNING: This is irreversible.
        
        Args:
            name: Collection identifier
            
        Raises:
            CollectionNotFoundError: If collection doesn't exist
            VectorStoreError: For other errors
        """
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[CollectionInfo]:
        """
        List all collections in the vector store.
        
        Returns:
            List of collection information objects
        """
        pass
    
    @abstractmethod
    async def upsert(
        self, 
        collection: str, 
        chunks: List[Chunk]
    ) -> None:
        """
        Insert or update chunks in the collection.
        
        - If chunk.id exists: updates the chunk
        - If chunk.id doesn't exist: inserts new chunk
        - Requires chunks to have embeddings pre-computed
        
        Args:
            collection: Collection name (domain_id)
            chunks: List of chunks to upsert (must have embeddings)
            
        Raises:
            CollectionNotFoundError: If collection doesn't exist
            VectorStoreError: For other errors
        """
        pass
    
    @abstractmethod
    async def search(
        self, 
        collection: str, 
        query_vector: List[float], 
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Semantic search over a collection.
        
        Performs vector similarity search to find chunks most similar
        to the query vector.
        
        Args:
            collection: Collection name (domain_id)
            query_vector: Embedding of the search query
            top_k: Maximum number of results to return
            filters: Optional metadata filters (implementation-specific)
            
        Returns:
            List of search results ordered by relevance (highest first)
            
        Raises:
            CollectionNotFoundError: If collection doesn't exist
            VectorStoreError: For other errors
        """
        pass
    
    @abstractmethod
    async def delete(
        self, 
        collection: str, 
        chunk_ids: List[str]
    ) -> None:
        """
        Delete chunks by their IDs.
        
        Args:
            collection: Collection name (domain_id)
            chunk_ids: List of chunk IDs to delete
            
        Raises:
            CollectionNotFoundError: If collection doesn't exist
            VectorStoreError: For other errors
        """
        pass
    
    @abstractmethod
    async def get_collection_count(self, collection: str) -> int:
        """
        Get the number of vectors in a collection.
        
        Args:
            collection: Collection name (domain_id)
            
        Returns:
            Number of vectors in the collection
            
        Raises:
            CollectionNotFoundError: If collection doesn't exist
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the vector store is accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        pass


class VectorStoreError(Exception):
    """Base exception for vector store errors."""
    pass


class CollectionExistsError(VectorStoreError):
    """Raised when trying to create a collection that already exists."""
    pass


class CollectionNotFoundError(VectorStoreError):
    """Raised when a collection is not found."""
    pass
