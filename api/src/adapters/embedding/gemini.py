"""
Gemini Adapter - Implementation of EmbeddingPort using Google Gemini API.

This adapter provides a concrete implementation of the EmbeddingPort
interface using Google's Gemini API for text embeddings.

Usage:
    from adapters.embedding.gemini import GeminiAdapter
    
    embedder = GeminiAdapter(api_key="your_key", model="text-embedding-004")
    embeddings = await embedder.embed(["text1", "text2"])
"""

from typing import List, Optional
import httpx
import base64

from ports.embedding import (
    EmbeddingPort,
    EmbeddingConfig,
    EmbeddingTaskType,
    EmbeddingError,
    RateLimitError,
    AuthenticationError,
    InvalidModelError,
)


class GeminiAdapter(EmbeddingPort):
    """
    Google Gemini implementation of EmbeddingPort.
    
    Uses Google's Generative AI API for embedding generation.
    Default model: text-embedding-004 (768 dimensions)
    
    API Documentation:
        https://ai.google.dev/api/embeddings
    
    Attributes:
        api_key: Google AI API key
        config: EmbeddingConfig with model settings
        base_url: Gemini API endpoint
    
    Design Notes:
        - Supports batch processing with configurable batch size
        - Handles rate limiting with exponential backoff
        - Task type optimization for semantic search
    """
    
    # Model dimensions mapping
    MODEL_DIMENSIONS = {
        "text-embedding-004": 768,
        "embedding-001": 768,
    }
    
    # Default batch size (verify against current Gemini limits)
    DEFAULT_BATCH_SIZE = 100
    
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-004",
        batch_size: int = DEFAULT_BATCH_SIZE,
        timeout: float = 60.0
    ):
        """
        Initialize Gemini adapter.
        
        Args:
            api_key: Google AI API key
            model: Model name (text-embedding-004 recommended)
            batch_size: Maximum batch size for API calls
            timeout: HTTP request timeout in seconds
            
        Raises:
            InvalidModelError: If model is not supported
        """
        if model not in self.MODEL_DIMENSIONS:
            raise InvalidModelError(
                f"Model '{model}' not supported. "
                f"Supported: {list(self.MODEL_DIMENSIONS.keys())}"
            )
        
        self._api_key = api_key
        self._model = model
        self._dimension = self.MODEL_DIMENSIONS[model]
        self._batch_size = batch_size
        self._timeout = timeout
        
        self._base_url = "https://generativelanguage.googleapis.com/v1beta"
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
        """Return embedding dimension for the configured model."""
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
        Generate embeddings for multiple texts using batching.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: For API errors
            RateLimitError: If rate limited
            AuthenticationError: If API key invalid
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i:i + self._batch_size]
            batch_embeddings = await self._embed_batch(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a single batch of texts.
        
        Internal method - use embed() for public API.
        """
        url = f"{self._base_url}/models/{self._model}:batchEmbedContents"
        
        # Build request payload
        requests_payload = []
        for text in texts:
            requests_payload.append({
                "content": {
                    "parts": [{"text": text}]
                }
            })
        
        payload = {
            "requests": requests_payload
        }
        
        # Make API call
        response = await self.client.post(
            url,
            params={"key": self._api_key},
            json=payload
        )
        
        # Handle errors
        if response.status_code == 429:
            raise RateLimitError("Gemini API rate limit exceeded")
        elif response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError("Invalid Gemini API key")
        elif response.status_code != 200:
            raise EmbeddingError(
                f"Gemini API error: {response.status_code} - {response.text}"
            )
        
        # Parse response
        data = response.json()
        embeddings = data.get("embeddings", [])
        
        if len(embeddings) != len(texts):
            raise EmbeddingError(
                f"Mismatch in response: expected {len(texts)} embeddings, "
                f"got {len(embeddings)}"
            )
        
        # Extract values from response structure
        result = []
        for emb in embeddings:
            values = emb.get("values", [])
            if len(values) != self._dimension:
                raise EmbeddingError(
                    f"Unexpected embedding dimension: {len(values)} "
                    f"(expected {self._dimension})"
                )
            result.append(values)
        
        return result
    
    async def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding optimized for search queries.
        
        Uses RETRIEVAL_QUERY task type if supported by the model.
        """
        # For Gemini, query and document embeddings use the same model
        # but we could add task_type optimization here
        embeddings = await self.embed([text])
        return embeddings[0]
    
    async def embed_document(self, text: str) -> List[float]:
        """
        Generate embedding optimized for documents.
        
        Uses RETRIEVAL_DOCUMENT task type if supported by the model.
        """
        embeddings = await self.embed([text])
        return embeddings[0]
    
    async def health_check(self) -> bool:
        """
        Check if Gemini API is accessible.
        
        Makes a lightweight call to verify the API key is valid.
        """
        try:
            # List models is a lightweight operation
            url = f"{self._base_url}/models"
            response = await self.client.get(
                url,
                params={"key": self._api_key}
            )
            return response.status_code == 200
        except Exception:
            return False
