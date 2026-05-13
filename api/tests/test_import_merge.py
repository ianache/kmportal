"""
Tests FEAT10-02: Import Merge (OWL/XML y TTL)
Cubre CA-IMP-1.5 a CA-IMP-1.12

  POST /v1/domains/{id}/ontology/import  (multipart, mode=merge)
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
CLASS2_URI = "http://km.local/ontology#Dog"
PROP_URI   = "http://km.local/ontology#hasName"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_owl_bytes(classes: list[dict], properties: list[dict] | None = None) -> bytes:
    """Build minimal OWL/XML bytes for testing."""
    KM = Namespace("http://km.local/ontology#")
    g = Graph()
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("km", KM)
    for cls in classes:
        uri = URIRef(cls["uri"])
        g.add((uri, RDF.type, OWL.Class))
        g.add((uri, RDFS.label, Literal(cls["label"])))
        if cls.get("comment"):
            g.add((uri, RDFS.comment, Literal(cls["comment"])))
    for prop in (properties or []):
        uri = URIRef(prop["uri"])
        ptype = OWL.DatatypeProperty if prop.get("type") == "DatatypeProperty" else OWL.ObjectProperty
        g.add((uri, RDF.type, ptype))
        g.add((uri, RDFS.label, Literal(prop["label"])))
        if prop.get("domain"):
            g.add((uri, RDFS.domain, URIRef(prop["domain"])))
    result = g.serialize(format="xml")
    return result.encode("utf-8") if isinstance(result, str) else result


def _make_ttl_bytes(classes: list[dict]) -> bytes:
    KM = Namespace("http://km.local/ontology#")
    g = Graph()
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("km", KM)
    for cls in classes:
        uri = URIRef(cls["uri"])
        g.add((uri, RDF.type, OWL.Class))
        g.add((uri, RDFS.label, Literal(cls["label"])))
    result = g.serialize(format="turtle")
    return result.encode("utf-8") if isinstance(result, str) else result


def _empty_ontology() -> dict:
    return {"domain_id": DOMAIN_ID, "concepts": [], "properties": []}


def _ontology_with_class(class_id: str, uri: str = CLASS_URI, label: str = "Animal") -> dict:
    return {
        "domain_id": DOMAIN_ID,
        "concepts": [{
            "id": class_id, "domain_id": DOMAIN_ID,
            "uri": uri, "label": label, "comment": None,
            "subclass_of": [], "equivalent_to": [], "restrictions": [], "annotations": {},
        }],
        "properties": [],
    }


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    with patch.dict("os.environ", {"BYPASS_AUTH": "true"}):
        from main import app
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac


# ── CA-IMP-1.5: clases nuevas se crean ───────────────────────────────────────

@pytest.mark.asyncio
async def test_import_creates_new_classes(client):
    """CA-IMP-1.5: clase del archivo no presente en el dominio → se crea."""
    owl_bytes = _make_owl_bytes([{"uri": CLASS_URI, "label": "Animal", "comment": "A base class"}])
    with patch("services.ontology_service.get_ontology",
               side_effect=[_empty_ontology(), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
            data={"mode": "merge"},
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["concepts_created"] == 1
    assert body["concepts_updated"] == 0
    mock_adapter.upsert_class.assert_called_once()


# ── CA-IMP-1.6: clases existentes (mismo URI) se actualizan ──────────────────

@pytest.mark.asyncio
async def test_import_updates_existing_classes(client):
    """CA-IMP-1.6: clase con mismo URI ya existe → se actualiza (concepts_updated)."""
    existing_id = str(uuid4())
    owl_bytes = _make_owl_bytes([{"uri": CLASS_URI, "label": "AnimalUpdated", "comment": "Updated"}])
    with patch("services.ontology_service.get_ontology",
               side_effect=[_ontology_with_class(existing_id), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
            data={"mode": "merge"},
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["concepts_updated"] == 1
    assert body["concepts_created"] == 0
    # Verify existing id was reused
    call_args = mock_adapter.upsert_class.call_args[0][0]
    assert call_args.id == existing_id


# ── CA-IMP-1.7: clases no en el archivo NO se eliminan ───────────────────────

@pytest.mark.asyncio
async def test_import_merge_does_not_delete_absent_classes(client):
    """CA-IMP-1.7: clases del dominio no presentes en el archivo quedan intactas."""
    existing_id = str(uuid4())
    other_id    = str(uuid4())
    two_class_ontology = {
        "domain_id": DOMAIN_ID,
        "concepts": [
            {"id": existing_id, "domain_id": DOMAIN_ID, "uri": CLASS_URI,  "label": "Animal",
             "comment": None, "subclass_of": [], "equivalent_to": [], "restrictions": [], "annotations": {}},
            {"id": other_id,    "domain_id": DOMAIN_ID, "uri": CLASS2_URI, "label": "Dog",
             "comment": None, "subclass_of": [], "equivalent_to": [], "restrictions": [], "annotations": {}},
        ],
        "properties": [],
    }
    owl_bytes = _make_owl_bytes([{"uri": CLASS_URI, "label": "Animal"}])

    with patch("services.ontology_service.get_ontology",
               side_effect=[two_class_ontology, two_class_ontology]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class    = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()
        mock_adapter.delete_class    = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
            data={"mode": "merge"},
        )

    assert resp.status_code == 200, resp.text
    mock_adapter.delete_class.assert_not_called()


# ── CA-IMP-1.8: propiedades se crean ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_import_creates_properties(client):
    """CA-IMP-1.8: propiedad del archivo → se crea (properties_created > 0)."""
    class_id = str(uuid4())
    with_class = _ontology_with_class(class_id, CLASS_URI)
    with_class["properties"] = []  # ensure no stale properties
    owl_bytes = _make_owl_bytes(
        classes=[{"uri": CLASS_URI, "label": "Animal"}],
        properties=[{"uri": PROP_URI, "label": "hasName",
                     "type": "DatatypeProperty", "domain": CLASS_URI}],
    )
    with patch("services.ontology_service.get_ontology",
               side_effect=[with_class, with_class]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class    = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
            data={"mode": "merge"},
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["properties_created"] >= 1


# ── CA-IMP-1.9: response tiene conteos y campo ontology ──────────────────────

@pytest.mark.asyncio
async def test_import_response_structure(client):
    """CA-IMP-1.9: response contiene todos los campos requeridos."""
    owl_bytes = _make_owl_bytes([{"uri": CLASS_URI, "label": "Animal"}])
    with patch("services.ontology_service.get_ontology",
               side_effect=[_empty_ontology(), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class    = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
            data={"mode": "merge"},
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    for field in ("concepts_created", "concepts_updated",
                  "properties_created", "properties_updated", "errors", "ontology"):
        assert field in body, f"Campo '{field}' ausente en el response"


# ── CA-IMP-1.11: TTL con @prefix importa correctamente ───────────────────────

@pytest.mark.asyncio
async def test_import_ttl_format(client):
    """CA-IMP-1.11: archivo .ttl con @prefix se parsea e importa sin error."""
    ttl_bytes = _make_ttl_bytes([{"uri": CLASS_URI, "label": "Animal"}])
    with patch("services.ontology_service.get_ontology",
               side_effect=[_empty_ontology(), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class    = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("onto.ttl", BytesIO(ttl_bytes), "text/turtle")},
            data={"mode": "merge"},
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["concepts_created"] == 1


# ── CA-IMP-1.12: archivo malformado → 422 ────────────────────────────────────

@pytest.mark.asyncio
async def test_import_malformed_file_returns_422(client):
    """CA-IMP-1.12: archivo que no es OWL/TTL válido → HTTP 422."""
    garbage = b"this is not valid owl xml or turtle !!!"
    with patch("services.ontology_service.get_ontology", return_value=_empty_ontology()), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value

        resp = await client.post(
            f"/v1/domains/{DOMAIN_ID}/ontology/import",
            files={"file": ("broken.owl", BytesIO(garbage), "application/rdf+xml")},
            data={"mode": "merge"},
        )

    assert resp.status_code == 422


# ── mode=replace → 501 ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_import_replace_mode_returns_501(client):
    """mode=replace devuelve 501 hasta que Iteración 3 lo implemente."""
    owl_bytes = _make_owl_bytes([{"uri": CLASS_URI, "label": "Animal"}])
    resp = await client.post(
        f"/v1/domains/{DOMAIN_ID}/ontology/import",
        files={"file": ("onto.owl", BytesIO(owl_bytes), "application/rdf+xml")},
        data={"mode": "replace"},
    )
    assert resp.status_code == 501
