"""Ingestion API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from core.dependencies import get_current_user, require_domain_access
from schemas import (
    IngestionResponse,
    IngestionStatusResponse,
    UserInToken,
)
from services.ingestion_service import (
    IngestionService,
    to_ingestion_response,
    to_ingestion_status_response,
    IngestionError
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
    title: Optional[str] = Form(None, description="Document title (defaults to filename)"),
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
    
    # Use filename as title if not provided
    document_title = title or file.filename
    
    try:
        # Create document and job
        document, job = await service.create_ingestion_job(
            domain_id=domain_id,
            title=document_title,
            source_type="upload",
            file_type=file.content_type,
            metadata={
                "original_filename": file.filename,
                "content_type": file.content_type,
                "uploaded_by": str(user.id)
            }
        )
        
        # Read file content
        content = await file.read()
        
        # Process document (in production, this should be queued)
        # For now, process synchronously
        await service.process_document(
            document_id=document.id,
            file_content=content,
            filename=file.filename
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


@router.get(
    "/{job_id}",
    response_model=IngestionStatusResponse,
    summary="Get ingestion job status",
    description="Get the status and progress of an ingestion job."
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
    
    # TODO: Check if user has access to this job's domain
    
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