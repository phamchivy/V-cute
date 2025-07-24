# 📝 File: rag_pipeline/src/embedding/sentence_transformer_client.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import torch

class SentenceTransformerClient:
    """Wrapper for sentence-transformers models"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Load the sentence transformer model"""
        print(f"📥 Loading model: {self.model_name}")
        print(f"🔧 Using device: {self.device}")
        
        self.model = SentenceTransformer(self.model_name, device=self.device)
        
        print("✅ Model loaded successfully")
        return self.model
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: int = 32,
               normalize_embeddings: bool = True,
               show_progress: bool = True) -> np.ndarray:
        """Generate embeddings for texts"""
        
        if self.model is None:
            self.load_model()
        
        if isinstance(texts, str):
            texts = [texts]
        
        print(f"🔢 Generating embeddings for {len(texts)} texts...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize_embeddings,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        print(f"✅ Generated embeddings: {embeddings.shape}")
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        if self.model is None:
            self.load_model()
        return self.model.get_sentence_embedding_dimension()