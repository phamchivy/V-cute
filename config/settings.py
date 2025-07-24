# 📝 File: config/settings.py - FIXED VERSION

from pathlib import Path
import os

class Config:
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent  # v-cute/
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    VECTORSTORE_DIR = DATA_DIR / "vectorstore" / "chroma_db"
    
    # ✅ SỬA: crawl_data nằm TRONG v-cute (cùng level với config)
    CSV_PATH = PROJECT_ROOT / "crawl_data" / "hungphat_data_4" / "processed_data" / "products_summary_20250723_163031.csv"
    
    # Models
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LLM_MODEL = "llama3:8b"
    
    # Text processing
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50
    MIN_CHUNK_SIZE = 100
    
    # Embedding settings
    BATCH_SIZE = 32
    MAX_LENGTH = 384
    
    # Vector store
    COLLECTION_NAME = "hungphat_products"
    TOP_K_RESULTS = 5
    
    # Ollama
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    OLLAMA_EXECUTABLE = r"C:\Users\DELL\AppData\Local\Programs\Ollama\ollama.exe"
    
    # Test method
    @classmethod
    def test_ollama(cls):
        """Test Ollama availability"""
        import subprocess
        import requests
        
        # Test 1: Executable
        try:
            result = subprocess.run([
                cls.OLLAMA_EXECUTABLE, "list"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Ollama executable working")
            else:
                print(f"❌ Ollama error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Ollama executable issue: {e}")
            return False
        
        # Test 2: HTTP API
        try:
            response = requests.get(f"{cls.OLLAMA_HOST}/api/version", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama API working")
                return True
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ollama API issue: {e}")
            return False
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        dirs = [
            cls.DATA_DIR, cls.RAW_DATA_DIR, cls.PROCESSED_DATA_DIR,
            cls.VECTORSTORE_DIR, cls.VECTORSTORE_DIR.parent
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod  
    def get_latest_csv(cls):
        """Find latest CSV file automatically"""
        crawl_data_dir = cls.PROJECT_ROOT / "crawl_data" / "hungphat_data_4" / "processed_data"
        
        print(f"🔍 Looking for CSV in: {crawl_data_dir}")
        
        if not crawl_data_dir.exists():
            raise FileNotFoundError(f"Directory not found: {crawl_data_dir}")
        
        csv_files = list(crawl_data_dir.glob("products_summary_*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {crawl_data_dir}")
        
        latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
        print(f"✅ Found latest CSV: {latest_csv}")
        return latest_csv

settings = Config()

# 🧪 DEBUG: Test path resolution
if __name__ == "__main__":
    print("🧪 Testing Config Paths:")
    print(f"PROJECT_ROOT: {Config.PROJECT_ROOT}")
    print(f"CSV_PATH: {Config.CSV_PATH}")
    print(f"CSV exists: {Config.CSV_PATH.exists()}")
    
    try:
        latest = Config.get_latest_csv()
        print(f"✅ Latest CSV: {latest}")
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # List available files for debugging
        crawl_dir = Config.PROJECT_ROOT / "crawl_data"
        if crawl_dir.exists():
            print(f"📁 Contents of {crawl_dir}:")
            for item in crawl_dir.rglob("*.csv"):
                print(f"   {item}")
        else:
            print(f"❌ {crawl_dir} does not exist")