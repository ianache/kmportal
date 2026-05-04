"""Ingestion service - orchestrates document processing pipeline."""

import uuid
from datetime import datetime
from typing import Optional, List, BinaryIO
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Document, IngestionJob, DocumentStatus, Domain
from schemas import IngestionResponse, IngestionStatusResponse
from ingestion.extractors import extract_text, UnsupportedFormatError, TextExtractionError
from ingestion.chunking import chunk_document, ChunkingConfig


class IngestionError(Exception):
    """Error during document ingestion."""
    pass


class IngestionService:
    """Service for document ingestion pipeline."""
    
    def __init__(
        self,
        db: AsyncSession,
        vector_store=None,
        embedding_provider=None
    ):
        self.db = db
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
    
    async def create_ingestion_job(
        self,
        domain_id: UUID,
        title: str,
        source_type: str,
        source_uri: Optional[str] = None,
        file_type: Optional[str] = None,
        metadata: dict = None
    ) -> tuple[Document, IngestionJob]:
        """
        Create a new document and ingestion job.
        
        Args:
            domain_id: Domain ID
            title: Document title
            source_type: Source type (upload, api, s3, etc.)
            source_uri: Optional source URI
            file_type: Optional file MIME type
            metadata: Optional document metadata
            
        Returns:
            Tuple of (Document, IngestionJob)
        """
        # Validate domain exists
        domain_check = await self.db.execute(
            select(Domain.id).where(Domain.id == domain_id)
        )
        if domain_check.scalar_one_or_none() is None:
            raise IngestionError(f"Domain {domain_id} not found")

        # Create document record
        document = Document(
            domain_id=domain_id,
            title=title,
            source_type=source_type,
            source_uri=source_uri,
            status=DocumentStatus.PENDING,
            metadata_=metadata or {},
            chunk_count=0
        )
        
        self.db.add(document)
        await self.db.flush()  # Get document ID
        
        # Create ingestion job
        job = IngestionJob(
            document_id=document.id,
            domain_id=domain_id,
            status=DocumentStatus.PENDING,
            progress=0
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(document)
        await self.db.refresh(job)
        
        return document, job
    
    async def process_document(
        self,
        document_id: UUID,
        file_content: bytes,
        filename: str
    ) -> None:
        """
        Process a document through the full pipeline.
        
        Pipeline steps:
        1. Extract text from file
        2. Chunk content
        3. Generate embeddings
        4. Store in vector database
        5. Update document status
        
        Args:
            document_id: Document ID
            file_content: Raw file bytes
            filename: Original filename
        """
        # Get document and job
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise IngestionError(f"Document {document_id} not found")
        
        # Get job
        result = await self.db.execute(
            select(IngestionJob).where(IngestionJob.document_id == document_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise IngestionError(f"Ingestion job for document {document_id} not found")
        
        try:
            # Update job status
            job.status = DocumentStatus.PROCESSING
            job.started_at = datetime.utcnow()
            job.progress = 10
            await self.db.commit()
            
            # Step 1: Extract text
            text = extract_text(file_content, filename)
            job.progress = 30
            await self.db.commit()
            
            # Step 2: Get domain for embedding config
            result = await self.db.execute(
                select(Domain).where(Domain.id == document.domain_id)
            )
            domain = result.scalar_one()
            
            # Step 3: Chunk content
            config = ChunkingConfig(
                chunk_size=1000,
                chunk_overlap=200,
                strategy="semantic"
            )
            chunks = chunk_document(text, config)
            job.progress = 50
            await self.db.commit()
            
            # Step 4: Generate embeddings and store (if providers available)
            if self.embedding_provider and self.vector_store:
                # Get collection name (domain-based)
                collection_name = str(domain.id)
                
                # Ensure collection exists
                try:
                    await self.vector_store.create_collection(
                        name=collection_name,
                        dimension=domain.embedding_dimension
                    )
                except Exception:
                    # Collection might already exist
                    pass
                
                # Process chunks in batches
                batch_size = 10
                total_chunks = len(chunks)
                
                for i in range(0, total_chunks, batch_size):
                    batch = chunks[i:i + batch_size]
                    batch_texts = [chunk.text for chunk in batch]
                    
                    # Generate embeddings
                    embeddings = await self.embedding_provider.embed(batch_texts)
                    
                    # Prepare chunks for vector store
                    from ports.vector_store import Chunk as VectorChunk
                    vector_chunks = []
                    for j, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                        chunk_id = f"{document.id}_{chunk.index}"
                        vector_chunks.append(VectorChunk(
                            id=chunk_id,
                            text=chunk.text,
                            embedding=embedding,
                            metadata={
                                "document_id": str(document.id),
                                "domain_id": str(domain.id),
                                "chunk_index": chunk.index,
                                "title": document.title
                            }
                        ))
                    
                    # Store in vector database
                    await self.vector_store.upsert(
                        collection=collection_name,
                        chunks=vector_chunks
                    )
                    
                    # Update progress
                    progress = 50 + int((i + len(batch)) / total_chunks * 40)
                    job.progress = min(progress, 90)
                    await self.db.commit()
            
            # Step 5: Update document
            document.status = DocumentStatus.DONE
            document.chunk_count = len(chunks)
            
            # Update job
            job.status = DocumentStatus.DONE
            job.progress = 100
            job.completed_at = datetime.utcnow()
            
            await self.db.commit()
            
        except UnsupportedFormatError as e:
            await self._fail_job(document, job, f"Unsupported format: {str(e)}")
            raise IngestionError(f"Unsupported format: {str(e)}")
        except TextExtractionError as e:
            await self._fail_job(document, job, f"Text extraction failed: {str(e)}")
            raise IngestionError(f"Text extraction failed: {str(e)}")
        except Exception as e:
            await self._fail_job(document, job, f"Processing error: {str(e)}")
            raise IngestionError(f"Failed to process document: {str(e)}")
    
    async def _fail_job(
        self,
        document: Document,
        job: IngestionJob,
        error_message: str
    ) -> None:
        """Mark document and job as failed."""
        document.status = DocumentStatus.FAILED
        document.error_message = error_message
        
        job.status = DocumentStatus.FAILED
        job.error_message = error_message
        job.completed_at = datetime.utcnow()
        
        await self.db.commit()
    
    async def get_job_status(self, job_id: UUID) -> Optional[IngestionJob]:
        """Get ingestion job status."""
        result = await self.db.execute(
            select(IngestionJob).where(IngestionJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_document_status(self, document_id: UUID) -> Optional[Document]:
        """Get document processing status."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()


def to_ingestion_response(document: Document, job: IngestionJob) -> IngestionResponse:
    """Convert to IngestionResponse schema."""
    return IngestionResponse(
        job_id=job.id,
        document_id=document.id,
        status=job.status.value,
        message=f"Document ingestion {job.status.value}"
    )


def to_ingestion_status_response(job: IngestionJob) -> IngestionStatusResponse:
    """Convert to IngestionStatusResponse schema."""
    return IngestionStatusResponse(
        id=job.id,
        document_id=job.document_id,
        domain_id=job.domain_id,
        status=job.status.value,
        progress=job.progress,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        created_at=job.created_at
    )