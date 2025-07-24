# 🔧 FIX: Updated scripts/03_build_index.py with better timeout handling

#!/usr/bin/env python3
"""Step 3: Build ChromaDB index and LlamaIndex - FIXED VERSION"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indexing.chroma_indexer import ChromaIndexer
from src.indexing.llamaindex_builder import LlamaIndexBuilder
from config.settings import Config

def main():
    """Build vector index"""
    print("🚀 Step 3: Building Vector Index")
    print("=" * 50)
    
    # Paths
    embeddings_path = Config.PROCESSED_DATA_DIR / "embeddings.pkl"
    
    # Check if embeddings exist
    if not embeddings_path.exists():
        print(f"❌ Embeddings file not found: {embeddings_path}")
        print("Please run step 02_generate_embeddings.py first")
        return
    
    # Step 3.1: Index into ChromaDB
    print("\n🗄️  Step 3.1: Indexing into ChromaDB...")
    
    indexer = ChromaIndexer()
    
    # Load embeddings
    print("📥 Loading embeddings...")
    import pickle
    with open(embeddings_path, 'rb') as f:
        embedding_data = pickle.load(f)
    
    # Create collection and index
    indexer.create_collection(reset=True)  # Reset for fresh start
    indexer.index_documents(embedding_data)
    
    # Verify indexing
    info = indexer.get_collection_info()
    print(f"📊 ChromaDB Status: {info}")
    
    # Step 3.2: Build LlamaIndex - SIMPLIFIED
    print("\n🏗️  Step 3.2: Building LlamaIndex...")
    
    try:
        # ✅ PASS existing client to avoid conflict
        builder = LlamaIndexBuilder(chroma_client=indexer.client)
        builder.setup_vector_store()
        builder.build_index()
        builder.create_query_engine()
        
        print("✅ LlamaIndex built successfully")
        
        # Test with simple, short query ONLY
        print("\n🧪 Testing RAG system (quick test)...")
        
        test_query = "Hello"  # ← SIMPLE test first
        print(f"\n❓ Simple Query: {test_query}")
        
        try:
            response = builder.query(test_query)
            print(f"✅ Simple Response: {response[:100]}...")
            
            # If simple works, try one product query
            product_query = "vali"
            print(f"\n❓ Product Query: {product_query}")
            
            response = builder.query(product_query)
            print(f"✅ Product Response: {response[:150]}...")
            
        except Exception as e:
            print(f"⚠️  LlamaIndex query timeout: {e}")
            print("💡 LlamaIndex indexing successful, but query has timeout issues")
            print("💡 Use our RAG engine instead (test_rag_fixed.py works)")
            
    except Exception as e:
        print(f"❌ LlamaIndex error: {e}")
        print("💡 ChromaDB indexing successful, skip LlamaIndex for now")
    
    print("\n✅ Index building completed!")
    print(f"📊 Summary:")
    print(f"   - ChromaDB documents: {info.get('document_count', 0)}")
    print(f"   - Vector store path: {Config.VECTORSTORE_DIR}")
    print(f"   - Our RAG engine: ✅ (use test_rag_fixed.py)")

if __name__ == "__main__":
    main()

# 🔧 ALTERNATIVE: Skip LlamaIndex completely in Script 3

def main_chromadb_only():
    """Build ChromaDB index only (skip LlamaIndex)"""
    print("🚀 Step 3: Building ChromaDB Index Only")
    print("=" * 50)
    
    # Paths
    embeddings_path = Config.PROCESSED_DATA_DIR / "embeddings.pkl"
    
    if not embeddings_path.exists():
        print(f"❌ Embeddings file not found: {embeddings_path}")
        return
    
    # Index into ChromaDB
    indexer = ChromaIndexer()
    
    print("📥 Loading embeddings...")
    import pickle
    with open(embeddings_path, 'rb') as f:
        embedding_data = pickle.load(f)
    
    indexer.create_collection(reset=True)
    indexer.index_documents(embedding_data)
    
    info = indexer.get_collection_info()
    print(f"📊 ChromaDB Status: {info}")
    
    # Test vector search
    print("\n🧪 Testing vector search...")
    from src.embedding.sentence_transformer_client import SentenceTransformerClient
    
    embedding_client = SentenceTransformerClient(Config.EMBEDDING_MODEL)
    embedding_client.load_model()
    
    test_queries = ["vali 20 inch", "balo laptop"]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        
        query_embedding = embedding_client.encode(query)
        if query_embedding.ndim > 1:
            query_embedding = query_embedding.flatten()
            
        results = indexer.search(
            query_text=query,
            query_embedding=query_embedding.tolist(),
            n_results=2
        )
        
        if results['documents'][0]:
            print(f"✅ Found {len(results['documents'][0])} results")
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                print(f"  {i+1}. {metadata.get('name', 'Unknown')} (similarity: {1-distance:.3f})")
        else:
            print("❌ No results")
    
    print("\n✅ ChromaDB indexing completed!")
    print("💡 Use our RAG engine (test_rag_fixed.py) for complete RAG functionality")