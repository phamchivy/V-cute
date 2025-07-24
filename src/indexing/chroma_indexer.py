# 📝 File: rag_pipeline/src/indexing/chroma_indexer.py
import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import json
import pickle

from config.settings import Config

class ChromaIndexer:
    """Index documents into ChromaDB"""
    
    def __init__(self, persist_directory: Path = None, collection_name: str = None):
        self.persist_directory = persist_directory or Config.VECTORSTORE_DIR
        self.collection_name = collection_name or Config.COLLECTION_NAME
        
        # Create directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = None
        
    def create_collection(self, reset: bool = False) -> None:
        """Create or get ChromaDB collection"""
        print(f"🗄️  Setting up ChromaDB collection: {self.collection_name}")
        
        try:
            if reset:
                # Delete existing collection
                try:
                    self.client.delete_collection(self.collection_name)
                    print("🗑️  Deleted existing collection")
                except:
                    pass
            
            # Try to get existing collection
            try:
                self.collection = self.client.get_collection(self.collection_name)
                print(f"✅ Using existing collection with {self.collection.count()} documents")
            except:
                # Create new collection
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Hùng Phát product database"}
                )
                print("✅ Created new collection")
                
        except Exception as e:
            print(f"❌ Error setting up collection: {e}")
            raise
    
    def index_documents(self, embedding_data: Dict) -> None:
        """Index documents with embeddings into ChromaDB"""
        print("📇 Indexing documents into ChromaDB...")
        
        if self.collection is None:
            self.create_collection()
        
        documents = embedding_data['documents']
        embeddings = embedding_data['embeddings']
        
        # Prepare data for ChromaDB
        ids = []
        texts = []
        metadatas = []
        embeddings_list = []
        
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            ids.append(doc['id'])
            texts.append(doc['content'])
            
            # Prepare metadata (ChromaDB doesn't support nested objects)
            metadata = {}
            for key, value in doc['metadata'].items():
                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = value
                elif isinstance(value, list):
                    # Convert list to string
                    metadata[key] = json.dumps(value) if value else ""
                else:
                    metadata[key] = str(value) if value is not None else ""
            
            metadatas.append(metadata)
            embeddings_list.append(embedding)
        
        # Add to collection in batches
        batch_size = 100
        total_docs = len(documents)
        
        for i in range(0, total_docs, batch_size):
            end_idx = min(i + batch_size, total_docs)
            batch_ids = ids[i:end_idx]
            batch_texts = texts[i:end_idx]
            batch_metadatas = metadatas[i:end_idx]
            batch_embeddings = embeddings_list[i:end_idx]
            
            try:
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    embeddings=batch_embeddings
                )
                print(f"📥 Indexed batch {i//batch_size + 1}/{(total_docs-1)//batch_size + 1} ({end_idx}/{total_docs} documents)")
                
            except Exception as e:
                print(f"❌ Error indexing batch {i//batch_size + 1}: {e}")
                raise
        
        print(f"✅ Successfully indexed {total_docs} documents into ChromaDB")
        
    def search(self, query_text: str, query_embedding: List[float] = None, 
               n_results: int = None) -> Dict:
        """Search similar documents"""
        if self.collection is None:
            self.create_collection()
        
        n_results = n_results or Config.TOP_K_RESULTS
        
        # Search using embedding if provided, otherwise use text
        if query_embedding:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
        else:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
        
        return results
    
    def get_collection_info(self) -> Dict:
        """Get collection information"""
        if self.collection is None:
            return {"status": "not_initialized"}
        
        try:
            count = self.collection.count()
            return {
                "status": "ready",
                "name": self.collection_name,
                "document_count": count,
                "persist_directory": str(self.persist_directory)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}