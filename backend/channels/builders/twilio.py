from .base import MessageBuilderBase
from ..schemas import StandardizedMessage
from typing import Dict, Any

class TwilioMessageBuilder(MessageBuilderBase):
    """
    Builds a StandardizedMessage from a raw Twilio SMS webhook payload.
    """
    CHANNEL_NAME = "twilio"

    def __init__(self, payload: Dict[str, Any]):
        """
        Example Payload (from Twilio webhook):
        {
            "SmsSid": "SMxxxxxxxxxxxxxxxxxxxxxxxx",
            "AccountSid": "ACxxxxxxxxxxxxxxxxxxxxxxxx",
            "From": "+15551234567",
            "To": "+15557654321",
            "Body": "Hi there!",
            "NumMedia": "0"
        }
        """
        super().__init__(payload)

    def build(self) -> StandardizedMessage:
        sender_id_raw = self.payload.get("From")
        if not sender_id_raw:
            raise ValueError("Missing 'From' in Twilio payload")

        # Standardize the sender_id by removing the "whatsapp:" prefix
        sender_id = sender_id_raw.replace("whatsapp:", "")

        content = self.payload.get("Body")
        if not content:
            raise ValueError("Missing 'Body' in Twilio payload")

        conversation_id = self._generate_conversation_id(sender_id, self.CHANNEL_NAME)

        return StandardizedMessage(
            channel_name=self.CHANNEL_NAME,
            sender_id=sender_id,
            content=content,
            conversation_id=conversation_id,
            attachments=[], # Twilio media handling would go here
            metadata=self.payload # Store original payload in metadata
        )
