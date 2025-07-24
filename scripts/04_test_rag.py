# 🔧 FIX: Update scripts/04_test_rag.py

#!/usr/bin/env python3
"""Step 4: Test RAG system - FIXED VERSION"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.query.rag_engine import RAGEngine

def main():
    """Test RAG system with sample queries"""
    print("🚀 Step 4: Testing RAG System")
    print("=" * 50)
    
    # Initialize RAG engine
    print("🔧 Initializing RAG Engine...")
    rag = RAGEngine()
    
    try:
        rag.initialize()
    except Exception as e:
        print(f"❌ Failed to initialize RAG engine: {e}")
        return
    
    # Test queries
    test_queries = [
        "Tôi cần vali 20 inch có khóa TSA",
        "Vali nào nhẹ nhất cho cabin?", 
        "So sánh vali nhựa ABS và PC",
        "Balo laptop tốt nhất",
        "Vali cho chuyến đi 1 tuần",
        "Sản phẩm nào có bánh xe spinner?"
    ]
    
    print(f"\n🧪 Testing with {len(test_queries)} queries...")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{len(test_queries)}: {query}")
        print("-" * 40)
        
        # Test 1: Vector Search Only
        print("🔍 Vector Search Results:")
        try:
            vector_results = rag.query_vector_only(query, n_results=3)  # ✅ FIXED METHOD
            
            if vector_results['documents'][0]:
                print(f"✅ Found {len(vector_results['documents'][0])} results")
                
                for j, doc in enumerate(vector_results['documents'][0]):
                    metadata = vector_results['metadatas'][0][j]
                    distance = vector_results['distances'][0][j]
                    similarity = 1 - distance
                    
                    print(f"  {j+1}. {metadata.get('name', 'Unknown')}")
                    print(f"     Similarity: {similarity:.3f}")
                    print(f"     Preview: {doc[:80]}...")
            else:
                print("❌ No vector results found")
                
        except Exception as e:
            print(f"❌ Vector search error: {e}")
        
        # Test 2: Full RAG (Vector + LLM)
        print(f"\n🤖 Complete RAG Response:")
        try:
            rag_response = rag.query_with_llm(query)  # ✅ FIXED METHOD
            print(f"✅ {rag_response}")
        except Exception as e:
            print(f"❌ RAG Error: {e}")
        
        print("-" * 40)
    
    print("\n✅ RAG Testing completed!")
    print("\n🎯 Next steps:")
    print("1. Fine-tune prompts for better responses")
    print("2. Add more test queries")
    print("3. Deploy as API service")

if __name__ == "__main__":
    main()