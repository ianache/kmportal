"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# ==================== Pagination ====================

class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response metadata."""
    items: list[Any]
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
    full_name: str | None = Field(None, description="User full name")


class UserCreate(UserBase):
    """User creation schema."""
    keycloak_id: str = Field(..., description="Keycloak user ID")
    roles: list[str] = Field(default=[], description="User roles")


class UserResponse(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    roles: list[str]
    is_active: bool
    last_login: datetime | None
    created_at: datetime


class UserInToken(BaseModel):
    """User info embedded in JWT token or API Key."""
    id: UUID | None = None
    keycloak_id: str
    email: str
    full_name: str | None = None
    roles: list[str] = []
    scopes: list[str] = []
    allowed_domains: list[UUID] = []


# ==================== Domain ====================

class DomainBase(BaseModel):
    """Base domain schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Domain name (ES)")
    description: str | None = Field(None, max_length=2000, description="Domain description (ES)")


class DomainCreate(DomainBase):
    """Domain creation schema."""
    embedding_model: str = Field("text-embedding-004", description="Embedding model to use")
    embedding_dimension: int = Field(768, ge=1, le=4096, description="Embedding dimension")
    name_en: str | None = Field(None, max_length=255, description="Domain name in English")
    description_en: str | None = Field(None, max_length=2000, description="Domain description in English")
    tags: list[str] = Field(default=[], description="Domain tags")
    visibility: str = Field("private", pattern="^(public|private)$", description="Domain visibility")
    cover_image: str | None = Field(None, description="Cover image data URL or URL")
    ingestion_flow: str | None = Field(None, description="Ingestion workflow name")


class DomainUpdate(BaseModel):
    """Domain update schema."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    name_en: str | None = Field(None, max_length=255)
    description_en: str | None = Field(None, max_length=2000)
    tags: list[str] | None = None
    visibility: str | None = Field(None, pattern="^(public|private)$")
    cover_image: str | None = None


class DomainResponse(DomainBase):
    """Domain response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    embedding_model: str
    embedding_dimension: int
    name_en: str | None = None
    description_en: str | None = None
    tags: list[str] = []
    visibility: str = "private"
    cover_image: str | None = None
    created_by: UUID
    created_by_name: str | None = None
    created_at: datetime
    updated_at: datetime
    document_count: int = Field(0, description="Number of documents in domain")


class DomainListResponse(PaginatedResponse):
    """Paginated domain list response."""
    items: list[DomainResponse]


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
    user: UserResponse | None = None


# ==================== Document ====================

class DocumentBase(BaseModel):
    """Base document schema."""
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    metadata: dict[str, Any] = Field(default={}, description="Document metadata")


class DocumentCreate(DocumentBase):
    """Document creation schema."""
    domain_id: UUID = Field(..., description="Domain ID")
    source_type: str = Field("upload", description="Source type (upload, s3, kafka, etc.)")
    source_uri: str | None = Field(None, description="Source URI")


class DocumentResponse(DocumentBase):
    """Document response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    domain_id: UUID
    source_type: str
    source_uri: str | None
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(PaginatedResponse):
    """Paginated document list response."""
    items: list[DocumentResponse]


# ==================== API Key ====================

class APIKeyCreate(BaseModel):
    """API Key creation schema."""
    name: str = Field(..., min_length=1, max_length=255, description="API Key name")
    scopes: list[str] = Field(default=["read"], description="Allowed scopes")
    domain_ids: list[UUID] = Field(default=[], description="Allowed domain IDs")
    rate_limit: int = Field(1000, ge=1, le=10000, description="Rate limit per hour")
    expires_at: datetime | None = Field(None, description="Expiration date")


class APIKeyResponse(BaseModel):
    """API Key response schema (without the actual key)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    scopes: list[str]
    domain_ids: list[UUID]
    rate_limit: int
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None
    is_active: bool


class APIKeyCreateResponse(APIKeyResponse):
    """API Key creation response (includes the actual key once)."""
    key: str = Field(..., description="The API key (shown only once)")


class APIKeyListResponse(PaginatedResponse):
    """Paginated API key list response."""
    items: list[APIKeyResponse]


# ==================== Search ====================

class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    domain_ids: list[UUID] = Field(default=[], description="Domain IDs to search")
    mode: str = Field("hybrid", pattern="^(semantic|keyword|hybrid)$", description="Search mode")
    top_k: int = Field(10, ge=1, le=100, description="Number of results")
    filters: dict[str, Any] | None = Field(None, description="Metadata filters")


class SearchResult(BaseModel):
    """Search result item."""
    chunk_id: str = Field(..., description="Chunk ID")
    score: float = Field(..., ge=0, description="Relevance score")
    text: str = Field(..., description="Chunk text content")
    document_id: UUID | str = Field(..., description="Document ID")
    document_title: str = Field(..., description="Document title")
    domain_id: UUID | str = Field(..., description="Domain ID")
    metadata: dict[str, Any] = Field(default={}, description="Chunk metadata")


class SearchResponse(BaseModel):
    """Search response."""
    query: str = Field(..., description="Original query")
    results: list[SearchResult]
    total: int = Field(..., description="Total results")
    search_time_ms: int = Field(..., description="Search time in milliseconds")


# ==================== Ingestion ====================

class IngestionRequest(BaseModel):
    """Document ingestion request."""
    domain_id: UUID = Field(..., description="Target domain ID")
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    content: str | None = Field(None, description="Document content (if inline)")
    source_type: str = Field("api", description="Source type")
    metadata: dict[str, Any] = Field(default={}, description="Document metadata")


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
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime


class IngestionJobListResponse(BaseModel):
    """Paginated list of ingestion jobs."""
    items: list[IngestionStatusResponse]
    total: int


# ==================== Health ====================

class HealthResponse(BaseModel):
    """Health check response."""
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment name")
    checks: dict[str, Any] | None = Field(None, description="Detailed health checks")


# ==================== Ontology ====================

class OntologyConceptCreate(BaseModel):
    """Create an OWL class in the ontology."""
    uri: str = Field(..., min_length=1, max_length=500, description="OWL class URI")
    label: str = Field(..., min_length=1, max_length=255, description="Human-readable label")
    comment: str | None = Field(None, max_length=2000, description="Description or comment")


class OntologyConceptUpdate(BaseModel):
    """Update an OWL class."""
    uri: str | None = Field(None, min_length=1, max_length=500)
    label: str | None = Field(None, min_length=1, max_length=255)
    comment: str | None = Field(None, max_length=2000)


class OntologyConceptResponse(BaseModel):
    """OWL class response."""
    id: str
    domain_id: str
    uri: str
    label: str
    comment: str | None = None


class OntologyPropertyCreate(BaseModel):
    """Create an OWL property (object or datatype)."""
    uri: str = Field(..., min_length=1, max_length=500, description="Property URI")
    label: str = Field(..., min_length=1, max_length=255, description="Property label")
    property_type: str = Field("ObjectProperty", pattern="^(ObjectProperty|DatatypeProperty)$")
    source_class_id: str = Field(..., description="Domain OWL class ID")
    target_class_id: str = Field(..., description="Range OWL class ID or XSD type URI")
    comment: str | None = Field(None, max_length=2000)


class OntologyPropertyUpdate(BaseModel):
    """Update an OWL property label, range, or comment."""
    label: str | None = Field(None, min_length=1, max_length=255)
    target_class_id: str | None = Field(None, description="Updated range (class ID or XSD type URI)")
    comment: str | None = Field(None, max_length=2000)


class OntologyPropertyResponse(BaseModel):
    """OWL property response."""
    id: str
    domain_id: str
    uri: str
    label: str
    property_type: str
    source_class_id: str
    target_class_id: str
    comment: str | None = None


class OntologyResponse(BaseModel):
    """Full ontology for a domain (concepts + properties)."""
    domain_id: str
    concepts: list[OntologyConceptResponse]
    properties: list[OntologyPropertyResponse]


# ==================== Extraction ====================

class ExtractedEntity(BaseModel):
    """An entity instance extracted from text."""
    label: str
    class_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExtractedRelation(BaseModel):
    """A relationship extracted between two entities."""
    source_label: str
    target_label: str
    property_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    """Full extraction result from a document."""
    entities: list[ExtractedEntity]
    relations: list[ExtractedRelation]


# ==================== Diagrams ====================

class DiagramNodePosition(BaseModel):
    x: float
    y: float


class DiagramNode(BaseModel):
    """Vue Flow node with concept reference and layout data."""
    id: str
    concept_id: str
    position: DiagramNodePosition
    style: dict[str, Any] = Field(default_factory=dict)


class DiagramEdge(BaseModel):
    """Vue Flow edge with property reference."""
    id: str
    property_id: str
    source: str
    target: str
    label: str = ""
    style: dict[str, Any] = Field(default_factory=dict)


class DiagramCreate(BaseModel):
    """Create a new diagram for a domain."""
    name: str = Field(..., min_length=1, max_length=255, description="Diagram name")


class DiagramUpdate(BaseModel):
    """Update diagram metadata or layout."""
    name: str | None = Field(None, min_length=1, max_length=255)
    nodes: list[dict[str, Any]] | None = None
    edges: list[dict[str, Any]] | None = None
    viewport: dict[str, Any] | None = None


class DiagramResponse(BaseModel):
    """Diagram response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    domain_id: UUID
    name: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    viewport: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class DiagramListResponse(BaseModel):
    """List of diagrams for a domain."""
    items: list[DiagramResponse]
    total: int


# ==================== Batch Operations ====================

class ConceptBatchOperation(BaseModel):
    """Single concept operation in a batch."""
    operation: str = Field(..., pattern="^(create|update|delete)$")
    id: str | None = None
    data: OntologyConceptCreate | None = None


class PropertyBatchOperation(BaseModel):
    """Single property operation in a batch."""
    operation: str = Field(..., pattern="^(create|update|delete)$")
    id: str | None = None
    data: OntologyPropertyCreate | None = None


class DiagramBatchOperation(BaseModel):
    """Single diagram operation in a batch."""
    operation: str = Field(..., pattern="^(create|update|delete)$")
    id: str | None = None
    data: DiagramUpdate | None = None


class OntologyBatchPayload(BaseModel):
    """Payload for batch ontology operations."""
    concepts: list[ConceptBatchOperation] = Field(default_factory=list)
    properties: list[PropertyBatchOperation] = Field(default_factory=list)
    diagrams: list[DiagramBatchOperation] = Field(default_factory=list)


class OntologyBatchResponse(BaseModel):
    """Response from batch ontology operations."""
    success: bool
    concepts_created: list[str] = Field(default_factory=list)
    concepts_updated: list[str] = Field(default_factory=list)
    concepts_deleted: list[str] = Field(default_factory=list)
    properties_created: list[str] = Field(default_factory=list)
    properties_updated: list[str] = Field(default_factory=list)
    properties_deleted: list[str] = Field(default_factory=list)
    diagrams_created: list[str] = Field(default_factory=list)
    diagrams_updated: list[str] = Field(default_factory=list)
    diagrams_deleted: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


# ==================== Semantic / FEAT6 ====================

class SemanticLink(BaseModel):
    """Provenance and governance metadata for a semantic knowledge item."""
    link_id: UUID = Field(default_factory=uuid4)
    owl_class: str = Field(..., description="OWL class that categorises this item")
    governance_level: str = Field("CONFIDENCIAL", description="ISO 27001 governance classification")
    source_ref: str = Field(..., description="Origin reference (filename, URL, etc.)")


class IngestionPayload(BaseModel):
    """Payload for atomic semantic ingestion (Neo4j + ChromaDB)."""
    content: str = Field(..., description="Text content to index")
    metadata: SemanticLink
    graph_properties: Dict[str, str] = Field(default_factory=dict, description="Extra Neo4j node properties")


class GraphNode(BaseModel):
    id: str
    label: str
    name: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relation_type: str


class SemanticProvenance(BaseModel):
    """Ontological lineage retrieved from Neo4j for a search hit."""
    owl_class: str
    iso_compliance: str
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class HybridSearchResult(BaseModel):
    """Single result from the hybrid semantic search endpoint."""
    link_id: UUID
    content: str
    score: float
    source_file: str
    provenance: SemanticProvenance


class SemanticIngestionResponse(BaseModel):
    success: bool
    link_id: str


# ==================== Error ====================

class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str = Field(..., description="Error message")
    code: str | None = Field(None, description="Error code")
    errors: list[dict[str, Any]] | None = Field(None, description="Validation errors")
