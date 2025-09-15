from datetime import datetime
from enum import Enum
from typing import Any, List, Dict, Union

from pydantic import BaseModel, Field


class DocumentSource(str, Enum):
    HUBSPOT = "hubspot"


class ConnectorMissingCredentialError(Exception):
    """Raised when a connector is missing a credential."""
    pass


class TextSection(BaseModel):
    text: str
    link: str | None = None


class ImageSection(BaseModel):
    image: bytes
    link: str | None = None


class Document(BaseModel):
    id: str
    sections: List[Union[TextSection, ImageSection]]
    source: DocumentSource
    semantic_identifier: str
    doc_updated_at: datetime | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
