#!/usr/bin/env python3
"""
Test Facebook webhook functionality
"""

import sys
import requests
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "server"))
sys.path.append(str(project_root / "facebook_bot"))

from facebook_bot.config.facebook_config import FacebookConfig

def test_webhook_verification():
    """Test webhook verification (GET request)"""
    print("🔍 Testing webhook verification...")
    
    try:
        url = f"http://localhost:{FacebookConfig.WEBHOOK_PORT}{FacebookConfig.WEBHOOK_PATH}"
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': FacebookConfig.VERIFY_TOKEN,
            'hub.challenge': 'test_challenge_123'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200 and response.text == 'test_challenge_123':
            print("✅ Webhook verification: PASSED")
            return True
        else:
            print(f"❌ Webhook verification: FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook verification error: {e}")
        return False

def test_webhook_message():
    """Test webhook message processing (POST request)"""
    print("📨 Testing webhook message processing...")
    
    try:
        url = f"http://localhost:{FacebookConfig.WEBHOOK_PORT}{FacebookConfig.WEBHOOK_PATH}"
        
        # Simulate Facebook message payload
        test_payload = {
            "object": "page",
            "entry": [
                {
                    "id": "123456789",
                    "time": 1234567890,
                    "messaging": [
                        {
                            "sender": {"id": "test_user_123"},
                            "recipient": {"id": "test_page_456"},
                            "timestamp": 1234567890,
                            "message": {
                                "mid": "test_message_id",
                                "text": "Tôi cần vali 20 inch"
                            }
                        }
                    ]
                }
            ]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=test_payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ Webhook message processing: PASSED")
            return True
        else:
            print(f"❌ Webhook message processing: FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook message processing error: {e}")
        return False

def test_health_endpoint():
    """Test health check endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        url = f"http://localhost:{FacebookConfig.WEBHOOK_PORT}/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check: PASSED")
            print(f"   Status: {data.get('status')}")
            print(f"   Components: {data.get('components', {})}")
            return True
        else:
            print(f"❌ Health check: FAILED")
            print(f"   Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_server_accessibility():
    """Test if server is accessible"""
    print("🌐 Testing server accessibility...")
    
    try:
        url = f"http://localhost:{FacebookConfig.WEBHOOK_PORT}/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Server accessible: PASSED")
            return True
        else:
            print(f"❌ Server accessibility: FAILED")
            print(f"   Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Server accessibility error: {e}")
        print("💡 Make sure the server is running: python scripts/05_start_facebook_bot.py")
        return False

def run_all_tests():
    """Run all webhook tests"""
    print("🧪 Facebook Webhook Test Suite")
    print("=" * 40)
    
    tests = [
        ("Server Accessibility", test_server_accessibility),
        ("Health Endpoint", test_health_endpoint),
        ("Webhook Verification", test_webhook_verification),
        ("Webhook Message Processing", test_webhook_message)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Webhook is ready for Facebook.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        
        if success:
            print("\n🚀 Next steps:")
            print("1. Make sure ngrok tunnel is running")
            print("2. Configure Facebook webhook with your ngrok URL")
            print("3. Start chatting with your Facebook page!")
        else:
            print("\n🔧 Troubleshooting tips:")
            print("1. Make sure the bot server is running")
            print("2. Check your configuration in facebook_credentials.env")
            print("3. Verify your RAG system is working")
            
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test suite error: {e}")

if __name__ == "__main__":
    main()