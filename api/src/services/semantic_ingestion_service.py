"""
Semantic Ingestion Service (FEAT6).

Implements atomic dual-write: Neo4j (TBox instance) then ChromaDB (vector).
If ChromaDB fails the Neo4j node is rolled back via DETACH DELETE so both
stores remain consistent.

Collection naming: ``semantic_{domain_id}``
Distance metric:   cosine  (hnsw:space = cosine)
"""
import logging

from ports.vector_store import Chunk, CollectionExistsError
from adapters.vector_store.chroma_db import ChromaDBAdapter
from schemas import IngestionPayload, SemanticIngestionResponse

logger = logging.getLogger(__name__)

_COSINE_META = {"hnsw:space": "cosine"}


class IngestionCoordinator:
    """
    Guarantees referential integrity between Neo4j and ChromaDB using link_id.

    Phase 1 (Neo4j):   MERGE OWLClass → CREATE KnowledgeItem → INSTANCE_OF
    Phase 2 (ChromaDB): embed content → upsert into semantic_{domain_id}

    On Phase-2 failure: DETACH DELETE the KnowledgeItem written in Phase 1.
    """

    def __init__(self, driver, vector_store: ChromaDBAdapter, embedding_provider) -> None:
        self._driver = driver
        self._vector_store = vector_store
        self._embedding_provider = embedding_provider

    async def execute_atomic_ingestion(
        self,
        payload: IngestionPayload,
        domain_id: str,
    ) -> SemanticIngestionResponse:
        link_id = str(payload.metadata.link_id)
        collection_name = f"semantic_{domain_id}"

        # ── Phase 1: Neo4j ────────────────────────────────────────────────────
        try:
            async with self._driver.session() as session:
                await session.run(
                    """
                    MERGE (c:OWLClass {name: $owl_class})
                    CREATE (n:KnowledgeItem {id: $link_id})
                    SET n += $props
                    SET n.governance_level = $governance_level
                    SET n.source_ref      = $source_ref
                    CREATE (n)-[:INSTANCE_OF]->(c)
                    """,
                    owl_class=payload.metadata.owl_class,
                    link_id=link_id,
                    props=payload.graph_properties,
                    governance_level=payload.metadata.governance_level,
                    source_ref=payload.metadata.source_ref,
                )
        except Exception as exc:
            logger.error("[FEAT6] Neo4j write failed link_id=%s: %s", link_id, exc)
            raise RuntimeError(f"Neo4j write failed: {exc}") from exc

        # ── Phase 2: ChromaDB ─────────────────────────────────────────────────
        try:
            try:
                await self._vector_store.create_collection(
                    name=collection_name,
                    dimension=self._embedding_provider.dimension,
                    metadata=_COSINE_META,
                )
            except CollectionExistsError:
                pass

            embeddings = await self._embedding_provider.embed([payload.content])

            chunk = Chunk(
                id=link_id,
                text=payload.content,
                embedding=embeddings[0],
                metadata={
                    "link_id": link_id,
                    "owl_class": payload.metadata.owl_class,
                    "governance": payload.metadata.governance_level,
                    "source": payload.metadata.source_ref,
                    "domain_id": domain_id,
                },
            )
            await self._vector_store.upsert(collection=collection_name, chunks=[chunk])

        except Exception as exc:
            logger.error(
                "[FEAT6] ChromaDB write failed link_id=%s: %s — rolling back Neo4j",
                link_id, exc,
            )
            await self._rollback_neo4j(link_id)
            raise RuntimeError(f"ChromaDB write failed (Neo4j rolled back): {exc}") from exc

        return SemanticIngestionResponse(success=True, link_id=link_id)

    async def _rollback_neo4j(self, link_id: str) -> None:
        try:
            async with self._driver.session() as session:
                await session.run(
                    "MATCH (n:KnowledgeItem {id: $link_id}) DETACH DELETE n",
                    link_id=link_id,
                )
        except Exception as exc:
            logger.error("[FEAT6] Neo4j rollback failed link_id=%s: %s", link_id, exc)
