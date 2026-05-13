"""
Tests FEAT10-01: Export Turtle (TTL)
Cubre CA-EXP-2.1 a CA-EXP-2.6 y regresion CA-EXP-1.1

  GET /v1/domains/{id}/ontology/export?format=ttl   -> text/turtle
  GET /v1/domains/{id}/ontology/export?format=owl   -> application/rdf+xml (regresion)
  GET /v1/domains/{id}/ontology/export              -> application/rdf+xml (default)
  GET /v1/domains/{id}/ontology/export?format=json  -> 422
"""
import sys
sys.path.insert(0, 'D:\\02-PERSONAL\\01-PROJECTS\\25-KnowledgeManagement\\api\\src')

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import OWL, RDFS, RDF

# -- Datos de prueba ----------------------------------------------------------

DOMAIN_ID = str(uuid4())
CLASS_ID  = str(uuid4())
CLASS2_ID = str(uuid4())
PROP_ID   = str(uuid4())

MOCK_ONTOLOGY = {
    "concepts": [
        {
            "id": CLASS_ID,
            "uri": "http://km.local/ontology#Animal",
            "label": "Animal",
            "comment": "Base class for all animals",
            "subclass_of": [],
            "equivalent_to": [],
            "restrictions": [
                {"property_id": PROP_ID, "restriction_type": "some"}
            ],
            "annotations": {
                "source": "manual",
                "owl:hasKey": "true",
            },
        },
        {
            "id": CLASS2_ID,
            "uri": "http://km.local/ontology#Dog",
            "label": "Dog",
            "comment": None,
            "subclass_of": [CLASS_ID],
            "equivalent_to": [],
            "restrictions": [],
            "annotations": {},
        },
    ],
    "properties": [
        {
            "id": PROP_ID,
            "uri": "http://km.local/ontology#hasName",
            "label": "hasName",
            "comment": "Name of the entity",
            "property_type": "DatatypeProperty",
            "source_class_id": CLASS_ID,
            "target_class_id": "http://www.w3.org/2001/XMLSchema#string",
        }
    ],
}


# -- Fixture ------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    with patch.dict("os.environ", {"BYPASS_AUTH": "true"}):
        with patch("services.ontology_service.get_ontology", return_value=MOCK_ONTOLOGY):
            from main import app
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as ac:
                yield ac


# -- CA-EXP-2.1: extension .ttl en Content-Disposition -----------------------

@pytest.mark.asyncio
async def test_ttl_filename(client):
    resp = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=ttl")
    assert resp.status_code == 200
    assert ".ttl" in resp.headers.get("content-disposition", "")


# -- CA-EXP-2.2: Turtle valido parseable por rdflib ---------------------------

@pytest.mark.asyncio
async def test_ttl_valid_turtle(client):
    resp = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=ttl")
    assert resp.status_code == 200
    g = Graph()
    g.parse(data=resp.text, format="turtle")
    assert len(g) > 0


# -- CA-EXP-2.3: mismo numero de tripletas que OWL ----------------------------

@pytest.mark.asyncio
async def test_ttl_same_triples_as_owl(client):
    resp_ttl = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=ttl")
    resp_owl = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=owl")
    assert resp_ttl.status_code == 200
    assert resp_owl.status_code == 200

    g_ttl = Graph()
    g_ttl.parse(data=resp_ttl.text, format="turtle")
    g_owl = Graph()
    g_owl.parse(data=resp_owl.text, format="xml")

    assert len(g_ttl) == len(g_owl), (
        f"TTL={len(g_ttl)} tripletas, OWL={len(g_owl)} tripletas -- deben ser iguales"
    )


# -- CA-EXP-2.4a: prefijos obligatorios presentes ----------------------------
# rdflib 7.x omite @prefix rdf: cuando usa la abreviatura 'a' para rdf:type.
# Verificamos los prefijos que rdflib emite explicitamente, y verificamos RDF
# mediante la presencia de la abreviatura 'a' (equivalente a rdf:type).

@pytest.mark.asyncio
async def test_ttl_required_prefixes(client):
    resp = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=ttl")
    assert resp.status_code == 200
    body = resp.text
    # Estos prefijos siempre aparecen explicitamente en el TTL
    for prefix in ("owl:", "rdfs:", "xsd:", "km:"):
        assert f"@prefix {prefix}" in body, f"Falta '@prefix {prefix}' en el TTL"
    # rdf:type se abrevia como 'a' en Turtle — verificar su uso
    assert " a " in body, "Falta uso del predicado rdf:type (abreviatura 'a') en el TTL"


# -- CA-EXP-2.4b: Content-Type es text/turtle ---------------------------------

@pytest.mark.asyncio
async def test_ttl_content_type(client):
    resp = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=ttl")
    assert resp.status_code == 200
    assert "text/turtle" in resp.headers.get("content-type", "")


# -- CA-EXP-2.5: contenido completo (clases, props, restricciones, hasKey) ----

@pytest.mark.asyncio
async def test_ttl_content_completeness(client):
    resp = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=ttl")
    assert resp.status_code == 200
    g = Graph()
    g.parse(data=resp.text, format="turtle")

    animal = URIRef("http://km.local/ontology#Animal")
    dog    = URIRef("http://km.local/ontology#Dog")
    prop   = URIRef("http://km.local/ontology#hasName")

    assert (animal, RDF.type, OWL.Class) in g,          "Animal debe ser owl:Class"
    assert (dog, RDF.type, OWL.Class) in g,             "Dog debe ser owl:Class"
    assert (animal, RDFS.label, Literal("Animal")) in g, "Label de Animal debe existir"
    assert (animal, RDFS.comment, Literal("Base class for all animals")) in g
    assert (dog, RDFS.subClassOf, animal) in g,         "Dog subClassOf Animal"
    assert (prop, RDF.type, OWL.DatatypeProperty) in g, "hasName debe ser DatatypeProperty"

    has_key = URIRef("http://km.local/ontology#hasKey")
    assert (animal, has_key, Literal("true")) in g,     "owl:hasKey debe estar presente"


# -- Regresion CA-EXP-1.1: OWL/XML sigue funcionando -------------------------

@pytest.mark.asyncio
async def test_owl_regression(client):
    resp = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=owl")
    assert resp.status_code == 200
    assert "application/rdf+xml" in resp.headers.get("content-type", "")
    assert ".owl" in resp.headers.get("content-disposition", "")
    g = Graph()
    g.parse(data=resp.text, format="xml")
    assert len(g) > 0


# -- Regresion: sin ?format el default es OWL ---------------------------------

@pytest.mark.asyncio
async def test_default_format_is_owl(client):
    resp = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export")
    assert resp.status_code == 200
    assert "application/rdf+xml" in resp.headers.get("content-type", "")


# -- Formato invalido -> 422 --------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_format_returns_422(client):
    resp = await client.get(f"/v1/domains/{DOMAIN_ID}/ontology/export?format=json")
    assert resp.status_code == 422
