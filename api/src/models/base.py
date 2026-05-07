"""Database models for Knowledge Management Center."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from db.database import Base


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class DocumentStatus(StrEnum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class DomainAccessRole(StrEnum):
    """Domain access roles."""
    ADMIN = "admin"
    READER = "reader"


class User(Base):
    """User model synced from Keycloak."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keycloak_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    roles = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    domains = relationship("Domain", back_populates="created_by_user")
    access_grants = relationship("DomainAccess", back_populates="user", foreign_keys="DomainAccess.user_id")
    api_keys = relationship("APIKey", back_populates="created_by_user")

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in (self.roles or [])

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.has_role("KM_ADMIN")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Domain(Base):
    """Knowledge domain model."""

    __tablename__ = "domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    name_en = Column(String(255), nullable=True)
    description_en = Column(Text, nullable=True)
    embedding_model = Column(String(100), default="text-embedding-004", nullable=False)
    embedding_dimension = Column(Integer, default=768, nullable=False)
    tags = Column(ARRAY(String), nullable=False, default=list, server_default='{}')
    visibility = Column(String(10), nullable=False, default='private', server_default='private')
    cover_image = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="domains")
    documents = relationship("Document", back_populates="domain", cascade="all, delete-orphan")
    access_grants = relationship("DomainAccess", back_populates="domain", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Domain(id={self.id}, name={self.name})>"


class Document(Base):
    """Document metadata model (content stored in MongoDB)."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)  # upload, s3, kafka, rabbitmq, api
    source_uri = Column(String(1000), nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict, nullable=False)
    chunk_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    domain = relationship("Domain", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title={self.title}, status={self.status})>"


class DomainAccess(Base):
    """Many-to-many relationship between users and domains with access level."""

    __tablename__ = "domain_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    role = Column(Enum(DomainAccessRole), default=DomainAccessRole.READER, nullable=False)
    granted_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="access_grants", foreign_keys=[user_id])
    domain = relationship("Domain", back_populates="access_grants")

    __table_args__ = (
        # Ensure a user can only have one access record per domain
        {"sqlite_autoincrement": True},
    )

    def __repr__(self) -> str:
        return f"<DomainAccess(user={self.user_id}, domain={self.domain_id}, role={self.role})>"


class APIKey(Base):
    """API Key model for external integrations."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256 hash
    name = Column(String(255), nullable=False)
    scopes = Column(JSON, default=list, nullable=False)
    domain_ids = Column(JSON, default=list, nullable=False)
    rate_limit = Column(Integer, default=1000, nullable=False)  # requests per hour
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name={self.name}, is_active={self.is_active})>"


class OntologyDiagram(Base):
    """Visual diagram for a domain's ontology (layout only, no semantic data)."""

    __tablename__ = "ontology_diagrams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    nodes = Column(JSON, default=list, nullable=False)
    edges = Column(JSON, default=list, nullable=False)
    viewport = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    domain = relationship("Domain")

    def __repr__(self) -> str:
        return f"<OntologyDiagram(id={self.id}, name={self.name}, domain={self.domain_id})>"


class IngestionJob(Base):
    """Ingestion job tracking."""

    __tablename__ = "ingestion_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<IngestionJob(id={self.id}, status={self.status}, progress={self.progress})>"
