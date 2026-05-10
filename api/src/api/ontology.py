"""Ontology API endpoints: OWL concepts (Neo4j) + diagram layouts (PostgreSQL)."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_domain_access
from db.database import get_db
from db.neo4j_client import get_neo4j
from schemas import (
    DiagramCreate,
    DiagramListResponse,
    DiagramResponse,
    DiagramUpdate,
    OntologyConceptCreate,
    OntologyConceptResponse,
    OntologyConceptUpdate,
    OntologyPropertyCreate,
    OntologyPropertyResponse,
    OntologyPropertyUpdate,
    OntologyResponse,
    UserInToken,
    OntologyBatchPayload,
    OntologyBatchResponse,
)
from services import ontology_service as svc

router = APIRouter(prefix="/domains", tags=["Ontology"])


# ──────────────────────────────── Ontology ────────────────────────────────────

@router.get(
    "/{domain_id}/ontology",
    response_model=OntologyResponse,
    summary="Get domain ontology",
)
async def get_ontology(
    domain_id: UUID,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    return await svc.get_ontology(driver, str(domain_id))


@router.post(
    "/{domain_id}/ontology/batch",
    response_model=OntologyBatchResponse,
    summary="Batch save ontology changes",
)
async def batch_save_ontology(
    domain_id: UUID,
    payload: OntologyBatchPayload,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
    db: AsyncSession = Depends(get_db),
):
    return await svc.save_ontology_batch(driver, db, str(domain_id), payload)


@router.post(
    "/{domain_id}/ontology/concepts",
    response_model=OntologyConceptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create OWL class",
)
async def create_concept(
    domain_id: UUID,
    data: OntologyConceptCreate,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    return await svc.create_concept(driver, str(domain_id), data)


@router.put(
    "/{domain_id}/ontology/concepts/{concept_id:path}",
    response_model=OntologyConceptResponse,
    summary="Update OWL class",
)
async def update_concept(
    domain_id: UUID,
    concept_id: str,
    data: OntologyConceptUpdate,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    result = await svc.update_concept(driver, concept_id, str(domain_id), data)
    if not result:
        raise HTTPException(status_code=404, detail="Concept not found")
    return result


@router.delete(
    "/{domain_id}/ontology/concepts/{concept_id:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete OWL class (cascades to properties)",
)
async def delete_concept(
    domain_id: UUID,
    concept_id: str,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    deleted = await svc.delete_concept(driver, concept_id, str(domain_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Concept not found")


@router.post(
    "/{domain_id}/ontology/properties",
    response_model=OntologyPropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create OWL property",
)
async def create_property(
    domain_id: UUID,
    data: OntologyPropertyCreate,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    return await svc.create_property(driver, str(domain_id), data)


@router.put(
    "/{domain_id}/ontology/properties/{property_id:path}",
    response_model=OntologyPropertyResponse,
    summary="Update OWL property label, range or comment",
)
async def update_property(
    domain_id: UUID,
    property_id: str,
    data: OntologyPropertyUpdate,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    result = await svc.update_property(driver, property_id, str(domain_id), data)
    if not result:
        raise HTTPException(status_code=404, detail="Property not found")
    return result


@router.delete(
    "/{domain_id}/ontology/properties/{property_id:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete OWL property",
)
async def delete_property(
    domain_id: UUID,
    property_id: str,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    deleted = await svc.delete_property(driver, property_id, str(domain_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Property not found")


@router.post(
    "/{domain_id}/ontology/import",
    response_model=OntologyResponse,
    summary="Import OWL/RDF file",
)
async def import_owl(
    domain_id: UUID,
    file: UploadFile = File(...),
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    content = await file.read()
    fmt = "turtle" if (file.filename or "").endswith(".ttl") else "xml"
    return await svc.import_owl(driver, str(domain_id), content, fmt)


@router.get(
    "/{domain_id}/ontology/export",
    summary="Export ontology as OWL/XML",
)
async def export_owl(
    domain_id: UUID,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
):
    owl_bytes = await svc.export_owl(driver, str(domain_id))
    return Response(
        content=owl_bytes,
        media_type="application/rdf+xml",
        headers={"Content-Disposition": f'attachment; filename="domain_{domain_id}.owl"'},
    )


# ───────────────────────────────── Diagrams ───────────────────────────────────

@router.get(
    "/{domain_id}/diagrams",
    response_model=DiagramListResponse,
    summary="List diagrams for domain",
)
async def list_diagrams(
    domain_id: UUID,
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db),
):
    items = await svc.list_diagrams(db, str(domain_id))
    if not items:
        default = await svc.ensure_default_diagram(db, str(domain_id))
        items = [default]
    return DiagramListResponse(items=items, total=len(items))


@router.post(
    "/{domain_id}/diagrams",
    response_model=DiagramResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create diagram",
)
async def create_diagram(
    domain_id: UUID,
    data: DiagramCreate,
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_diagram(db, str(domain_id), data)


@router.get(
    "/{domain_id}/diagrams/{diagram_id}",
    response_model=DiagramResponse,
    summary="Get diagram with layout",
)
async def get_diagram(
    domain_id: UUID,
    diagram_id: UUID,
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db),
):
    diagram = await svc.get_diagram(db, str(diagram_id))
    if not diagram or str(diagram.domain_id) != str(domain_id):
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diagram


@router.put(
    "/{domain_id}/diagrams/{diagram_id}",
    response_model=DiagramResponse,
    summary="Save diagram layout",
)
async def update_diagram(
    domain_id: UUID,
    diagram_id: UUID,
    data: DiagramUpdate,
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db),
):
    diagram = await svc.update_diagram(db, str(diagram_id), str(domain_id), data)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diagram


@router.delete(
    "/{domain_id}/diagrams/{diagram_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete diagram",
)
async def delete_diagram(
    domain_id: UUID,
    diagram_id: UUID,
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db),
):
    deleted = await svc.delete_diagram(db, str(diagram_id), str(domain_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Diagram not found")


# ──────────────────────────── Batch Operations ───────────────────────────────

@router.post(
    "/{domain_id}/ontology/batch",
    response_model=OntologyBatchResponse,
    summary="Batch save ontology changes",
)
async def batch_save_ontology(
    domain_id: UUID,
    data: OntologyBatchPayload,
    user: UserInToken = Depends(require_domain_access),
    driver=Depends(get_neo4j),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute batch operations for ontology changes.
    Processes concepts, properties, and diagrams in a single request.
    """
    return await svc.save_ontology_batch(driver, db, str(domain_id), data)
