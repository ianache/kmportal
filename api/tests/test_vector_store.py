"""Unit tests for VectorStorePort abstraction."""

import pytest
from abc import ABC
from src.ports.vector_store import (
    VectorStorePort,
    Chunk,
    SearchResult,
    CollectionInfo,
    VectorStoreError,
    CollectionExistsError,
    CollectionNotFoundError,
)


class MockVectorStoreAdapter(VectorStorePort):
    """Mock implementation for testing."""

    def __init__(self):
        self._collections = {}
        self._chunks = {}

    async def create_collection(
        self,
        name: str,
        dimension: int,
        metadata: dict | None = None
    ) -> None:
        if name in self._collections:
            raise CollectionExistsError(f"Collection {name} already exists")
        self._collections[name] = {
            "dimension": dimension,
            "metadata": metadata or {},
        }
        self._chunks[name] = []

    async def delete_collection(self, name: str) -> None:
        if name not in self._collections:
            raise CollectionNotFoundError(f"Collection {name} not found")
        del self._collections[name]
        del self._chunks[name]

    async def list_collections(self) -> list[CollectionInfo]:
        return [
            CollectionInfo(name=name, dimension=data["dimension"], count=0)
            for name, data in self._collections.items()
        ]

    async def upsert(self, collection: str, chunks: list[Chunk]) -> None:
        if collection not in self._collections:
            raise CollectionNotFoundError(f"Collection {collection} not found")
        for chunk in chunks:
            self._chunks[collection].append(chunk)

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict | None = None
    ) -> list[SearchResult]:
        return []

    async def delete(self, collection: str, chunk_ids: list[str]) -> None:
        pass

    async def get_collection_count(self, collection: str) -> int:
        return len(self._chunks.get(collection, []))

    async def health_check(self) -> bool:
        return True


class TestVectorStorePort:
    """Tests for VectorStorePort interface."""

    def test_is_abstract_class(self):
        """VectorStorePort should be an ABC."""
        assert issubclass(VectorStorePort, ABC)

    @pytest.mark.asyncio
    async def test_create_collection(self):
        adapter = MockVectorStoreAdapter()
        await adapter.create_collection("domain-1", dimension=768)

        collections = await adapter.list_collections()
        assert len(collections) == 1
        assert collections[0].name == "domain-1"
        assert collections[0].dimension == 768

    @pytest.mark.asyncio
    async def test_create_collection_already_exists(self):
        adapter = MockVectorStoreAdapter()
        await adapter.create_collection("domain-1", dimension=768)

        with pytest.raises(CollectionExistsError):
            await adapter.create_collection("domain-1", dimension=768)

    @pytest.mark.asyncio
    async def test_delete_collection(self):
        adapter = MockVectorStoreAdapter()
        await adapter.create_collection("domain-1", dimension=768)
        await adapter.delete_collection("domain-1")

        collections = await adapter.list_collections()
        assert len(collections) == 0

    @pytest.mark.asyncio
    async def test_delete_collection_not_found(self):
        adapter = MockVectorStoreAdapter()

        with pytest.raises(CollectionNotFoundError):
            await adapter.delete_collection("nonexistent")

    @pytest.mark.asyncio
    async def test_upsert_chunks(self):
        adapter = MockVectorStoreAdapter()
        await adapter.create_collection("domain-1", dimension=768)

        chunks = [
            Chunk(id="chunk-1", text="First chunk", embedding=[0.1] * 768),
            Chunk(id="chunk-2", text="Second chunk", embedding=[0.2] * 768),
        ]
        await adapter.upsert("domain-1", chunks)

        count = await adapter.get_collection_count("domain-1")
        assert count == 2

    @pytest.mark.asyncio
    async def test_upsert_collection_not_found(self):
        adapter = MockVectorStoreAdapter()

        chunks = [Chunk(id="chunk-1", text="Test", embedding=[0.1] * 768)]
        with pytest.raises(CollectionNotFoundError):
            await adapter.upsert("nonexistent", chunks)

    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        adapter = MockVectorStoreAdapter()
        await adapter.create_collection("domain-1", dimension=768)

        results = await adapter.search("domain-1", [0.1] * 768, top_k=5)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_health_check(self):
        adapter = MockVectorStoreAdapter()
        is_healthy = await adapter.health_check()
        assert is_healthy is True


class TestChunk:
    """Tests for Chunk dataclass."""

    def test_chunk_creation(self):
        chunk = Chunk(
            id="chunk-1",
            text="Test text",
            embedding=[0.1, 0.2, 0.3],
            metadata={"doc_id": "doc-1"}
        )
        assert chunk.id == "chunk-1"
        assert chunk.text == "Test text"
        assert chunk.embedding == [0.1, 0.2, 0.3]
        assert chunk.metadata == {"doc_id": "doc-1"}

    def test_chunk_optional_fields(self):
        chunk = Chunk(id="chunk-1", text="Test text")
        assert chunk.embedding is None
        assert chunk.metadata is None


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_search_result_creation(self):
        result = SearchResult(
            chunk_id="chunk-1",
            score=0.95,
            text="Found text",
            metadata={"doc_id": "doc-1"}
        )
        assert result.chunk_id == "chunk-1"
        assert result.score == 0.95
        assert result.text == "Found text"


class TestExceptions:
    """Tests for exception classes."""

    def test_vector_store_error(self):
        err = VectorStoreError("Test error")
        assert str(err) == "Test error"

    def test_collection_exists_error(self):
        err = CollectionExistsError("Collection exists")
        assert isinstance(err, VectorStoreError)

    def test_collection_not_found_error(self):
        err = CollectionNotFoundError("Collection not found")
        assert isinstance(err, VectorStoreError)