"""
Tests FEAT10-03: Import Replace + Atomicidad
CA-IMP-2.4 — Replace elimina todas las clases/propiedades existentes
CA-IMP-2.5 — Tras eliminar, crea las clases del archivo
CA-IMP-2.7 — Archivo inválido no dispara delete (atomicidad semántica)
"""
import sys
sys.path.insert(0, 'D:\\02-PERSONAL\\01-PROJECTS\\25-KnowledgeManagement\\api\\src')

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from io import BytesIO
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import OWL, RDFS, RDF

DOMAIN_ID = str(uuid4())
CLASS_URI  = "http://km.local/ontology#Animal"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_owl_bytes(classes: list[dict]) -> bytes:
    KM = Namespace("http://km.local/ontology#")
    g = Graph()
    g.bind("owl", OWL); g.bind("rdfs", RDFS); g.bind("km", KM)
    for cls in classes:
        uri = URIRef(cls["uri"])
        g.add((uri, RDF.type, OWL.Class))
        g.add((uri, RDFS.label, Literal(cls["label"])))
    result = g.serialize(format="xml")
    return result.encode("utf-8") if isinstance(result, str) else result


def _empty_ontology():
    return {"domain_id": DOMAIN_ID, "concepts": [], "properties": []}


@pytest_asyncio.fixture
async def client():
    with patch.dict("os.environ", {"BYPASS_AUTH": "true"}):
        from main import app
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac


# ── CA-IMP-2.4: replace llama delete_all_ontology ────────────────────────────

@pytest.mark.asyncio
async def test_replace_calls_delete_all(client):
    """CA-IMP-2.4: mode=replace invoca delete_all_ontology con el domain_id correcto."""
    owl_bytes = _make_owl_bytes([{"uri": CLASS_URI, "label": "Animal"}])
    with patch("services.ontology_service.get_ontology",
               return_value=_empty_ontology()), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.delete_all_ontology = AsyncMock(return_value=(2, 1))
        mock_adapter.upsert_class        = AsyncMock()
        mock_adapter.upsert_property     = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
            data={"mode": "replace"},
        )

    assert resp.status_code == 200, resp.text
    mock_adapter.delete_all_ontology.assert_called_once_with(DOMAIN_ID)


# ── CA-IMP-2.5: tras delete, clases del archivo se crean ─────────────────────

@pytest.mark.asyncio
async def test_replace_creates_classes_after_delete(client):
    """CA-IMP-2.5: después del delete_all, las clases del archivo se crean."""
    owl_bytes = _make_owl_bytes([{"uri": CLASS_URI, "label": "Animal"}])
    with patch("services.ontology_service.get_ontology",
               return_value=_empty_ontology()), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.delete_all_ontology = AsyncMock(return_value=(0, 0))
        mock_adapter.upsert_class        = AsyncMock()
        mock_adapter.upsert_property     = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
            data={"mode": "replace"},
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["concepts_created"] == 1, f"Expected 1 created, got {body}"
    mock_adapter.upsert_class.assert_called_once()


# ── CA-IMP-2.7: archivo inválido → 422, delete NO se llama ───────────────────

@pytest.mark.asyncio
async def test_replace_invalid_file_does_not_delete(client):
    """CA-IMP-2.7: parse falla ANTES de delete → ontología no se toca."""
    garbage = b"not valid xml or turtle !!!"
    with patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.delete_all_ontology = AsyncMock(return_value=(0, 0))

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("broken.owl", BytesIO(garbage), "application/rdf+xml")},
            data={"mode": "replace"},
        )

    assert resp.status_code == 422, resp.text
    mock_adapter.delete_all_ontology.assert_not_called()


# ── Regresión: mode=merge no llama delete_all ─────────────────────────────────

@pytest.mark.asyncio
async def test_merge_does_not_call_delete_all(client):
    """Regresión: mode=merge nunca invoca delete_all_ontology."""
    owl_bytes = _make_owl_bytes([{"uri": CLASS_URI, "label": "Animal"}])
    with patch("services.ontology_service.get_ontology",
               side_effect=[_empty_ontology(), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.delete_all_ontology = AsyncMock(return_value=(0, 0))
        mock_adapter.upsert_class        = AsyncMock()
        mock_adapter.upsert_property     = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
            data={"mode": "merge"},
        )

    assert resp.status_code == 200, resp.text
    mock_adapter.delete_all_ontology.assert_not_called()
