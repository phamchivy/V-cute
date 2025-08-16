# File: setup.py (Safe version)
from setuptools import setup, find_packages

setup(
    name="hungphat-facebook-bot",
    version="1.0.0",
    description="RAG-powered Facebook Bot for Hung Phat products",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "flask",
        "requests", 
        "llama-index==0.9.48",
        "chromadb==0.4.24",
        "sentence-transformers==2.2.2",
        "ollama==0.1.7",
        "pandas==2.1.4",
        "python-dotenv",
        "pyngrok"
    ],
    # ✅ SAFE: Only include template/example configs
    package_data={
        "facebook_bot": [
            "config/*.yaml",           # ✅ Safe config templates
            "config/*.json",           # ✅ Safe settings
            "config/example.env",      # ✅ Example only
        ],
        "rag_pipeline": [
            "config/*.yaml",           # ✅ Model configs
            "config/*.json"            # ✅ Safe settings
        ]
    },
    # ✅ EXCLUDE sensitive files explicitly
    exclude_package_data={
        "": [
            "*.env",                   # ❌ Exclude all .env files
            "*_credentials.*",         # ❌ Exclude credentials
            "config/*_secret*",        # ❌ Exclude secret configs
            "*.key",                   # ❌ Exclude key files
            "*.pem"                    # ❌ Exclude certificates
        ]
    }
)