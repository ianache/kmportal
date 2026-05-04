import asyncio
import sys
sys.path.insert(0, 'src')

from db.database import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as session:
        # Check documents
        result = await session.execute(text('SELECT id, title, status FROM documents LIMIT 5'))
        docs = result.fetchall()
        print('Documents:')
        for doc in docs:
            print(f'  {doc[0]}: {doc[1]} (status: {doc[2]})')
        
        # Check domains
        result = await session.execute(text("SELECT id, name FROM domains WHERE name = 'Machine Learning'"))
        domain = result.fetchone()
        if domain:
            print(f'\nMachine Learning domain ID: {domain[0]}')
        
        # List all tables
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = result.fetchall()
        print(f'\nDatabase tables:')
        for t in tables:
            print(f'  - {t[0]}')

if __name__ == "__main__":
    asyncio.run(check())
