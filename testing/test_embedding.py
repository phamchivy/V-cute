# 🔧 FIX: Use pre-computed embeddings instead of ChromaDB default

# Cancel current download (Ctrl+C) and use this approach:

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from src.indexing.chroma_indexer import ChromaIndexer
from src.embedding.sentence_transformer_client import SentenceTransformerClient

def test_with_precomputed_embeddings():
    """Test using our pre-computed embedding model"""
    
    print("🔍 Testing with pre-computed embedding model...")
    
    # 1. Initialize our embedding client (same model as indexing)
    embedding_client = SentenceTransformerClient(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    embedding_client.load_model()
    
    # 2. Initialize ChromaDB indexer
    indexer = ChromaIndexer()
    indexer.create_collection()
    
    # 3. Test queries
    queries = ["vali 20 inch", "vali có khóa TSA", "balo laptop"]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        
        try:
            # Encode query using OUR model (not ChromaDB default)
            query_embedding = embedding_client.encode(query)
            
            # Search using embedding vector (not text)
            results = indexer.search(
                query_text=query,  # For logging
                query_embedding=query_embedding.tolist(),  # Use our embedding
                n_results=3
            )
            
            if results['documents'][0]:
                print(f"✅ Found {len(results['documents'][0])} results")
                
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    
                    print(f"\n{i+1}. {metadata.get('name', 'Unknown')}")
                    print(f"   Similarity: {similarity:.3f}")
                    print(f"   Preview: {doc[:80]}...")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    print("\n✅ Pre-computed embedding test completed!")

# 🔧 UPDATE: Fix chroma_indexer.py search method

def update_chroma_indexer_search():
    """Show updated search method"""
    
    class ChromaIndexer:
        def search(self, query_text: str, query_embedding: list = None, n_results: int = 5):
            """Search using embedding if provided, otherwise use text"""
            
            if query_embedding:
                # Use pre-computed embedding (OUR approach)
                print("🔍 Using pre-computed embedding for search")
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    include=['documents', 'metadatas', 'distances']
                )
            else:
                # Use ChromaDB default embedding (causes download)
                print("⚠️  Using ChromaDB default embedding")
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    include=['documents', 'metadatas', 'distances']
                )
            
            return results

# 🧪 QUICK TEST: Cancel download and run this
def quick_test_no_download():
    """Quick test without model download"""
    
    print("🧪 Quick test - using existing embeddings...")
    
    # Load our embeddings
    import pickle
    with open('data/processed/embeddings.pkl', 'rb') as f:
        embedding_data = pickle.load(f)
    
    print(f"✅ Loaded {len(embedding_data['documents'])} documents")
    print(f"✅ Embedding model: {embedding_data['metadata']['model_name']}")
    print(f"✅ Embedding dimension: {embedding_data['metadata']['embedding_dim']}")
    
    # Test: Find similar documents by comparing embeddings directly
    import numpy as np
    
    # Get first few document embeddings
    embeddings = np.array(embedding_data['embeddings'])
    documents = embedding_data['documents']
    
    print(f"\n📋 Sample documents:")
    for i in range(min(3, len(documents))):
        doc = documents[i]
        print(f"{i+1}. {doc['metadata'].get('name', 'Unknown')}")
        print(f"   Content: {doc['content'][:80]}...")
    
    print("\n✅ Embeddings are ready - no download needed!")

if __name__ == "__main__":
    # Run this instead of ChromaDB search
    quick_test_no_download()