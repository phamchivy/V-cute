# 📝 File: rag_pipeline/setup.py
from setuptools import setup, find_packages

setup(
    name="hungphat-rag-pipeline",
    version="1.0.0",
    description="RAG Pipeline for Hùng Phát Product Consultation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "llama-index>=0.9.48",
        "chromadb>=0.4.24", 
        "sentence-transformers>=2.2.2",
        "ollama>=0.1.7",
        "pandas>=2.1.4",
        "numpy>=1.24.3",
        "transformers>=4.36.2",
        "torch>=2.1.1",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "tqdm>=4.66.1",
        "unidecode>=1.3.7"
    ],
    python_requires=">=3.9",
)