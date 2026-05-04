"""
Re-ingest existing documents into ChromaDB with embeddings.

This script processes all documents with status 'DONE' and indexes them
into ChromaDB using the configured embedding adapter (Ollama).
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from db.database import AsyncSessionLocal
from sqlalchemy import text, select
from models import Document
from adapters import get_embedding_adapter
from adapters.vector_store.chroma_db import ChromaDBAdapter
from ports.vector_store import Chunk
import os

# Configuration
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))

# Sample content for common document types
SAMPLE_CONTENTS = {
    "Intro to Neural Networks": """
Neural networks are a subset of machine learning and are at the heart of deep learning algorithms. 
They are comprised of node layers, containing an input layer, one or more hidden layers, and an output layer.
Each node connects to another and has an associated weight and threshold. If the output of any individual 
node is above the specified threshold value, that node is activated, sending data to the next layer of the network.

Machine learning is a branch of artificial intelligence that enables systems to learn and improve from 
experience without being explicitly programmed. Neural networks are particularly effective for tasks like 
image recognition, natural language processing, and complex pattern recognition.

Deep learning uses multiple layers to progressively extract higher-level features from raw input. 
For example, in image processing, lower layers may identify edges, while higher layers may identify 
concepts relevant to a human such as digits or letters.
""",
    "Transformer Architecture": """
The Transformer architecture, introduced in the paper "Attention Is All You Need" by Vaswani et al., 
has revolutionized natural language processing and machine learning.

Transformers use a mechanism called self-attention to weigh the importance of different parts of the 
input sequence. Unlike recurrent neural networks (RNNs), transformers process the entire input sequence 
at once, making them highly parallelizable and efficient.

Key components of the Transformer architecture include:
- Multi-head self-attention mechanism
- Position-wise feed-forward networks
- Positional encoding
- Layer normalization
- Residual connections

The architecture has become the foundation for models like BERT, GPT, T5, and many others that have 
achieved state-of-the-art results across various NLP tasks including machine translation, text summarization,
and question answering.
""",
    "Gradient Descent Notes": """
Gradient descent is an optimization algorithm used to minimize some function by iteratively moving 
in the direction of steepest descent as defined by the negative of the gradient. In machine learning, 
we use gradient descent to update the parameters of our model.

Types of gradient descent:
1. Batch Gradient Descent: Uses the entire training dataset to compute the gradient
2. Stochastic Gradient Descent (SGD): Uses a single sample at each iteration
3. Mini-batch Gradient Descent: Uses a small batch of samples at each iteration

The learning rate is a crucial hyperparameter that determines how big of a step we take in the 
direction of the gradient. If the learning rate is too small, convergence is slow. If it's too large,
the algorithm might overshoot the minimum.

Gradient descent is fundamental to training neural networks and many other machine learning algorithms.
It allows models to learn from data by adjusting weights to minimize error or loss.
""",
    "Backpropagation Explained": """
Backpropagation is the fundamental algorithm used to train neural networks. It's a supervised learning 
algorithm that calculates the gradient of the loss function with respect to the weights of the network.

The process works as follows:
1. Forward pass: Input data flows through the network to produce output
2. Calculate loss: Compare predicted output with actual target
3. Backward pass: Compute gradients of the loss with respect to each weight
4. Update weights: Adjust weights using gradient descent

Backpropagation uses the chain rule from calculus to efficiently compute gradients layer by layer, 
starting from the output layer and moving backward through the network.

This algorithm is essential for deep learning and enables neural networks to learn complex patterns 
from data. Combined with gradient descent, backpropagation allows neural networks to optimize millions 
or even billions of parameters.
"""
}

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks

async def reingest_documents():
    """Re-ingest all done documents."""
    print("=== Document Re-ingestion Tool ===\n")
    
    # Initialize adapters
    print("Initializing adapters...")
    embedding_adapter = await get_embedding_adapter()
    print(f"  Embedding adapter: {embedding_adapter.__class__.__name__}")
    print(f"  Model: {embedding_adapter.model_name}")
    print(f"  Dimension: {embedding_adapter.dimension}")
    
    vector_store = ChromaDBAdapter(host=CHROMA_HOST, port=CHROMA_PORT)
    print(f"  Vector store: ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}\n")
    
    async with AsyncSessionLocal() as session:
        # Get all done documents
        result = await session.execute(
            select(Document).where(Document.status == 'done')
        )
        documents = result.scalars().all()
        
        print(f"Found {len(documents)} documents with status 'done'\n")
        
        if not documents:
            print("No documents to re-ingest.")
            return
        
        # Process each document
        for doc in documents:
            print(f"Processing: {doc.title} (ID: {doc.id})")
            print(f"  Domain: {doc.domain_id}")
            
            # Get sample content based on title
            content = SAMPLE_CONTENTS.get(doc.title)
            if not content:
                print(f"  [WARN] No sample content for '{doc.title}', skipping\n")
                continue
            
            # Create chunks
            chunks = chunk_text(content, chunk_size=500, overlap=50)
            print(f"  Created {len(chunks)} chunks")
            
            # Create collection for domain if not exists
            # Use only the UUID as collection name (ChromaDB requirement)
            collection_name = str(doc.domain_id)
            try:
                await vector_store.create_collection(
                    name=collection_name,
                    dimension=embedding_adapter.dimension,
                    metadata={"domain_id": str(doc.domain_id), "name": doc.title}
                )
                print(f"  Created collection: {collection_name}")
            except Exception as e:
                if "already exists" in str(e).lower() or "409" in str(e):
                    print(f"  Collection exists: {collection_name}")
                else:
                    print(f"  Error creating collection: {e}")
            
            # Generate embeddings and add to vector store
            print(f"  Generating embeddings with {embedding_adapter.model_name}...")
            try:
                embeddings = await embedding_adapter.embed(chunks)
                print(f"  Generated {len(embeddings)} embeddings")
                
                # Create Chunk objects
                chunk_objects = [
                    Chunk(
                        id=f"{doc.id}-chunk-{i}",
                        text=chunks[i],
                        embedding=embeddings[i],
                        metadata={
                            "document_id": str(doc.id),
                            "chunk_index": i,
                            "domain_id": str(doc.domain_id),
                            "title": doc.title
                        }
                    )
                    for i in range(len(chunks))
                ]
                
                # Add to ChromaDB using upsert
                await vector_store.upsert(
                    collection=collection_name,
                    chunks=chunk_objects
                )
                print(f"  [OK] Indexed {len(chunks)} chunks in ChromaDB\n")
                
            except Exception as e:
                print(f"  [ERROR] Error processing document: {e}\n")
                import traceback
                traceback.print_exc()
    
    print("=== Re-ingestion complete ===")

if __name__ == "__main__":
    asyncio.run(reingest_documents())
