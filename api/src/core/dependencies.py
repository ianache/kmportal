"""FastAPI dependencies for authentication and authorization."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import get_db
from core.auth import verify_jwt_token, extract_user_from_token, hash_api_key
from schemas import UserInToken, UserResponse
from models import User, DomainAccess, DomainAccessRole


# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserInToken]:
    """
    Get current user from JWT token (optional).
    
    Returns None if no valid token provided.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    # Try JWT auth first
    payload = await verify_jwt_token(token)
    if payload:
        user_data = extract_user_from_token(payload)
        
        # Get or create user in database
        result = await db.execute(
            select(User).where(User.keycloak_id == user_data.keycloak_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user_data.id = user.id
            # Update roles if changed
            if set(user.roles) != set(user_data.roles):
                user.roles = user_data.roles
                await db.commit()
        
        return user_data
    
    # Try API Key auth
    # TODO: Implement API key validation
    
    return None


async def get_current_user(
    user: Optional[UserInToken] = Depends(get_current_user_optional)
) -> UserInToken:
    """
    Get current user (required).
    
    Raises 401 if no valid authentication provided.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def require_admin(
    user: UserInToken = Depends(get_current_user)
) -> UserInToken:
    """
    Require km-admin role.
    
    Raises 403 if user is not admin.
    """
    if "km-admin" not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def require_reader(
    user: UserInToken = Depends(get_current_user)
) -> UserInToken:
    """
    Require km-reader or km-admin role.
    
    Raises 403 if user has neither role.
    """
    if "km-admin" not in user.roles and "km-reader" not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reader access required"
        )
    return user


class DomainAccessChecker:
    """Check if user has access to a specific domain."""
    
    def __init__(self, require_admin: bool = False):
        self.require_admin = require_admin
    
    async def __call__(
        self,
        domain_id: UUID,
        user: UserInToken = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> UserInToken:
        """Check domain access."""
        # Global admins always have access
        if "km-admin" in user.roles:
            return user
        
        # Check specific domain access
        if not user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Domain access required"
            )
        
        result = await db.execute(
            select(DomainAccess).where(
                DomainAccess.user_id == user.id,
                DomainAccess.domain_id == domain_id
            )
        )
        access = result.scalar_one_or_none()
        
        if not access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Domain access required"
            )
        
        if self.require_admin and access.role != DomainAccessRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Domain admin access required"
            )
        
        return user


# Pre-defined access checkers
require_domain_access = DomainAccessChecker(require_admin=False)
require_domain_admin = DomainAccessChecker(require_admin=True)