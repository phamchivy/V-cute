import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify
import json

# Set UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    import locale
    if locale.getpreferredencoding().upper() != 'UTF-8':
        os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "facebook_bot"))

try:
    from facebook_bot.core.bot_handler import HungPhatBot
    from facebook_bot.config.facebook_config import FacebookConfig
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    print("[INFO] Please install dependencies: pip install flask requests")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)

# Initialize bot (will be done in main)
bot = None

@app.route('/')
def home():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Hung Phat Facebook Bot",
        "webhook": f"POST {FacebookConfig.WEBHOOK_PATH}",
        "health": "OK"
    }

@app.route('/health')
def health():
    """Detailed health check"""
    try:
        rag_status = "ready" if bot and bot.rag_engine else "not initialized"
        return {
            "status": "healthy",
            "components": {
                "flask_server": "running",
                "rag_engine": rag_status,
                "facebook_webhook": "active"
            },
            "webhook_url": f"{request.host_url.rstrip('/')}{FacebookConfig.WEBHOOK_PATH}"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

@app.route('/test')
def test_endpoint():
    """Test endpoint for webhook verification"""
    return {
        "message": "Webhook server is working!",
        "timestamp": str(Path(__file__).stat().st_mtime),
        "webhook_path": FacebookConfig.WEBHOOK_PATH,
        "verify_token": FacebookConfig.VERIFY_TOKEN
    }

@app.route(FacebookConfig.WEBHOOK_PATH, methods=['GET'])
def webhook_verify():
    """Verify webhook with Facebook"""
    try:
        # Facebook sends these parameters for verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        print(f"[WEBHOOK] Verification: mode={mode}, token={token}")
        
        # Check if mode and token are correct
        if mode == 'subscribe' and token == FacebookConfig.VERIFY_TOKEN:
            print("[WEBHOOK] Verification successful!")
            return challenge
        else:
            print("[WEBHOOK] Verification failed!")
            return "Verification failed", 403
            
    except Exception as e:
        print(f"[ERROR] Webhook verification error: {e}")
        return "Verification error", 500

@app.route(FacebookConfig.WEBHOOK_PATH, methods=['POST'])
def webhook_receive():
    """Receive messages from Facebook"""
    try:
        data = request.get_json()
        print(f"[WEBHOOK] Received data: {json.dumps(data, indent=2)}")
        
        if not bot:
            print("[ERROR] Bot not initialized")
            return "Bot not ready", 500
        
        # Process each entry
        for entry in data.get('entry', []):
            # Process each messaging event
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event.get('sender', {}).get('id')
                
                if not sender_id:
                    continue
                
                # Handle text messages
                if 'message' in messaging_event:
                    message = messaging_event['message']
                    
                    # Handle text messages
                    if 'text' in message:
                        message_text = message['text']
                        print(f"[MESSAGE] Processing from {sender_id}: {message_text}")
                        bot.handle_message(sender_id, message_text)
                    
                    # Handle attachments (images, files, etc.)
                    elif 'attachments' in message:
                        attachment_response = "Toi nhan duoc file/hinh cua ban! Tuy nhien, toi chi co the tra loi cau hoi bang text. Hay hoi toi ve san pham vali, balo nhe!"
                        bot.messenger.send_message(sender_id, attachment_response)
                
                # Handle postbacks (button clicks)
                elif 'postback' in messaging_event:
                    postback = messaging_event['postback']
                    payload = postback.get('payload', '')
                    print(f"[POSTBACK] Processing from {sender_id}: {payload}")
                    bot.handle_postback(sender_id, payload)
                
                # Handle when user first starts conversation
                elif 'delivery' in messaging_event or 'read' in messaging_event:
                    # Ignore delivery receipts and read confirmations
                    pass
        
        return "OK", 200
        
    except Exception as e:
        print(f"[ERROR] Webhook processing error: {e}")
        return "Processing error", 500

@app.errorhandler(404)
def not_found(error):
    return {"error": "Endpoint not found", "webhook": FacebookConfig.WEBHOOK_PATH}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error", "details": str(error)}, 500

def create_app():
    """Create and configure Flask app"""
    global bot
    
    try:
        print("[INFO] Starting Hung Phat Facebook Bot Server...")
        
        # Validate configuration
        FacebookConfig.print_config_status()
        FacebookConfig.validate_config()
        
        # Initialize bot
        print("[INFO] Initializing bot...")
        bot = HungPhatBot()
        
        print("[SUCCESS] Server ready!")
        return app
        
    except Exception as e:
        print(f"[ERROR] Failed to create app: {e}")
        raise

if __name__ == '__main__':
    try:
        app = create_app()
        
        print(f"[INFO] Starting server on port {FacebookConfig.WEBHOOK_PORT}...")
        print(f"[INFO] Webhook URL: http://localhost:{FacebookConfig.WEBHOOK_PORT}{FacebookConfig.WEBHOOK_PATH}")
        print("[INFO] Use ngrok to expose this to Facebook!")
        
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=FacebookConfig.WEBHOOK_PORT,
            debug=False,  # Disable debug to reduce emoji usage
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")