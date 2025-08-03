#!/usr/bin/env python3
"""
Start Facebook Bot with Ngrok tunnel - Fixed for free ngrok plan
"""

import sys
import time
import threading
import subprocess
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "server"))
sys.path.append(str(project_root / "facebook_bot"))

def start_ngrok_simple():
    """Start simple ngrok tunnel without custom domain"""
    print("🔗 Starting Ngrok tunnel (free plan)...")
    
    try:
        from pyngrok import ngrok
        from facebook_bot.config.facebook_config import FacebookConfig
        
        # Set auth token if available
        if FacebookConfig.NGROK_AUTH_TOKEN:
            ngrok.set_auth_token(FacebookConfig.NGROK_AUTH_TOKEN)
            print("✅ Ngrok auth token set")
        
        # Create simple tunnel (no custom domain)
        print("🔄 Creating tunnel with random URL...")
        tunnel = ngrok.connect(FacebookConfig.WEBHOOK_PORT)
        public_url = tunnel.public_url
        webhook_url = f"{public_url}{FacebookConfig.WEBHOOK_PATH}"
        
        print(f"✅ Ngrok tunnel created!")
        print(f"🌐 Public URL: {public_url}")
        print(f"📡 Webhook URL: {webhook_url}")
        
        # Print Facebook setup instructions
        print("\n" + "="*60)
        print("📋 COPY THIS WEBHOOK URL TO FACEBOOK:")
        print("="*60)
        print(f"📡 Webhook URL: {webhook_url}")
        print(f"🔑 Verify Token: {FacebookConfig.VERIFY_TOKEN}")
        print("="*60)
        
        return public_url, webhook_url
        
    except Exception as e:
        print(f"❌ Ngrok error: {e}")
        print("\n💡 Try manual ngrok:")
        print("   1. Open new terminal")
        print("   2. Run: ngrok http 5000")
        print("   3. Copy the https URL")
        return None, None

def start_flask_server():
    """Start Flask webhook server"""
    print("🚀 Starting Flask server...")
    
    try:
        # Import and run Flask app
        server_path = project_root / "server" / "app.py"
        
        # Run Flask app using subprocess
        cmd = [sys.executable, str(server_path)]
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Flask server: {e}")
        return None

def monitor_server(process):
    """Monitor server output"""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
            if process.poll() is not None:
                break
    except Exception as e:
        print(f"❌ Server monitoring error: {e}")

def main():
    """Main function to start Facebook bot"""
    print("🤖 Starting Hùng Phát Facebook Bot Service")
    print("=" * 50)
    
    flask_process = None
    
    try:
        # Step 1: Check configuration
        print("🔧 Checking configuration...")
        try:
            from facebook_bot.config.facebook_config import FacebookConfig
            FacebookConfig.validate_config()
            FacebookConfig.print_config_status()
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            print("\n💡 Please check your config/facebook_credentials.env file")
            return
        except Exception as e:
            print(f"❌ Import error: {e}")
            print("💡 Make sure all dependencies are installed:")
            print("   pip install flask requests pyngrok")
            return
        
        # Step 2: Start Flask server first
        print("🌐 Starting webhook server...")
        flask_process = start_flask_server()
        
        if not flask_process:
            print("❌ Failed to start server")
            return
        
        # Wait for server to start
        print("⏰ Waiting for server to start...")
        time.sleep(3)
        
        # Step 3: Start ngrok tunnel
        public_url, webhook_url = start_ngrok_simple()
        
        if not public_url:
            print("❌ Failed to start ngrok, but server is running on localhost:5000")
            print("💡 You can:")
            print("   1. Run 'ngrok http 5000' manually")
            print("   2. Or test locally with http://localhost:5000/webhook")
        
        print("✅ Bot service started successfully!")
        print(f"✅ Flask server: Running (PID: {flask_process.pid})")
        
        if webhook_url:
            print(f"✅ Webhook URL: {webhook_url}")
            print("\n🎯 Next steps:")
            print("1. Copy the webhook URL above")
            print("2. Configure Facebook webhook with this URL")
            print("3. Test the webhook")
            print("4. Start chatting with your page!")
        
        print("\n🔄 Monitoring server output...")
        print("Press Ctrl+C to stop all services")
        print("-" * 50)
        
        # Monitor server
        monitor_server(flask_process)
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot service...")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        
        if flask_process:
            try:
                flask_process.terminate()
                flask_process.wait(timeout=5)
                print("✅ Flask server stopped")
            except Exception as e:
                print(f"⚠️ Error stopping Flask: {e}")
        
        try:
            from pyngrok import ngrok
            ngrok.kill()
            print("✅ Ngrok tunnels closed")
        except Exception as e:
            print(f"⚠️ Error stopping Ngrok: {e}")
        
        print("👋 Bot service stopped")

if __name__ == "__main__":
    main()