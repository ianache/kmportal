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
    OntologyBatchPayload,
    OntologyBatchResponse,
    ConceptBatchOperation,
    PropertyBatchOperation,
    DiagramBatchOperation,
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
        metadata={"comment": data.comment} if data.comment else None,
        subclass_of=data.subclass_of or [],
        equivalent_to=data.equivalent_to or [],
        restrictions=data.restrictions or [],
        annotations=data.annotations or {},
    )
    await adapter.upsert_class(info)
    return {
        "id": concept_id,
        "domain_id": domain_id,
        "uri": data.uri,
        "label": data.label,
        "comment": data.comment,
        "subclass_of": info.subclass_of,
        "equivalent_to": info.equivalent_to,
        "restrictions": info.restrictions,
        "annotations": info.annotations,
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
        metadata={"comment": data.comment} if data.comment is not None else {"comment": existing.get("comment")},
        subclass_of=data.subclass_of if data.subclass_of is not None else existing.get("subclass_of", []),
        equivalent_to=data.equivalent_to if data.equivalent_to is not None else existing.get("equivalent_to", []),
        restrictions=data.restrictions if data.restrictions is not None else existing.get("restrictions", []),
        annotations=data.annotations if data.annotations is not None else existing.get("annotations", {}),
    )
    await adapter.upsert_class(info)
    return {
        "id": concept_id,
        "domain_id": domain_id,
        "uri": info.uri,
        "label": info.label,
        "comment": data.comment if data.comment is not None else existing.get("comment"),
        "subclass_of": info.subclass_of,
        "equivalent_to": info.equivalent_to,
        "restrictions": info.restrictions,
        "annotations": info.annotations,
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
    """
    Merge-import an OWL/XML or Turtle file into an existing domain ontology.

    Strategy: merge by URI.
    - Classes/properties with a URI already in the domain → update (same internal id).
    - Classes/properties with a new URI → create (new uuid4 id).
    - Classes/properties NOT in the file → untouched.
    """
    import re
    import uuid as _uuid
    from rdflib import Graph, URIRef, BNode
    from rdflib.namespace import OWL, RDFS, RDF, Namespace

    KM = Namespace("http://km.local/ontology#")

    # ── 1. Parse ──────────────────────────────────────────────────────────────
    rdflib_fmt = "turtle" if fmt == "ttl" else "xml"
    g = Graph()
    try:
        g.parse(data=content, format=rdflib_fmt)
    except Exception as exc:
        raise ValueError(f"Cannot parse file as {fmt}: {exc}") from exc

    # ── 2. Load existing ontology to build URI→id maps ────────────────────────
    existing = await get_ontology(driver, domain_id)
    uri_to_concept_id: dict[str, str] = {c["uri"]: c["id"] for c in existing["concepts"] if c.get("uri")}
    uri_to_prop_id: dict[str, str]    = {p["uri"]: p["id"] for p in existing["properties"] if p.get("uri")}

    adapter = Neo4jAdapter(driver)
    concepts_created = 0
    concepts_updated = 0
    properties_created = 0
    properties_updated = 0
    errors: list[str] = []

    # ── 3. First pass: assign IDs to all classes in the file ─────────────────
    # Build uri→id for classes IN the file (may be new or existing).
    file_class_ids: dict[str, str] = {}
    for class_uri in g.subjects(RDF.type, OWL.Class):
        if not isinstance(class_uri, URIRef):
            continue
        uri_str = str(class_uri)
        file_class_ids[uri_str] = uri_to_concept_id.get(uri_str) or str(_uuid.uuid4())

    # Merge maps so cross-references from file can resolve to existing IDs too
    all_class_ids = {**uri_to_concept_id, **file_class_ids}

    # ── 4. Upsert classes ─────────────────────────────────────────────────────
    for class_uri in g.subjects(RDF.type, OWL.Class):
        if not isinstance(class_uri, URIRef):
            continue
        uri_str = str(class_uri)
        concept_id = file_class_ids[uri_str]
        is_new = uri_str not in uri_to_concept_id

        # Label: rdfs:label preferred, fallback to local name
        label_node = g.value(class_uri, RDFS.label)
        label = str(label_node) if label_node else (uri_str.split("#")[-1].split("/")[-1] or uri_str)

        # Comment
        comment_node = g.value(class_uri, RDFS.comment)
        comment = str(comment_node) if comment_node else None

        # subclass_of: only URIRef parents (skip blank node restrictions)
        subclass_ids: list[str] = []
        for parent in g.objects(class_uri, RDFS.subClassOf):
            if isinstance(parent, URIRef):
                pid = all_class_ids.get(str(parent))
                if pid:
                    subclass_ids.append(pid)

        # equivalent_to
        equiv_ids: list[str] = []
        for equiv in g.objects(class_uri, OWL.equivalentClass):
            if isinstance(equiv, URIRef):
                eid = all_class_ids.get(str(equiv))
                if eid:
                    equiv_ids.append(eid)

        # Restrictions (blank node pattern)
        restrictions: list[dict] = []
        for obj in g.objects(class_uri, RDFS.subClassOf):
            if not isinstance(obj, BNode):
                continue
            if (obj, RDF.type, OWL.Restriction) not in g:
                continue
            on_prop = g.value(obj, OWL.onProperty)
            if not on_prop:
                continue
            prop_uri_str = str(on_prop)
            # Resolve property URI to internal id (existing or file)
            prop_id = uri_to_prop_id.get(prop_uri_str)
            if not prop_id:
                continue  # property not yet imported; skip restriction silently
            if g.value(obj, OWL.someValuesFrom) is not None:
                r_type = "some"
            elif g.value(obj, OWL.allValuesFrom) is not None:
                r_type = "all"
            elif g.value(obj, OWL.minCardinality) is not None:
                r_type = "cardinality"
            else:
                continue
            restrictions.append({"property_id": prop_id, "restriction_type": r_type})

        # Annotations (owl:AnnotationProperty triples on this class)
        annotations: dict[str, str] = {}
        for pred, obj in g.predicate_objects(class_uri):
            if not isinstance(pred, URIRef):
                continue
            if (pred, RDF.type, OWL.AnnotationProperty) not in g:
                continue
            key = str(pred).split("#")[-1].split("/")[-1]
            # Normalize km:hasKey back to the canonical annotation key
            if str(pred) == str(KM.hasKey):
                annotations["owl:hasKey"] = str(obj)
            else:
                annotations[key] = str(obj)

        try:
            await adapter.upsert_class(OWLClassInfo(
                id=concept_id,
                label=label,
                uri=uri_str,
                domain_id=domain_id,
                metadata={"comment": comment},
                subclass_of=subclass_ids,
                equivalent_to=equiv_ids,
                restrictions=restrictions,
                annotations=annotations,
            ))
            if is_new:
                concepts_created += 1
                uri_to_concept_id[uri_str] = concept_id  # make available for properties pass
            else:
                concepts_updated += 1
        except Exception as exc:
            errors.append(f"Class {uri_str}: {exc}")

    # Rebuild merged map after class upserts
    all_class_ids = {**uri_to_concept_id, **file_class_ids}

    # ── 5. First pass for properties: assign IDs ──────────────────────────────
    file_prop_ids: dict[str, str] = {}
    for prop_type in (OWL.ObjectProperty, OWL.DatatypeProperty):
        for prop_uri in g.subjects(RDF.type, prop_type):
            if not isinstance(prop_uri, URIRef):
                continue
            uri_str = str(prop_uri)
            file_prop_ids[uri_str] = uri_to_prop_id.get(uri_str) or str(_uuid.uuid4())

    # ── 6. Upsert properties ──────────────────────────────────────────────────
    for prop_type in (OWL.ObjectProperty, OWL.DatatypeProperty):
        for prop_uri in g.subjects(RDF.type, prop_type):
            if not isinstance(prop_uri, URIRef):
                continue
            uri_str = str(prop_uri)
            prop_id = file_prop_ids[uri_str]
            is_new = uri_str not in uri_to_prop_id
            p_type = "DatatypeProperty" if prop_type == OWL.DatatypeProperty else "ObjectProperty"

            label_node = g.value(prop_uri, RDFS.label)
            label = str(label_node) if label_node else (uri_str.split("#")[-1].split("/")[-1] or uri_str)

            comment_node = g.value(prop_uri, RDFS.comment)
            comment = str(comment_node) if comment_node else None

            domain_uri = g.value(prop_uri, RDFS.domain)
            source_id = all_class_ids.get(str(domain_uri)) if domain_uri else None

            range_uri = g.value(prop_uri, RDFS.range)
            target_id: str | None = None
            if range_uri:
                target_id = all_class_ids.get(str(range_uri)) or str(range_uri)

            if not source_id:
                errors.append(f"Property {uri_str}: source class not found, skipped")
                continue

            try:
                await adapter.upsert_property(OWLPropertyInfo(
                    id=prop_id,
                    label=label,
                    uri=uri_str,
                    property_type=p_type,
                    domain_id=domain_id,
                    source_class_id=source_id,
                    target_class_id=target_id or "",
                    metadata={"comment": comment},
                ))
                if is_new:
                    properties_created += 1
                else:
                    properties_updated += 1
            except Exception as exc:
                errors.append(f"Property {uri_str}: {exc}")

    # ── 7. Return result ──────────────────────────────────────────────────────
    updated_ontology = await get_ontology(driver, domain_id)
    return {
        "concepts_created": concepts_created,
        "concepts_updated": concepts_updated,
        "properties_created": properties_created,
        "properties_updated": properties_updated,
        "errors": errors,
        "ontology": updated_ontology,
    }


async def export_owl(driver, domain_id: str, fmt: str = "owl") -> bytes:
    import re
    from rdflib import Graph, URIRef, Literal, Namespace, BNode, RDF, RDFS, OWL, XSD

    data = await get_ontology(driver, domain_id)
    concepts = data["concepts"]
    properties = data["properties"]

    g = Graph()
    KM = Namespace("http://km.local/ontology#")
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("rdf", RDF)
    g.bind("xsd", XSD)
    g.bind("km", KM)

    ontology_uri = URIRef(f"http://km.local/ontology/{domain_id}")
    g.add((ontology_uri, RDF.type, OWL.Ontology))

    # Build id → URI maps for reference resolution
    concept_uri_map: dict[str, str] = {}
    for concept in concepts:
        uri = concept["uri"] or f"http://km.local/ontology#{concept['label'].replace(' ', '_')}"
        concept_uri_map[concept["id"]] = uri

    property_uri_map: dict[str, str] = {}
    for prop in properties:
        p_uri = prop["uri"] or f"http://km.local/ontology#{prop['label'].replace(' ', '_')}"
        property_uri_map[prop["id"]] = p_uri

    _RESTRICTION_QUANTIFIER = {
        "some": OWL.someValuesFrom,
        "all": OWL.allValuesFrom,
    }

    # OWL Classes
    for concept in concepts:
        class_ref = URIRef(concept_uri_map[concept["id"]])
        g.add((class_ref, RDF.type, OWL.Class))
        g.add((class_ref, RDFS.label, Literal(concept["label"])))
        if concept.get("comment"):
            g.add((class_ref, RDFS.comment, Literal(concept["comment"])))
        for parent_id in concept.get("subclass_of", []):
            if parent_id in concept_uri_map:
                g.add((class_ref, RDFS.subClassOf, URIRef(concept_uri_map[parent_id])))
        for equiv_id in concept.get("equivalent_to", []):
            if equiv_id in concept_uri_map:
                g.add((class_ref, OWL.equivalentClass, URIRef(concept_uri_map[equiv_id])))

        # Property restrictions → anonymous owl:Restriction blank nodes
        for r in concept.get("restrictions") or []:
            prop_id = r.get("property_id", "")
            r_type = r.get("restriction_type", "some")
            if not prop_id or prop_id not in property_uri_map:
                continue
            restr = BNode()
            g.add((restr, RDF.type, OWL.Restriction))
            g.add((restr, OWL.onProperty, URIRef(property_uri_map[prop_id])))
            if r_type == "cardinality":
                g.add((restr, OWL.minCardinality, Literal(1, datatype=XSD.nonNegativeInteger)))
            else:
                quantifier = _RESTRICTION_QUANTIFIER.get(r_type, OWL.someValuesFrom)
                g.add((restr, quantifier, OWL.Thing))
            g.add((class_ref, RDFS.subClassOf, restr))

        # Custom annotations and owl:hasKey flag
        annotations = concept.get("annotations") or {}
        for ann_key, ann_val in annotations.items():
            if ann_key == "owl:hasKey":
                # Emit as a dedicated KM annotation property
                has_key_prop = KM.hasKey
                g.add((has_key_prop, RDF.type, OWL.AnnotationProperty))
                g.add((class_ref, has_key_prop, Literal("true")))
            else:
                key_slug = re.sub(r"[^\w.-]", "_", ann_key)
                ann_prop = URIRef(f"http://km.local/ontology#{key_slug}")
                g.add((ann_prop, RDF.type, OWL.AnnotationProperty))
                g.add((class_ref, ann_prop, Literal(ann_val)))

    # OWL Properties
    for prop in properties:
        prop_ref = URIRef(property_uri_map[prop["id"]])
        owl_type = OWL.DatatypeProperty if prop["property_type"] == "DatatypeProperty" else OWL.ObjectProperty
        g.add((prop_ref, RDF.type, owl_type))
        g.add((prop_ref, RDFS.label, Literal(prop["label"])))
        if prop.get("comment"):
            g.add((prop_ref, RDFS.comment, Literal(prop["comment"])))
        source_id = prop.get("source_class_id")
        if source_id and source_id in concept_uri_map:
            g.add((prop_ref, RDFS.domain, URIRef(concept_uri_map[source_id])))
        target_id = prop.get("target_class_id")
        if target_id:
            if target_id.startswith("http://") or target_id.startswith("https://"):
                g.add((prop_ref, RDFS.range, URIRef(target_id)))
            elif target_id in concept_uri_map:
                g.add((prop_ref, RDFS.range, URIRef(concept_uri_map[target_id])))

    if fmt == "ttl":
        result = g.serialize(format="turtle")
        return result.encode("utf-8") if isinstance(result, str) else result
    return g.serialize(format="xml").encode("utf-8")


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
    try:
        diagram_uuid = uuid.UUID(diagram_id)
    except ValueError:
        return None
    result = await db.execute(
        select(OntologyDiagram).where(OntologyDiagram.id == diagram_uuid)
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


# ──────────────────────────── Batch Operations ───────────────────────────────

async def save_ontology_batch(
    driver,
    db: AsyncSession,
    domain_id: str,
    payload: OntologyBatchPayload
) -> OntologyBatchResponse:
    """
    Execute batch operations for ontology concepts, properties, and diagrams.
    All operations are executed in a transaction-like manner (best effort).
    """
    response = OntologyBatchResponse(success=True)
    adapter = Neo4jAdapter(driver)
    errors = []
    
    # Process concept operations
    for op in payload.concepts:
        try:
            if op.operation == 'create' and op.data:
                concept_id = str(uuid.uuid4())
                info = OWLClassInfo(
                    id=concept_id,
                    label=op.data.label,
                    uri=op.data.uri,
                    domain_id=domain_id,
                    metadata={"comment": op.data.comment} if op.data.comment else None,
                    subclass_of=op.data.subclass_of or [],
                    equivalent_to=op.data.equivalent_to or [],
                    restrictions=op.data.restrictions or [],
                    annotations=op.data.annotations or {},
                )
                await adapter.upsert_class(info)
                response.concepts_created.append(concept_id)

            elif op.operation == 'update' and op.id and op.data:
                current = await adapter.get_ontology(domain_id)
                existing = next((c for c in current["concepts"] if c["id"] == op.id), None)
                if existing:
                    info = OWLClassInfo(
                        id=op.id,
                        label=op.data.label if op.data.label else existing["label"],
                        uri=op.data.uri if op.data.uri else existing["uri"],
                        domain_id=domain_id,
                        metadata={"comment": op.data.comment} if op.data.comment is not None else {"comment": existing.get("comment")},
                        subclass_of=op.data.subclass_of if op.data.subclass_of is not None else existing.get("subclass_of", []),
                        equivalent_to=op.data.equivalent_to if op.data.equivalent_to is not None else existing.get("equivalent_to", []),
                        restrictions=op.data.restrictions if op.data.restrictions is not None else existing.get("restrictions", []),
                        annotations=op.data.annotations if op.data.annotations is not None else existing.get("annotations", {}),
                    )
                    await adapter.upsert_class(info)
                    response.concepts_updated.append(op.id)
                else:
                    errors.append(f"Concept {op.id} not found for update")
                    
            elif op.operation == 'delete' and op.id:
                deleted = await adapter.delete_class(op.id, domain_id)
                if deleted:
                    response.concepts_deleted.append(op.id)
                else:
                    errors.append(f"Concept {op.id} not found for deletion")
                    
        except Exception as e:
            errors.append(f"Concept operation failed: {str(e)}")
            logger.error(f"Batch concept operation failed: {e}", exc_info=True)
    
    # Process property operations
    for op in payload.properties:
        try:
            if op.operation == 'create' and op.data:
                prop_id = str(uuid.uuid4())
                info = OWLPropertyInfo(
                    id=prop_id,
                    label=op.data.label,
                    uri=op.data.uri,
                    property_type=op.data.property_type,
                    domain_id=domain_id,
                    source_class_id=op.data.source_class_id,
                    target_class_id=op.data.target_class_id,
                    metadata={"comment": op.data.comment} if op.data.comment else None
                )
                await adapter.upsert_property(info)
                response.properties_created.append(prop_id)
                
            elif op.operation == 'update' and op.id and op.data:
                current = await adapter.get_ontology(domain_id)
                existing = next((p for p in current["properties"] if p["id"] == op.id), None)
                if existing:
                    info = OWLPropertyInfo(
                        id=op.id,
                        label=op.data.label if op.data.label else existing["label"],
                        uri=existing["uri"],
                        property_type=existing["property_type"],
                        domain_id=domain_id,
                        source_class_id=existing["source_class_id"],
                        target_class_id=op.data.target_class_id if op.data.target_class_id else existing["target_class_id"],
                        metadata={"comment": op.data.comment} if op.data.comment is not None else {"comment": existing.get("comment")}
                    )
                    await adapter.upsert_property(info)
                    response.properties_updated.append(op.id)
                else:
                    errors.append(f"Property {op.id} not found for update")
                    
            elif op.operation == 'delete' and op.id:
                deleted = await adapter.delete_property(op.id, domain_id)
                if deleted:
                    response.properties_deleted.append(op.id)
                else:
                    errors.append(f"Property {op.id} not found for deletion")
                    
        except Exception as e:
            errors.append(f"Property operation failed: {str(e)}")
            logger.error(f"Batch property operation failed: {e}", exc_info=True)
    
    # Process diagram operations
    for op in payload.diagrams:
        try:
            if op.operation == 'create' and op.data:
                diagram = OntologyDiagram(
                    domain_id=uuid.UUID(domain_id),
                    name=op.data.name or "Untitled",
                    nodes=op.data.nodes or [],
                    edges=op.data.edges or [],
                    viewport=op.data.viewport or {"x": 0, "y": 0, "zoom": 1}
                )
                db.add(diagram)
                await db.commit()
                await db.refresh(diagram)
                response.diagrams_created.append(str(diagram.id))
                
            elif op.operation == 'update' and op.id and op.data:
                diagram = await get_diagram(db, op.id)
                if diagram and str(diagram.domain_id) == domain_id:
                    if op.data.name is not None:
                        diagram.name = op.data.name
                    if op.data.nodes is not None:
                        diagram.nodes = op.data.nodes
                    if op.data.edges is not None:
                        diagram.edges = op.data.edges
                    if op.data.viewport is not None:
                        diagram.viewport = op.data.viewport
                    await db.commit()
                    await db.refresh(diagram)
                    response.diagrams_updated.append(op.id)
                else:
                    errors.append(f"Diagram {op.id} not found for update")
                    
            elif op.operation == 'delete' and op.id:
                diagram = await get_diagram(db, op.id)
                if diagram and str(diagram.domain_id) == domain_id:
                    await db.delete(diagram)
                    await db.commit()
                    response.diagrams_deleted.append(op.id)
                else:
                    errors.append(f"Diagram {op.id} not found for deletion")
                    
        except Exception as e:
            errors.append(f"Diagram operation failed: {str(e)}")
            logger.error(f"Batch diagram operation failed: {e}", exc_info=True)
    
    # Set final response state
    response.errors = errors
    response.success = len(errors) == 0
    
    return response
