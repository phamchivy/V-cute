# 📝 File: rag_pipeline/scripts/run_full_pipeline.py
#!/usr/bin/env python3
"""Run complete RAG pipeline from start to finish"""

import sys
import subprocess
from pathlib import Path
import time

def run_step(step_script: str, step_name: str) -> bool:
    """Run a pipeline step"""
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {step_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            sys.executable, step_script
        ], cwd=Path(__file__).parent, check=True, capture_output=False)
        
        elapsed = time.time() - start_time
        print(f"\n✅ {step_name} completed in {elapsed:.1f}s")
        return True
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n❌ {step_name} failed after {elapsed:.1f}s")
        print(f"Error code: {e.returncode}")
        return False

def main():
    """Run full RAG pipeline"""
    print("🌟 HÙNG PHÁT RAG PIPELINE - FULL EXECUTION")
    print("=" * 60)
    print("This will run the complete RAG pipeline:")
    print("1. Data Preprocessing")
    print("2. Embedding Generation") 
    print("3. Vector Indexing")
    print("4. RAG Testing")
    print("5. Facebook Testing")
    print("6. Webhook Testing")
    print("=" * 60)
    
    # Confirm execution
    response = input("\n🤔 Do you want to proceed? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Pipeline execution cancelled")
        return
    
    total_start = time.time()
    
    # Pipeline steps
    steps = [
        ("01_preprocess_data.py", "Step 1: Data Preprocessing"),
        ("02_generate_embeddings.py", "Step 2: Embedding Generation"),
        ("03_build_index.py", "Step 3: Vector Indexing"),
        ("04_test_rag.py", "Step 4: RAG Testing"),
        ("05_start_facebook_bot.py", "Step 5: Facebook Testing"),
        ("06_test_facebook_webhook.py", "Step 6: Webhook Testing")
    ]
    
    # Execute steps
    success_count = 0
    for step_script, step_name in steps:
        success = run_step(step_script, step_name)
        if success:
            success_count += 1
        else:
            print(f"\n💥 Pipeline failed at: {step_name}")
            break
    
    # Final summary
    total_elapsed = time.time() - total_start
    
    print(f"\n{'='*60}")
    print("🎯 PIPELINE EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"⏱️  Total time: {total_elapsed:.1f}s")
    print(f"✅ Successful steps: {success_count}/{len(steps)}")
    
    if success_count == len(steps):
        print("🎉 FULL PIPELINE COMPLETED SUCCESSFULLY!")
        print("\n🚀 Your RAG system is ready!")
        print("   - ChromaDB indexed with product data")
        print("   - LlamaIndex configured with Llama3")
        print("   - Ready for queries and integration")
        
        print("\n🎯 Next actions:")
        print("   - Test with custom queries")
        print("   - Integrate with Facebook bot")
        print("   - Deploy as API service")
    else:
        print("❌ Pipeline incomplete - please check errors above")

if __name__ == "__main__":
    main()