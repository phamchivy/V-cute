import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "src"))

from query.rag_engine import RAGEngine
from facebook_bot.api.messenger_api import MessengerAPI
from facebook_bot.core.response_formatter import ResponseFormatter
from facebook_bot.config.facebook_config import BotSettings

class HungPhatBot:
    """Main Facebook Bot Handler"""
    
    def __init__(self):
        """Initialize bot with RAG engine"""
        print("[BOT] Initializing Hung Phat Bot...")
        
        try:
            # Initialize RAG Engine
            print("[BOT] Loading RAG Engine...")
            self.rag_engine = RAGEngine()
            print("[BOT] RAG Engine loaded successfully")
            
            # Initialize Messenger API
            self.messenger = MessengerAPI()
            
            # Initialize Response Formatter
            self.formatter = ResponseFormatter()
            
            # Bot state
            self.active = True
            
            print("[BOT] Hung Phat Bot ready!")
            
        except Exception as e:
            print(f"[ERROR] Error initializing bot: {e}")
            raise
    
    def handle_message(self, sender_id: str, message_text: str) -> bool:
        """Handle incoming message from user"""
        try:
            print(f"[MESSAGE] Received from {sender_id}: {message_text}")
            
            # Send typing indicator
            self.messenger.send_typing_indicator(sender_id, True)
            
            # Process message with RAG
            print("[RAG] Processing with RAG...")
            response = self.rag_engine.query(message_text)
            
            # Format response for Facebook
            formatted_response = self.formatter.format_for_facebook(response)
            
            # Send typing indicator off
            self.messenger.send_typing_indicator(sender_id, False)
            
            # Send response
            success = self.messenger.send_message(sender_id, formatted_response)
            
            if success:
                print(f"[SUCCESS] Response sent to {sender_id}")
                return True
            else:
                print(f"[ERROR] Failed to send response to {sender_id}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error handling message: {e}")
            
            # Send error message
            error_msg = BotSettings.FALLBACK_RESPONSE
            self.messenger.send_message(sender_id, error_msg)
            return False
    
    def handle_postback(self, sender_id: str, payload: str) -> bool:
        """Handle postback from quick reply buttons"""
        try:
            print(f"[POSTBACK] Received from {sender_id}: {payload}")
            
            # Map payload to query
            query_map = {
                'VALI_20': 'Vali 20 inch tot nhat',
                'BALO_LAPTOP': 'Balo laptop chat luong cao',
                'TUI_XACH': 'Tui xach dep va ben',
                'GIA_RE': 'San pham gia re duoi 500k'
            }
            
            query = query_map.get(payload, payload)
            return self.handle_message(sender_id, query)
            
        except Exception as e:
            print(f"[ERROR] Error handling postback: {e}")
            return False
    
    def send_welcome_message(self, sender_id: str):
        """Send welcome message to new users"""
        welcome_text = """Xin chao! 

Toi la tro ly tu van cua Hung Phat Store. Toi co the giup ban:

- Tim vali, balo phu hop
- So sanh gia ca
- Tu van tinh nang
- Chon size phu hop

Hay hoi toi bat cu dieu gi ve san pham nhe!"""
        
        # Send welcome message with quick replies
        self.messenger.send_message(
            sender_id, 
            welcome_text, 
            quick_replies=BotSettings.QUICK_REPLIES
        )
    
    def shutdown(self):
        """Gracefully shutdown bot"""
        print("[BOT] Shutting down Hung Phat Bot...")
        self.active = False