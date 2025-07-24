# 📝 File: rag_pipeline/scripts/02_generate_embeddings.py
#!/usr/bin/env python3
"""Step 2: Generate embeddings"""

import sys
from pathlib import Path

# Add src to path
#sys.path.append(str(Path(__file__).parent.parent / "src"))

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent  # Go up from scripts/ to v-cute/
sys.path.insert(0, str(PROJECT_ROOT))

from src.embedding.embedding_generator import EmbeddingGenerator
from config.settings import Config

def main():
    """Generate embeddings for processed documents"""
    print("🚀 Step 2: Embedding Generation")
    print("=" * 50)
    
    # Input/output paths
    docs_path = Config.PROCESSED_DATA_DIR / "documents.json"
    embeddings_path = Config.PROCESSED_DATA_DIR / "embeddings.pkl"
    
    # Check if documents exist
    if not docs_path.exists():
        print(f"❌ Documents file not found: {docs_path}")
        print("Please run step 01_preprocess_data.py first")
        return
    
    # Initialize generator
    generator = EmbeddingGenerator()
    
    # Load documents
    documents = generator.load_documents(docs_path)
    
    # Generate embeddings
    embedding_data = generator.generate_embeddings(documents)
    
    # Save embeddings
    generator.save_embeddings(embedding_data, embeddings_path)
    
    print("\n✅ Embedding generation completed!")
    print(f"📊 Summary:")
    print(f"   - Model: {embedding_data['metadata']['model_name']}")
    print(f"   - Documents: {embedding_data['metadata']['num_documents']}")
    print(f"   - Embedding dimension: {embedding_data['metadata']['embedding_dim']}")
    print(f"   - Output file: {embeddings_path}")

if __name__ == "__main__":
    main()