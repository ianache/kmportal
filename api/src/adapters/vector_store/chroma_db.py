"""
ChromaDB Adapter - Implementation of VectorStorePort using ChromaDB.

This adapter provides a concrete implementation of the VectorStorePort
interface using ChromaDB as the underlying vector store. It's designed
to be swappable with QdrantAdapter in v2 without changes to business logic.

Usage:
    from adapters.vector_store.chroma_db import ChromaDBAdapter
    
    store = ChromaDBAdapter(host="localhost", port=8000)
    await store.create_collection("domain-123", dimension=768)
    await store.upsert("domain-123", chunks)
"""

from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

from ports.vector_store import (
    VectorStorePort,
    Chunk,
    SearchResult,
    CollectionInfo,
    VectorStoreError,
    CollectionExistsError,
    CollectionNotFoundError,
)


class ChromaDBAdapter(VectorStorePort):
    """
    ChromaDB implementation of VectorStorePort.
    
    Uses ChromaDB's HTTP API for all operations. This allows the adapter
to connect to a separate ChromaDB container without requiring the
    ChromaDB Python client to be installed.
    
    Attributes:
        base_url: Full URL to ChromaDB HTTP API
        client: httpx.AsyncClient for HTTP requests
    
    Design Notes:
        - One collection per domain (isolation)
        - Uses ChromaDB's metadata filtering for additional query constraints
        - ChromaDB 0.5+ required (verify API compatibility)
    """
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 8000,
        timeout: float = 30.0
    ):
        """
        Initialize ChromaDB adapter.
        
        Args:
            host: ChromaDB server hostname
            port: ChromaDB server port
            timeout: HTTP request timeout in seconds
        """
        self.base_url = f"http://{host}:{port}/api/v1"
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self) -> None:
        """Close HTTP client connections."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def create_collection(
        self, 
        name: str, 
        dimension: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a new ChromaDB collection."""
        url = f"{self.base_url}/collections"
        
        # Prepare collection metadata
        collection_metadata = metadata or {}
        collection_metadata["embedding_dimension"] = dimension
        collection_metadata["created_at"] = datetime.utcnow().isoformat()
        
        payload = {
            "name": name,
            "metadata": collection_metadata
        }
        
        response = await self.client.post(url, json=payload)
        
        if response.status_code == 409:
            raise CollectionExistsError(f"Collection '{name}' already exists")
        elif response.status_code != 200:
            raise VectorStoreError(
                f"Failed to create collection: {response.text}"
            )
    
    async def delete_collection(self, name: str) -> None:
        """Delete a ChromaDB collection."""
        url = f"{self.base_url}/collections/{name}"
        
        response = await self.client.delete(url)
        
        if response.status_code == 404:
            raise CollectionNotFoundError(f"Collection '{name}' not found")
        elif response.status_code != 200:
            raise VectorStoreError(
                f"Failed to delete collection: {response.text}"
            )
    
    async def list_collections(self) -> List[CollectionInfo]:
        """List all ChromaDB collections."""
        url = f"{self.base_url}/collections"
        
        response = await self.client.get(url)
        
        if response.status_code != 200:
            raise VectorStoreError(
                f"Failed to list collections: {response.text}"
            )
        
        collections_data = response.json()
        collections = []
        
        for coll in collections_data:
            metadata = coll.get("metadata", {})
            collections.append(CollectionInfo(
                name=coll["name"],
                dimension=metadata.get("embedding_dimension", 0),
                count=coll.get("count", 0),
                created_at=None  # ChromaDB doesn't expose this directly
            ))
        
        return collections
    
    async def _get_collection_id(self, name: str) -> str:
        """Get the internal ID for a collection by name."""
        url = f"{self.base_url}/collections"
        response = await self.client.get(url)
        
        if response.status_code != 200:
            raise VectorStoreError(f"Failed to list collections: {response.text}")
        
        collections = response.json()
        for coll in collections:
            if coll.get("name") == name:
                return coll.get("id")
        
        raise CollectionNotFoundError(f"Collection '{name}' not found")
    
    async def upsert(
        self, 
        collection: str, 
        chunks: List[Chunk]
    ) -> None:
        """Upsert chunks into ChromaDB collection."""
        if not chunks:
            return
        
        # Validate all chunks have embeddings
        for chunk in chunks:
            if chunk.embedding is None:
                raise VectorStoreError(
                    f"Chunk {chunk.id} has no embedding. "
                    "All chunks must have embeddings before upsert."
                )
        
        # Get collection ID (ChromaDB uses UUID, not name)
        collection_id = await self._get_collection_id(collection)
        
        url = f"{self.base_url}/collections/{collection_id}/upsert"
        
        payload = {
            "ids": [chunk.id for chunk in chunks],
            "embeddings": [chunk.embedding for chunk in chunks],
            "documents": [chunk.text for chunk in chunks],
            "metadatas": [chunk.metadata or {} for chunk in chunks]
        }
        
        response = await self.client.post(url, json=payload)
        
        if response.status_code == 404:
            raise CollectionNotFoundError(f"Collection '{collection}' not found")
        elif response.status_code != 200:
            raise VectorStoreError(
                f"Failed to upsert chunks: {response.text}"
            )
    
    async def search(
        self, 
        collection: str, 
        query_vector: List[float], 
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search ChromaDB collection with vector similarity."""
        # Get collection ID (ChromaDB uses UUID, not name)
        collection_id = await self._get_collection_id(collection)
        
        url = f"{self.base_url}/collections/{collection_id}/query"
        
        payload = {
            "query_embeddings": [query_vector],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"]
        }
        
        if filters:
            payload["where"] = filters
        
        response = await self.client.post(url, json=payload)
        
        if response.status_code == 404:
            raise CollectionNotFoundError(f"Collection '{collection}' not found")
        elif response.status_code != 200:
            raise VectorStoreError(
                f"Failed to search collection: {response.text}"
            )
        
        data = response.json()
        results = []
        
        # ChromaDB returns results grouped by query
        if data.get("ids") and len(data["ids"]) > 0:
            ids = data["ids"][0]
            documents = data.get("documents", [[]])[0] or []
            metadatas = data.get("metadatas", [[]])[0] or []
            distances = data.get("distances", [[]])[0] or []
            
            for i, chunk_id in enumerate(ids):
                # Convert distance to similarity score
                # ChromaDB uses L2 distance by default, convert to similarity
                # Using exponential decay: score = exp(-distance)
                distance = distances[i] if i < len(distances) else 0.0
                import math
                score = math.exp(-distance)
                
                results.append(SearchResult(
                    chunk_id=chunk_id,
                    score=score,
                    text=documents[i] if i < len(documents) else "",
                    metadata=metadatas[i] if i < len(metadatas) else {}
                ))
        
        return results
    
    async def delete(
        self, 
        collection: str, 
        chunk_ids: List[str]
    ) -> None:
        """Delete chunks from ChromaDB collection."""
        if not chunk_ids:
            return
        
        url = f"{self.base_url}/collections/{collection}/delete"
        
        payload = {"ids": chunk_ids}
        
        response = await self.client.post(url, json=payload)
        
        if response.status_code == 404:
            raise CollectionNotFoundError(f"Collection '{collection}' not found")
        elif response.status_code != 200:
            raise VectorStoreError(
                f"Failed to delete chunks: {response.text}"
            )
    
    async def get_collection_count(self, collection: str) -> int:
        """Get count of vectors in ChromaDB collection."""
        url = f"{self.base_url}/collections/{collection}/count"
        
        response = await self.client.get(url)
        
        if response.status_code == 404:
            raise CollectionNotFoundError(f"Collection '{collection}' not found")
        elif response.status_code != 200:
            raise VectorStoreError(
                f"Failed to get collection count: {response.text}"
            )
        
        data = response.json()
        return data.get("count", 0)
    
    async def health_check(self) -> bool:
        """Check ChromaDB health."""
        try:
            url = f"{self.base_url}/heartbeat"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception:
            return False
