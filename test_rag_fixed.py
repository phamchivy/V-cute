# Test updated RAG 
import sys 
sys.path.insert(0, '.') 
 
from src.query.rag_engine import RAGEngine 
 
print('🧪 Testing Fixed RAG Engine...') 
rag = RAGEngine() 
rag.initialize() 
 
# Test vector search only 
results = rag.query_vector_only('vali 20 inch', 2) 
print(f'Found {len(results["documents"][0])} results') 
for i, doc in enumerate(results['documents'][0]): 
    metadata = results['metadatas'][0][i] 
    print(f'{i+1}. {metadata.get("name", "Unknown")}') 
