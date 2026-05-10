"""
Unit + API tests for FEAT5 batch ontology save.

  Service: services.ontology_service.save_ontology_batch()
  Endpoint: POST /v1/domains/{domain_id}/ontology/batch

Covers concept / property / diagram create-update-delete operations,
mixed batches, and partial-failure error reporting.
"""
import sys
sys.path.insert(0, 'D:\\02-PERSONAL\\01-PROJECTS\\25-KnowledgeManagement\\api\\src')

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID

from schemas import (
    ConceptBatchOperation,
    DiagramBatchOperation,
    OntologyBatchPayload,
    OntologyConceptCreate,
    OntologyPropertyCreate,
    PropertyBatchOperation,
)


# ─────────────────────────────── helpers ────────────────────────────────────

DOMAIN_ID = str(uuid4())


def _concept_create_op(label: str = "MyClass", uri: str | None = None) -> ConceptBatchOperation:
    return ConceptBatchOperation(
        operation="create",
        data=OntologyConceptCreate(
            uri=uri or f"http://km.local/ontology#{label}",
            label=label,
            comment="A test class",
        ),
    )


def _concept_update_op(concept_id: str, label: str = "UpdatedClass") -> ConceptBatchOperation:
    return ConceptBatchOperation(
        operation="update",
        id=concept_id,
        data=OntologyConceptCreate(
            uri=f"http://km.local/ontology#{label}",
            label=label,
        ),
    )


def _concept_delete_op(concept_id: str) -> ConceptBatchOperation:
    return ConceptBatchOperation(operation="delete", id=concept_id)


def _property_create_op(
    label: str = "hasRelation",
    source_id: str = "src-class",
    target_id: str = "tgt-class",
) -> PropertyBatchOperation:
    return PropertyBatchOperation(
        operation="create",
        data=OntologyPropertyCreate(
            uri=f"http://km.local/ontology#{label}",
            label=label,
            property_type="ObjectProperty",
            source_class_id=source_id,
            target_class_id=target_id,
        ),
    )


def _property_delete_op(prop_id: str) -> PropertyBatchOperation:
    return PropertyBatchOperation(operation="delete", id=prop_id)


def _diagram_create_op(name: str = "Default") -> DiagramBatchOperation:
    return DiagramBatchOperation(
        operation="create",
        data={"name": name, "nodes": [], "edges": [], "viewport": {"x": 0, "y": 0, "zoom": 1}},
    )


def _diagram_update_op(diagram_id: str, name: str = "Renamed") -> DiagramBatchOperation:
    return DiagramBatchOperation(operation="update", id=diagram_id, data={"name": name})


def _diagram_delete_op(diagram_id: str) -> DiagramBatchOperation:
    return DiagramBatchOperation(operation="delete", id=diagram_id)


def _make_neo4j_driver():
    """Return a Neo4j driver mock whose upsert/delete methods succeed."""
    adapter = AsyncMock()
    adapter.upsert_class = AsyncMock()
    adapter.upsert_property = AsyncMock()
    adapter.delete_class = AsyncMock(return_value=True)
    adapter.delete_property = AsyncMock(return_value=True)
    adapter.get_ontology = AsyncMock(return_value={"concepts": [], "properties": []})
    return adapter


# ──────────────────────── service-level unit tests ───────────────────────────

class TestSaveOntologyBatchConcepts:

    async def test_create_concept_is_recorded_in_response(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        payload = OntologyBatchPayload(concepts=[_concept_create_op("Animal")])
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is True
        assert len(result.concepts_created) == 1

    async def test_create_multiple_concepts(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        payload = OntologyBatchPayload(
            concepts=[_concept_create_op("A"), _concept_create_op("B"), _concept_create_op("C")]
        )
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert len(result.concepts_created) == 3

    async def test_update_existing_concept(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        existing_id = str(uuid4())
        adapter = _make_neo4j_driver()
        adapter.get_ontology = AsyncMock(
            return_value={
                "concepts": [{"id": existing_id, "label": "Old", "uri": "http://old", "comment": ""}],
                "properties": [],
            }
        )
        payload = OntologyBatchPayload(concepts=[_concept_update_op(existing_id, label="NewLabel")])
        with patch("services.ontology_service.Neo4jAdapter", return_value=adapter):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is True
        assert existing_id in result.concepts_updated

    async def test_update_nonexistent_concept_reports_error(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        missing_id = str(uuid4())
        adapter = _make_neo4j_driver()
        adapter.get_ontology = AsyncMock(return_value={"concepts": [], "properties": []})
        payload = OntologyBatchPayload(concepts=[_concept_update_op(missing_id)])
        with patch("services.ontology_service.Neo4jAdapter", return_value=adapter):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is False
        assert any(missing_id in e for e in result.errors)

    async def test_delete_concept_is_recorded(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        concept_id = str(uuid4())
        payload = OntologyBatchPayload(concepts=[_concept_delete_op(concept_id)])
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert concept_id in result.concepts_deleted

    async def test_delete_nonexistent_concept_reports_error(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        missing_id = str(uuid4())
        adapter = _make_neo4j_driver()
        adapter.delete_class = AsyncMock(return_value=False)
        payload = OntologyBatchPayload(concepts=[_concept_delete_op(missing_id)])
        with patch("services.ontology_service.Neo4jAdapter", return_value=adapter):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is False
        assert any(missing_id in e for e in result.errors)

    async def test_neo4j_exception_is_captured_as_error(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        adapter = _make_neo4j_driver()
        adapter.upsert_class = AsyncMock(side_effect=Exception("connection error"))
        payload = OntologyBatchPayload(concepts=[_concept_create_op()])
        with patch("services.ontology_service.Neo4jAdapter", return_value=adapter):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is False
        assert len(result.errors) == 1
        assert "Concept operation failed" in result.errors[0]


class TestSaveOntologyBatchProperties:

    async def test_create_property_is_recorded(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        payload = OntologyBatchPayload(properties=[_property_create_op()])
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is True
        assert len(result.properties_created) == 1

    async def test_delete_property_is_recorded(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        prop_id = str(uuid4())
        payload = OntologyBatchPayload(properties=[_property_delete_op(prop_id)])
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert prop_id in result.properties_deleted

    async def test_delete_nonexistent_property_reports_error(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        prop_id = str(uuid4())
        adapter = _make_neo4j_driver()
        adapter.delete_property = AsyncMock(return_value=False)
        payload = OntologyBatchPayload(properties=[_property_delete_op(prop_id)])
        with patch("services.ontology_service.Neo4jAdapter", return_value=adapter):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is False


class TestSaveOntologyBatchDiagrams:

    async def test_create_diagram_is_persisted(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        payload = OntologyBatchPayload(diagrams=[_diagram_create_op("My Diagram")])
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is True
        assert len(result.diagrams_created) == 1

    async def test_update_nonexistent_diagram_reports_error(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        fake_id = str(uuid4())
        # get_diagram returns None for unknown id
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            with patch("services.ontology_service.get_diagram", new=AsyncMock(return_value=None)):
                payload = OntologyBatchPayload(diagrams=[_diagram_update_op(fake_id, name="X")])
                result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is False
        assert any(fake_id in e for e in result.errors)

    async def test_delete_nonexistent_diagram_reports_error(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        fake_id = str(uuid4())
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            with patch("services.ontology_service.get_diagram", new=AsyncMock(return_value=None)):
                payload = OntologyBatchPayload(diagrams=[_diagram_delete_op(fake_id)])
                result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is False


class TestSaveOntologyBatchMixed:

    async def test_empty_payload_succeeds(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        payload = OntologyBatchPayload()
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is True
        assert result.errors == []

    async def test_mixed_batch_success(self):
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        payload = OntologyBatchPayload(
            concepts=[_concept_create_op("Vehicle")],
            properties=[_property_create_op("owns", "Person", "Vehicle")],
            diagrams=[_diagram_create_op("Fleet")],
        )
        with patch("services.ontology_service.Neo4jAdapter", return_value=_make_neo4j_driver()):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is True
        assert len(result.concepts_created) == 1
        assert len(result.properties_created) == 1
        assert len(result.diagrams_created) == 1

    async def test_partial_failure_collects_all_errors(self):
        """A failing concept op must not abort the property ops that follow."""
        from services.ontology_service import save_ontology_batch
        db = AsyncMock()
        adapter = _make_neo4j_driver()
        adapter.upsert_class = AsyncMock(side_effect=Exception("neo4j error"))
        payload = OntologyBatchPayload(
            concepts=[_concept_create_op("FailClass")],
            properties=[_property_create_op()],
        )
        with patch("services.ontology_service.Neo4jAdapter", return_value=adapter):
            result = await save_ontology_batch(None, db, DOMAIN_ID, payload)
        assert result.success is False
        assert len(result.errors) >= 1
        assert len(result.properties_created) == 1


# ─────────────────────── API endpoint (batch route) ──────────────────────────

@pytest_asyncio.fixture
async def client():
    """No SQLite dependency — batch endpoint uses mocked get_db."""
    async with AsyncClient(
        transport=ASGITransport(app=__import__("main").app),
        base_url="http://test",
    ) as ac:
        yield ac
    __import__("main").app.dependency_overrides.clear()


class TestOntologyBatchEndpoint:

    @pytest.fixture(autouse=True)
    def _setup_db_override(self):
        from main import app
        from db.database import get_db

        async def mock_db():
            yield AsyncMock()

        app.dependency_overrides[get_db] = mock_db
        yield
        app.dependency_overrides.pop(get_db, None)

    async def test_unauthenticated_returns_401(self, client):
        response = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/batch",
            json={"concepts": [], "properties": [], "diagrams": []},
        )
        assert response.status_code == 401

    async def test_successful_batch_returns_200(self, client):
        from main import app
        from core.dependencies import require_domain_access
        from db.neo4j_client import get_neo4j
        from schemas import UserInToken

        async def mock_auth(domain_id=None, user=None, db=None):
            return UserInToken(
                id=uuid4(),
                keycloak_id="admin-kc",
                email="admin@test.com",
                roles=["KM_ADMIN"],
                scopes=[],
                allowed_domains=[],
            )

        async def mock_neo4j():
            return None

        app.dependency_overrides[require_domain_access] = mock_auth
        app.dependency_overrides[get_neo4j] = mock_neo4j

        try:
            with patch(
                "services.ontology_service.Neo4jAdapter",
                return_value=_make_neo4j_driver()
            ):
                response = await client.post(
                    f"/v1/domains/{DOMAIN_ID}/ontology/batch",
                    json={
                        "concepts": [
                            {
                                "operation": "create",
                                "data": {
                                    "uri": "http://km.local/ontology#Dog",
                                    "label": "Dog",
                                    "comment": "A dog class",
                                },
                            }
                        ],
                        "properties": [],
                        "diagrams": [],
                    },
                    headers={"Authorization": "Bearer fake"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["concepts_created"]) == 1
        finally:
            app.dependency_overrides.pop(require_domain_access, None)
            app.dependency_overrides.pop(get_neo4j, None)

    async def test_batch_response_schema_is_complete(self, client):
        """All response fields defined in OntologyBatchResponse must be present."""
        from main import app
        from core.dependencies import require_domain_access
        from db.neo4j_client import get_neo4j
        from schemas import UserInToken

        async def mock_auth(domain_id=None, user=None, db=None):
            return UserInToken(
                id=uuid4(),
                keycloak_id="admin-kc",
                email="admin@test.com",
                roles=["KM_ADMIN"],
                scopes=[],
                allowed_domains=[],
            )

        async def mock_neo4j():
            return None

        app.dependency_overrides[require_domain_access] = mock_auth
        app.dependency_overrides[get_neo4j] = mock_neo4j

        required_fields = {
            "success",
            "concepts_created", "concepts_updated", "concepts_deleted",
            "properties_created", "properties_updated", "properties_deleted",
            "diagrams_created", "diagrams_updated", "diagrams_deleted",
            "errors",
        }

        try:
            with patch(
                "services.ontology_service.Neo4jAdapter",
                return_value=_make_neo4j_driver()
            ):
                response = await client.post(
                    f"/v1/domains/{DOMAIN_ID}/ontology/batch",
                    json={"concepts": [], "properties": [], "diagrams": []},
                    headers={"Authorization": "Bearer fake"},
                )

            assert response.status_code == 200
            data = response.json()
            assert required_fields.issubset(data.keys())
        finally:
            app.dependency_overrides.pop(require_domain_access, None)
            app.dependency_overrides.pop(get_neo4j, None)
