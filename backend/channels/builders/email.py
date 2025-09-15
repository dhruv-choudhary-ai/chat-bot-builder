from .base import MessageBuilderBase
from ..schemas import StandardizedMessage
from typing import Dict, Any

class EmailMessageBuilder(MessageBuilderBase):
    """
    Builds a StandardizedMessage from a raw email payload.
    Supports both webhook-based email (like SendGrid, Mailgun) and IMAP-based email.
    """
    CHANNEL_NAME = "email"

    def __init__(self, payload: Dict[str, Any]):
        """
        Example Payload (from email webhook or IMAP parsing):
        {
            "from": "user@example.com",
            "to": "support@yourdomain.com", 
            "subject": "Need help with my account",
            "text": "Hi, I'm having trouble logging in...",
            "html": "<p>Hi, I'm having trouble logging in...</p>",
            "attachments": []
        }
        """
        super().__init__(payload)

    def build(self) -> StandardizedMessage:
        sender_id = self.payload.get("from") or self.payload.get("sender")
        if not sender_id:
            raise ValueError("Missing 'from' or 'sender' in email payload")

        # Extract email address if it's in "Name <email>" format
        if "<" in sender_id and ">" in sender_id:
            sender_id = sender_id.split("<")[1].split(">")[0].strip()

        # Get email content - prefer text over html
        content = self.payload.get("text") or self.payload.get("body")
        if not content and self.payload.get("html"):
            # Basic HTML to text conversion
            import re
            html_content = self.payload.get("html", "")
            # Remove HTML tags
            content = re.sub('<[^<]+?>', '', html_content)
            # Replace common HTML entities
            content = content.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        if not content:
            raise ValueError("Missing email content")

        # Include subject in content for better context
        subject = self.payload.get("subject", "")
        if subject:
            content = f"Subject: {subject}\n\n{content}"

        conversation_id = self._generate_conversation_id(sender_id, self.CHANNEL_NAME)

        # Extract attachments info
        attachments = self.payload.get("attachments", [])
        
        return StandardizedMessage(
            channel_name=self.CHANNEL_NAME,
            sender_id=sender_id,
            content=content.strip(),
            conversation_id=conversation_id,
            attachments=attachments,
            metadata=self.payload # Store original email data
        )
