from .base import MessageBuilderBase
from ..schemas import StandardizedMessage
from typing import Dict, Any

class InstagramMessageBuilder(MessageBuilderBase):
    """
    Builds a StandardizedMessage from a raw Instagram webhook payload.
    Instagram uses Facebook Graph API for messaging.
    """
    CHANNEL_NAME = "instagram"

    def __init__(self, payload: Dict[str, Any]):
        """
        Example Payload (from Instagram webhook):
        {
            "object": "instagram",
            "entry": [
                {
                    "id": "instagram_page_id",
                    "time": 1640995200,
                    "messaging": [
                        {
                            "sender": {
                                "id": "instagram_user_id"
                            },
                            "recipient": {
                                "id": "instagram_page_id"
                            },
                            "timestamp": 1640995200000,
                            "message": {
                                "mid": "message_id",
                                "text": "Hello, I need help with my order!"
                            }
                        }
                    ]
                }
            ]
        }
        """
        super().__init__(payload)

    def build(self) -> StandardizedMessage:
        entry = self.payload.get("entry", [])
        if not entry:
            raise ValueError("Missing 'entry' in Instagram payload")

        # Get the first entry (usually there's only one)
        first_entry = entry[0]
        messaging = first_entry.get("messaging", [])
        
        if not messaging:
            raise ValueError("Missing 'messaging' in Instagram entry")

        # Get the first message
        message_event = messaging[0]
        sender = message_event.get("sender", {})
        message = message_event.get("message", {})
        
        # Extract sender ID and message content
        sender_id = sender.get("id")
        if not sender_id:
            raise ValueError("Missing sender ID in Instagram payload")

        message_text = message.get("text", "")
        if not message_text:
            # Handle other message types (images, etc.)
            if "attachments" in message:
                message_text = "[Media message received]"
            else:
                message_text = "[Unsupported message type]"

        # Generate conversation ID
        conversation_id = self._generate_conversation_id(sender_id, self.CHANNEL_NAME)

        return StandardizedMessage(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=message_text,
            channel=self.CHANNEL_NAME,
            sender_name=f"Instagram User {sender_id}",  # Instagram doesn't provide name in webhook
            timestamp=message_event.get("timestamp", 0)
        )

    def get_sender_psid(self) -> str:
        """
        Extract the Page-Scoped ID (PSID) for sending replies.
        """
        entry = self.payload.get("entry", [])
        if entry and entry[0].get("messaging"):
            return entry[0]["messaging"][0]["sender"]["id"]
        return None
