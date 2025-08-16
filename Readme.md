# 🏗️ V-CUTE (Ollama + Ngrok version)

Complete RAG (Retrieval-Augmented Generation) pipeline for Hùng Phát product consultation using:
- **LlamaIndex** for RAG framework
- **ChromaDB** for vector storage
- **Sentence Transformers** for embeddings
- **Llama3** via Ollama for generation

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv rag_env
source rag_env/bin/activate  # Linux/Mac
# rag_env\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Ollama and Llama3
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3:8b
```

### 2. Prepare Data
```bash
# Link your CSV data
ln -s /path/to/your/products.csv data/raw/products.csv
```

### 3. Run Pipeline
```bash
# Option 1: Run complete pipeline
python scripts/run_full_pipeline.py

# Option 2: Run step by step
python scripts/01_preprocess_data.py
python scripts/02_generate_embeddings.py  
python scripts/03_build_index.py
python scripts/04_test_rag.py
```

## 📁 Structure
```
rag_pipeline/
├── data/              # Data storage
├── src/               # Source code
│   ├── preprocessing/ # Text processing & chunking
│   ├── embedding/     # Embedding generation
│   ├── indexing/      # ChromaDB & LlamaIndex
│   └── query/         # RAG query engine
├── scripts/           # Execution scripts
└── config/            # Configuration files
```

## 🔧 Configuration

Edit `config/settings.py` to customize:
- Embedding model
- Chunk size/overlap
- Vector store settings
- Llama3 parameters

## 🧪 Testing

```bash
# Test RAG system
python scripts/04_test_rag.py

# Interactive testing
python -c "
from src.query.rag_engine import RAGEngine
rag = RAGEngine()
rag.initialize()
print(rag.query_hybrid('Vali 20 inch có khóa TSA'))
"
```

## 📊 Performance

Expected processing times:
- **Preprocessing**: ~30s for 200 products
- **Embeddings**: ~2-5min depending on model
- **Indexing**: ~10-30s
- **Query**: ~1-3s per query

## 🎯 Next Steps

1. ✅ RAG Pipeline Setup
2. 🔄 Facebook Bot Integration
3. 🚀 API Deployment
4. 📈 Performance Monitoring

## 🐛 Troubleshooting

**Ollama Connection Issues:**
```bash
# Check Ollama status
ollama list
ollama serve

# Test Llama3
ollama run llama3:8b "Hello"
```

**ChromaDB Issues:**
```bash
# Clear ChromaDB
rm -rf data/vectorstore/chroma_db
python scripts/03_build_index.py
```

**Memory Issues:**
- Reduce batch_size in config/settings.py
- Use smaller embedding model
- Process data in chunks