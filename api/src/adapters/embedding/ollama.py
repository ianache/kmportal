"""
Ollama Embedding Adapter - Implementation using local Ollama instance.

This adapter provides embeddings using locally running Ollama models.
Useful for privacy-sensitive applications or when API access is not available.

Usage:
    from adapters.embedding.ollama import OllamaAdapter
    
    embedder = OllamaAdapter(model="nomic-embed-text", host="localhost", port=11434)
    embeddings = await embedder.embed(["text1", "text2"])
"""

from typing import List, Optional
import httpx
import asyncio

from ports.embedding import (
    EmbeddingPort,
    EmbeddingConfig,
    EmbeddingTaskType,
    EmbeddingError,
)


class OllamaAdapter(EmbeddingPort):
    """
    Ollama implementation of EmbeddingPort.
    
    Uses locally running Ollama instance for embedding generation.
    Default model: nomic-embed-text (768 dimensions)
    
    Prerequisites:
        - Ollama must be installed and running locally
        - The embedding model must be pulled: `ollama pull nomic-embed-text`
    
    Attributes:
        host: Ollama host (default: localhost)
        port: Ollama port (default: 11434)
        model: Model name to use for embeddings
    
    Example:
        adapter = OllamaAdapter(model="nomic-embed-text")
        embeddings = await adapter.embed(["text to embed"])
    """
    
    # Model dimensions mapping
    MODEL_DIMENSIONS = {
        "nomic-embed-text": 768,
        "mxbai-embed-large": 1024,
        "snowflake-arctic-embed": 1024,
        "embeddinggemma": 768,  # Custom/user-defined model
    }
    
    DEFAULT_BATCH_SIZE = 10
    
    def __init__(
        self,
        model: str = "nomic-embed-text",
        host: str = "localhost",
        port: int = 11434,
        batch_size: int = DEFAULT_BATCH_SIZE,
        timeout: float = 60.0
    ):
        """
        Initialize Ollama adapter.
        
        Args:
            model: Model name (must be pulled in Ollama)
            host: Ollama host
            port: Ollama port
            batch_size: Maximum batch size for API calls
            timeout: HTTP request timeout in seconds
        """
        self._model = model
        self._host = host
        self._port = port
        self._batch_size = batch_size
        self._timeout = timeout
        
        # Use known dimension or default to 768
        self._dimension = self.MODEL_DIMENSIONS.get(model, 768)
        
        self._base_url = f"http://{host}:{port}/api"
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client
    
    async def close(self) -> None:
        """Close HTTP client connections."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension
    
    @property
    def model_name(self) -> str:
        """Return the model identifier."""
        return self._model
    
    @property
    def config(self) -> EmbeddingConfig:
        """Return the embedding configuration."""
        return EmbeddingConfig(
            model=self._model,
            dimension=self._dimension,
            batch_size=self._batch_size,
            task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT
        )
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If Ollama is not running or model not found
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i:i + self._batch_size]
            
            # Process batch concurrently
            tasks = [self._embed_single(text) for text in batch]
            batch_embeddings = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any errors
            for emb in batch_embeddings:
                if isinstance(emb, Exception):
                    raise EmbeddingError(f"Ollama embedding failed: {str(emb)}")
                all_embeddings.append(emb)
        
        return all_embeddings
    
    async def _embed_single(self, text: str) -> List[float]:
        """
        Embed a single text using Ollama API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        url = f"{self._base_url}/embeddings"
        
        payload = {
            "model": self._model,
            "prompt": text
        }
        
        try:
            response = await self.client.post(url, json=payload)
            
            if response.status_code != 200:
                error_text = response.text
                if "model not found" in error_text.lower():
                    raise EmbeddingError(
                        f"Model '{self._model}' not found in Ollama. "
                        f"Run: ollama pull {self._model}"
                    )
                raise EmbeddingError(f"Ollama API error: {response.status_code} - {error_text}")
            
            data = response.json()
            embedding = data.get("embedding", [])
            
            if not embedding:
                raise EmbeddingError("Empty embedding returned from Ollama")
            
            # Verify dimension
            if len(embedding) != self._dimension:
                # Update dimension if different
                self._dimension = len(embedding)
            
            return embedding
            
        except httpx.ConnectError as e:
            raise EmbeddingError(
                f"Cannot connect to Ollama at {self._host}:{self._port}. "
                f"Make sure Ollama is running. Error: {str(e)}"
            )
        except Exception as e:
            if isinstance(e, EmbeddingError):
                raise
            raise EmbeddingError(f"Ollama embedding failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Check if Ollama is accessible.
        
        Returns:
            True if Ollama is running and accessible
        """
        try:
            url = f"{self._base_url}/tags"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception:
            return False
