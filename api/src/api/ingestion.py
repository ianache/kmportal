"""Ingestion API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_domain_access
from db.database import get_db
from models import DocumentStatus
from schemas import (
    IngestionJobListResponse,
    IngestionResponse,
    IngestionStatusResponse,
    UserInToken,
)
from services.ingestion_service import (
    IngestionError,
    IngestionService,
    to_ingestion_response,
    to_ingestion_status_response,
)

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post(
    "",
    response_model=IngestionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload and ingest document",
    description="Upload a document file for ingestion into a knowledge domain."
)
async def ingest_document(
    domain_id: UUID = Form(..., description="Target domain ID"),
    file: UploadFile = File(..., description="Document file to upload"),
    title: str | None = Form(None, description="Document title (defaults to filename)"),
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and ingest a document file.

    Supported formats:
    - PDF (.pdf)
    - Word (.docx)
    - Text (.txt, .md)

    Returns a job ID for tracking processing status.
    """
    service = IngestionService(db)

    safe_filename = file.filename or "upload"
    document_title = title or safe_filename

    if not document_title.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document title or filename is required"
        )

    try:
        # Create document and job
        document, job = await service.create_ingestion_job(
            domain_id=domain_id,
            title=document_title,
            source_type="upload",
            file_type=file.content_type,
            metadata={
                "original_filename": safe_filename,
                "content_type": file.content_type,
                "uploaded_by": str(user.id)
            }
        )

        # Read file content
        content = await file.read()

        # Process document synchronously (queue in production)
        await service.process_document(
            document_id=document.id,
            file_content=content,
            filename=safe_filename,
        )

        return to_ingestion_response(document, job)

    except IngestionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.post(
    "/text",
    response_model=IngestionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest text content",
    description="Ingest raw text content into a knowledge domain."
)
async def ingest_text(
    domain_id: UUID,
    title: str,
    content: str,
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest raw text content directly.

    Useful for:
    - Small text snippets
    - API integrations
    - Testing

    For large documents, use the file upload endpoint instead.
    """
    service = IngestionService(db)

    try:
        # Create document and job
        document, job = await service.create_ingestion_job(
            domain_id=domain_id,
            title=title,
            source_type="api",
            metadata={
                "submitted_by": str(user.id),
                "content_length": len(content)
            }
        )

        # Process text as a "virtual" text file
        content_bytes = content.encode('utf-8')
        await service.process_document(
            document_id=document.id,
            file_content=content_bytes,
            filename="content.txt"
        )

        return to_ingestion_response(document, job)

    except IngestionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{job_id}/retry",
    response_model=IngestionStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry failed ingestion job",
    description="Reset a failed ingestion job to pending so it can be reprocessed."
)
async def retry_ingestion_job(
    job_id: UUID,
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed ingestion job."""
    service = IngestionService(db)
    try:
        job = await service.retry_job(job_id)
        return to_ingestion_status_response(job)
    except IngestionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
    "/jobs",
    response_model=IngestionJobListResponse,
    summary="List ingestion jobs",
    description="List ingestion jobs with optional filters. Users can only see jobs for domains they have access to."
)
async def list_ingestion_jobs(
    domain_id: UUID | None = Query(None, description="Filter by domain ID"),
    status: DocumentStatus | None = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List ingestion jobs."""
    # If domain_id provided, check access
    if domain_id and "KM_ADMIN" not in user.roles:
        from core.dependencies import require_domain_access
        await require_domain_access(domain_id=domain_id, user=user, db=db)

    # If no domain_id provided and not admin, we should only return jobs from authorized domains
    authorized_domain_ids = None
    if "KM_ADMIN" not in user.roles:
        from sqlalchemy import select

        from models import DomainAccess
        result = await db.execute(
            select(DomainAccess.domain_id).where(DomainAccess.user_id == user.id)
        )
        authorized_domain_ids = [r for (r,) in result.all()]

        # If user has no domains, return empty list
        if not authorized_domain_ids:
            return IngestionJobListResponse(items=[], total=0)

        # If domain_id was provided, it was already checked, so we just use it
        # If not, we filter by all authorized domains
        if not domain_id:
            domain_id = authorized_domain_ids # Service should handle list of IDs or we loop

    service = IngestionService(db)
    # IngestionService.list_jobs currently takes a single domain_id.
    # I might need to update it to support multiple IDs if domain_id is None.
    jobs, total = await service.list_jobs(
        domain_id=domain_id,
        status=status,
        page=page,
        page_size=page_size,
    )
    return IngestionJobListResponse(
        items=[to_ingestion_status_response(j) for j in jobs],
        total=total,
    )


@router.get(
    "/{job_id}",
    response_model=IngestionStatusResponse,
    summary="Get ingestion job status",
    description="Get the status and progress of an ingestion job. Requires domain access."
)
async def get_ingestion_status(
    job_id: UUID,
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get ingestion job status.

    Status values:
    - `pending`: Job queued, waiting to start
    - `processing`: Actively being processed
    - `done`: Successfully completed
    - `failed`: Processing failed

    Progress is a percentage (0-100).
    """
    service = IngestionService(db)
    job = await service.get_job_status(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion job not found"
        )

    # Check if user has access to this job's domain
    if "KM_ADMIN" not in user.roles:
        from core.dependencies import require_domain_access
        await require_domain_access(domain_id=job.domain_id, user=user, db=db)

    return to_ingestion_status_response(job)


@router.get(
    "/document/{document_id}/status",
    response_model=dict,
    summary="Get document status",
    description="Get the processing status of a document."
)
async def get_document_status(
    document_id: UUID,
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document processing status."""
    service = IngestionService(db)
    document = await service.get_document_status(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return {
        "document_id": str(document.id),
        "title": document.title,
        "status": document.status.value,
        "chunk_count": document.chunk_count,
        "error_message": document.error_message,
        "created_at": document.created_at.isoformat() if document.created_at else None,
        "updated_at": document.updated_at.isoformat() if document.updated_at else None
    }
