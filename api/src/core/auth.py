"""Authentication and authorization core module."""

import hashlib
import os
import secrets
from datetime import datetime
from typing import Any

import httpx
from jose import JWTError, jwt
from jose.exceptions import JWTClaimsError

from schemas import UserInToken

# Configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://oauth2.qa.comsatel.com.pe")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "Apps")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "kmplatform")
ALGORITHM = "RS256"

# Cache for JWKS
_jwks_cache: dict[str, Any] | None = None
_jwks_last_fetch: datetime | None = None


async def fetch_jwks() -> dict[str, Any]:
    """Fetch JWKS from Keycloak."""
    global _jwks_cache, _jwks_last_fetch

    # Return cached JWKS if available
    if _jwks_cache is not None:
        return _jwks_cache

    jwks_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"

    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_last_fetch = datetime.utcnow()
        return _jwks_cache


def get_signing_key(jwks: dict[str, Any], kid: str) -> dict[str, Any] | None:
    """Get signing key from JWKS by key ID."""
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


def rsa_key_to_pem(rsa_key: dict[str, Any]) -> str:
    """Convert RSA key from JWK format to PEM."""
    # This is a simplified version - in production use a proper JWK to PEM library
    # For now, we'll use the key as-is with python-jose which supports JWK
    return rsa_key


async def verify_jwt_token(token: str) -> dict[str, Any] | None:
    """
    Verify and decode JWT token from Keycloak.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        # Get unverified header to extract key ID
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        if not kid:
            return None

        # Fetch JWKS
        jwks = await fetch_jwks()
        signing_key = get_signing_key(jwks, kid)

        if not signing_key:
            return None

        # Verify token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[ALGORITHM],
            audience=KEYCLOAK_CLIENT_ID,
            issuer=f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
        )

        return payload

    except (JWTError, JWTClaimsError) as e:
        import logging
        logging.error(f"JWT Verification failed: {e}")
        return None
    except Exception as e:
        import logging
        logging.error(f"Unexpected error in JWT verification: {e}")
        return None


def extract_user_from_token(token_payload: dict[str, Any]) -> UserInToken:
    """
    Extract user information from JWT token payload.

    Args:
        token_payload: Decoded JWT payload

    Returns:
        UserInToken with user information
    """
    # Extract realm roles
    realm_access = token_payload.get("realm_access", {})
    roles = realm_access.get("roles", [])

    # Extract client roles if present
    resource_access = token_payload.get("resource_access", {})
    client_roles = resource_access.get(KEYCLOAK_CLIENT_ID, {}).get("roles", [])
    roles.extend(client_roles)

    return UserInToken(
        keycloak_id=token_payload.get("sub", ""),
        email=token_payload.get("email", ""),
        roles=list(set(roles))  # Remove duplicates
    )


# ==================== API Key Utilities ====================

def generate_api_key() -> str:
    """Generate a new API key (UUID format)."""
    return secrets.token_urlsafe(32)


def hash_api_key(key: str) -> str:
    """Hash API key using SHA-256."""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(key: str, key_hash: str) -> bool:
    """Verify an API key against its hash."""
    return hash_api_key(key) == key_hash
