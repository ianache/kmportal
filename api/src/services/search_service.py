"""Search service - semantic and hybrid search over documents."""

import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from models import Document, Domain
from schemas import SearchRequest, SearchResult, SearchResponse
from ports.vector_store import VectorStorePort
from ports.embedding import EmbeddingPort


class SearchService:
    """Service for document search."""
    
    def __init__(
        self,
        db: AsyncSession,
        vector_store: VectorStorePort,
        embedding_provider: EmbeddingPort
    ):
        self.db = db
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
    
    async def semantic_search(
        self,
        query: str,
        domain_ids: List[UUID],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform semantic search using vector similarity.
        
        Args:
            query: Search query text
            domain_ids: List of domain IDs to search
            top_k: Number of results per domain
            filters: Optional metadata filters
            
        Returns:
            List of search results sorted by relevance
        """
        # Generate query embedding
        if not domain_ids:
            return []

        query_embedding = await self.embedding_provider.embed_query(query)

        all_results = []

        # Search each domain
        for domain_id in domain_ids:
            try:
                # Search vector store
                collection_name = str(domain_id)
                vector_results = await self.vector_store.search(
                    collection=collection_name,
                    query_vector=query_embedding,
                    top_k=top_k,
                    filters=filters
                )
                
                # Convert to SearchResult
                for vr in vector_results:
                    # Extract document_id from chunk_id (format: doc_id_chunk_index)
                    chunk_parts = vr.chunk_id.rsplit('_', 1)
                    document_id = chunk_parts[0] if len(chunk_parts) > 1 else vr.chunk_id
                    
                    all_results.append(SearchResult(
                        chunk_id=vr.chunk_id,
                        score=vr.score,
                        text=vr.text,
                        document_id=UUID(document_id) if len(document_id) == 36 else document_id,
                        document_title=vr.metadata.get('title', 'Untitled'),
                        domain_id=domain_id,
                        metadata=vr.metadata
                    ))
                    
            except Exception as e:
                # Log error but continue with other domains
                print(f"Error searching domain {domain_id}: {e}")
                continue
        
        # Sort by score (descending)
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        return all_results[:top_k]
    
    async def keyword_search(
        self,
        query: str,
        domain_ids: List[UUID],
        limit: int = 100
    ) -> List[SearchResult]:
        """
        Perform keyword search using PostgreSQL full-text search.
        
        Args:
            query: Search query text
            domain_ids: List of domain IDs to search
            limit: Maximum results
            
        Returns:
            List of search results
        """
        # Convert domain_ids to strings for SQL
        domain_strs = [str(d) for d in domain_ids]
        
        # PostgreSQL full-text search query
        # Note: This requires documents to have content stored in metadata
        # For now, search on title only (content is in MongoDB)
        sql = text("""
            SELECT 
                d.id,
                d.title,
                d.domain_id,
                d.metadata,
                ts_rank_cd(
                    to_tsvector('english', COALESCE(d.title, '')),
                    plainto_tsquery('english', :query),
                    32
                ) AS rank
            FROM documents d
            WHERE 
                d.domain_id = ANY(:domain_ids)
                AND d.status::text = 'DONE'
                AND to_tsvector('english', COALESCE(d.title, '')) 
                    @@ plainto_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :limit
        """)
        
        result = await self.db.execute(
            sql,
            {
                "query": query,
                "domain_ids": domain_strs,
                "limit": limit
            }
        )
        
        results = []
        for row in result:
            results.append(SearchResult(
                chunk_id=f"{row.id}_title",  # Synthetic chunk for title
                score=float(row.rank) / 10.0,  # Normalize to ~0-1 range
                text=row.title,
                document_id=row.id,
                document_title=row.title,
                domain_id=row.domain_id,
                metadata=row.metadata or {}
            ))
        
        return results
    
    async def hybrid_search(
        self,
        query: str,
        domain_ids: List[UUID],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and keyword search.
        
        Uses Reciprocal Rank Fusion (RRF) to combine results.
        
        Args:
            query: Search query text
            domain_ids: List of domain IDs to search
            top_k: Number of results to return
            filters: Optional metadata filters
            vector_weight: Weight for vector search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            
        Returns:
            List of search results
        """
        # Run searches in parallel
        import asyncio
        
        vector_task = self.semantic_search(
            query=query,
            domain_ids=domain_ids,
            top_k=top_k * 2,  # Get more for fusion
            filters=filters
        )
        
        keyword_task = self.keyword_search(
            query=query,
            domain_ids=domain_ids,
            limit=top_k * 2
        )
        
        vector_results, keyword_results = await asyncio.gather(
            vector_task,
            keyword_task
        )
        
        # Apply RRF fusion
        fused_results = self._reciprocal_rank_fusion(
            vector_results=vector_results,
            keyword_results=keyword_results,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight
        )
        
        return fused_results[:top_k]
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
        k: int = 60,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[SearchResult]:
        """
        Apply Reciprocal Rank Fusion to combine search results.
        
        RRF formula: score = Σ(weight_i / (k + rank_i))
        
        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search
            k: RRF constant (default 60)
            vector_weight: Weight for vector results
            keyword_weight: Weight for keyword results
            
        Returns:
            Combined and re-ranked results
        """
        # Create score dictionaries
        # Key: (document_id, chunk_id) tuple
        scores: Dict[tuple, float] = {}
        result_map: Dict[tuple, SearchResult] = {}
        
        # Add vector results
        for rank, result in enumerate(vector_results, start=1):
            key = (str(result.document_id), result.chunk_id)
            scores[key] = scores.get(key, 0) + (vector_weight / (k + rank))
            result_map[key] = result
        
        # Add keyword results
        for rank, result in enumerate(keyword_results, start=1):
            key = (str(result.document_id), result.chunk_id)
            scores[key] = scores.get(key, 0) + (keyword_weight / (k + rank))
            if key not in result_map:
                result_map[key] = result
        
        # Sort by RRF score
        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        
        # Create final results with updated scores
        fused_results = []
        for key in sorted_keys:
            result = result_map[key]
            # Update score with fused score
            fused_result = SearchResult(
                chunk_id=result.chunk_id,
                score=scores[key],
                text=result.text,
                document_id=result.document_id,
                document_title=result.document_title,
                domain_id=result.domain_id,
                metadata={**result.metadata, 'fused': True}
            )
            fused_results.append(fused_result)
        
        return fused_results
    
    async def search(
        self,
        request: SearchRequest,
        domain_ids: List[UUID]
    ) -> SearchResponse:
        """
        Main search method.
        
        Args:
            request: Search request with query and parameters
            domain_ids: List of authorized domain IDs
            
        Returns:
            Search response with results
        """
        start_time = time.time()
        
        # Determine search mode
        if request.mode == "semantic":
            results = await self.semantic_search(
                query=request.query,
                domain_ids=domain_ids,
                top_k=request.top_k,
                filters=request.filters
            )
        elif request.mode == "keyword":
            results = await self.keyword_search(
                query=request.query,
                domain_ids=domain_ids,
                limit=request.top_k
            )
        else:  # hybrid (default)
            results = await self.hybrid_search(
                query=request.query,
                domain_ids=domain_ids,
                top_k=request.top_k,
                filters=request.filters
            )
        
        # Apply metadata filters (post-search for now)
        if request.filters:
            results = self._apply_filters(results, request.filters)
        
        search_time = int((time.time() - start_time) * 1000)
        
        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results),
            search_time_ms=search_time
        )
    
    def _apply_filters(
        self,
        results: List[SearchResult],
        filters: Dict[str, Any]
    ) -> List[SearchResult]:
        """
        Apply metadata filters to search results.
        
        Args:
            results: Search results
            filters: Metadata filters
            
        Returns:
            Filtered results
        """
        filtered = results
        
        # Filter by document type
        if 'type' in filters:
            doc_type = filters['type'].lower()
            filtered = [
                r for r in filtered 
                if r.metadata.get('type', '').lower() == doc_type
                or r.metadata.get('file_type', '').lower() == doc_type
            ]
        
        # Filter by source
        if 'source' in filters:
            source = filters['source'].lower()
            filtered = [
                r for r in filtered 
                if r.metadata.get('source', '').lower() == source
                or r.metadata.get('source_type', '').lower() == source
            ]
        
        # Note: date_from and date_to would require storing dates in metadata
        # This is a simplified implementation
        
        return filtered