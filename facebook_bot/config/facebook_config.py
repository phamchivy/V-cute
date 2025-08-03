import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
env_file = project_root / "config" / "facebook_credentials.env"

if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # Load from system env

class FacebookConfig:
    """Facebook API Configuration"""
    
    # Facebook App Credentials (Get from Facebook Developer Console)
    PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    VERIFY_TOKEN = os.getenv('FACEBOOK_VERIFY_TOKEN', 'v_cute_verify_token_2025')
    APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    
    # API URLs
    GRAPH_API_URL = "https://graph.facebook.com/v19.0"
    MESSAGES_URL = f"{GRAPH_API_URL}/me/messages"
    
    # Webhook Settings
    WEBHOOK_PATH = "/webhook"
    WEBHOOK_PORT = 5000
    
    # Ngrok Settings (for local development)
    NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.PAGE_ACCESS_TOKEN:
            errors.append("FACEBOOK_PAGE_ACCESS_TOKEN is required")
        
        if not cls.VERIFY_TOKEN:
            errors.append("FACEBOOK_VERIFY_TOKEN is required")
            
        if errors:
            raise ValueError("Missing Facebook configuration:\n" + "\n".join(errors))
        
        return True
    
    @classmethod
    def print_config_status(cls):
        """Print configuration status for debugging"""
        print("[CONFIG] Facebook Configuration Status:")
        print(f"[CONFIG] Page Token: {'Set' if cls.PAGE_ACCESS_TOKEN else 'Missing'}")
        print(f"[CONFIG] Verify Token: {'Set' if cls.VERIFY_TOKEN else 'Missing'}")
        print(f"[CONFIG] App Secret: {'Set' if cls.APP_SECRET else 'Optional'}")
        print(f"[CONFIG] Ngrok Token: {'Set' if cls.NGROK_AUTH_TOKEN else 'Will use free plan'}")
        print(f"[CONFIG] Webhook URL will be: http://localhost:{cls.WEBHOOK_PORT}{cls.WEBHOOK_PATH}")

class BotSettings:
    """Bot Behavior Settings"""
    
    # Response Settings
    MAX_RESPONSE_LENGTH = 2000  # Facebook message limit
    TYPING_DELAY = 2  # Seconds to show "typing" indicator
    
    # RAG Settings
    RAG_TIMEOUT = 30  # Seconds
    FALLBACK_RESPONSE = "Xin loi, toi dang gap su co ky thuat. Vui long thu lai sau."
    
    # Rate Limiting
    MAX_MESSAGES_PER_USER_PER_MINUTE = 10
    
    # Quick Replies
    QUICK_REPLIES = [
        {"content_type": "text", "title": "Vali 20 inch", "payload": "VALI_20"},
        {"content_type": "text", "title": "Balo laptop", "payload": "BALO_LAPTOP"},
        {"content_type": "text", "title": "Tui xach", "payload": "TUI_XACH"},
        {"content_type": "text", "title": "Gia re", "payload": "GIA_RE"}
    ]