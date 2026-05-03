"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import List, Optional, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ==================== Pagination ====================

class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response metadata."""
    items: List[Any]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "items": [],
            "total": 100,
            "page": 1,
            "page_size": 20,
            "pages": 5
        }
    })


# ==================== User ====================

class UserBase(BaseModel):
    """Base user schema."""
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    

class UserCreate(UserBase):
    """User creation schema."""
    keycloak_id: str = Field(..., description="Keycloak user ID")
    roles: List[str] = Field(default=[], description="User roles")


class UserResponse(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    roles: List[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    

class UserInToken(BaseModel):
    """User info embedded in JWT token."""
    id: Optional[UUID] = None
    keycloak_id: str
    email: str
    roles: List[str] = []


# ==================== Domain ====================

class DomainBase(BaseModel):
    """Base domain schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Domain name")
    description: Optional[str] = Field(None, max_length=2000, description="Domain description")


class DomainCreate(DomainBase):
    """Domain creation schema."""
    embedding_model: str = Field("text-embedding-004", description="Embedding model to use")
    embedding_dimension: int = Field(768, ge=1, le=4096, description="Embedding dimension")


class DomainUpdate(BaseModel):
    """Domain update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class DomainResponse(DomainBase):
    """Domain response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    embedding_model: str
    embedding_dimension: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    document_count: int = Field(0, description="Number of documents in domain")
    

class DomainListResponse(PaginatedResponse):
    """Paginated domain list response."""
    items: List[DomainResponse]


# ==================== Domain Access ====================

class DomainAccessGrant(BaseModel):
    """Grant access to domain."""
    user_id: UUID = Field(..., description="User ID to grant access")
    role: str = Field("reader", pattern="^(admin|reader)$", description="Access role")


class DomainAccessRevoke(BaseModel):
    """Revoke access from domain."""
    user_id: UUID = Field(..., description="User ID to revoke access")


class DomainAccessResponse(BaseModel):
    """Domain access response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    domain_id: UUID
    role: str
    granted_at: datetime
    user: UserResponse


# ==================== Document ====================

class DocumentBase(BaseModel):
    """Base document schema."""
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    metadata: Dict[str, Any] = Field(default={}, description="Document metadata")


class DocumentCreate(DocumentBase):
    """Document creation schema."""
    domain_id: UUID = Field(..., description="Domain ID")
    source_type: str = Field("upload", description="Source type (upload, s3, kafka, etc.)")
    source_uri: Optional[str] = Field(None, description="Source URI")


class DocumentResponse(DocumentBase):
    """Document response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    domain_id: UUID
    source_type: str
    source_uri: Optional[str]
    status: str
    chunk_count: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(PaginatedResponse):
    """Paginated document list response."""
    items: List[DocumentResponse]


# ==================== API Key ====================

class APIKeyCreate(BaseModel):
    """API Key creation schema."""
    name: str = Field(..., min_length=1, max_length=255, description="API Key name")
    scopes: List[str] = Field(default=["read"], description="Allowed scopes")
    domain_ids: List[UUID] = Field(default=[], description="Allowed domain IDs")
    rate_limit: int = Field(1000, ge=1, le=10000, description="Rate limit per hour")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")


class APIKeyResponse(BaseModel):
    """API Key response schema (without the actual key)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    scopes: List[str]
    domain_ids: List[UUID]
    rate_limit: int
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool


class APIKeyCreateResponse(APIKeyResponse):
    """API Key creation response (includes the actual key once)."""
    key: str = Field(..., description="The API key (shown only once)")


class APIKeyListResponse(PaginatedResponse):
    """Paginated API key list response."""
    items: List[APIKeyResponse]


# ==================== Search ====================

class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    domain_ids: List[UUID] = Field(default=[], description="Domain IDs to search")
    top_k: int = Field(10, ge=1, le=100, description="Number of results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class SearchResult(BaseModel):
    """Search result item."""
    chunk_id: str = Field(..., description="Chunk ID")
    score: float = Field(..., ge=0, le=1, description="Relevance score")
    text: str = Field(..., description="Chunk text content")
    document_id: UUID = Field(..., description="Document ID")
    document_title: str = Field(..., description="Document title")
    domain_id: UUID = Field(..., description="Domain ID")
    metadata: Dict[str, Any] = Field(default={}, description="Chunk metadata")


class SearchResponse(BaseModel):
    """Search response."""
    query: str = Field(..., description="Original query")
    results: List[SearchResult]
    total: int = Field(..., description="Total results")
    search_time_ms: int = Field(..., description="Search time in milliseconds")


# ==================== Ingestion ====================

class IngestionRequest(BaseModel):
    """Document ingestion request."""
    domain_id: UUID = Field(..., description="Target domain ID")
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    content: Optional[str] = Field(None, description="Document content (if inline)")
    source_type: str = Field("api", description="Source type")
    metadata: Dict[str, Any] = Field(default={}, description="Document metadata")


class IngestionResponse(BaseModel):
    """Ingestion response."""
    job_id: UUID = Field(..., description="Ingestion job ID")
    document_id: UUID = Field(..., description="Document ID")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")


class IngestionStatusResponse(BaseModel):
    """Ingestion job status response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    document_id: UUID
    domain_id: UUID
    status: str
    progress: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime


# ==================== Health ====================

class HealthResponse(BaseModel):
    """Health check response."""
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment name")
    checks: Optional[Dict[str, Any]] = Field(None, description="Detailed health checks")


# ==================== Error ====================

class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Validation errors")