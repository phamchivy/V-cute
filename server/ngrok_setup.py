import os
import sys
from pathlib import Path
from pyngrok import ngrok, conf
import time

# Add project path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "facebook_bot"))

from facebook_bot.config.facebook_config import FacebookConfig

class NgrokManager:
    """Manage Ngrok tunnel for Facebook webhook"""
    
    def __init__(self):
        self.tunnel = None
        self.public_url = None
    
    def setup_ngrok(self):
        """Setup ngrok tunnel"""
        try:
            print("🔗 Setting up Ngrok tunnel...")
            
            # Set auth token if provided
            if FacebookConfig.NGROK_AUTH_TOKEN:
                ngrok.set_auth_token(FacebookConfig.NGROK_AUTH_TOKEN)
                print("✅ Ngrok auth token set")
            else:
                print("⚠️ No Ngrok auth token provided (will use default limits)")
            
            # Create tunnel - USE RANDOM URL FOR FREE PLAN
            port = FacebookConfig.WEBHOOK_PORT
            
            # DON'T use custom domain for free plan
            print("🔄 Creating tunnel with random URL (free plan)...")
            self.tunnel = ngrok.connect(port)
            
            self.public_url = self.tunnel.public_url
            
            print(f"✅ Ngrok tunnel created!")
            print(f"🌐 Public URL: {self.public_url}")
            print(f"📡 Webhook URL: {self.public_url}{FacebookConfig.WEBHOOK_PATH}")
            
            return self.public_url
            
        except Exception as e:
            print(f"❌ Ngrok setup error: {e}")
            
            # Try alternative approach
            print("🔄 Trying alternative ngrok setup...")
            return self._setup_ngrok_alternative()
    
    def _setup_ngrok_alternative(self):
        """Alternative ngrok setup without auth token"""
        try:
            print("🔄 Setting up ngrok without auth token...")
            
            # Clear any existing auth
            ngrok.kill()
            
            # Create simple tunnel
            port = FacebookConfig.WEBHOOK_PORT
            self.tunnel = ngrok.connect(port, bind_tls=True)
            self.public_url = self.tunnel.public_url
            
            print(f"✅ Alternative tunnel created!")
            print(f"🌐 Public URL: {self.public_url}")
            print(f"📡 Webhook URL: {self.public_url}{FacebookConfig.WEBHOOK_PATH}")
            
            return self.public_url
            
        except Exception as e:
            print(f"❌ Alternative ngrok failed: {e}")
            print("💡 Try running ngrok manually:")
            print(f"   ngrok http {FacebookConfig.WEBHOOK_PORT}")
            return None
    
    def get_webhook_url(self):
        """Get full webhook URL for Facebook"""
        if self.public_url:
            return f"{self.public_url}{FacebookConfig.WEBHOOK_PATH}"
        return None
    
    def print_setup_instructions(self):
        """Print setup instructions for Facebook"""
        webhook_url = self.get_webhook_url()
        
        if not webhook_url:
            print("❌ No webhook URL available")
            return
        
        print("\n" + "="*60)
        print("📋 FACEBOOK WEBHOOK SETUP INSTRUCTIONS")
        print("="*60)
        print()
        print("🔗 1. Go to Facebook Developer Console:")
        print("   https://developers.facebook.com/apps/")
        print()
        print("📡 2. Add this Webhook URL:")
        print(f"   {webhook_url}")
        print()
        print("🔑 3. Use this Verify Token:")
        print(f"   {FacebookConfig.VERIFY_TOKEN}")
        print()
        print("📋 4. Subscribe to these events:")
        print("   ✅ messages")
        print("   ✅ messaging_postbacks")
        print("   ✅ message_deliveries")
        print()
        print("🎯 5. Test webhook:")
        print(f"   GET  {webhook_url}?hub.mode=subscribe&hub.verify_token={FacebookConfig.VERIFY_TOKEN}&hub.challenge=test")
        print(f"   POST {webhook_url}")
        print()
        print("="*60)
        print("🚀 Keep this terminal open to maintain the tunnel!")
        print("🔄 URL will change each time ngrok restarts (free plan)")
        print("="*60)
    
    def monitor_tunnel(self):
        """Monitor tunnel status"""
        try:
            print("\n🔄 Monitoring tunnel...")
            print("Press Ctrl+C to stop")
            
            while True:
                tunnels = ngrok.get_tunnels()
                if not tunnels:
                    print("❌ Tunnel disconnected!")
                    break
                
                print(f"✅ Tunnel active: {self.public_url}")
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping tunnel monitoring...")
        except Exception as e:
            print(f"❌ Tunnel monitoring error: {e}")
    
    def cleanup(self):
        """Clean up ngrok tunnel"""
        try:
            if self.tunnel:
                ngrok.disconnect(self.tunnel.public_url)
                print("🧹 Ngrok tunnel disconnected")
            ngrok.kill()
        except Exception as e:
            print(f"⚠️ Tunnel cleanup error: {e}")

def main():
    """Main ngrok setup function"""
    manager = NgrokManager()
    
    try:
        # Setup tunnel
        public_url = manager.setup_ngrok()
        
        if public_url:
            # Print setup instructions
            manager.print_setup_instructions()
            
            # Monitor tunnel
            manager.monitor_tunnel()
        else:
            print("❌ Failed to create tunnel")
            print("\n💡 Manual ngrok command:")
            print(f"   ngrok http {FacebookConfig.WEBHOOK_PORT}")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping ngrok...")
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()