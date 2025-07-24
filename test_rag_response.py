import sys
sys.path.insert(0, '.')
from src.query.rag_engine import RAGEngine

print('🧪 Testing correct methods...')
rag = RAGEngine()
rag.initialize()

query = 'vali 20 inch có khóa TSA'

print(f'\n🔍 Vector search: {query}')
vector_results = rag.query_vector_only(query, 2)
print(f"✅ Found {len(vector_results['documents'][0])} results")

print(f'\n🤖 Full RAG response:')
rag_response = rag.query_with_llm(query)
print(f'Response: {rag_response}')