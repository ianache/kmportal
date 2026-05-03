"""Tests for API key endpoints."""

import pytest
from unittest.mock import patch, AsyncMock


class TestAPICKeyCreation:
    """Tests for API key creation."""
    
    @pytest.mark.asyncio
    async def test_create_api_key(self, client, test_user, mock_user_payload):
        """Should create an API key and return it once."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_user_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.post(
                    "/v1/api-keys",
                    json={
                        "name": "Test API Key",
                        "scopes": ["read", "search"],
                        "rate_limit": 1000
                    },
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 201
                data = response.json()
                assert data["name"] == "Test API Key"
                assert data["scopes"] == ["read", "search"]
                assert data["rate_limit"] == 1000
                assert "key" in data  # Plain key only returned on creation
                assert len(data["key"]) > 20  # Should be a secure key


class TestAPIKeyList:
    """Tests for API key listing."""
    
    @pytest.mark.asyncio
    async def test_list_api_keys(self, client, test_user, mock_user_payload):
        """Should list API keys without exposing the actual key."""
        # First create an API key
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_user_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                # Create key
                await client.post(
                    "/v1/api-keys",
                    json={"name": "Test Key"},
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                # List keys
                response = await client.get(
                    "/v1/api-keys",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert "total" in data
                assert data["total"] >= 1
                
                # Verify key is not exposed in list
                for item in data["items"]:
                    assert "key" not in item  # Should not expose the actual key
                    assert "key_hash" not in item


class TestAPIKeyRevoke:
    """Tests for API key revocation."""
    
    @pytest.mark.asyncio
    async def test_revoke_api_key(self, client, test_user, mock_user_payload):
        """Should revoke an API key."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_user_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                # Create key
                create_response = await client.post(
                    "/v1/api-keys",
                    json={"name": "Key to Revoke"},
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                key_id = create_response.json()["id"]
                
                # Revoke key
                response = await client.delete(
                    f"/v1/api-keys/{key_id}",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 204
                
                # Verify key is revoked by checking is_active
                get_response = await client.get(
                    f"/v1/api-keys/{key_id}",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert get_response.status_code == 200
                assert get_response.json()["is_active"] is False