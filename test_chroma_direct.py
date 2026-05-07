import asyncio
import os
import sys
import httpx
from uuid import UUID

# Add api/src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'api', 'src'))

from adapters.embedding.gemini import GeminiAdapter

async def test_chroma_query():
    # 1. Setup
    from dotenv import load_dotenv
    load_dotenv(os.path.join('api', '.env'))
    load_dotenv('.env')
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    embedder = GeminiAdapter(api_key=gemini_key)
    
    query_text = "localStorage"
    print(f"Generating embedding for '{query_text}'...")
    query_vector = await embedder.embed_query(query_text)
    
    # 2. Query each relevant collection
    collections = [
        "917b2658-86c6-4d12-b879-481e85802c53",
        "ca927bdc-d0be-4fcb-92c9-8c4a04daa423"
    ]
    
    base_url = "http://localhost:8001/api/v1"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Get Internal IDs first
        colls_res = await client.get(f"{base_url}/collections")
        id_map = {c['name']: c['id'] for c in colls_res.json()}
        
        for name in collections:
            coll_id = id_map.get(name)
            if not coll_id:
                print(f"Collection {name} not found in map")
                continue
                
            print(f"\n--- Querying Collection: {name} ({coll_id}) ---")
            query_payload = {
                "query_embeddings": [query_vector],
                "n_results": 5,
                "include": ["documents", "metadatas", "distances"]
            }
            
            res = await client.post(f"{base_url}/collections/{coll_id}/query", json=query_payload)
            if res.status_code == 200:
                data = res.json()
                ids = data.get('ids', [[]])[0]
                docs = data.get('documents', [[]])[0]
                dist = data.get('distances', [[]])[0]
                
                if not ids:
                    print("No results found.")
                else:
                    for i in range(len(ids)):
                        score = 1.0 / (1.0 + dist[i])
                        print(f"{i+1}. [{score:.4f}] ID: {ids[i]}")
                        print(f"   Text: {docs[i][:200]}...")
            else:
                print(f"Query failed: {res.text}")

if __name__ == "__main__":
    asyncio.run(test_chroma_query())
