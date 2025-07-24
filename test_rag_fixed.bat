# Create test file
echo # Test updated RAG > test_rag_fixed.py
echo import sys >> test_rag_fixed.py
echo sys.path.insert(0, '.') >> test_rag_fixed.py
echo. >> test_rag_fixed.py
echo from src.query.rag_engine import RAGEngine >> test_rag_fixed.py
echo. >> test_rag_fixed.py
echo print('🧪 Testing Fixed RAG Engine...') >> test_rag_fixed.py
echo rag = RAGEngine() >> test_rag_fixed.py
echo rag.initialize() >> test_rag_fixed.py
echo. >> test_rag_fixed.py
echo # Test vector search only >> test_rag_fixed.py
echo results = rag.query_vector_only('vali 20 inch', 2) >> test_rag_fixed.py
echo print(f'Found {len(results["documents"][0])} results') >> test_rag_fixed.py
echo for i, doc in enumerate(results['documents'][0]): >> test_rag_fixed.py
echo     metadata = results['metadatas'][0][i] >> test_rag_fixed.py
echo     print(f'{i+1}. {metadata.get("name", "Unknown")}') >> test_rag_fixed.py

python test_rag_fixed.py