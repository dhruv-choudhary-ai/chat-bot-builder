from pydantic import BaseModel
from typing import Optional, Any, Dict

class StandardizedMessage(BaseModel):
    """
    A standardized representation of a message received from any channel.
    This is the schema that all Channel Builders will produce.
    """
    channel_name: str  # e.g., 'web', 'twilio', 'facebook'
    sender_id: str     # Unique identifier for the user on that channel
    content: str
    conversation_id: str # A unique ID to group messages (e.g., sender_id + channel_name)

    # Optional fields
    attachments: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None
