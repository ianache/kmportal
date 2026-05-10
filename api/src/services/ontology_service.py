"""Ontology service layer: manages OWL concepts (Neo4j) and diagrams (SQL)."""

import logging
import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.graph.neo4j_adapter import Neo4jAdapter
from ports.graph import OWLClassInfo, OWLPropertyInfo, EntityInfo, RelationInfo
from models.base import OntologyDiagram
from schemas import (
    OntologyConceptCreate,
    OntologyConceptUpdate,
    OntologyPropertyCreate,
    OntologyPropertyUpdate,
    DiagramCreate,
    DiagramUpdate,
    ExtractionResult,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────── Ontology ────────────────────────────────────

async def get_ontology(driver, domain_id: str) -> dict[str, Any]:
    adapter = Neo4jAdapter(driver)
    return await adapter.get_ontology(domain_id)


async def create_concept(driver, domain_id: str, data: OntologyConceptCreate) -> dict[str, Any]:
    adapter = Neo4jAdapter(driver)
    concept_id = str(uuid.uuid4())
    info = OWLClassInfo(
        id=concept_id,
        label=data.label,
        uri=data.uri,
        domain_id=domain_id,
        metadata={"comment": data.comment} if data.comment else None
    )
    await adapter.upsert_class(info)
    return {
        "id": concept_id,
        "domain_id": domain_id,
        "uri": data.uri,
        "label": data.label,
        "comment": data.comment
    }


async def update_concept(driver, concept_id: str, domain_id: str, data: OntologyConceptUpdate) -> dict[str, Any] | None:
    adapter = Neo4jAdapter(driver)
    current = await adapter.get_ontology(domain_id)
    existing = next((c for c in current["concepts"] if c["id"] == concept_id), None)
    if not existing:
        return None
    
    info = OWLClassInfo(
        id=concept_id,
        label=data.label if data.label is not None else existing["label"],
        uri=data.uri if data.uri is not None else existing["uri"],
        domain_id=domain_id,
        metadata={"comment": data.comment} if data.comment is not None else {"comment": existing.get("comment")}
    )
    await adapter.upsert_class(info)
    return {
        "id": concept_id,
        "domain_id": domain_id,
        "uri": info.uri,
        "label": info.label,
        "comment": data.comment if data.comment is not None else existing.get("comment")
    }


async def delete_concept(driver, concept_id: str, domain_id: str) -> bool:
    adapter = Neo4jAdapter(driver)
    return await adapter.delete_class(concept_id, domain_id)


async def create_property(driver, domain_id: str, data: OntologyPropertyCreate) -> dict[str, Any]:
    adapter = Neo4jAdapter(driver)
    prop_id = str(uuid.uuid4())
    info = OWLPropertyInfo(
        id=prop_id,
        label=data.label,
        uri=data.uri,
        property_type=data.property_type,
        domain_id=domain_id,
        source_class_id=data.source_class_id,
        target_class_id=data.target_class_id,
        metadata={"comment": data.comment} if data.comment else None
    )
    await adapter.upsert_property(info)
    return {
        "id": prop_id,
        "domain_id": domain_id,
        "uri": data.uri,
        "label": data.label,
        "property_type": data.property_type,
        "source_class_id": data.source_class_id,
        "target_class_id": data.target_class_id,
        "comment": data.comment
    }


async def update_property(driver, property_id: str, domain_id: str, data: OntologyPropertyUpdate) -> dict[str, Any] | None:
    adapter = Neo4jAdapter(driver)
    current = await adapter.get_ontology(domain_id)
    existing = next((p for p in current["properties"] if p["id"] == property_id), None)
    if not existing:
        return None
    
    info = OWLPropertyInfo(
        id=property_id,
        label=data.label if data.label is not None else existing["label"],
        uri=existing["uri"],
        property_type=existing["property_type"],
        domain_id=domain_id,
        source_class_id=existing["source_class_id"],
        target_class_id=data.target_class_id if data.target_class_id is not None else existing["target_class_id"],
        metadata={"comment": data.comment} if data.comment is not None else {"comment": existing.get("comment")}
    )
    await adapter.upsert_property(info)
    return {
        "id": property_id,
        "domain_id": domain_id,
        "uri": info.uri,
        "label": info.label,
        "property_type": info.property_type,
        "source_class_id": info.source_class_id,
        "target_class_id": info.target_class_id,
        "comment": data.comment if data.comment is not None else existing.get("comment")
    }


async def delete_property(driver, property_id: str, domain_id: str) -> bool:
    adapter = Neo4jAdapter(driver)
    return await adapter.delete_property(property_id, domain_id)


# ──────────────────────────────── Instances (ABox) ────────────────────────────

async def register_extracted_data(
    driver, 
    domain_id: str, 
    document_id: str, 
    extraction: Any # ExtractionResult
) -> None:
    """
    Register entities and relations extracted from a document.
    """
    adapter = Neo4jAdapter(driver)
    
    # 1. Register Entities
    # We use label as part of ID generation for now to handle simple entity resolution
    entity_label_to_id = {}
    
    for ent in extraction.entities:
        # Simple deterministic ID based on label and class for basic resolution
        import hashlib
        ent_id = hashlib.sha256(f"{ent.label}:{ent.class_id}".encode()).hexdigest()
        entity_label_to_id[ent.label] = ent_id
        
        info = EntityInfo(
            id=ent_id,
            label=ent.label,
            class_id=ent.class_id,
            domain_id=domain_id,
            document_id=document_id,
            metadata=ent.metadata
        )
        await adapter.upsert_entity(info)
    
    # 2. Register Relations
    for rel in extraction.relations:
        source_id = entity_label_to_id.get(rel.source_label)
        target_id = entity_label_to_id.get(rel.target_label)
        
        if source_id and target_id:
            info = RelationInfo(
                source_entity_id=source_id,
                target_entity_id=target_id,
                property_id=rel.property_id,
                domain_id=domain_id,
                metadata=rel.metadata
            )
            await adapter.upsert_relation(info)


async def import_owl(driver, domain_id: str, content: bytes, fmt: str) -> dict[str, Any]:
    # Placeholder for RDFLib parsing and batch registration
    return await get_ontology(driver, domain_id)


async def export_owl(driver, domain_id: str) -> bytes:
    # Placeholder for OWL export
    return b'<?xml version="1.0"?><rdf:RDF xmlns="http://km.local/ontology#"></rdf:RDF>'


# ───────────────────────────────── Diagrams ───────────────────────────────────

async def list_diagrams(db: AsyncSession, domain_id: str) -> list[OntologyDiagram]:
    result = await db.execute(
        select(OntologyDiagram).where(OntologyDiagram.domain_id == uuid.UUID(domain_id))
    )
    return list(result.scalars().all())


async def ensure_default_diagram(db: AsyncSession, domain_id: str) -> OntologyDiagram:
    domain_uuid = uuid.UUID(domain_id)
    result = await db.execute(
        select(OntologyDiagram).where(OntologyDiagram.domain_id == domain_uuid, OntologyDiagram.name == "Default")
    )
    diagram = result.scalar_one_or_none()
    
    if not diagram:
        diagram = OntologyDiagram(
            domain_id=domain_uuid,
            name="Default",
            nodes=[],
            edges=[],
            viewport={"x": 0, "y": 0, "zoom": 1}
        )
        db.add(diagram)
        await db.commit()
        await db.refresh(diagram)
    
    return diagram


async def create_diagram(db: AsyncSession, domain_id: str, data: DiagramCreate) -> OntologyDiagram:
    diagram = OntologyDiagram(
        domain_id=uuid.UUID(domain_id),
        name=data.name,
        nodes=[],
        edges=[],
        viewport={"x": 0, "y": 0, "zoom": 1}
    )
    db.add(diagram)
    await db.commit()
    await db.refresh(diagram)
    return diagram


async def get_diagram(db: AsyncSession, diagram_id: str) -> OntologyDiagram | None:
    result = await db.execute(
        select(OntologyDiagram).where(OntologyDiagram.id == uuid.UUID(diagram_id))
    )
    return result.scalar_one_or_none()


async def update_diagram(db: AsyncSession, diagram_id: str, domain_id: str, data: DiagramUpdate) -> OntologyDiagram | None:
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
        
    await db.commit()
    await db.refresh(diagram)
    return diagram


async def delete_diagram(db: AsyncSession, diagram_id: str, domain_id: str) -> bool:
    diagram = await get_diagram(db, diagram_id)
    if not diagram or str(diagram.domain_id) != domain_id:
        return False
        
    await db.delete(diagram)
    await db.commit()
    return True
