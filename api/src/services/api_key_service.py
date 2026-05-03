"""API Key service layer."""

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models import APIKey
from schemas import APIKeyCreate, APIKeyResponse
from core.auth import generate_api_key, hash_api_key


class APIKeyService:
    """Service for API Key operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_api_key(
        self,
        key_data: APIKeyCreate,
        created_by: UUID
    ) -> Tuple[APIKey, str]:
        """
        Create a new API key.
        
        Returns:
            Tuple of (APIKey object, plain key string)
            The plain key is only returned once on creation.
        """
        # Generate API key
        plain_key = generate_api_key()
        key_hash = hash_api_key(plain_key)
        
        # Create API key record
        api_key = APIKey(
            key_hash=key_hash,
            name=key_data.name,
            scopes=key_data.scopes,
            domain_ids=key_data.domain_ids,
            rate_limit=key_data.rate_limit,
            expires_at=key_data.expires_at,
            created_by=created_by
        )
        
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        
        return api_key, plain_key
    
    async def get_api_key(self, key_id: UUID) -> Optional[APIKey]:
        """Get API key by ID."""
        result = await self.db.execute(
            select(APIKey).where(APIKey.id == key_id)
        )
        return result.scalar_one_or_none()
    
    async def validate_api_key(self, plain_key: str) -> Optional[APIKey]:
        """Validate an API key and return the key object if valid."""
        key_hash = hash_api_key(plain_key)
        
        result = await self.db.execute(
            select(APIKey).where(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            return None
        
        # Check if expired
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        api_key.last_used_at = datetime.utcnow()
        await self.db.commit()
        
        return api_key
    
    async def list_api_keys(
        self,
        created_by: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[APIKey], int]:
        """List API keys created by user."""
        # Count total
        count_result = await self.db.execute(
            select(func.count(APIKey.id)).where(APIKey.created_by == created_by)
        )
        total = count_result.scalar()
        
        # Get paginated results
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(APIKey)
            .where(APIKey.created_by == created_by)
            .offset(offset)
            .limit(page_size)
        )
        
        return list(result.scalars().all()), total
    
    async def revoke_api_key(self, key_id: UUID, created_by: UUID) -> bool:
        """Revoke (deactivate) an API key."""
        result = await self.db.execute(
            select(APIKey).where(
                APIKey.id == key_id,
                APIKey.created_by == created_by
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            return False
        
        api_key.is_active = False
        await self.db.commit()
        
        return True


def to_api_key_response(api_key: APIKey) -> APIKeyResponse:
    """Convert APIKey model to APIKeyResponse schema."""
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        scopes=api_key.scopes,
        domain_ids=api_key.domain_ids,
        rate_limit=api_key.rate_limit,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        is_active=api_key.is_active
    )