# 🔧 FIX: Update src/query/rag_engine.py to use our embeddings

from typing import List, Dict, Optional
from pathlib import Path

from src.indexing.chroma_indexer import ChromaIndexer
from src.indexing.llamaindex_builder import LlamaIndexBuilder
from src.query.llama3_client import Llama3Client
from config.settings import Config
from src.embedding.sentence_transformer_client import SentenceTransformerClient
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import Config

class RAGEngine:
    """Complete RAG system - FIXED to use our embeddings"""
    
    def __init__(self):
        # Components
        self.chroma_indexer = ChromaIndexer()
        self.llamaindex_builder = LlamaIndexBuilder()
        self.llama3_client = Llama3Client()
        
        # ✅ Use SAME embedding model as indexing
        self.embedding_client = SentenceTransformerClient(Config.EMBEDDING_MODEL)
        
        # State
        self.is_initialized = False
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
    
    def initialize(self) -> None:
        """Initialize all components"""
        print("Initializing RAG Engine...")
        self.chroma_indexer.create_collection()
        
        # Check ChromaDB
        info = self.chroma_indexer.get_collection_info()
        if info['status'] != 'ready':
            raise Exception(f"ChromaDB not ready: {info}")
        
        print(f"ChromaDB ready: {info['document_count']} documents")
        
        # ✅ Load OUR embedding model (not ChromaDB default)
        print("Loading our embedding model...")
        self.embedding_client.load_model()
        print("Embedding model ready")
        
        # Check Llama3
        if not self.llama3_client.check_model_availability():
            print(f"Warning: Llama3 model {self.llama3_client.model} not available")
        else:
            print("Llama3 model ready")
        
        self.is_initialized = True
        print("RAG Engine initialized successfully!")
    
    def query_vector_only(self, question: str, n_results: int = None) -> Dict:
        """Query using vector search only (no LLM) - FIXED"""
        if not self.is_initialized:
            self.initialize()
        
        n_results = n_results or Config.TOP_K_RESULTS
        
        try:
            # ✅ Use OUR embedding model for query
            query_embedding = self.embedding_client.encode(question)
            
            # ✅ FIX: Flatten embedding properly
            if query_embedding.ndim > 1:
                query_embedding_flat = query_embedding.flatten()
            else:
                query_embedding_flat = query_embedding
                
            print(f"Embedding shape: {query_embedding.shape} -> flattened: {query_embedding_flat.shape}")
            
            # ✅ Search with properly formatted embedding
            search_results = self.chroma_indexer.search(
                query_text=question,
                query_embedding=query_embedding_flat.tolist(),  # Now 1D
                n_results=n_results
            )
            
            return search_results
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def query_with_llm(self, question: str, n_results: int = None) -> str:
        """Query with vector search + LLM generation"""
        if not self.is_initialized:
            self.initialize()
        
        # Step 1: Vector search
        search_results = self.query_vector_only(question, n_results)
        
        if not search_results['documents'][0]:
            return "Xin lỗi, tôi không tìm thấy thông tin phù hợp với câu hỏi của bạn."
        
        # Step 2: Build context
        context = self._build_context(search_results, question)
        
        # Step 3: Generate response with Llama3
        try:
            response = self.llama3_client.generate(
                prompt=question,
                system_prompt=context,
                temperature=0.3,  # Lower for more focused response
                max_tokens=300    # Shorter to avoid timeout
            )
            return response
        except Exception as e:
            # Fallback: return vector search results
            print(f"LLM error: {e}")
            return self._format_vector_results(search_results)
    
    def _format_vector_results(self, search_results: Dict) -> str:
        """Format vector search results as fallback"""
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        distances = search_results['distances'][0]
        
        response_parts = ["Dựa trên tìm kiếm vector, tôi tìm thấy:\n"]
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), 1):
            similarity = 1 - distance
            response_parts.append(f"\n{i}. {metadata.get('name', 'Sản phẩm')}")
            response_parts.append(f"   Độ liên quan: {similarity:.2f}")
            response_parts.append(f"   {doc[:150]}...")
        
        return "\n".join(response_parts)
    
    def _build_context(self, search_results: Dict, question: str) -> str:
        """Build context from search results using query templates"""
        try:
            from config.settings import Config
            
            # Load template file
            templates_file = Config.PROJECT_ROOT / "config" / "prompts" / "query_templates.txt"
            
            # Default template fallback
            default_template = """{system_prompt}

            THÔNG TIN SẢN PHẨM LIÊN QUAN:
            {retrieved_products}

            CÂU HỎI: {user_question}

            Hãy phân tích thông tin trên và đưa ra lời khuyên phù hợp nhất cho khách hàng."""

            # Try to load template from file
            template = default_template
            if templates_file.exists():
                with open(templates_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract PRODUCT_RECOMMENDATION template
                    if '[PRODUCT_RECOMMENDATION]' in content:
                        start = content.find('[PRODUCT_RECOMMENDATION]') + len('[PRODUCT_RECOMMENDATION]')
                        end = content.find('[', start)
                        if end == -1:
                            end = len(content)
                        template = content[start:end].strip()
                        print("Loaded template from file")
                    else:
                        print("PRODUCT_RECOMMENDATION template not found, using default")
            else:
                print("Templates file not found, using default")
            
            # Format products data
            documents = search_results['documents'][0]
            metadatas = search_results['metadatas'][0] if 'metadatas' in search_results else [{}] * len(documents)
            distances = search_results['distances'][0] if 'distances' in search_results else [0.5] * len(documents)
            
            product_parts = []
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), 1):
                product_info = f"""Sản phẩm {i}:
                - Tên: {metadata.get('name', 'N/A')}
                - Danh mục: {metadata.get('category', 'N/A')}
                - Chi tiết: {doc[:200]}{'...' if len(doc) > 200 else ''}
                - Độ liên quan: {1-distance:.2f}"""
                product_parts.append(product_info)
            
            formatted_products = '\n\n'.join(product_parts)
            
            # Use template to build context
            context = template.format(
                system_prompt=self.system_prompt,
                retrieved_products=formatted_products,
                user_question=question
            )
            
            return context
            
        except Exception as e:
            print(f"Error with template: {e}, using fallback")
            
            # Fallback to original logic
            context_parts = [self.system_prompt]
            context_parts.append("\nTHÔNG TIN SẢN PHẨM LIÊN QUAN:")
            
            documents = search_results['documents'][0]
            metadatas = search_results['metadatas'][0] if 'metadatas' in search_results else [{}] * len(documents)
            distances = search_results['distances'][0] if 'distances' in search_results else [0.5] * len(documents)
            
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), 1):
                context_parts.append(f"\nSản phẩm {i}:")
                context_parts.append(f"Tên: {metadata.get('name', 'N/A')}")
                context_parts.append(f"Danh mục: {metadata.get('category', 'N/A')}")
                
                doc_snippet = doc[:200] + "..." if len(doc) > 200 else doc
                context_parts.append(f"Chi tiết: {doc_snippet}")
                context_parts.append(f"Độ liên quan: {1-distance:.2f}")
            
            context_parts.append(f"\nCâu hỏi: {question}")
            
            return "\n".join(context_parts)
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file with fallback to default"""
        try:
            # Import Config directly since RAGEngine doesn't have self.config
            from config.settings import Config
            
            # Build path to system prompt file
            prompt_file = Config.PROJECT_ROOT / "config" / "prompts" / "system_prompt.txt"
            
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    system_prompt = f.read().strip()
                    
                if system_prompt:  # Check if file is not empty
                    print(f"Loaded system prompt from: {prompt_file}")
                    return system_prompt
                else:
                    print(f"System prompt file is empty: {prompt_file}")
            else:
                print(f"⚠️ System prompt file not found: {prompt_file}")
                # Auto-create the prompt file
                Config.create_default_prompts()
                
                # Try loading again after creation
                if prompt_file.exists():
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        system_prompt = f.read().strip()
                    if system_prompt:
                        print(f"Created and loaded system prompt from: {prompt_file}")
                        return system_prompt
                
        except Exception as e:
            print(f"Error loading system prompt file: {e}")
        
        # Fallback to default prompt
        fallback_prompt = """Bạn là chuyên gia tư vấn sản phẩm vali, balo của Công ty Cổ phần Hùng Phát. 
    Hãy tư vấn sản phẩm phù hợp nhất cho khách hàng dựa trên thông tin được cung cấp. 
    Trả lời bằng tiếng Việt, ngắn gọn và thực tế, tập trung vào 1-2 sản phẩm tốt nhất."""
        
        print("Using fallback system prompt")
        return fallback_prompt

# 🧪 TEST: Create comprehensive test

def test_rag_comprehensive():
    """Test RAG engine comprehensively"""
    
    print("Testing RAG Engine...")
    
    # Initialize
    rag = RAGEngine()
    rag.initialize()
    
    test_queries = [
        "Vali 20 inch tốt nhất",
        "Vali có khóa TSA",
        "Balo laptop"
    ]
    
    for query in test_queries:
        print(f"\n" + "="*50)
        print(f"Query: {query}")
        print("="*50)
        
        # Test 1: Vector search only
        print("\n🔍 Vector Search Results:")
        vector_results = rag.query_vector_only(query, n_results=3)
        
        if vector_results['documents'][0]:
            for i, doc in enumerate(vector_results['documents'][0]):
                metadata = vector_results['metadatas'][0][i]
                distance = vector_results['distances'][0][i]
                similarity = 1 - distance
                
                print(f"\n{i+1}. {metadata.get('name', 'Unknown')}")
                print(f"   Similarity: {similarity:.3f}")
                print(f"   Preview: {doc[:80]}...")
        else:
            print("No vector results")
        
        # Test 2: Full RAG (Vector + LLM)
        print(f"\nRAG Response:")
        try:
            rag_response = rag.query_with_llm(query)
            print(f"{rag_response}")
        except Exception as e:
            print(f"RAG Error: {e}")
    
    print(f"\nRAG testing completed!")

if __name__ == "__main__":
    test_rag_comprehensive()