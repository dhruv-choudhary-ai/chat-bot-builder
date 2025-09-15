from .base import MessageBuilderBase
from ..schemas import StandardizedMessage
from typing import Dict, Any

class WebMessageBuilder(MessageBuilderBase):
    """
    Builds a StandardizedMessage from a raw web chat payload.
    """
    CHANNEL_NAME = "web"

    def __init__(self, payload: Dict[str, Any]):
        """
        Example Payload:
        {
            "user_id": "user-123-abc",
            "text": "Hello, I need help with my order.",
            "attachments": []
        }
        """
        super().__init__(payload)

    def build(self) -> StandardizedMessage:
        sender_id = self.payload.get("user_id")
        if not sender_id:
            raise ValueError("Missing 'user_id' in web payload")

        content = self.payload.get("text")
        if not content:
            raise ValueError("Missing 'text' in web payload")

        conversation_id = self._generate_conversation_id(sender_id, self.CHANNEL_NAME)

        return StandardizedMessage(
            channel_name=self.CHANNEL_NAME,
            sender_id=sender_id,
            content=content,
            conversation_id=conversation_id,
            attachments=self.payload.get("attachments", []),
            metadata=self.payload # Store original payload in metadata
        )
