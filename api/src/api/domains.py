"""Domain API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from core.dependencies import (
    get_current_user,
    require_admin,
    require_domain_admin,
    require_domain_access
)
from schemas import (
    DomainCreate,
    DomainUpdate,
    DomainResponse,
    DomainListResponse,
    DomainAccessGrant,
    DomainAccessRevoke,
    DomainAccessResponse,
    PaginationParams,
    UserInToken,
)
from services.domain_service import (
    DomainService,
    to_domain_response,
    to_domain_access_response
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
    domain = await service.create_domain(domain_data, user.id)
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
    is_admin = "km-admin" in user.roles
    
    domains, total = await service.list_domains(
        user_id=user.id,
        is_admin=is_admin,
        page=pagination.page,
        page_size=pagination.page_size
    )
    
    pages = (total + pagination.page_size - 1) // pagination.page_size
    
    return DomainListResponse(
        items=[to_domain_response(d) for d in domains],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=pages
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
    response_model=List[DomainAccessResponse],
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