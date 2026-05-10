"""
Unit tests for IngestionCoordinator (FEAT6).

Covers:
- Happy path: Neo4j write + ChromaDB write succeed
- Collection naming (semantic_{domain_id}) and cosine metadata
- Neo4j failure: aborts before ChromaDB write
- ChromaDB failure: rollbacks Neo4j via DETACH DELETE
- ChromaDB as_distances=True score passthrough
"""
import sys
sys.path.insert(0, 'D:\\02-PERSONAL\\01-PROJECTS\\25-KnowledgeManagement\\api\\src')

import pytest
from unittest.mock import AsyncMock, MagicMock, call, patch
from uuid import UUID, uuid4

from ports.vector_store import Chunk, CollectionExistsError, VectorStoreError
from schemas import IngestionPayload, SemanticLink
from services.semantic_ingestion_service import IngestionCoordinator, _COSINE_META


# ─────────────────────────── helpers ────────────────────────────────────────

def make_payload(
    link_id: UUID | None = None,
    owl_class: str = "Document",
    source_ref: str = "report.pdf",
    content: str = "Test knowledge content.",
    graph_properties: dict | None = None,
) -> IngestionPayload:
    return IngestionPayload(
        content=content,
        metadata=SemanticLink(
            link_id=link_id or uuid4(),
            owl_class=owl_class,
            governance_level="CONFIDENCIAL",
            source_ref=source_ref,
        ),
        graph_properties=graph_properties or {"author": "tester"},
    )


def make_mock_driver(run_side_effect=None):
    """Return (driver, session_mock). session.run() defaults to AsyncMock."""
    session = AsyncMock()
    session.run = AsyncMock(side_effect=run_side_effect)

    driver = MagicMock()
    driver.session.return_value.__aenter__ = AsyncMock(return_value=session)
    driver.session.return_value.__aexit__ = AsyncMock(return_value=False)
    return driver, session


def make_mock_vector_store(
    create_side_effect=None,
    upsert_side_effect=None,
):
    vs = AsyncMock()
    if create_side_effect:
        vs.create_collection.side_effect = create_side_effect
    if upsert_side_effect:
        vs.upsert.side_effect = upsert_side_effect
    return vs


def make_mock_embedding(dimension: int = 768):
    ep = MagicMock()
    ep.dimension = dimension
    ep.embed = AsyncMock(return_value=[[0.1] * dimension])
    return ep


# ─────────────────────────── happy path ─────────────────────────────────────

class TestIngestionCoordinatorHappyPath:

    async def test_returns_success_response(self):
        driver, _ = make_mock_driver()
        vs = make_mock_vector_store()
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        payload = make_payload()
        result = await coordinator.execute_atomic_ingestion(payload, "domain-abc")

        assert result.success is True
        assert result.link_id == str(payload.metadata.link_id)

    async def test_collection_name_has_semantic_prefix(self):
        driver, _ = make_mock_driver()
        vs = make_mock_vector_store()
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        await coordinator.execute_atomic_ingestion(make_payload(), "dom-123")

        vs.create_collection.assert_awaited_once()
        call_kwargs = vs.create_collection.call_args
        assert call_kwargs.kwargs["name"] == "semantic_dom-123"

    async def test_collection_created_with_cosine_metadata(self):
        driver, _ = make_mock_driver()
        vs = make_mock_vector_store()
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        await coordinator.execute_atomic_ingestion(make_payload(), "dom-1")

        vs.create_collection.assert_awaited_once()
        _, kwargs = vs.create_collection.call_args
        assert kwargs["metadata"] == _COSINE_META

    async def test_collection_dimension_matches_embedding_provider(self):
        driver, _ = make_mock_driver()
        vs = make_mock_vector_store()
        ep = make_mock_embedding(dimension=512)
        coordinator = IngestionCoordinator(driver, vs, ep)

        await coordinator.execute_atomic_ingestion(make_payload(), "dom-1")

        _, kwargs = vs.create_collection.call_args
        assert kwargs["dimension"] == 512

    async def test_existing_collection_does_not_raise(self):
        driver, _ = make_mock_driver()
        vs = make_mock_vector_store(create_side_effect=CollectionExistsError("exists"))
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        # Should not raise even if collection already exists
        result = await coordinator.execute_atomic_ingestion(make_payload(), "dom-1")
        assert result.success is True

    async def test_link_id_used_as_chroma_chunk_id(self):
        driver, _ = make_mock_driver()
        vs = make_mock_vector_store()
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        fixed_id = uuid4()
        payload = make_payload(link_id=fixed_id)
        await coordinator.execute_atomic_ingestion(payload, "dom-1")

        vs.upsert.assert_awaited_once()
        _, kwargs = vs.upsert.call_args
        chunks: list[Chunk] = kwargs["chunks"]
        assert len(chunks) == 1
        assert chunks[0].id == str(fixed_id)

    async def test_chunk_metadata_contains_governance_fields(self):
        driver, _ = make_mock_driver()
        vs = make_mock_vector_store()
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        payload = make_payload(owl_class="Policy", source_ref="policy.pdf")
        await coordinator.execute_atomic_ingestion(payload, "dom-1")

        _, kwargs = vs.upsert.call_args
        meta = kwargs["chunks"][0].metadata
        assert meta["owl_class"] == "Policy"
        assert meta["governance"] == "CONFIDENCIAL"
        assert meta["source"] == "policy.pdf"
        assert meta["domain_id"] == "dom-1"

    async def test_neo4j_receives_correct_cypher_params(self):
        driver, session = make_mock_driver()
        vs = make_mock_vector_store()
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        payload = make_payload(owl_class="Regulation", source_ref="reg.pdf")
        link_id_str = str(payload.metadata.link_id)
        await coordinator.execute_atomic_ingestion(payload, "dom-1")

        session.run.assert_awaited_once()
        _, kwargs = session.run.call_args
        assert kwargs["owl_class"] == "Regulation"
        assert kwargs["link_id"] == link_id_str
        assert kwargs["source_ref"] == "reg.pdf"
        assert kwargs["governance_level"] == "CONFIDENCIAL"


# ────────────────────── Neo4j failure scenarios ──────────────────────────────

class TestIngestionCoordinatorNeo4jFailure:

    async def test_neo4j_failure_raises_runtime_error(self):
        driver, _ = make_mock_driver(
            run_side_effect=Exception("Neo4j connection refused")
        )
        vs = make_mock_vector_store()
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        with pytest.raises(RuntimeError, match="Neo4j write failed"):
            await coordinator.execute_atomic_ingestion(make_payload(), "dom-1")

    async def test_neo4j_failure_does_not_write_to_chroma(self):
        driver, _ = make_mock_driver(
            run_side_effect=Exception("timeout")
        )
        vs = make_mock_vector_store()
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        with pytest.raises(RuntimeError):
            await coordinator.execute_atomic_ingestion(make_payload(), "dom-1")

        vs.upsert.assert_not_awaited()


# ──────────────────── ChromaDB failure + rollback ────────────────────────────

class TestIngestionCoordinatorChromaFailure:

    async def test_chroma_upsert_failure_raises_runtime_error(self):
        driver, _ = make_mock_driver()
        vs = make_mock_vector_store(upsert_side_effect=VectorStoreError("disk full"))
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        with pytest.raises(RuntimeError, match="ChromaDB write failed"):
            await coordinator.execute_atomic_ingestion(make_payload(), "dom-1")

    async def test_chroma_failure_triggers_neo4j_rollback(self):
        run_calls = []

        async def side_effect(query, **kwargs):
            run_calls.append(query.strip())

        driver, session = make_mock_driver()
        session.run.side_effect = side_effect

        vs = make_mock_vector_store(upsert_side_effect=VectorStoreError("error"))
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        with pytest.raises(RuntimeError):
            await coordinator.execute_atomic_ingestion(make_payload(), "dom-1")

        # The second call must be the DETACH DELETE rollback
        assert len(run_calls) == 2
        assert "DETACH DELETE" in run_calls[1]

    async def test_rollback_uses_correct_link_id(self):
        fixed_id = uuid4()
        rollback_kwargs: list[dict] = []

        call_count = 0

        async def side_effect(query, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # rollback call
                rollback_kwargs.append(kwargs)

        driver, session = make_mock_driver()
        session.run.side_effect = side_effect

        vs = make_mock_vector_store(upsert_side_effect=VectorStoreError("err"))
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        with pytest.raises(RuntimeError):
            await coordinator.execute_atomic_ingestion(
                make_payload(link_id=fixed_id), "dom-1"
            )

        assert rollback_kwargs[0]["link_id"] == str(fixed_id)

    async def test_rollback_failure_does_not_swallow_original_error(self):
        """If rollback itself fails, the original RuntimeError must still propagate."""
        call_count = 0

        async def side_effect(query, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("rollback also failed")

        driver, session = make_mock_driver()
        session.run.side_effect = side_effect

        vs = make_mock_vector_store(upsert_side_effect=VectorStoreError("upsert err"))
        ep = make_mock_embedding()
        coordinator = IngestionCoordinator(driver, vs, ep)

        with pytest.raises(RuntimeError, match="ChromaDB write failed"):
            await coordinator.execute_atomic_ingestion(make_payload(), "dom-1")


# ─────────────── ChromaDB adapter as_distances parameter ─────────────────────

class TestChromaDBAsDistances:
    """Verify the as_distances flag added to ChromaDBAdapter.search().

    Note: adapter.client is a lazy @property; set adapter._client directly
    to inject a mock HTTP client.
    """

    def _make_chroma_response(self, distances: list[float]) -> dict:
        n = len(distances)
        return {
            "ids": [["id-" + str(i) for i in range(n)]],
            "documents": [["doc " + str(i) for i in range(n)]],
            "metadatas": [[{"k": "v"} for _ in range(n)]],
            "distances": [distances],
        }

    def _inject_mock_client(self, adapter, distances: list[float]):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = self._make_chroma_response(distances)

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_resp)
        adapter._client = mock_http  # bypass lazy property
        return mock_http

    async def test_default_score_is_l2_conversion(self):
        from adapters.vector_store.chroma_db import ChromaDBAdapter
        adapter = ChromaDBAdapter()
        self._inject_mock_client(adapter, [1.0])

        with patch.object(adapter, "_get_collection_id", new=AsyncMock(return_value="col-id")):
            results = await adapter.search("col", [0.0], top_k=1)

        assert abs(results[0].score - (1.0 / (1.0 + 1.0))) < 1e-6

    async def test_as_distances_true_returns_raw_distance(self):
        from adapters.vector_store.chroma_db import ChromaDBAdapter
        adapter = ChromaDBAdapter()
        raw_distance = 0.35
        self._inject_mock_client(adapter, [raw_distance])

        with patch.object(adapter, "_get_collection_id", new=AsyncMock(return_value="col-id")):
            results = await adapter.search("col", [0.0], top_k=1, as_distances=True)

        assert abs(results[0].score - raw_distance) < 1e-9

    async def test_cosine_score_formula_with_as_distances(self):
        """Verify 1.0 - distance gives expected values for typical cosine ranges."""
        for distance, expected in [(0.0, 1.0), (0.5, 0.5), (1.0, 0.0), (2.0, 0.0)]:
            score = max(0.0, 1.0 - distance)
            assert abs(score - expected) < 1e-9

    async def test_as_distances_false_is_backward_compatible(self):
        from adapters.vector_store.chroma_db import ChromaDBAdapter
        adapter = ChromaDBAdapter()
        self._inject_mock_client(adapter, [0.0])

        with patch.object(adapter, "_get_collection_id", new=AsyncMock(return_value="col-id")):
            results = await adapter.search("col", [0.0], top_k=1)

        assert results[0].score == 1.0  # 1 / (1 + 0) = 1.0
