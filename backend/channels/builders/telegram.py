from .base import MessageBuilderBase
from ..schemas import StandardizedMessage
from typing import Dict, Any

class TelegramMessageBuilder(MessageBuilderBase):
    """
    Builds a StandardizedMessage from a raw Telegram webhook payload.
    """
    CHANNEL_NAME = "telegram"

    def __init__(self, payload: Dict[str, Any]):
        """
        Example Payload (from Telegram webhook):
        {
            "update_id": 123456789,
            "message": {
                "message_id": 1234,
                "from": {
                    "id": 987654321,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe"
                },
                "chat": {
                    "id": 987654321,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "Hello, I need help!"
            }
        }
        """
        super().__init__(payload)

    def build(self) -> StandardizedMessage:
        message = self.payload.get("message", {})
        
        if not message:
            raise ValueError("Missing 'message' in Telegram payload")

        # Extract sender information
        from_user = message.get("from", {})
        chat = message.get("chat", {})
        
        # Use chat ID as sender_id (unique identifier)
        sender_id = str(chat.get("id") or from_user.get("id"))
        if not sender_id:
            raise ValueError("Missing sender ID in Telegram payload")

        # Get message content
        content = message.get("text")
        if not content:
            # Handle other message types (photos, documents, etc.)
            if message.get("photo"):
                content = message.get("caption", "[Photo message]")
            elif message.get("document"):
                content = message.get("caption", "[Document message]")
            elif message.get("voice"):
                content = "[Voice message]"
            elif message.get("sticker"):
                content = "[Sticker message]"
            else:
                content = "[Unsupported message type]"

        conversation_id = self._generate_conversation_id(sender_id, self.CHANNEL_NAME)

        # Extract user info for metadata
        user_info = {
            "telegram_user_id": from_user.get("id"),
            "first_name": from_user.get("first_name"),
            "last_name": from_user.get("last_name"),
            "username": from_user.get("username"),
            "chat_type": chat.get("type")
        }

        return StandardizedMessage(
            channel_name=self.CHANNEL_NAME,
            sender_id=sender_id,
            content=content,
            conversation_id=conversation_id,
            attachments=[],
            metadata={**self.payload, "user_info": user_info}
        )
