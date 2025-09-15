from .base import MessageBuilderBase
from ..schemas import StandardizedMessage
from typing import Dict, Any

class MessengerMessageBuilder(MessageBuilderBase):
    """
    Builds a StandardizedMessage from a raw Messenger webhook payload.
    Messenger uses Facebook Graph API for messaging.
    """
    CHANNEL_NAME = "messenger"

    def __init__(self, payload: Dict[str, Any]):
        """
        Example Payload (from Messenger webhook):
        {
            "object": "page",
            "entry": [
                {
                    "id": "page_id",
                    "time": 1640995200,
                    "messaging": [
                        {
                            "sender": {
                                "id": "user_psid"
                            },
                            "recipient": {
                                "id": "page_id"
                            },
                            "timestamp": 1640995200000,
                            "message": {
                                "mid": "message_id",
                                "text": "Hello! I have a question about your services."
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
            raise ValueError("Missing 'entry' in Messenger payload")

        # Get the first entry (usually there's only one)
        first_entry = entry[0]
        messaging = first_entry.get("messaging", [])
        
        if not messaging:
            raise ValueError("Missing 'messaging' in Messenger entry")

        # Get the first message
        message_event = messaging[0]
        sender = message_event.get("sender", {})
        message = message_event.get("message", {})
        
        # Extract sender ID and message content
        sender_id = sender.get("id")
        if not sender_id:
            raise ValueError("Missing sender ID in Messenger payload")

        message_text = message.get("text", "")
        if not message_text:
            # Handle other message types (images, attachments, quick replies, etc.)
            if "attachments" in message:
                attachments = message["attachments"]
                if attachments and len(attachments) > 0:
                    attachment_type = attachments[0].get("type", "unknown")
                    message_text = f"[{attachment_type.title()} attachment received]"
                else:
                    message_text = "[Media message received]"
            elif "quick_reply" in message:
                message_text = message["quick_reply"].get("payload", "[Quick reply]")
            else:
                message_text = "[Unsupported message type]"

        # Generate conversation ID
        conversation_id = self._generate_conversation_id(sender_id, self.CHANNEL_NAME)

        # Try to get sender name from the payload (if available in postback or referral)
        sender_name = f"Messenger User {sender_id[-8:]}"  # Use last 8 digits for privacy
        
        return StandardizedMessage(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=message_text,
            channel=self.CHANNEL_NAME,
            sender_name=sender_name,
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

    def is_postback(self) -> bool:
        """
        Check if this is a postback event (button click, etc.)
        """
        entry = self.payload.get("entry", [])
        if entry and entry[0].get("messaging"):
            return "postback" in entry[0]["messaging"][0]
        return False

    def get_postback_payload(self) -> str:
        """
        Get the postback payload if this is a postback event.
        """
        if self.is_postback():
            entry = self.payload.get("entry", [])
            messaging = entry[0]["messaging"][0]
            return messaging.get("postback", {}).get("payload", "")
        return ""
