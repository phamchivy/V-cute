# 📝 File: rag_pipeline/scripts/01_preprocess_data.py
#!/usr/bin/env python3
"""Step 1: Preprocess raw data"""

import sys
from pathlib import Path

# Add src to path
#sys.path.append(str(Path(__file__).parent.parent / "src"))

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent  # Go up from scripts/ to v-cute/
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import Config
from src.preprocessing.data_cleaner import DataCleaner
from src.preprocessing.text_processor import TextProcessor
from src.preprocessing.chunking import DocumentChunker
import pandas as pd
import json

def main():
    """Run preprocessing pipeline"""
    print("🚀 Step 1: Data Preprocessing")
    print("=" * 50)
    
    # Create directories
    Config.create_directories()

    # ✅ SỬA: Check CSV exists before processing
    try:
        csv_path = Config.get_latest_csv()
        print(f"📂 Found CSV: {csv_path}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Please ensure crawl_data is in parent directory")
        return
    
    # Step 1.1: Clean data
    print("\n📋 Step 1.1: Cleaning CSV data...")
    cleaner = DataCleaner(Config.CSV_PATH)
    cleaned_df = cleaner.clean_data()
    
    # Save cleaned data
    cleaned_csv_path = Config.PROCESSED_DATA_DIR / "cleaned_data.csv"
    cleaner.save_cleaned_data(cleaned_csv_path)
    
    # Step 1.2: Create documents
    print("\n📄 Step 1.2: Creating documents...")
    documents = []
    
    for _, row in cleaned_df.iterrows():
        doc = TextProcessor.create_product_document(row)
        documents.append(doc)
    
    # Save documents
    docs_path = Config.PROCESSED_DATA_DIR / "documents.json"
    with open(docs_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(documents)} documents to: {docs_path}")
    
    # Step 1.3: Chunk documents
    print("\n✂️  Step 1.3: Chunking documents...")
    chunker = DocumentChunker(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    
    chunks = chunker.chunk_documents(documents)
    
    # Save chunks
    chunks_path = Config.PROCESSED_DATA_DIR / "chunks.json"
    chunker.save_chunks(chunks, chunks_path)
    
    print("\n✅ Preprocessing completed!")
    print(f"📊 Summary:")
    print(f"   - Cleaned records: {len(cleaned_df)}")
    print(f"   - Documents created: {len(documents)}")
    print(f"   - Text chunks: {len(chunks)}")
    print(f"   - Average chunk size: {sum(len(c.text) for c in chunks) // len(chunks)} chars")

if __name__ == "__main__":
    main()