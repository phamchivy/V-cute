# 📝 File: rag_pipeline/src/embedding/embedding_generator.py
import json
from pathlib import Path
from typing import List, Dict
import pickle
from src.embedding.sentence_transformer_client import SentenceTransformerClient
from config.settings import Config

class EmbeddingGenerator:
    """Generate embeddings for documents"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.client = SentenceTransformerClient(self.model_name)
        
    def load_documents(self, docs_path: Path) -> List[Dict]:
        """Load documents from JSON"""
        print(f"📂 Loading documents from: {docs_path}")
        
        with open(docs_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        print(f"✅ Loaded {len(documents)} documents")
        return documents
    
    def generate_embeddings(self, documents: List[Dict]) -> Dict:
        """Generate embeddings for all documents"""
        print("🔢 Generating embeddings...")
        
        # Extract texts
        texts = [doc['content'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.client.encode(
            texts,
            batch_size=Config.BATCH_SIZE,
            normalize_embeddings=True,
            show_progress=True
        )
        
        # Create embedding data structure
        embedding_data = {
            'embeddings': embeddings.tolist(),  # Convert to list for JSON
            'documents': documents,
            'metadata': {
                'model_name': self.model_name,
                'embedding_dim': self.client.get_embedding_dimension(),
                'num_documents': len(documents),
                'embedding_shape': embeddings.shape
            }
        }
        
        return embedding_data
    
    def save_embeddings(self, embedding_data: Dict, output_path: Path) -> None:
        """Save embeddings to file"""
        print(f"💾 Saving embeddings to: {output_path}")
        
        # Save as pickle for efficiency
        with open(output_path, 'wb') as f:
            pickle.dump(embedding_data, f)
        
        # Also save metadata as JSON
        metadata_path = output_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(embedding_data['metadata'], f, indent=2)
        
        print(f"✅ Embeddings saved successfully")
        print(f"   - Embedding file: {output_path}")
        print(f"   - Metadata file: {metadata_path}")
    
    def load_embeddings(self, embeddings_path: Path) -> Dict:
        """Load embeddings from file"""
        print(f"📥 Loading embeddings from: {embeddings_path}")
        
        with open(embeddings_path, 'rb') as f:
            embedding_data = pickle.load(f)
        
        print(f"✅ Loaded embeddings: {embedding_data['metadata']['embedding_shape']}")
        return embedding_data