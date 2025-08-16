# 🔧 FIX: Update src/indexing/llamaindex_builder.py

from llama_index import VectorStoreIndex, StorageContext, ServiceContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import Ollama
import chromadb
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import Config

class LlamaIndexBuilder:
    """Build LlamaIndex with ChromaDB backend - FIXED VERSION"""
    
    def __init__(self, chroma_client=None):  # ← ADD: Accept existing client
        self.chroma_client = chroma_client  # ← REUSE existing client
        self.vector_store = None
        self.index = None
        self.query_engine = None
        
        # Setup embedding model
        self.embed_model = HuggingFaceEmbedding(
            model_name=Config.EMBEDDING_MODEL,
            max_length=Config.MAX_LENGTH
        )
        
        # Setup LLM
        self.llm = Ollama(
            model=Config.LLM_MODEL,
            base_url=Config.OLLAMA_HOST,
            temperature=0.7
        )
        
        # Configure service context
        self.service_context = ServiceContext.from_defaults(
            embed_model=self.embed_model,
            llm=self.llm,
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
    
    def setup_vector_store(self, collection_name: str = None) -> None:
        """Setup ChromaDB vector store - REUSE existing client"""
        print("🔗 Setting up ChromaDB vector store for LlamaIndex...")
        
        collection_name = collection_name or Config.COLLECTION_NAME
        
        # ✅ REUSE existing client instead of creating new one
        if self.chroma_client is None:
            print("⚠️  No existing client provided, creating new one...")
            # Only create if no existing client
            try:
                self.chroma_client = chromadb.PersistentClient(
                    path=str(Config.VECTORSTORE_DIR)
                )
            except ValueError as e:
                if "already exists" in str(e):
                    print("🔧 Using ephemeral client to avoid conflict...")
                    # Fallback: use ephemeral client
                    self.chroma_client = chromadb.EphemeralClient()
                    # But this means we can't access existing data...
                    raise Exception("ChromaDB client conflict. Please restart Python process.")
                else:
                    raise e
        else:
            print("✅ Reusing existing ChromaDB client")
        
        # Get collection
        try:
            chroma_collection = self.chroma_client.get_collection(collection_name)
            print(f"✅ Connected to existing collection: {collection_name}")
        except Exception as e:
            print(f"❌ Collection not found: {e}")
            raise Exception(f"Collection {collection_name} not found. Check indexing step.")
        
        # Create LlamaIndex vector store
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        print("✅ ChromaDB vector store ready")
    
    def build_index(self) -> VectorStoreIndex:
        """Build LlamaIndex from existing ChromaDB"""
        print("🏗️  Building LlamaIndex...")
        
        if self.vector_store is None:
            self.setup_vector_store()
        
        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        # Build index from existing vector store
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            storage_context=storage_context,
            service_context=self.service_context
        )
        
        print("✅ LlamaIndex built successfully")
        return self.index
    
    def create_query_engine(self, similarity_top_k: int = None):
        """Create query engine"""
        print("🔍 Creating query engine...")
        
        if self.index is None:
            self.build_index()
        
        similarity_top_k = similarity_top_k or Config.TOP_K_RESULTS
        
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=similarity_top_k,
            response_mode="compact"
        )
        
        print("✅ Query engine ready")
        return self.query_engine
    
    def query(self, question: str) -> str:
        """Query the RAG system"""
        if self.query_engine is None:
            self.create_query_engine()
        
        response = self.query_engine.query(question)
        return str(response)