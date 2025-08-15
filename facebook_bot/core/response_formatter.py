import re
#from typing import str
from facebook_bot.config.facebook_config import BotSettings

class ResponseFormatter:
    """Format RAG responses for Facebook Messenger"""
    
    def __init__(self):
        self.max_length = BotSettings.MAX_RESPONSE_LENGTH
    
    def format_for_facebook(self, rag_response: str) -> str:
        """Format RAG response for Facebook Messenger"""
        try:
            # Clean and format the response
            formatted = self._clean_text(rag_response)
            #formatted = self._add_emojis(formatted)
            formatted = self._truncate_if_needed(formatted)
            formatted = self._add_call_to_action(formatted)
            
            return formatted
            
        except Exception as e:
            print(f"❌ Error formatting response: {e}")
            return BotSettings.FALLBACK_RESPONSE
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common formatting issues
        text = text.replace('- ', '• ')  # Use bullet points
        text = text.replace('*', '')     # Remove asterisks
        
        # Ensure proper spacing around punctuation
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', text)
        
        return text
    
    def _add_emojis(self, text: str) -> str:
        """Add relevant emojis to make response more engaging"""
        # Product type emojis
        emoji_map = {
            'vali': '🧳',
            'balo': '🎒', 
            'túi xách': '👜',
            'giá': '💰',
            'khuyên': '👍',
            'tốt': '⭐',
            'chất lượng': '✨',
            'TSA': '🔒',
            'bánh xe': '🎡',
            'nhẹ': '🪶',
            'bền': '💪',
            'inch': '📏'
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword.lower() in text.lower():
                text = text.replace(keyword, f"{keyword} {emoji}", 1)  # Only first occurrence
        
        return text
    
    def _truncate_if_needed(self, text: str) -> str:
        """Truncate text if too long for Facebook"""
        if len(text) <= self.max_length:
            return text
        
        # Find a good break point
        truncated = text[:self.max_length - 50]  # Leave room for ending
        
        # Try to break at sentence end
        last_sentence = truncated.rfind('.')
        if last_sentence > len(truncated) * 0.7:  # If sentence break is reasonable
            truncated = truncated[:last_sentence + 1]
        
        # Add continuation message
        truncated += "\n\n💬 Hỏi tôi thêm để biết chi tiết hơn nhé!"
        
        return truncated
    
    def _add_call_to_action(self, text: str) -> str:
        """Add call-to-action to encourage engagement"""
        # Don't add if already has a question
        if '?' in text or 'hỏi' in text.lower():
            return text
        
        cta_options = [
            "\n\n❓ Bạn có muốn biết thêm về sản phẩm nào khác không?",
            "\n\n💭 Cần tư vấn thêm gì nữa không?",
            "\n\n🔍 Tôi có thể giúp bạn tìm sản phẩm khác!"
        ]
        
        # Choose based on response content
        if 'giá' in text.lower():
            cta = cta_options[0]
        elif 'sản phẩm' in text.lower():
            cta = cta_options[1] 
        else:
            cta = cta_options[2]
        
        return text + cta