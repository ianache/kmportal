"""Ontology service: manages OWL concepts in Neo4j and diagrams in PostgreSQL."""

import io
import uuid
from typing import Any

from neo4j import AsyncDriver
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import OntologyDiagram
from schemas import (
    DiagramCreate,
    DiagramUpdate,
    OntologyConceptCreate,
    OntologyConceptResponse,
    OntologyConceptUpdate,
    OntologyPropertyCreate,
    OntologyPropertyResponse,
    OntologyResponse,
)


# ─────────────────────────────── Neo4j helpers ────────────────────────────────

def _row_to_concept(record: dict[str, Any]) -> OntologyConceptResponse:
    n = record["c"]
    return OntologyConceptResponse(
        id=n["id"],
        domain_id=n["domain_id"],
        uri=n["uri"],
        label=n["label"],
        comment=n.get("comment"),
    )


def _row_to_property(record: dict[str, Any]) -> OntologyPropertyResponse:
    p = record["p"]
    return OntologyPropertyResponse(
        id=p["id"],
        domain_id=p["domain_id"],
        uri=p["uri"],
        label=p["label"],
        property_type=p["property_type"],
        source_class_id=p["source_class_id"],
        target_class_id=p["target_class_id"],
        comment=p.get("comment"),
    )


# ─────────────────────────── Concept CRUD (Neo4j) ─────────────────────────────

async def create_concept(
    driver: AsyncDriver,
    domain_id: str,
    data: OntologyConceptCreate,
) -> OntologyConceptResponse:
    concept_id = str(uuid.uuid4())
    async with driver.session() as session:
        result = await session.run(
            """
            CREATE (c:OWLClass {
                id: $id,
                domain_id: $domain_id,
                uri: $uri,
                label: $label,
                comment: $comment
            })
            RETURN c
            """,
            id=concept_id,
            domain_id=domain_id,
            uri=data.uri,
            label=data.label,
            comment=data.comment,
        )
        record = await result.single()
    return OntologyConceptResponse(
        id=concept_id,
        domain_id=domain_id,
        uri=data.uri,
        label=data.label,
        comment=data.comment,
    )


async def update_concept(
    driver: AsyncDriver,
    concept_id: str,
    domain_id: str,
    data: OntologyConceptUpdate,
) -> OntologyConceptResponse | None:
    sets = []
    params: dict[str, Any] = {"id": concept_id, "domain_id": domain_id}
    if data.uri is not None:
        sets.append("c.uri = $uri")
        params["uri"] = data.uri
    if data.label is not None:
        sets.append("c.label = $label")
        params["label"] = data.label
    if data.comment is not None:
        sets.append("c.comment = $comment")
        params["comment"] = data.comment
    if not sets:
        return await get_concept(driver, concept_id, domain_id)
    async with driver.session() as session:
        result = await session.run(
            f"MATCH (c:OWLClass {{id: $id, domain_id: $domain_id}}) SET {', '.join(sets)} RETURN c",
            **params,
        )
        record = await result.single()
        if not record:
            return None
        return _row_to_concept(dict(record))


async def delete_concept(driver: AsyncDriver, concept_id: str, domain_id: str) -> bool:
    async with driver.session() as session:
        # Delete associated properties too
        await session.run(
            "MATCH (p:OWLProperty {domain_id: $domain_id}) "
            "WHERE p.source_class_id = $id OR p.target_class_id = $id DETACH DELETE p",
            id=concept_id,
            domain_id=domain_id,
        )
        result = await session.run(
            "MATCH (c:OWLClass {id: $id, domain_id: $domain_id}) DETACH DELETE c RETURN count(c) AS cnt",
            id=concept_id,
            domain_id=domain_id,
        )
        record = await result.single()
        return bool(record and record["cnt"] > 0)


async def get_concept(
    driver: AsyncDriver,
    concept_id: str,
    domain_id: str,
) -> OntologyConceptResponse | None:
    async with driver.session() as session:
        result = await session.run(
            "MATCH (c:OWLClass {id: $id, domain_id: $domain_id}) RETURN c",
            id=concept_id,
            domain_id=domain_id,
        )
        record = await result.single()
        if not record:
            return None
        return _row_to_concept(dict(record))


async def list_concepts(driver: AsyncDriver, domain_id: str) -> list[OntologyConceptResponse]:
    async with driver.session() as session:
        result = await session.run(
            "MATCH (c:OWLClass {domain_id: $domain_id}) RETURN c ORDER BY c.label",
            domain_id=domain_id,
        )
        records = await result.data()
    return [_row_to_concept(r) for r in records]


# ─────────────────────────── Property CRUD (Neo4j) ────────────────────────────

async def create_property(
    driver: AsyncDriver,
    domain_id: str,
    data: OntologyPropertyCreate,
) -> OntologyPropertyResponse:
    prop_id = str(uuid.uuid4())
    async with driver.session() as session:
        await session.run(
            """
            CREATE (p:OWLProperty {
                id: $id,
                domain_id: $domain_id,
                uri: $uri,
                label: $label,
                property_type: $property_type,
                source_class_id: $source_class_id,
                target_class_id: $target_class_id,
                comment: $comment
            })
            """,
            id=prop_id,
            domain_id=domain_id,
            uri=data.uri,
            label=data.label,
            property_type=data.property_type,
            source_class_id=data.source_class_id,
            target_class_id=data.target_class_id,
            comment=data.comment,
        )
    return OntologyPropertyResponse(
        id=prop_id,
        domain_id=domain_id,
        uri=data.uri,
        label=data.label,
        property_type=data.property_type,
        source_class_id=data.source_class_id,
        target_class_id=data.target_class_id,
        comment=data.comment,
    )


async def delete_property(driver: AsyncDriver, prop_id: str, domain_id: str) -> bool:
    async with driver.session() as session:
        result = await session.run(
            "MATCH (p:OWLProperty {id: $id, domain_id: $domain_id}) DELETE p RETURN count(p) AS cnt",
            id=prop_id,
            domain_id=domain_id,
        )
        record = await result.single()
        return bool(record and record["cnt"] > 0)


async def list_properties(driver: AsyncDriver, domain_id: str) -> list[OntologyPropertyResponse]:
    async with driver.session() as session:
        result = await session.run(
            "MATCH (p:OWLProperty {domain_id: $domain_id}) RETURN p ORDER BY p.label",
            domain_id=domain_id,
        )
        records = await result.data()
    return [_row_to_property(r) for r in records]


# ──────────────────────────── Full ontology retrieval ─────────────────────────

async def get_ontology(driver: AsyncDriver, domain_id: str) -> OntologyResponse:
    concepts = await list_concepts(driver, domain_id)
    properties = await list_properties(driver, domain_id)
    return OntologyResponse(domain_id=domain_id, concepts=concepts, properties=properties)


# ──────────────────────────── OWL import/export ───────────────────────────────

async def import_owl(driver: AsyncDriver, domain_id: str, owl_bytes: bytes, fmt: str = "xml") -> OntologyResponse:
    """Parse OWL file and persist concepts/properties to Neo4j."""
    g = Graph()
    g.parse(io.BytesIO(owl_bytes), format=fmt)

    # Collect classes
    class_map: dict[str, str] = {}  # uri → id
    for cls_uri in g.subjects(RDF.type, OWL.Class):
        if not str(cls_uri).startswith("http"):
            continue
        uri_str = str(cls_uri)
        label = g.value(cls_uri, RDFS.label)
        comment = g.value(cls_uri, RDFS.comment)
        concept = await create_concept(
            driver,
            domain_id,
            OntologyConceptCreate(
                uri=uri_str,
                label=str(label) if label else uri_str.split("/")[-1].split("#")[-1],
                comment=str(comment) if comment else None,
            ),
        )
        class_map[uri_str] = concept.id

    # Collect object properties
    for prop_uri in g.subjects(RDF.type, OWL.ObjectProperty):
        uri_str = str(prop_uri)
        label = g.value(prop_uri, RDFS.label)
        comment = g.value(prop_uri, RDFS.comment)
        domain_val = g.value(prop_uri, RDFS.domain)
        range_val = g.value(prop_uri, RDFS.range)
        src_id = class_map.get(str(domain_val)) if domain_val else None
        tgt_id = class_map.get(str(range_val)) if range_val else None
        if src_id and tgt_id:
            await create_property(
                driver,
                domain_id,
                OntologyPropertyCreate(
                    uri=uri_str,
                    label=str(label) if label else uri_str.split("/")[-1].split("#")[-1],
                    property_type="ObjectProperty",
                    source_class_id=src_id,
                    target_class_id=tgt_id,
                    comment=str(comment) if comment else None,
                ),
            )

    return await get_ontology(driver, domain_id)


async def export_owl(driver: AsyncDriver, domain_id: str) -> bytes:
    """Serialize domain ontology to OWL/XML format (visual data excluded)."""
    onto = await get_ontology(driver, domain_id)
    g = Graph()
    NS = Namespace(f"http://km.local/ontology/{domain_id}#")
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("km", NS)

    for c in onto.concepts:
        uri = URIRef(c.uri if c.uri.startswith("http") else str(NS[c.label.replace(" ", "_")]))
        g.add((uri, RDF.type, OWL.Class))
        g.add((uri, RDFS.label, Literal(c.label)))
        if c.comment:
            g.add((uri, RDFS.comment, Literal(c.comment)))

    concept_uri_map = {c.id: c.uri for c in onto.concepts}
    for p in onto.properties:
        puri = URIRef(p.uri if p.uri.startswith("http") else str(NS[p.label.replace(" ", "_")]))
        is_datatype = p.property_type == "DatatypeProperty"
        g.add((puri, RDF.type, OWL.DatatypeProperty if is_datatype else OWL.ObjectProperty))
        g.add((puri, RDFS.label, Literal(p.label)))
        if p.comment:
            g.add((puri, RDFS.comment, Literal(p.comment)))
        src_uri = concept_uri_map.get(p.source_class_id)
        if src_uri:
            g.add((puri, RDFS.domain, URIRef(src_uri)))
        if is_datatype:
            # target_class_id holds the XSD type URI for DatatypeProperties
            if p.target_class_id.startswith("http"):
                g.add((puri, RDFS.range, URIRef(p.target_class_id)))
        else:
            tgt_uri = concept_uri_map.get(p.target_class_id)
            if tgt_uri:
                g.add((puri, RDFS.range, URIRef(tgt_uri)))

    return g.serialize(format="xml").encode()


# ──────────────────────────── Diagram CRUD (PostgreSQL) ───────────────────────

async def create_diagram(db: AsyncSession, domain_id: str, data: DiagramCreate) -> OntologyDiagram:
    diagram = OntologyDiagram(
        domain_id=domain_id,
        name=data.name,
        nodes=[],
        edges=[],
        viewport={"x": 0, "y": 0, "zoom": 1},
    )
    db.add(diagram)
    await db.flush()
    await db.refresh(diagram)
    return diagram


async def get_diagram(db: AsyncSession, diagram_id: str) -> OntologyDiagram | None:
    result = await db.execute(select(OntologyDiagram).where(OntologyDiagram.id == diagram_id))
    return result.scalar_one_or_none()


async def list_diagrams(db: AsyncSession, domain_id: str) -> list[OntologyDiagram]:
    result = await db.execute(
        select(OntologyDiagram)
        .where(OntologyDiagram.domain_id == domain_id)
        .order_by(OntologyDiagram.created_at)
    )
    return list(result.scalars().all())


async def update_diagram(
    db: AsyncSession,
    diagram_id: str,
    domain_id: str,
    data: DiagramUpdate,
) -> OntologyDiagram | None:
    diagram = await get_diagram(db, diagram_id)
    if not diagram or str(diagram.domain_id) != domain_id:
        return None
    if data.name is not None:
        diagram.name = data.name
    if data.nodes is not None:
        diagram.nodes = data.nodes
    if data.edges is not None:
        diagram.edges = data.edges
    if data.viewport is not None:
        diagram.viewport = data.viewport
    await db.flush()
    await db.refresh(diagram)
    return diagram


async def delete_diagram(db: AsyncSession, diagram_id: str, domain_id: str) -> bool:
    diagram = await get_diagram(db, diagram_id)
    if not diagram or str(diagram.domain_id) != domain_id:
        return False
    await db.delete(diagram)
    await db.flush()
    return True


async def ensure_default_diagram(db: AsyncSession, domain_id: str) -> OntologyDiagram:
    """Create a default diagram if none exist for the domain."""
    diagrams = await list_diagrams(db, domain_id)
    if not diagrams:
        return await create_diagram(db, domain_id, DiagramCreate(name="Main Diagram"))
    return diagrams[0]
