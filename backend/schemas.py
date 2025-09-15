from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TicketBase(BaseModel):
    topic: str
    description: Optional[str] = None

class TicketCreate(TicketBase):
    pass

class Ticket(TicketBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Bot(BaseModel):
    id: int
    name: str
    bot_type: str
    admin_id: int

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: str
    phone_number: str | None
    name: str | None
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    interaction: dict
    resolved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    question: str

class HumanAssistanceRequest(BaseModel):
    user_id: int
    query: str
    context: str = ""