"""
Tests FEAT10-06: Round-trip Export → Import
CA-RT-1.1 — OWL round-trip: export OWL → import merge → all classes/properties created
CA-RT-1.2 — TTL round-trip: export TTL → import merge → all classes/properties created
CA-RT-1.3 — Counts (classes, props, restrictions, annotation-props) preserved in export graph
CA-RT-1.4 — OWL and TTL exports of same ontology produce same import counts
"""
import sys
sys.path.insert(0, 'D:\\02-PERSONAL\\01-PROJECTS\\25-KnowledgeManagement\\api\\src')

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from rdflib import Graph
from rdflib.namespace import OWL, RDF

DOMAIN_ID = str(uuid4())

MOCK_ONTOLOGY = {
    "domain_id": DOMAIN_ID,
    "concepts": [
        {
            "id": "cls-animal",
            "uri": "http://km.local/ontology#Animal",
            "label": "Animal",
            "comment": "Base class for all animals",
            "subclass_of": [],
            "equivalent_to": [],
            "restrictions": [],
            "annotations": {"owl:hasKey": "true", "source": "manual"},
        },
        {
            "id": "cls-dog",
            "uri": "http://km.local/ontology#Dog",
            "label": "Dog",
            "comment": None,
            "subclass_of": ["cls-animal"],
            "equivalent_to": [],
            "restrictions": [{"property_id": "prop-hasname", "restriction_type": "some"}],
            "annotations": {},
        },
    ],
    "properties": [
        {
            "id": "prop-hasname",
            "uri": "http://km.local/ontology#hasName",
            "label": "hasName",
            "comment": "Name of the entity",
            "property_type": "DatatypeProperty",
            "source_class_id": "cls-animal",
            "target_class_id": "http://www.w3.org/2001/XMLSchema#string",
        }
    ],
}


def _empty_ontology():
    return {"domain_id": DOMAIN_ID, "concepts": [], "properties": []}


# ── CA-RT-1.1: OWL round-trip creates all classes and properties ──────────────

@pytest.mark.asyncio
async def test_round_trip_owl_creates_all_classes():
    """CA-RT-1.1: Export OWL → import merge into empty domain → all classes/props created."""
    from services.ontology_service import export_owl, import_owl

    mock_driver = MagicMock()

    with patch("services.ontology_service.get_ontology", return_value=MOCK_ONTOLOGY):
        owl_bytes = await export_owl(mock_driver, DOMAIN_ID, fmt="owl")

    assert isinstance(owl_bytes, bytes) and len(owl_bytes) > 0

    with patch("services.ontology_service.get_ontology",
               side_effect=[_empty_ontology(), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()
        result = await import_owl(mock_driver, DOMAIN_ID, owl_bytes, fmt="xml", mode="merge")

    assert result["concepts_created"] == len(MOCK_ONTOLOGY["concepts"]), (
        f"Expected {len(MOCK_ONTOLOGY['concepts'])} classes created, got {result['concepts_created']}"
    )
    assert result["properties_created"] == len(MOCK_ONTOLOGY["properties"]), (
        f"Expected {len(MOCK_ONTOLOGY['properties'])} properties created, got {result['properties_created']}"
    )
    assert result["errors"] == []


# ── CA-RT-1.2: TTL round-trip creates all classes and properties ──────────────

@pytest.mark.asyncio
async def test_round_trip_ttl_creates_all_classes():
    """CA-RT-1.2: Export TTL → import merge into empty domain → all classes/props created."""
    from services.ontology_service import export_owl, import_owl

    mock_driver = MagicMock()

    with patch("services.ontology_service.get_ontology", return_value=MOCK_ONTOLOGY):
        ttl_bytes = await export_owl(mock_driver, DOMAIN_ID, fmt="ttl")

    assert isinstance(ttl_bytes, bytes) and len(ttl_bytes) > 0

    with patch("services.ontology_service.get_ontology",
               side_effect=[_empty_ontology(), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()
        result = await import_owl(mock_driver, DOMAIN_ID, ttl_bytes, fmt="ttl", mode="merge")

    assert result["concepts_created"] == len(MOCK_ONTOLOGY["concepts"]), (
        f"Expected {len(MOCK_ONTOLOGY['concepts'])} classes created, got {result['concepts_created']}"
    )
    assert result["properties_created"] == len(MOCK_ONTOLOGY["properties"]), (
        f"Expected {len(MOCK_ONTOLOGY['properties'])} properties created, got {result['properties_created']}"
    )
    assert result["errors"] == []


# ── CA-RT-1.3: counts preserved in the exported graph ─────────────────────────

@pytest.mark.asyncio
async def test_round_trip_counts_preserved():
    """CA-RT-1.3: class, property, restriction, and annotation-prop counts match export graph."""
    from services.ontology_service import export_owl

    mock_driver = MagicMock()

    original_classes = len(MOCK_ONTOLOGY["concepts"])
    original_props = len(MOCK_ONTOLOGY["properties"])
    original_restrictions = sum(
        len(c.get("restrictions") or []) for c in MOCK_ONTOLOGY["concepts"]
    )
    # Each distinct annotation key → one owl:AnnotationProperty declaration in the graph
    all_annotation_keys: set[str] = set()
    for c in MOCK_ONTOLOGY["concepts"]:
        for k in (c.get("annotations") or {}):
            all_annotation_keys.add(k)

    with patch("services.ontology_service.get_ontology", return_value=MOCK_ONTOLOGY):
        owl_bytes = await export_owl(mock_driver, DOMAIN_ID, fmt="owl")

    g = Graph()
    g.parse(data=owl_bytes, format="xml")

    exported_classes = sum(1 for _ in g.subjects(RDF.type, OWL.Class))
    exported_props = sum(
        1 for _ in (
            list(g.subjects(RDF.type, OWL.DatatypeProperty))
            + list(g.subjects(RDF.type, OWL.ObjectProperty))
        )
    )
    exported_restrictions = sum(1 for _ in g.subjects(RDF.type, OWL.Restriction))
    exported_annotation_props = sum(1 for _ in g.subjects(RDF.type, OWL.AnnotationProperty))

    assert exported_classes == original_classes, (
        f"Classes: original={original_classes}, exported={exported_classes}"
    )
    assert exported_props == original_props, (
        f"Properties: original={original_props}, exported={exported_props}"
    )
    assert exported_restrictions == original_restrictions, (
        f"Restrictions: original={original_restrictions}, exported={exported_restrictions}"
    )
    assert exported_annotation_props == len(all_annotation_keys), (
        f"AnnotationProps: expected {len(all_annotation_keys)}, got {exported_annotation_props}"
    )


# ── CA-RT-1.4: OWL and TTL round-trips produce same import counts ─────────────

@pytest.mark.asyncio
async def test_round_trip_owl_ttl_same_result():
    """CA-RT-1.4: importing OWL and TTL exports of the same ontology yields identical counts."""
    from services.ontology_service import export_owl, import_owl

    mock_driver = MagicMock()

    with patch("services.ontology_service.get_ontology", return_value=MOCK_ONTOLOGY):
        owl_bytes = await export_owl(mock_driver, DOMAIN_ID, fmt="owl")
        ttl_bytes = await export_owl(mock_driver, DOMAIN_ID, fmt="ttl")

    with patch("services.ontology_service.get_ontology",
               side_effect=[_empty_ontology(), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()
        result_owl = await import_owl(mock_driver, DOMAIN_ID, owl_bytes, fmt="xml", mode="merge")

    with patch("services.ontology_service.get_ontology",
               side_effect=[_empty_ontology(), _empty_ontology()]), \
         patch("services.ontology_service.Neo4jAdapter") as MockAdapter:
        mock_adapter = MockAdapter.return_value
        mock_adapter.upsert_class = AsyncMock()
        mock_adapter.upsert_property = AsyncMock()
        result_ttl = await import_owl(mock_driver, DOMAIN_ID, ttl_bytes, fmt="ttl", mode="merge")

    assert result_owl["concepts_created"] == result_ttl["concepts_created"], (
        f"OWL created {result_owl['concepts_created']} classes, "
        f"TTL created {result_ttl['concepts_created']}"
    )
    assert result_owl["properties_created"] == result_ttl["properties_created"], (
        f"OWL created {result_owl['properties_created']} props, "
        f"TTL created {result_ttl['properties_created']}"
    )
    assert result_owl["errors"] == []
    assert result_ttl["errors"] == []
