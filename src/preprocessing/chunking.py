from typing import List, Dict
from llama_index import Document  # ← SỬA: Không có .core
from llama_index.text_splitter import SentenceSplitter  # ← SỬA: Không có .core
import json

class DocumentChunker:
    """Split documents into chunks for RAG"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator="\n"
        )
    
    def chunk_documents(self, documents: List[Dict]) -> List[Document]:
        """Split documents into chunks"""
        print(f"📝 Chunking {len(documents)} documents...")
        
        chunked_docs = []
        
        for doc in documents:
            # Create LlamaIndex Document
            llamaindex_doc = Document(
                text=doc['content'],
                metadata=doc['metadata']
            )
            
            # Split into chunks
            chunks = self.splitter.split_text(doc['content'])
            
            for i, chunk_text in enumerate(chunks):
                # Create chunk metadata
                chunk_metadata = doc['metadata'].copy()
                chunk_metadata.update({
                    'chunk_id': f"{doc['id']}_chunk_{i}",
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'chunk_size': len(chunk_text)
                })
                
                # Create chunk document
                chunk_doc = Document(
                    text=chunk_text,
                    metadata=chunk_metadata
                )
                
                chunked_docs.append(chunk_doc)
        
        print(f"✅ Created {len(chunked_docs)} chunks from {len(documents)} documents")
        return chunked_docs
    
    def save_chunks(self, chunks: List[Document], output_path) -> None:
        """Save chunks to JSON file"""
        chunk_data = []
        
        for chunk in chunks:
            chunk_data.append({
                'text': chunk.text,
                'metadata': chunk.metadata
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {len(chunks)} chunks to: {output_path}")