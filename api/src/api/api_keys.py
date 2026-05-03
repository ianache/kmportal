"""API Key API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from core.dependencies import get_current_user
from schemas import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyCreateResponse,
    APIKeyListResponse,
    PaginationParams,
    UserInToken,
)
from services.api_key_service import (
    APIKeyService,
    to_api_key_response
)

router = APIRouter(prefix="/v1/api-keys", tags=["API Keys"])


@router.post(
    "",
    response_model=APIKeyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
    description="Create a new API key for external integrations."
)
async def create_api_key(
    key_data: APIKeyCreate,
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key."""
    service = APIKeyService(db)
    api_key, plain_key = await service.create_api_key(key_data, user.id)
    
    response = to_api_key_response(api_key)
    return APIKeyCreateResponse(
        **response.model_dump(),
        key=plain_key  # Only returned on creation
    )


@router.get(
    "",
    response_model=APIKeyListResponse,
    summary="List API keys",
    description="List all API keys created by the current user."
)
async def list_api_keys(
    pagination: PaginationParams = Depends(),
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List API keys."""
    service = APIKeyService(db)
    keys, total = await service.list_api_keys(
        created_by=user.id,
        page=pagination.page,
        page_size=pagination.page_size
    )
    
    pages = (total + pagination.page_size - 1) // pagination.page_size
    
    return APIKeyListResponse(
        items=[to_api_key_response(k) for k in keys],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=pages
    )


@router.get(
    "/{key_id}",
    response_model=APIKeyResponse,
    summary="Get API key",
    description="Get API key details by ID."
)
async def get_api_key(
    key_id: UUID,
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get API key by ID."""
    service = APIKeyService(db)
    api_key = await service.get_api_key(key_id)
    
    if not api_key or api_key.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return to_api_key_response(api_key)


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke API key",
    description="Revoke (deactivate) an API key."
)
async def revoke_api_key(
    key_id: UUID,
    user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke API key."""
    service = APIKeyService(db)
    revoked = await service.revoke_api_key(key_id, user.id)
    
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return None