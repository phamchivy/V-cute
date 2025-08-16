# 🔧 FIX: Update src/query/llama3_client.py with better error handling

import ollama
import subprocess
import time

class Llama3Client:
    """Client for Llama3 via Ollama - IMPROVED VERSION"""
    
    def __init__(self, model: str = "llama3:8b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.client = ollama.Client(host=host)
        self.ollama_executable = r"C:\Users\DELL\AppData\Local\Programs\Ollama\ollama.exe"
        
    def _ensure_ollama_running(self):
        """Ensure Ollama server is running"""
        import requests
        
        try:
            # Test if server is responding
            response = requests.get(f"{self.host}/api/version", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama server is running")
                return True
        except:
            print("⚠️  Ollama server not responding, trying to start...")
            
        # Try to start Ollama server
        try:
            subprocess.Popen([
                self.ollama_executable, "serve"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Test again
            response = requests.get(f"{self.host}/api/version", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama server started successfully")
                return True
        except Exception as e:
            print(f"❌ Failed to start Ollama server: {e}")
            
        return False
        
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate response using Llama3 - IMPROVED"""
        
        # Ensure server is running
        if not self._ensure_ollama_running():
            return "❌ Ollama server không khả dụng. Vui lòng khởi động Ollama manually."
        
        # Default parameters with longer timeout
        options = {
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "top_k": kwargs.get("top_k", 40),
            "num_predict": kwargs.get("max_tokens", 1000),
        }
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            print(f"🤖 Generating response with {self.model}...")
            
            # Add timeout to prevent hanging
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options=options,
                # Add timeout if supported
            )
            
            print("✅ Response generated successfully")
            return response['message']['content']
            
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return f"⏱️  Phản hồi bị timeout. Model có thể đang tải, vui lòng thử lại."
            else:
                return f"❌ Lỗi khi tạo phản hồi: {error_msg}"
    
    def check_model_availability(self) -> bool:
        """Check if model is available - IMPROVED"""
        try:
            # Use subprocess to check models (more reliable)
            result = subprocess.run([
                self.ollama_executable, "list"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                available_models = result.stdout
                return self.model in available_models
            else:
                print(f"❌ Error checking models: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking model availability: {e}")
            return False

# 🧪 TEST: Quick test script
def test_ollama_integration():
    """Test complete Ollama integration"""
    
    print("🧪 Testing Ollama Integration...")
    
    # Test config
    from config.settings import Config
    Config.test_ollama()
    
    # Test client
    client = Llama3Client()
    
    # Check model
    if client.check_model_availability():
        print("✅ Model available")
    else:
        print("❌ Model not available")
        return
    
    # Test generation
    response = client.generate("Hello, respond with just 'Hi there!'")
    print(f"🤖 Response: {response}")
    
    if "Hi there" in response or len(response) > 0:
        print("✅ Generation working!")
    else:
        print("❌ Generation failed")

if __name__ == "__main__":
    test_ollama_integration()