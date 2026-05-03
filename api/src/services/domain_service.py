"""Domain service layer."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from models import Domain, DomainAccess, DomainAccessRole, User
from schemas import (
    DomainCreate,
    DomainUpdate,
    DomainResponse,
    DomainAccessGrant,
    DomainAccessResponse,
    UserResponse,
)


class DomainService:
    """Service for domain operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_domain(
        self,
        domain_data: DomainCreate,
        created_by: UUID
    ) -> Domain:
        """Create a new domain."""
        domain = Domain(
            name=domain_data.name,
            description=domain_data.description,
            embedding_model=domain_data.embedding_model,
            embedding_dimension=domain_data.embedding_dimension,
            created_by=created_by
        )
        
        self.db.add(domain)
        await self.db.commit()
        await self.db.refresh(domain)
        
        # Grant admin access to creator
        access = DomainAccess(
            user_id=created_by,
            domain_id=domain.id,
            role=DomainAccessRole.ADMIN,
            granted_by=created_by
        )
        self.db.add(access)
        await self.db.commit()
        
        return domain
    
    async def get_domain(self, domain_id: UUID) -> Optional[Domain]:
        """Get domain by ID."""
        result = await self.db.execute(
            select(Domain).where(Domain.id == domain_id)
        )
        return result.scalar_one_or_none()
    
    async def list_domains(
        self,
        user_id: UUID,
        is_admin: bool,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Domain], int]:
        """List domains accessible to user."""
        # Build query
        if is_admin:
            # Admins see all domains
            query = select(Domain)
            count_query = select(func.count(Domain.id))
        else:
            # Regular users see only domains they have access to
            query = (
                select(Domain)
                .join(DomainAccess)
                .where(DomainAccess.user_id == user_id)
            )
            count_query = (
                select(func.count(Domain.id))
                .join(DomainAccess)
                .where(DomainAccess.user_id == user_id)
            )
        
        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get paginated results
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        domains = result.scalars().all()
        
        return list(domains), total
    
    async def update_domain(
        self,
        domain_id: UUID,
        domain_data: DomainUpdate
    ) -> Optional[Domain]:
        """Update domain."""
        domain = await self.get_domain(domain_id)
        if not domain:
            return None
        
        if domain_data.name is not None:
            domain.name = domain_data.name
        if domain_data.description is not None:
            domain.description = domain_data.description
        
        await self.db.commit()
        await self.db.refresh(domain)
        
        return domain
    
    async def delete_domain(self, domain_id: UUID) -> bool:
        """Delete domain."""
        domain = await self.get_domain(domain_id)
        if not domain:
            return False
        
        await self.db.delete(domain)
        await self.db.commit()
        
        return True
    
    async def grant_access(
        self,
        domain_id: UUID,
        grant_data: DomainAccessGrant,
        granted_by: UUID
    ) -> DomainAccess:
        """Grant access to domain."""
        # Check if access already exists
        result = await self.db.execute(
            select(DomainAccess).where(
                DomainAccess.user_id == grant_data.user_id,
                DomainAccess.domain_id == domain_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing access
            existing.role = DomainAccessRole(grant_data.role)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        
        # Create new access
        access = DomainAccess(
            user_id=grant_data.user_id,
            domain_id=domain_id,
            role=DomainAccessRole(grant_data.role),
            granted_by=granted_by
        )
        
        self.db.add(access)
        await self.db.commit()
        await self.db.refresh(access)
        
        return access
    
    async def revoke_access(
        self,
        domain_id: UUID,
        user_id: UUID
    ) -> bool:
        """Revoke access from domain."""
        result = await self.db.execute(
            select(DomainAccess).where(
                DomainAccess.user_id == user_id,
                DomainAccess.domain_id == domain_id
            )
        )
        access = result.scalar_one_or_none()
        
        if not access:
            return False
        
        await self.db.delete(access)
        await self.db.commit()
        
        return True
    
    async def list_access_grants(
        self,
        domain_id: UUID
    ) -> List[DomainAccess]:
        """List all access grants for domain."""
        result = await self.db.execute(
            select(DomainAccess)
            .where(DomainAccess.domain_id == domain_id)
            .options(selectinload(DomainAccess.user))
        )
        return list(result.scalars().all())


def to_domain_response(domain: Domain) -> DomainResponse:
    """Convert Domain model to DomainResponse schema."""
    return DomainResponse(
        id=domain.id,
        name=domain.name,
        description=domain.description,
        embedding_model=domain.embedding_model,
        embedding_dimension=domain.embedding_dimension,
        created_by=domain.created_by,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        document_count=len(domain.documents) if domain.documents else 0
    )


def to_domain_access_response(access: DomainAccess) -> DomainAccessResponse:
    """Convert DomainAccess model to DomainAccessResponse schema."""
    return DomainAccessResponse(
        id=access.id,
        user_id=access.user_id,
        domain_id=access.domain_id,
        role=access.role.value,
        granted_at=access.granted_at,
        user=UserResponse(
            id=access.user.id,
            email=access.user.email,
            full_name=access.user.full_name,
            roles=access.user.roles,
            is_active=access.user.is_active,
            last_login=access.user.last_login,
            created_at=access.user.created_at
        ) if access.user else None
    )