import requests
import json
from typing import Dict, List, Optional
from facebook_bot.config.facebook_config import FacebookConfig

class MessengerAPI:
    """Facebook Messenger API Client"""
    
    def __init__(self):
        """Initialize Messenger API client"""
        FacebookConfig.validate_config()
        self.access_token = FacebookConfig.PAGE_ACCESS_TOKEN
        self.messages_url = FacebookConfig.MESSAGES_URL
    
    def send_message(self, recipient_id: str, message_text: str, 
                    quick_replies: Optional[List[Dict]] = None) -> bool:
        """Send text message to user"""
        try:
            # Build message payload
            message_data = {
                "text": message_text
            }
            
            # Add quick replies if provided
            if quick_replies:
                message_data["quick_replies"] = quick_replies
            
            payload = {
                "recipient": {"id": recipient_id},
                "message": message_data,
                "messaging_type": "RESPONSE"
            }
            
            # Send request
            response = self._send_request(payload)
            
            if response and response.get("message_id"):
                return True
            else:
                print(f"Failed to send message: {response}")
                return False
                
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def send_typing_indicator(self, recipient_id: str, typing_on: bool = True) -> bool:
        """Send typing indicator"""
        try:
            action = "typing_on" if typing_on else "typing_off"
            
            payload = {
                "recipient": {"id": recipient_id},
                "sender_action": action
            }
            
            response = self._send_request(payload)
            return response is not None
            
        except Exception as e:
            print(f"Error sending typing indicator: {e}")
            return False
    
    def send_quick_replies(self, recipient_id: str, text: str, 
                          quick_replies: List[Dict]) -> bool:
        """Send message with quick reply buttons"""
        return self.send_message(recipient_id, text, quick_replies)
    
    def _send_request(self, payload: Dict) -> Optional[Dict]:
        """Send request to Facebook Graph API"""
        try:
            params = {"access_token": self.access_token}
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(
                self.messages_url,
                params=params,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Facebook API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None