"""Tests for domain API endpoints."""

import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from schemas import DomainCreate, DomainUpdate


class TestDomainCreation:
    """Tests for domain creation endpoint."""
    
    @pytest.mark.asyncio
    async def test_create_domain_as_admin(self, client, test_admin, mock_admin_payload):
        """Admin should be able to create a domain."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.post(
                    "/v1/domains",
                    json={
                        "name": "New Test Domain",
                        "description": "Created by test",
                        "embedding_model": "text-embedding-004",
                        "embedding_dimension": 768
                    },
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 201
                data = response.json()
                assert data["name"] == "New Test Domain"
                assert data["description"] == "Created by test"
                assert data["embedding_dimension"] == 768
    
    @pytest.mark.asyncio
    async def test_create_domain_as_reader(self, client, test_user, mock_user_payload):
        """Reader should not be able to create a domain."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_user_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.post(
                    "/v1/domains",
                    json={
                        "name": "New Domain",
                        "description": "Should fail"
                    },
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 403


class TestDomainList:
    """Tests for domain listing endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_domains_as_admin(self, client, test_admin, test_domain, mock_admin_payload):
        """Admin should see all domains."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.get(
                    "/v1/domains",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                assert "total" in data
                assert "page" in data
                assert "pages" in data
    
    @pytest.mark.asyncio
    async def test_list_domains_pagination(self, client, test_admin, mock_admin_payload):
        """Should respect pagination parameters."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.get(
                    "/v1/domains?page=1&page_size=10",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["page"] == 1
                assert data["page_size"] == 10


class TestDomainGet:
    """Tests for domain retrieval endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_domain_by_id(self, client, test_admin, test_domain, mock_admin_payload):
        """Should retrieve domain by ID."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.get(
                    f"/v1/domains/{test_domain.id}",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == str(test_domain.id)
                assert data["name"] == test_domain.name
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_domain(self, client, test_admin, mock_admin_payload):
        """Should return 404 for non-existent domain."""
        fake_id = str(uuid4())
        
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.get(
                    f"/v1/domains/{fake_id}",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 404


class TestDomainUpdate:
    """Tests for domain update endpoint."""
    
    @pytest.mark.asyncio
    async def test_update_domain(self, client, test_admin, test_domain, mock_admin_payload):
        """Admin should be able to update a domain."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.put(
                    f"/v1/domains/{test_domain.id}",
                    json={
                        "name": "Updated Domain Name",
                        "description": "Updated description"
                    },
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["name"] == "Updated Domain Name"
                assert data["description"] == "Updated description"


class TestDomainDelete:
    """Tests for domain deletion endpoint."""
    
    @pytest.mark.asyncio
    async def test_delete_domain(self, client, test_admin, test_domain, mock_admin_payload):
        """Admin should be able to delete a domain."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.delete(
                    f"/v1/domains/{test_domain.id}",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_domain(self, client, test_admin, mock_admin_payload):
        """Should return 404 when deleting non-existent domain."""
        fake_id = str(uuid4())
        
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.delete(
                    f"/v1/domains/{fake_id}",
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 404


class TestDomainAccess:
    """Tests for domain access management."""
    
    @pytest.mark.asyncio
    async def test_grant_domain_access(self, client, test_admin, test_domain, test_user, mock_admin_payload):
        """Admin should be able to grant access to a domain."""
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                response = await client.post(
                    f"/v1/domains/{test_domain.id}/access",
                    json={
                        "user_id": str(test_user.id),
                        "role": "reader"
                    },
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 201
                data = response.json()
                assert data["user_id"] == str(test_user.id)
                assert data["role"] == "reader"
    
    @pytest.mark.asyncio
    async def test_revoke_domain_access(self, client, test_admin, test_domain, test_user, mock_admin_payload):
        """Admin should be able to revoke access from a domain."""
        # First grant access
        with patch("core.auth.verify_jwt_token", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = mock_admin_payload
            
            with patch("core.auth.fetch_jwks", new_callable=AsyncMock):
                # Grant access first
                await client.post(
                    f"/v1/domains/{test_domain.id}/access",
                    json={
                        "user_id": str(test_user.id),
                        "role": "reader"
                    },
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                # Then revoke
                response = await client.request(
                    "DELETE",
                    f"/v1/domains/{test_domain.id}/access",
                    json={"user_id": str(test_user.id)},
                    headers={"Authorization": "Bearer fake_token"}
                )
                
                assert response.status_code == 204