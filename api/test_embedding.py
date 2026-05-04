import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from adapters import get_embedding_adapter

async def test():
    print("Testing embedding adapter...")
    try:
        adapter = await get_embedding_adapter()
        print(f"Adapter: {adapter.__class__.__name__}")
        print(f"Model: {adapter.model_name}")
        print(f"Dimension: {adapter.dimension}")
        
        print("\nEmbedding test text...")
        embeddings = await adapter.embed(["What is machine learning?"])
        print(f"Success! Got {len(embeddings)} embeddings")
        print(f"Embedding length: {len(embeddings[0])}")
        print(f"First 5 values: {embeddings[0][:5]}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
