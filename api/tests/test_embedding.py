"""Unit tests for EmbeddingPort abstraction."""

import pytest
from abc import ABC
from src.ports.embedding import (
    EmbeddingPort,
    EmbeddingConfig,
    EmbeddingTaskType,
    EmbeddingError,
    RateLimitError,
    AuthenticationError,
    InvalidModelError,
)


class MockEmbeddingAdapter(EmbeddingPort):
    """Mock implementation for testing."""

    def __init__(self, dimension: int = 768, model: str = "mock-model"):
        self._dimension = dimension
        self._model = model
        self._config = EmbeddingConfig(
            model=model,
            dimension=dimension,
            batch_size=10,
        )
        self._healthy = True

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def config(self) -> EmbeddingConfig:
        return self._config

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self._dimension for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [0.1] * self._dimension

    async def embed_document(self, text: str) -> list[float]:
        return [0.1] * self._dimension

    async def health_check(self) -> bool:
        return self._healthy


class TestEmbeddingPort:
    """Tests for EmbeddingPort interface."""

    def test_is_abstract_class(self):
        """EmbeddingPort should be an ABC."""
        assert issubclass(EmbeddingPort, ABC)

    @pytest.mark.asyncio
    async def test_dimension_property(self):
        adapter = MockEmbeddingAdapter(dimension=768)
        assert adapter.dimension == 768

    @pytest.mark.asyncio
    async def test_model_name_property(self):
        adapter = MockEmbeddingAdapter(model="text-embedding-004")
        assert adapter.model_name == "text-embedding-004"

    @pytest.mark.asyncio
    async def test_config_property(self):
        adapter = MockEmbeddingAdapter(dimension=768, model="test-model")
        config = adapter.config
        assert config.model == "test-model"
        assert config.dimension == 768
        assert config.batch_size == 10

    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self):
        adapter = MockEmbeddingAdapter(dimension=768)
        texts = ["First text", "Second text", "Third text"]
        embeddings = await adapter.embed(texts)

        assert len(embeddings) == 3
        for emb in embeddings:
            assert len(emb) == 768

    @pytest.mark.asyncio
    async def test_embed_query(self):
        adapter = MockEmbeddingAdapter(dimension=768)
        embedding = await adapter.embed_query("test query")

        assert len(embedding) == 768

    @pytest.mark.asyncio
    async def test_embed_document(self):
        adapter = MockEmbeddingAdapter(dimension=768)
        embedding = await adapter.embed_document("test document")

        assert len(embedding) == 768

    @pytest.mark.asyncio
    async def test_health_check(self):
        adapter = MockEmbeddingAdapter()
        is_healthy = await adapter.health_check()
        assert is_healthy is True


class TestEmbeddingConfig:
    """Tests for EmbeddingConfig dataclass."""

    def test_config_creation(self):
        config = EmbeddingConfig(
            model="text-embedding-004",
            dimension=768,
            batch_size=50,
            task_type=EmbeddingTaskType.RETRIEVAL_QUERY,
        )
        assert config.model == "text-embedding-004"
        assert config.dimension == 768
        assert config.batch_size == 50
        assert config.task_type == EmbeddingTaskType.RETRIEVAL_QUERY

    def test_config_defaults(self):
        config = EmbeddingConfig(model="test", dimension=128)
        assert config.batch_size == 100
        assert config.task_type is None


class TestEmbeddingTaskType:
    """Tests for EmbeddingTaskType enum."""

    def test_task_types(self):
        assert EmbeddingTaskType.SEMANTIC_SIMILARITY.value == "SEMANTIC_SIMILARITY"
        assert EmbeddingTaskType.CLASSIFICATION.value == "CLASSIFICATION"
        assert EmbeddingTaskType.CLUSTERING.value == "CLUSTERING"
        assert EmbeddingTaskType.RETRIEVAL_DOCUMENT.value == "RETRIEVAL_DOCUMENT"
        assert EmbeddingTaskType.RETRIEVAL_QUERY.value == "RETRIEVAL_QUERY"


class TestExceptions:
    """Tests for exception classes."""

    def test_embedding_error(self):
        err = EmbeddingError("Test error")
        assert str(err) == "Test error"

    def test_rate_limit_error(self):
        err = RateLimitError("Rate limit exceeded")
        assert isinstance(err, EmbeddingError)

    def test_authentication_error(self):
        err = AuthenticationError("Auth failed")
        assert isinstance(err, EmbeddingError)

    def test_invalid_model_error(self):
        err = InvalidModelError("Invalid model")
        assert isinstance(err, EmbeddingError)