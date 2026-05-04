"""
Mock Embedding Adapter - For testing without API access.

This adapter provides deterministic embeddings for testing purposes.
It uses simple hashing to generate consistent embeddings.
"""

from typing import List
import hashlib
import struct

from ports.embedding import (
    EmbeddingPort,
    EmbeddingConfig,
    EmbeddingTaskType,
)


class MockEmbeddingAdapter(EmbeddingPort):
    """
    Mock implementation of EmbeddingPort for testing.
    
    Generates deterministic embeddings based on text content hash.
    Useful for testing without API access.
    
    Attributes:
        dimension: Fixed embedding dimension (768)
    """
    
    def __init__(self, dimension: int = 768):
        """
        Initialize mock adapter.
        
        Args:
            dimension: Embedding dimension (default 768)
        """
        self._dimension = dimension
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate deterministic mock embeddings.
        
        Uses SHA-256 hash of text to generate consistent embeddings.
        """
        embeddings = []
        for text in texts:
            # Generate deterministic embedding from text hash
            hash_bytes = hashlib.sha256(text.encode()).digest()
            
            # Convert hash bytes to floats
            floats = []
            for i in range(0, min(len(hash_bytes), self._dimension * 4), 4):
                # Pack 4 bytes into a float
                val = struct.unpack('f', hash_bytes[i:i+4])[0]
                # Normalize to [-1, 1]
                floats.append(max(-1.0, min(1.0, val)))
            
            # Pad or truncate to dimension
            while len(floats) < self._dimension:
                floats.append(0.0)
            floats = floats[:self._dimension]
            
            # Normalize to unit vector
            import math
            norm = math.sqrt(sum(x*x for x in floats))
            if norm > 0:
                floats = [x/norm for x in floats]
            
            embeddings.append(floats)
        
        return embeddings
    
    async def close(self) -> None:
        """No-op for mock adapter."""
        pass
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension
    
    @property
    def model_name(self) -> str:
        """Return mock model name."""
        return "mock-embedding"
    
    @property
    def config(self) -> EmbeddingConfig:
        """Return mock configuration."""
        return EmbeddingConfig(
            model="mock-embedding",
            dimension=self._dimension,
            batch_size=100,
            task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT
        )
