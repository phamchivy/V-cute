#!/usr/bin/env python3
"""
Comprehensive webhook testing before Facebook integration
"""

import sys
import requests
import json
import time
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "facebook_bot"))

def test_server_basic():
    """Test if server is running"""
    print("\n=== TEST 1: Server Accessibility ===")
    
    try:
        url = "http://localhost:5000/"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Server is running")
            print(f"       Status: {data.get('status')}")
            print(f"       Service: {data.get('service')}")
            return True
        else:
            print(f"[FAIL] Server returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[FAIL] Server not accessible")
        print("       Make sure to run: python scripts/05_start_facebook_bot.py")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_health_endpoint():
    """Test health check endpoint"""
    print("\n=== TEST 2: Health Check ===")
    
    try:
        url = "http://localhost:5000/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Health check successful")
            print(f"       Status: {data.get('status')}")
            
            components = data.get('components', {})
            for component, status in components.items():
                print(f"       {component}: {status}")
            
            return True
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Health check error: {e}")
        return False

def test_webhook_verification():
    """Test Facebook webhook verification"""
    print("\n=== TEST 3: Webhook Verification ===")
    
    try:
        url = "http://localhost:5000/webhook"
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'v_cute_verify_token_2025',  # Updated token
            'hub.challenge': 'test_challenge_12345'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200 and response.text == 'test_challenge_12345':
            print("[PASS] Webhook verification successful")
            print(f"       Challenge response: {response.text}")
            return True
        else:
            print(f"[FAIL] Webhook verification failed")
            print(f"       Status: {response.status_code}")
            print(f"       Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Webhook verification error: {e}")
        return False

def test_webhook_verification_wrong_token():
    """Test webhook verification with wrong token"""
    print("\n=== TEST 4: Webhook Security (Wrong Token) ===")
    
    try:
        url = "http://localhost:5000/webhook"
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'wrong_token',
            'hub.challenge': 'test_challenge_12345'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 403:
            print("[PASS] Webhook correctly rejected wrong token")
            return True
        else:
            print(f"[FAIL] Webhook should reject wrong token")
            print(f"       Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Webhook security test error: {e}")
        return False

def test_rag_integration():
    """Test RAG system integration"""
    print("\n=== TEST 5: RAG Integration ===")
    
    try:
        # Test webhook message processing
        url = "http://localhost:5000/webhook"
        
        # Simulate Facebook message payload
        test_payload = {
            "object": "page",
            "entry": [
                {
                    "id": "123456789",
                    "time": int(time.time()),
                    "messaging": [
                        {
                            "sender": {"id": "test_user_123"},
                            "recipient": {"id": "test_page_456"},
                            "timestamp": int(time.time()),
                            "message": {
                                "mid": "test_message_id",
                                "text": "Toi can vali 20 inch"
                            }
                        }
                    ]
                }
            ]
        }
        
        headers = {'Content-Type': 'application/json'}
        print("       Sending test message: 'Toi can vali 20 inch'")
        print("       (This will test RAG processing...)")
        
        response = requests.post(url, json=test_payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("[PASS] RAG integration working")
            print("       Message processed successfully")
            return True
        else:
            print(f"[FAIL] RAG integration failed")
            print(f"       Status: {response.status_code}")
            print(f"       Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] RAG integration test error: {e}")
        return False

def test_ngrok_url(ngrok_url):
    """Test ngrok URL accessibility"""
    print(f"\n=== TEST 6: Ngrok URL Test ===")
    print(f"Testing URL: {ngrok_url}")
    
    try:
        # Test basic accessibility
        response = requests.get(ngrok_url, timeout=10)
        
        if response.status_code == 200:
            print("[PASS] Ngrok URL accessible")
            
            # Test webhook verification through ngrok
            webhook_url = f"{ngrok_url}/webhook"
            params = {
                'hub.mode': 'subscribe',
                'hub.verify_token': 'v_cute_verify_token_2025',
                'hub.challenge': 'ngrok_test_12345'
            }
            
            response = requests.get(webhook_url, params=params, timeout=15)
            
            if response.status_code == 200 and response.text == 'ngrok_test_12345':
                print("[PASS] Ngrok webhook verification successful")
                print(f"       Ready for Facebook: {webhook_url}")
                return True
            else:
                print(f"[FAIL] Ngrok webhook verification failed")
                return False
        else:
            print(f"[FAIL] Ngrok URL not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Ngrok URL test error: {e}")
        return False

def run_comprehensive_tests():
    """Run all webhook tests"""
    print("="*60)
    print("COMPREHENSIVE WEBHOOK TEST SUITE")
    print("="*60)
    
    tests = [
        ("Server Basic", test_server_basic),
        ("Health Check", test_health_endpoint),
        ("Webhook Verification", test_webhook_verification),
        ("Webhook Security", test_webhook_verification_wrong_token),
        ("RAG Integration", test_rag_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Test ngrok if URL provided
    ngrok_url = input("\nEnter your ngrok URL (or press Enter to skip): ").strip()
    if ngrok_url:
        if not ngrok_url.startswith('http'):
            ngrok_url = f"https://{ngrok_url}"
        result = test_ngrok_url(ngrok_url)
        results.append(("Ngrok URL", result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Webhook ready for Facebook.")
        print("\nNext steps:")
        print("1. Copy your ngrok webhook URL")
        print("2. Configure Facebook Developer Console")
        print("3. Test with real Facebook messages")
    else:
        print(f"\n[WARNING] {total - passed} tests failed.")
        print("\nTroubleshooting:")
        print("1. Check server logs for errors")
        print("2. Verify RAG system is working")
        print("3. Check network connectivity")
    
    return passed == total

if __name__ == "__main__":
    try:
        print("Starting comprehensive webhook tests...")
        print("Make sure your bot server is running first!")
        
        input("\nPress Enter when your bot server is ready...")
        
        success = run_comprehensive_tests()
        
        if success:
            print("\n[READY] Your webhook is ready for Facebook integration!")
        else:
            print("\n[NOT READY] Fix the failing tests before proceeding.")
            
    except KeyboardInterrupt:
        print("\n[STOPPED] Tests interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test suite error: {e}")