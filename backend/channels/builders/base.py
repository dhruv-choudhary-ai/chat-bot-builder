from abc import ABC, abstractmethod
from typing import Dict, Any
from ..schemas import StandardizedMessage

class MessageBuilderBase(ABC):
    """
    Abstract base class for all channel-specific message builders.
    """
    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    @abstractmethod
    def build(self) -> StandardizedMessage:
        """
        Takes the raw payload and transforms it into a StandardizedMessage.
        This method must be implemented by each subclass.
        """
        pass

    def _generate_conversation_id(self, sender_id: str, channel_name: str) -> str:
        """
        A consistent way to generate conversation IDs.
        """
        return f"{channel_name}-{sender_id}"
