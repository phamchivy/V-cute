#!/usr/bin/env python3
"""
Check for dependency conflicts before installing Facebook bot packages
"""

import pkg_resources
import subprocess
import sys

def get_installed_packages():
    """Get currently installed packages"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error getting packages: {e}")
        return ""

def check_conflicts():
    """Check for potential conflicts"""
    print("🔍 Checking current RAG environment...")
    
    # Current packages
    installed = get_installed_packages()
    print("✅ Current packages:")
    
    key_packages = ['llama-index', 'chromadb', 'torch', 'transformers', 'flask', 'requests']
    
    for package in key_packages:
        if package.lower() in installed.lower():
            # Extract version info
            lines = installed.split('\n')
            for line in lines:
                if package.lower() in line.lower():
                    print(f"   📦 {line.strip()}")
                    break
        else:
            print(f"   ❌ {package}: Not installed")
    
    # Check for known conflicts
    conflicts = []
    
    # Flask version conflicts
    if 'flask' in installed.lower():
        print("\n⚠️ Flask already installed - check version compatibility")
        conflicts.append("Flask version")
    
    # Requests conflicts
    if 'requests' in installed.lower():
        print("✅ Requests already installed - should be compatible")
    
    print(f"\n🎯 Recommendation:")
    if conflicts:
        print("⚠️ POTENTIAL CONFLICTS detected")
        print("💡 Consider using separate environment")
        print("   OR test installation in current environment first")
    else:
        print("✅ NO CONFLICTS expected")
        print("💡 Safe to install in current rag_env")
        print("\nInstall command:")
        print("pip install flask requests pyngrok werkzeug pytz emoji")

def test_imports():
    """Test if key imports work"""
    print("\n🧪 Testing key imports...")
    
    imports_to_test = [
        ('llama_index', 'LlamaIndex'),
        ('chromadb', 'ChromaDB'),
        ('sentence_transformers', 'SentenceTransformers'),
        ('torch', 'PyTorch'),
        ('flask', 'Flask'),
        ('requests', 'Requests'),
        ('ollama', 'Ollama')
    ]
    
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"   ✅ {name}: OK")
        except ImportError:
            print(f"   ❌ {name}: Not available")
        except Exception as e:
            print(f"   ⚠️ {name}: Error - {e}")

if __name__ == "__main__":
    print("🔧 RAG Environment Dependency Check")
    print("=" * 40)
    
    check_conflicts()
    test_imports()
    
    print("\n" + "=" * 40)
    print("🎯 Final Recommendation:")
    print("1. Try installing in current rag_env first")
    print("2. If any conflicts, create separate environment") 
    print("3. Test both RAG and Facebook bot functionality")