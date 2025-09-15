# inbox.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.sessions import get_db
from database.database import Conversation, User


def get_inbox_dates(db: Session, bot_id: int = None):
    """
    Returns all distinct dates where interactions happened.
    """
    query = db.query(func.date(Conversation.created_at).label("date"))
    if bot_id:
        query = query.filter(Conversation.bot_id == bot_id)
    dates = (
        query
        .distinct()
        .order_by(func.date(Conversation.created_at).desc())
        .all()
    )
    return [d.date for d in dates]

def get_users_by_date(db: Session, date, bot_id: int = None):
    """
    Returns all unique users who interacted with the bot on a given date.
    """
    query = (
        db.query(User)
        .join(Conversation, Conversation.user_id == User.id)
        .filter(func.date(Conversation.created_at) == date)
    )
    if bot_id:
        query = query.filter(Conversation.bot_id == bot_id)
    users = (
        query
        .group_by(User.id)
        .all()
    )
    return users

def get_user_conversation_by_date(db: Session, user_id: int, date, bot_id: int = None):
    """
    Returns all conversations of a given user on a given date.
    """
    query = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user_id,
            func.date(Conversation.created_at) == date
        )
    )
    if bot_id:
        query = query.filter(Conversation.bot_id == bot_id)
    conversations = (
        query
        .order_by(Conversation.created_at.asc())
        .all()
    )
    return conversations

