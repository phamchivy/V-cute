import re
#from typing import str
from facebook_bot.config.facebook_config import BotSettings

class ResponseFormatter:
    """Format RAG responses for Facebook Messenger"""
    
    def __init__(self):
        self.max_length = BotSettings.MAX_RESPONSE_LENGTH
    
    def format_for_facebook(self, rag_response: str, tone: str = "friendly") -> str:
        """Format RAG response for Facebook Messenger with tone conversion"""
        try:
            # Clean and format the response
            formatted = self._clean_text(rag_response)
            
            # Convert tone BEFORE adding emojis
            formatted = self._convert_tone(formatted, tone)
            
            # Add casual expressions
            formatted = self._add_casual_expressions(formatted)
            
            # Add emojis
            formatted = self._add_emojis(formatted)
            
            # Truncate if needed
            formatted = self._truncate_if_needed(formatted)
            
            # Add call to action
            formatted = self._add_call_to_action(formatted)
            
            return formatted
        
        except Exception as e:
            print(f"⚠️ Error formatting response: {e}")
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
    
    def _convert_tone(self, text: str, tone: str = "friendly") -> str:
        """Convert formal tone to friendly/casual tone"""
        
        # Define tone conversion mappings
        tone_mappings = {
            "friendly": {
                # Pronouns - more casual
                "tôi": "tớ",
                "Tôi": "Tớ", 
                "mình": "tớ",
                "Mình": "Tớ",
                
                # Negations - softer
                "không": "hơm",
                "Không": "Hơm",
                "không có": "hơm có",
                "Không có": "Hơm có",
                
                # Politeness - more casual
                "anh": "cậu",
                "chị": "cậu", 
                "bạn": "cậu",
                "Bạn": "Cậu",
                
                # Responses - friendlier
                "được": "okela",
                "có thể": "có thể nhé",
                "rồi": "rồi đó",
                "nhé": "nha",
                "ạ": "á",
                
                # Common phrases
                "xin chào": "chào cậu",
                "Xin chào": "Chào cậu",
                "cảm ơn": "thanks",
                "Cảm ơn": "Thanks",
            },
            
            "playful": {
                # More playful conversions
                "tôi": "tui",
                "Tôi": "Tui",
                "không": "hong",
                "Không": "Hong", 
                "rồi": "ròi",
                "được": "dc",
                "có": "cóa",
                "thế": "zậy",
                "gì": "dzì",
                "nhé": "nè",
                "ạ": "ớ",
            },
            
            "casual": {
                # Casual but not too playful  
                "tôi": "mình",
                "Tôi": "Mình",
                "không": "ko",
                "Không": "Ko",
                "được": "được nè", 
                "có thể": "có thể đó",
                "nhé": "nhá",
                "ạ": "ó",
            }
        }
        
        # Get the mapping for specified tone
        mapping = tone_mappings.get(tone, tone_mappings["friendly"])
        
        # Apply conversions
        converted_text = text
        for formal, casual in mapping.items():
            # Use word boundaries to avoid partial replacements
            import re
            pattern = r'\b' + re.escape(formal) + r'\b'
            converted_text = re.sub(pattern, casual, converted_text)
        
        return converted_text

    def _add_casual_expressions(self, text: str) -> str:
        """Add casual expressions and interjections"""
        casual_additions = [
            # Friendly interjections
            "nè", "đó", "ấy mà", "hihi", "hehe", 
            "ơi", "zậy", "nha", "í", "ớ"
        ]
        
        # Add random casual expression occasionally
        import random
        if random.random() < 0.3:  # 30% chance
            expression = random.choice(casual_additions)
            # Add at end of sentences randomly
            sentences = text.split('.')
            if len(sentences) > 1:
                # Add to a random sentence (not the last empty one)
                idx = random.randint(0, len(sentences) - 2)
                sentences[idx] = sentences[idx].rstrip() + f" {expression}"
                text = '.'.join(sentences)
        
        return text
    
    # Example usage method for testing different tones
    def preview_tone_conversion(self, text: str):
        """Preview different tone conversions"""
        print("🎭 Tone Conversion Preview:")
        print("=" * 40)
        
        tones = ["friendly", "casual", "playful"]
        
        for tone in tones:
            converted = self._convert_tone(text, tone)
            print(f"📝 {tone.upper()}:")
            print(f"   {converted}")
            print()
        
        return tones