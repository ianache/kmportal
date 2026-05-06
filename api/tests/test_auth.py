"""Tests for authentication module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from core.auth import (
    verify_jwt_token,
    extract_user_from_token,
    generate_api_key,
    hash_api_key,
    verify_api_key
)
from schemas import UserInToken


class TestJWTVerification:
    """Tests for JWT token verification."""
    
    @pytest.mark.asyncio
    async def test_verify_valid_jwt_token(self, mock_user_payload):
        """Should verify a valid JWT token successfully."""
        # Mock the jwks fetch and jwt decode
        mock_jwks = {"keys": [{"kid": "test-key"}]}
        
        with patch("core.auth.fetch_jwks", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_jwks
            
            with patch("core.auth.jwt.decode") as mock_decode:
                mock_decode.return_value = mock_user_payload
                
                with patch("core.auth.jwt.get_unverified_header") as mock_header:
                    mock_header.return_value = {"kid": "test-key"}
                    
                    result = await verify_jwt_token("valid_token")
                    
                    assert result is not None
                    assert result["sub"] == "test-keycloak-id"
                    assert result["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_verify_invalid_jwt_token(self):
        """Should return None for invalid token."""
        result = await verify_jwt_token("invalid_token")
        # This will fail because the token format is invalid
        assert result is None
    
    @pytest.mark.asyncio
    async def test_verify_expired_jwt_token(self):
        """Should return None for expired token."""
        with patch("core.auth.jwt.decode") as mock_decode:
            from jose import JWTError
            mock_decode.side_effect = JWTError("Token expired")
            
            result = await verify_jwt_token("expired_token")
            assert result is None


class TestUserExtraction:
    """Tests for user extraction from token."""
    
    def test_extract_user_from_token(self, mock_user_payload):
        """Should extract user info from token payload."""
        user = extract_user_from_token(mock_user_payload)
        
        assert isinstance(user, UserInToken)
        assert user.keycloak_id == "test-keycloak-id"
        assert user.email == "test@example.com"
        assert "KM_VIEWER" in user.roles
    
    def test_extract_user_with_client_roles(self):
        """Should extract user with client-specific roles."""
        payload = {
            "sub": "user-123",
            "email": "user@test.com",
            "realm_access": {
                "roles": ["KM_ADMIN"]
            },
            "resource_access": {
                "kmplatform": {
                    "roles": ["custom-role"]
                }
            }
        }
        
        user = extract_user_from_token(payload)
        
        assert "KM_ADMIN" in user.roles
        assert "custom-role" in user.roles
    
    def test_extract_user_without_realm_access(self):
        """Should handle token without realm_access."""
        payload = {
            "sub": "user-123",
            "email": "user@test.com"
        }
        
        user = extract_user_from_token(payload)
        
        assert user.roles == []


class TestAPIKeyUtils:
    """Tests for API key utilities."""
    
    def test_generate_api_key(self):
        """Should generate a secure API key."""
        key1 = generate_api_key()
        key2 = generate_api_key()
        
        assert isinstance(key1, str)
        assert len(key1) > 20  # Should be reasonably long
        assert key1 != key2  # Should be unique
    
    def test_hash_api_key(self):
        """Should hash API key consistently."""
        key = "test-api-key-123"
        hash1 = hash_api_key(key)
        hash2 = hash_api_key(key)
        
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 produces 64 hex chars
        assert hash1 == hash2  # Same key should produce same hash
    
    def test_verify_api_key(self):
        """Should verify API key against hash."""
        key = "my-secret-key"
        key_hash = hash_api_key(key)
        
        assert verify_api_key(key, key_hash) is True
        assert verify_api_key("wrong-key", key_hash) is False