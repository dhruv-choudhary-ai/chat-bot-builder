from sqlalchemy.orm import Session
from database.database import Ticket, User
import schemas

def create_ticket(db: Session, ticket: schemas.TicketCreate, user_id: int, bot_id: int = None):
    db_ticket = Ticket(**ticket.dict(), user_id=user_id, bot_id=bot_id)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_user_tickets(db: Session, user_id: int):
    return db.query(Ticket).filter(Ticket.user_id == user_id).all()

def get_all_tickets(db: Session):
    return db.query(Ticket).all()

def get_bot_tickets(db: Session, bot_id: int):
    return db.query(Ticket).filter(Ticket.bot_id == bot_id).all()

def get_bot_ticket_details(db: Session, bot_id: int, ticket_id: int):
    return db.query(Ticket).filter(Ticket.bot_id == bot_id, Ticket.id == ticket_id).first()

def get_ticket_details(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def update_ticket_status(db: Session, ticket_id: int, new_status: str):
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if db_ticket:
        db_ticket.status = new_status
        db.commit()
        db.refresh(db_ticket)
    return db_ticket
