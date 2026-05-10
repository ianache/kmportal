"""Domain API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_current_user,
    require_admin,
    require_domain_access,
    require_domain_admin,
)
from db.database import get_db
from models import DocumentStatus
from schemas import (
    DocumentListResponse,
    DomainAccessGrant,
    DomainAccessResponse,
    DomainAccessRevoke,
    DomainCreate,
    DomainListResponse,
    DomainResponse,
    DomainUpdate,
    PaginationParams,
    UserInToken,
)
from services.domain_service import (
    DomainService,
    to_document_response,
    to_domain_access_response,
    to_domain_response,
)

router = APIRouter(prefix="/domains", tags=["Domains"])


@router.post(
    "",
    response_model=DomainResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create domain",
    description="Create a new knowledge domain. Requires admin role."
)
async def create_domain(
    domain_data: DomainCreate,
    user: UserInToken = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new domain."""
    service = DomainService(db)
    domain = await service.create_domain(domain_data, user.id, user.full_name)
    return to_domain_response(domain)


@router.get(
    "",
    response_model=DomainListResponse,
    summary="List domains",
    description="List all domains accessible to the current user."
)
async def list_domains(
    pagination: PaginationParams = Depends(),
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List domains."""
    service = DomainService(db)
    is_admin = "KM_ADMIN" in user.roles

    try:
        domains, total = await service.list_domains(
            user_id=user.id,
            is_admin=is_admin,
            page=pagination.page,
            page_size=pagination.page_size
        )

        page_size = max(1, pagination.page_size)
        pages = (total + page_size - 1) // page_size if total > 0 else 1

        return DomainListResponse(
            items=[to_domain_response(d) for d in domains],
            total=total,
            page=pagination.page,
            page_size=page_size,
            pages=pages
        )
    except Exception as e:
        from core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"Failed to list domains: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list domains: {str(e)}"
        )


@router.get(
    "/{domain_id}",
    response_model=DomainResponse,
    summary="Get domain",
    description="Get domain by ID. Requires domain access."
)
async def get_domain(
    domain_id: UUID,
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db)
):
    """Get domain by ID."""
    service = DomainService(db)
    domain = await service.get_domain(domain_id)

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )

    return to_domain_response(domain)


@router.put(
    "/{domain_id}",
    response_model=DomainResponse,
    summary="Update domain",
    description="Update domain. Requires domain admin access."
)
async def update_domain(
    domain_id: UUID,
    domain_data: DomainUpdate,
    user: UserInToken = Depends(require_domain_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update domain."""
    service = DomainService(db)
    domain = await service.update_domain(domain_id, domain_data)

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )

    return to_domain_response(domain)


@router.delete(
    "/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete domain",
    description="Delete domain. Requires domain admin access."
)
async def delete_domain(
    domain_id: UUID,
    user: UserInToken = Depends(require_domain_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete domain."""
    service = DomainService(db)
    deleted = await service.delete_domain(domain_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )

    return None


# ==================== Domain Documents ====================

@router.get(
    "/{domain_id}/documents",
    response_model=DocumentListResponse,
    summary="List domain documents",
    description="List all documents in a domain. Requires domain access."
)
async def list_domain_documents(
    domain_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: DocumentStatus | None = Query(None, description="Filter by document status"),
    type: str | None = Query(None, description="Filter by source type (upload, api, etc.)"),
    q: str | None = Query(None, description="Search by title"),
    user: UserInToken = Depends(require_domain_access),
    db: AsyncSession = Depends(get_db)
):
    """List documents in a domain."""
    service = DomainService(db)
    documents, total = await service.list_documents(
        domain_id=domain_id,
        page=page,
        page_size=page_size,
        status=status,
        source_type=type,
        query=q,
    )

    pages = max(1, (total + page_size - 1) // page_size)

    return DocumentListResponse(
        items=[to_document_response(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


# ==================== Domain Access Management ====================

@router.post(
    "/{domain_id}/access",
    response_model=DomainAccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Grant domain access",
    description="Grant access to a user. Requires domain admin access."
)
async def grant_domain_access(
    domain_id: UUID,
    grant_data: DomainAccessGrant,
    user: UserInToken = Depends(require_domain_admin),
    db: AsyncSession = Depends(get_db)
):
    """Grant access to domain."""
    service = DomainService(db)
    access = await service.grant_access(domain_id, grant_data, user.id)
    return to_domain_access_response(access)


@router.delete(
    "/{domain_id}/access",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke domain access",
    description="Revoke access from a user. Requires domain admin access."
)
async def revoke_domain_access(
    domain_id: UUID,
    revoke_data: DomainAccessRevoke,
    user: UserInToken = Depends(require_domain_admin),
    db: AsyncSession = Depends(get_db)
):
    """Revoke access from domain."""
    service = DomainService(db)
    revoked = await service.revoke_access(domain_id, revoke_data.user_id)

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access grant not found"
        )

    return None


@router.get(
    "/{domain_id}/access",
    response_model=list[DomainAccessResponse],
    summary="List domain access grants",
    description="List all access grants for domain. Requires domain admin access."
)
async def list_domain_access(
    domain_id: UUID,
    user: UserInToken = Depends(require_domain_admin),
    db: AsyncSession = Depends(get_db)
):
    """List domain access grants."""
    service = DomainService(db)
    grants = await service.list_access_grants(domain_id)
    return [to_domain_access_response(g) for g in grants]
