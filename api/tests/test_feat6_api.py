"""
API integration tests for FEAT6 endpoints.

  POST /v1/search/semantic-ingest  — atomic ingestion
  GET  /v1/search/hybrid           — hybrid search with provenance

All external I/O (Neo4j, ChromaDB, Ollama) is mocked via dependency overrides
and unittest.mock patches, following the same patterns as test_domains.py.
"""
import sys
sys.path.insert(0, 'D:\\02-PERSONAL\\01-PROJECTS\\25-KnowledgeManagement\\api\\src')

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app
from core.dependencies import require_domain_access, get_current_user
from db.neo4j_client import get_neo4j
from db.database import get_db
from schemas import UserInToken, SemanticIngestionResponse
from ports.vector_store import CollectionNotFoundError, SearchResult


# ─────────────────────── shared fixtures ─────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    """Lightweight client fixture — no SQLite schema, no db_session dependency.

    FEAT6 endpoints (semantic-ingest, hybrid search) only touch Neo4j and
    ChromaDB; they never use PostgreSQL directly.  We override get_db with
    an AsyncMock in each test class via autouse.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()

DOMAIN_ID = str(uuid4())
LINK_ID = str(uuid4())


def _admin_user() -> UserInToken:
    return UserInToken(
        id=uuid4(),
        keycloak_id="admin-kc-id",
        email="admin@test.com",
        roles=["KM_ADMIN"],
        scopes=["read", "write"],
        allowed_domains=[],
    )


def _make_driver_mock(records: list[dict] | None = None):
    """Build a Neo4j driver mock whose session.run().single() returns records."""
    single_result = records[0] if records else None

    result_mock = AsyncMock()
    result_mock.single = AsyncMock(return_value=single_result)

    session_mock = AsyncMock()
    session_mock.run = AsyncMock(return_value=result_mock)

    driver_mock = MagicMock()
    driver_mock.session.return_value.__aenter__ = AsyncMock(return_value=session_mock)
    driver_mock.session.return_value.__aexit__ = AsyncMock(return_value=False)
    return driver_mock


def _make_embedding_mock(dimension: int = 768):
    ep = MagicMock()
    ep.dimension = dimension
    ep.embed = AsyncMock(return_value=[[0.1] * dimension])
    return ep


def _make_vector_store_mock(
    search_results: list[SearchResult] | None = None,
    search_side_effect=None,
):
    vs = AsyncMock()
    if search_side_effect:
        vs.search.side_effect = search_side_effect
    else:
        vs.search.return_value = search_results or []
    return vs


# ─────────────────────── semantic-ingest endpoint ────────────────────────────

class TestSemanticIngestEndpoint:

    @pytest.fixture(autouse=True)
    def _setup_overrides(self):
        """Override get_db with a lightweight mock — FEAT6 ingest does not use PostgreSQL."""
        async def mock_db():
            yield AsyncMock()

        app.dependency_overrides[get_db] = mock_db
        yield
        app.dependency_overrides.pop(get_db, None)

    def _override_auth(self):
        async def mock_auth(domain_id=None, user=None, db=None):
            return _admin_user()
        app.dependency_overrides[require_domain_access] = mock_auth

    def _clear_overrides(self):
        app.dependency_overrides.pop(require_domain_access, None)
        app.dependency_overrides.pop(get_neo4j, None)

    def _ingest_payload(self, link_id: str | None = None):
        return {
            "content": "This is a test knowledge fragment.",
            "metadata": {
                "link_id": link_id or str(uuid4()),
                "owl_class": "Report",
                "governance_level": "CONFIDENCIAL",
                "source_ref": "report.pdf",
            },
            "graph_properties": {"author": "tester"},
        }

    async def test_unauthenticated_returns_401(self, client):
        response = await client.post(
            f"/v1/search/semantic-ingest?domain_id={DOMAIN_ID}",
            json=self._ingest_payload(),
        )
        assert response.status_code == 401

    async def test_missing_domain_id_returns_422(self, client):
        self._override_auth()
        try:
            response = await client.post(
                "/v1/search/semantic-ingest",
                json=self._ingest_payload(),
                headers={"Authorization": "Bearer fake"},
            )
            assert response.status_code == 422
        finally:
            self._clear_overrides()

    async def test_successful_ingest_returns_202(self, client):
        self._override_auth()
        driver_mock = _make_driver_mock()

        async def mock_neo4j():
            return driver_mock

        app.dependency_overrides[get_neo4j] = mock_neo4j

        ep_mock = _make_embedding_mock()
        vs_mock = _make_vector_store_mock()

        try:
            with patch("api.search.get_embedding_adapter", new=AsyncMock(return_value=ep_mock)):
                with patch("api.search._make_vector_store", return_value=vs_mock):
                    response = await client.post(
                        f"/v1/search/semantic-ingest?domain_id={DOMAIN_ID}",
                        json=self._ingest_payload(),
                        headers={"Authorization": "Bearer fake"},
                    )

            assert response.status_code == 202
            data = response.json()
            assert data["success"] is True
            assert "link_id" in data
        finally:
            self._clear_overrides()

    async def test_successful_ingest_echo_link_id(self, client):
        self._override_auth()
        driver_mock = _make_driver_mock()
        fixed_link_id = str(uuid4())

        async def mock_neo4j():
            return driver_mock

        app.dependency_overrides[get_neo4j] = mock_neo4j

        ep_mock = _make_embedding_mock()
        vs_mock = _make_vector_store_mock()

        try:
            with patch("api.search.get_embedding_adapter", new=AsyncMock(return_value=ep_mock)):
                with patch("api.search._make_vector_store", return_value=vs_mock):
                    response = await client.post(
                        f"/v1/search/semantic-ingest?domain_id={DOMAIN_ID}",
                        json=self._ingest_payload(link_id=fixed_link_id),
                        headers={"Authorization": "Bearer fake"},
                    )

            assert response.json()["link_id"] == fixed_link_id
        finally:
            self._clear_overrides()

    async def test_neo4j_failure_returns_500(self, client):
        self._override_auth()
        driver_mock = MagicMock()
        session_mock = AsyncMock()
        session_mock.run = AsyncMock(side_effect=Exception("DB down"))
        driver_mock.session.return_value.__aenter__ = AsyncMock(return_value=session_mock)
        driver_mock.session.return_value.__aexit__ = AsyncMock(return_value=False)

        async def mock_neo4j():
            return driver_mock

        app.dependency_overrides[get_neo4j] = mock_neo4j

        ep_mock = _make_embedding_mock()
        vs_mock = _make_vector_store_mock()

        try:
            with patch("api.search.get_embedding_adapter", new=AsyncMock(return_value=ep_mock)):
                with patch("api.search._make_vector_store", return_value=vs_mock):
                    response = await client.post(
                        f"/v1/search/semantic-ingest?domain_id={DOMAIN_ID}",
                        json=self._ingest_payload(),
                        headers={"Authorization": "Bearer fake"},
                    )

            assert response.status_code == 500
            assert "Neo4j write failed" in response.json()["detail"]
        finally:
            self._clear_overrides()


# ─────────────────────── hybrid search endpoint ──────────────────────────────

class TestHybridSearchEndpoint:

    @pytest.fixture(autouse=True)
    def _setup_overrides(self):
        """Override get_db with a lightweight mock — hybrid search does not use PostgreSQL."""
        async def mock_db():
            yield AsyncMock()

        app.dependency_overrides[get_db] = mock_db
        yield
        app.dependency_overrides.pop(get_db, None)

    def _override_auth(self):
        async def mock_auth(domain_id=None, user=None, db=None):
            return _admin_user()
        app.dependency_overrides[require_domain_access] = mock_auth

    def _clear_overrides(self):
        app.dependency_overrides.pop(require_domain_access, None)
        app.dependency_overrides.pop(get_neo4j, None)

    def _neo4j_provenance_record(self, link_id: str, owl_class: str = "Report"):
        record = MagicMock()
        record.__getitem__ = lambda self, key: {
            "owl_class": owl_class,
            "related_nodes": [],
            "relations": [],
        }[key]
        return record

    async def test_unauthenticated_returns_401(self, client):
        response = await client.get(
            f"/v1/search/hybrid?q=test&domain_id={DOMAIN_ID}&limit=5"
        )
        assert response.status_code == 401

    async def test_missing_query_returns_422(self, client):
        self._override_auth()
        try:
            response = await client.get(
                f"/v1/search/hybrid?domain_id={DOMAIN_ID}",
                headers={"Authorization": "Bearer fake"},
            )
            assert response.status_code == 422
        finally:
            self._clear_overrides()

    async def test_missing_domain_id_returns_422(self, client):
        self._override_auth()
        try:
            response = await client.get(
                "/v1/search/hybrid?q=something",
                headers={"Authorization": "Bearer fake"},
            )
            assert response.status_code == 422
        finally:
            self._clear_overrides()

    async def test_empty_collection_returns_empty_list(self, client):
        self._override_auth()
        driver_mock = _make_driver_mock()

        async def mock_neo4j():
            return driver_mock

        app.dependency_overrides[get_neo4j] = mock_neo4j

        ep_mock = _make_embedding_mock()
        vs_mock = _make_vector_store_mock(
            search_side_effect=CollectionNotFoundError("not found")
        )

        try:
            with patch("api.search.get_embedding_adapter", new=AsyncMock(return_value=ep_mock)):
                with patch("api.search._make_vector_store", return_value=vs_mock):
                    response = await client.get(
                        f"/v1/search/hybrid?q=test&domain_id={DOMAIN_ID}",
                        headers={"Authorization": "Bearer fake"},
                    )

            assert response.status_code == 200
            assert response.json() == []
        finally:
            self._clear_overrides()

    async def test_search_returns_hybrid_results(self, client):
        self._override_auth()

        hit_link_id = str(uuid4())
        chroma_hit = SearchResult(
            chunk_id=hit_link_id,
            score=0.25,  # raw cosine distance (as_distances=True)
            text="Knowledge fragment content.",
            metadata={
                "link_id": hit_link_id,
                "owl_class": "Report",
                "governance": "CONFIDENCIAL",
                "source": "report.pdf",
                "domain_id": DOMAIN_ID,
            },
        )

        # Build Neo4j record mock
        record = MagicMock()
        def getitem(key):
            return {
                "owl_class": "Report",
                "related_nodes": [],
                "relations": [],
            }[key]
        record.__getitem__ = lambda self, key: getitem(key)

        driver_mock = _make_driver_mock(records=[record])

        async def mock_neo4j():
            return driver_mock

        app.dependency_overrides[get_neo4j] = mock_neo4j

        ep_mock = _make_embedding_mock()
        vs_mock = _make_vector_store_mock(search_results=[chroma_hit])

        try:
            with patch("api.search.get_embedding_adapter", new=AsyncMock(return_value=ep_mock)):
                with patch("api.search._make_vector_store", return_value=vs_mock):
                    response = await client.get(
                        f"/v1/search/hybrid?q=test&domain_id={DOMAIN_ID}&limit=5",
                        headers={"Authorization": "Bearer fake"},
                    )

            assert response.status_code == 200
            results = response.json()
            assert len(results) == 1
            r = results[0]
            assert r["link_id"] == hit_link_id
            assert r["content"] == "Knowledge fragment content."
            assert r["source_file"] == "report.pdf"
            assert r["provenance"]["owl_class"] == "Report"
            assert r["provenance"]["iso_compliance"] == "ISO_27001"
        finally:
            self._clear_overrides()

    async def test_score_is_one_minus_distance(self, client):
        """score in response = max(0, 1.0 - raw_distance) for cosine distance."""
        self._override_auth()

        raw_distance = 0.3
        expected_score = 1.0 - raw_distance

        hit = SearchResult(
            chunk_id=str(uuid4()),
            score=raw_distance,
            text="text",
            metadata={"link_id": str(uuid4()), "source": ""},
        )

        record = MagicMock()
        def getitem(key):
            return {
                "owl_class": "Class",
                "related_nodes": [],
                "relations": [],
            }[key]
        record.__getitem__ = lambda self, key: getitem(key)

        driver_mock = _make_driver_mock(records=[record])

        async def mock_neo4j():
            return driver_mock

        app.dependency_overrides[get_neo4j] = mock_neo4j

        ep_mock = _make_embedding_mock()
        vs_mock = _make_vector_store_mock(search_results=[hit])

        try:
            with patch("api.search.get_embedding_adapter", new=AsyncMock(return_value=ep_mock)):
                with patch("api.search._make_vector_store", return_value=vs_mock):
                    response = await client.get(
                        f"/v1/search/hybrid?q=test&domain_id={DOMAIN_ID}",
                        headers={"Authorization": "Bearer fake"},
                    )

            result = response.json()[0]
            assert abs(result["score"] - expected_score) < 1e-6
        finally:
            self._clear_overrides()

    async def test_score_clamped_at_zero_for_large_distances(self, client):
        """Cosine distance can be up to 2.0; score must not go negative."""
        self._override_auth()

        # distance > 1.0 → 1.0 - distance < 0 → should be clamped to 0
        hit = SearchResult(
            chunk_id=str(uuid4()),
            score=1.8,  # raw distance
            text="text",
            metadata={"link_id": str(uuid4()), "source": ""},
        )

        record = MagicMock()
        def getitem(key):
            return {"owl_class": "C", "related_nodes": [], "relations": []}[key]
        record.__getitem__ = lambda self, key: getitem(key)

        driver_mock = _make_driver_mock(records=[record])

        async def mock_neo4j():
            return driver_mock

        app.dependency_overrides[get_neo4j] = mock_neo4j

        ep_mock = _make_embedding_mock()
        vs_mock = _make_vector_store_mock(search_results=[hit])

        try:
            with patch("api.search.get_embedding_adapter", new=AsyncMock(return_value=ep_mock)):
                with patch("api.search._make_vector_store", return_value=vs_mock):
                    response = await client.get(
                        f"/v1/search/hybrid?q=test&domain_id={DOMAIN_ID}",
                        headers={"Authorization": "Bearer fake"},
                    )

            result = response.json()[0]
            assert result["score"] >= 0.0
        finally:
            self._clear_overrides()

    async def test_hit_without_neo4j_record_is_skipped(self, client):
        """If Neo4j has no KnowledgeItem for a link_id, that hit is omitted."""
        self._override_auth()

        hit = SearchResult(
            chunk_id=str(uuid4()),
            score=0.2,
            text="orphan content",
            metadata={"link_id": str(uuid4()), "source": ""},
        )

        # Neo4j returns None (no record found)
        result_mock = AsyncMock()
        result_mock.single = AsyncMock(return_value=None)
        session_mock = AsyncMock()
        session_mock.run = AsyncMock(return_value=result_mock)
        driver_mock = MagicMock()
        driver_mock.session.return_value.__aenter__ = AsyncMock(return_value=session_mock)
        driver_mock.session.return_value.__aexit__ = AsyncMock(return_value=False)

        async def mock_neo4j():
            return driver_mock

        app.dependency_overrides[get_neo4j] = mock_neo4j

        ep_mock = _make_embedding_mock()
        vs_mock = _make_vector_store_mock(search_results=[hit])

        try:
            with patch("api.search.get_embedding_adapter", new=AsyncMock(return_value=ep_mock)):
                with patch("api.search._make_vector_store", return_value=vs_mock):
                    response = await client.get(
                        f"/v1/search/hybrid?q=test&domain_id={DOMAIN_ID}",
                        headers={"Authorization": "Bearer fake"},
                    )

            assert response.status_code == 200
            assert response.json() == []
        finally:
            self._clear_overrides()
