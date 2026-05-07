"""FastAPI dependencies for authentication and authorization."""

import os
from uuid import UUID

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import extract_user_from_token, verify_jwt_token
from core.rate_limiter import rate_limiter
from db.database import AsyncSessionLocal, get_db
from models import DomainAccess, DomainAccessRole, User
from schemas import UserInToken
from services.api_key_service import APIKeyService

# Security scheme
security = HTTPBearer(auto_error=False)

# Cache only the scalar UUID — ORM objects become detached when their session closes
_dev_user_id_cache: UUID | None = None

_DEV_KEYCLOAK_ID = "dev-user-00000000-0000-0000-0000-000000000000"


async def _get_or_create_dev_user_id(db: AsyncSession) -> UUID:
    """Return the dev bypass user's UUID, creating the user if needed. Cached."""
    global _dev_user_id_cache

    if _dev_user_id_cache is not None:
        return _dev_user_id_cache

    result = await db.execute(
        select(User.id).where(User.keycloak_id == _DEV_KEYCLOAK_ID)
    )
    user_id = result.scalar_one_or_none()

    if not user_id:
        async with AsyncSessionLocal() as write_session:
            dev_user = User(
                keycloak_id=_DEV_KEYCLOAK_ID,
                email="dev@localhost",
                full_name="Dev Bypass User",
                roles=["KM_ADMIN"],
                is_active=True,
            )
            write_session.add(dev_user)
            await write_session.commit()
            await write_session.refresh(dev_user)
            user_id = dev_user.id

    _dev_user_id_cache = user_id
    return user_id


async def get_current_user_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    db: AsyncSession = Depends(get_db)
) -> UserInToken | None:
    """
    Get current user from JWT token or API Key (optional).

    Returns None if no valid authentication provided.
    """
    bypass_auth = os.getenv("BYPASS_AUTH", "false").lower() == "true"

    if bypass_auth:
        user_id = await _get_or_create_dev_user_id(db)
        return UserInToken(
            id=user_id,
            keycloak_id=_DEV_KEYCLOAK_ID,
            email="dev@localhost",
            roles=["KM_ADMIN"],
        )

    # Try API Key auth first (from X-API-Key header)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        api_key_service = APIKeyService(db)
        valid_key = await api_key_service.validate_api_key(api_key)

        if valid_key:
            # Enforce per-key rate limit (sliding 1-hour window)
            allowed, retry_after = rate_limiter.check(str(valid_key.id), valid_key.rate_limit)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(retry_after)},
                )

            # Get the user who created the API key
            result = await db.execute(
                select(User).where(User.id == valid_key.created_by)
            )
            user = result.scalar_one_or_none()

            if user:
                return UserInToken(
                    id=user.id,
                    keycloak_id=user.keycloak_id,
                    email=user.email,
                    roles=user.roles,
                    scopes=valid_key.scopes,
                    allowed_domains=valid_key.domain_ids,
                )

    if not credentials:
        return None

    token = credentials.credentials

    # Try JWT auth
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
            # Sync roles if changed
            if set(user.roles) != set(user_data.roles):
                user.roles = user_data.roles
                await db.commit()
        else:
            # First login — provision the user record
            async with AsyncSessionLocal() as write_session:
                new_user = User(
                    keycloak_id=user_data.keycloak_id,
                    email=user_data.email,
                    full_name=None,
                    roles=user_data.roles,
                    is_active=True,
                )
                write_session.add(new_user)
                await write_session.commit()
                await write_session.refresh(new_user)
                user_data.id = new_user.id

        return user_data

    return None


async def get_current_user(
    user: UserInToken | None = Depends(get_current_user_optional)
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
    Require KM_ADMIN role.

    Raises 403 if user is not admin.
    """
    if "KM_ADMIN" not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def require_reader(
    user: UserInToken = Depends(get_current_user)
) -> UserInToken:
    """
    Require KM_VIEWER, KM_MANAGER, or KM_ADMIN role.

    Raises 403 if user has none of these roles.
    """
    if not any(r in user.roles for r in ("KM_VIEWER", "KM_MANAGER", "KM_ADMIN")):
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
        domain_id: UUID | None = None,
        user: UserInToken = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> UserInToken:
        """Check domain access.

        domain_id is optional here so Form-body endpoints (e.g. ingest) don't
        produce a 422. Admins bypass the check entirely; non-admins must supply
        a domain_id (from path or query) that they have access to.
        """
        # Check if API key restricts domains
        if user.allowed_domains and domain_id not in user.allowed_domains:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API Key does not have access to domain {domain_id}"
            )

        # Global admins always have access (unless restricted by API key above)
        if "KM_ADMIN" in user.roles:
            return user

        if not domain_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Domain access required"
            )

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
