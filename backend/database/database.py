import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy.orm import Session

Base = sqlalchemy.orm.declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)

    # Link to registered user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User")

    # Store the user query and LLM response as JSON
    interaction = Column(JSON, nullable=False)  # e.g., {"question": "...", "answer": "..."}

    # Track if issue is resolved
    resolved = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=True)
    bot = relationship("Bot")


class Bot(Base):
    __tablename__ = 'bots'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bot_type = Column(String, index=True)
    admin_id = Column(Integer, ForeignKey('admins.id'))
    admin = relationship("Admin")


class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=True)
    topic = Column(String, nullable=False)
    description = Column(String, nullable=True)  # Store the full query/context
    status = Column(String, default='open')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user = relationship("User")
    bot = relationship("Bot")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    # Basic credentials
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # hashed password (never store plain text)

    # Optional profile fields
    name = Column(String, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)

    # Roles / permissions (for scalability: superadmin, moderator, etc.)
    role = Column(String, default="admin")

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()