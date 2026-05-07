import asyncio
import os
import sys
import httpx
from uuid import UUID

# Add api/src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'api', 'src'))

async def check_all():
    # 1. Check ChromaDB
    print("--- Checking ChromaDB ---")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            hb = await client.get("http://localhost:8001/api/v1/heartbeat")
            print(f"ChromaDB Heartbeat: {hb.status_code}")
            
            colls = await client.get("http://localhost:8001/api/v1/collections")
            print(f"Collections: {colls.status_code}")
            if colls.status_code == 200:
                for c in colls.json():
                    print(f" - Collection: {c['name']}")
    except Exception as e:
        print(f"ChromaDB Error: {e}")

    # 2. Check Database directly with psql via docker (bypass python driver issues)
    print("\n--- Checking Database (via Docker) ---")
    os.system('docker exec km_postgres psql -U knowledge -d knowledge_db -c "SELECT id, name FROM domains;"')

if __name__ == "__main__":
    asyncio.run(check_all())
