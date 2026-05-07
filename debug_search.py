import asyncio
import os
import sys
from uuid import UUID

# Add api/src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'api', 'src'))

from db.database import AsyncSessionLocal
from sqlalchemy import select
from models import Domain, Document, User
from services.search_service import SearchService
from adapters.vector_store.chroma_db import ChromaDBAdapter
from adapters.embedding.gemini import GeminiAdapter

async def test_search():
    # Load .env
    from dotenv import load_dotenv
    load_dotenv(os.path.join('api', '.env'))
    load_dotenv('.env')
    
    # Configuration
    os.environ['DATABASE_URL'] = "postgresql+asyncpg://knowledge:change_me_in_production@localhost:5432/knowledge_db"
    
    chroma_host = "localhost" # Internal is 'chromadb', but we are running outside
    chroma_port = 8001        # Docker port mapping 8001:8000
    
    query_text = "localStorage"
    
    async with AsyncSessionLocal() as db:
        # 1. Get all domains
        res = await db.execute(select(Domain))
        domains = res.scalars().all()
        domain_ids = [d.id for d in domains]
        
        print(f"Searching in {len(domain_ids)} domains: {[d.name for d in domains]}")
        
        # 2. Setup services
        vector_store = ChromaDBAdapter(host=chroma_host, port=chroma_port)
        embedding_provider = GeminiAdapter(api_key=os.getenv("GEMINI_API_KEY"))
        
        search_service = SearchService(db, vector_store, embedding_provider)
        
        # 3. Perform search
        print(f"Performing semantic search for: '{query_text}'...")
        results = await search_service.semantic_search(
            query=query_text,
            domain_ids=domain_ids,
            top_k=5
        )
        
        print(f"\n--- Search Results ({len(results)}) ---")
        for i, r in enumerate(results):
            print(f"{i+1}. [{r.score:.4f}] {r.document_title} (ID: {r.document_id})")
            print(f"   Excerpt: {r.text[:200]}...")
            print(f"   Metadata: {r.metadata}")
            print("-" * 40)
            
        # 4. Also try to list documents with this term in DB to verify ingestion
        doc_res = await db.execute(
            select(Document).where(Document.title.ilike(f"%{query_text}%"))
        )
        docs_with_title = doc_res.scalars().all()
        if docs_with_title:
            print(f"\nFound {len(docs_with_title)} documents with '{query_text}' in TITLE:")
            for d in docs_with_title:
                print(f" - {d.title} (Status: {d.status}, Chunks: {d.chunk_count})")
        else:
            print(f"\nNo documents found with '{query_text}' in TITLE.")

if __name__ == "__main__":
    asyncio.run(test_search())
