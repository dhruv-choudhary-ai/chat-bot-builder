#!/usr/bin/env python3
"""
Minimal FastAPI application to test tickets functionality
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sessions import get_db
from database.database import User, Admin, Ticket
from adminbackend import tickets as tickets_crud
import schemas

app = FastAPI(title="AILifeBotAssist - Tickets Test", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "AILifeBotAssist Tickets API is running", "status": "ok"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}

# Ticket endpoints for testing
@app.post("/tickets/", response_model=schemas.Ticket)
def create_ticket_test(
    topic: str,
    user_id: int,
    bot_id: int = None,
    db: Session = Depends(get_db)
):
    """Create a test ticket"""
    ticket_data = schemas.TicketCreate(topic=topic)
    return tickets_crud.create_ticket(db=db, ticket=ticket_data, user_id=user_id, bot_id=bot_id)

@app.get("/tickets/", response_model=List[schemas.Ticket])
def get_all_tickets_test(db: Session = Depends(get_db)):
    """Get all tickets for testing"""
    return tickets_crud.get_all_tickets(db=db)

@app.get("/tickets/user/{user_id}", response_model=List[schemas.Ticket])
def get_user_tickets_test(user_id: int, db: Session = Depends(get_db)):
    """Get tickets for a specific user"""
    return tickets_crud.get_user_tickets(db=db, user_id=user_id)

@app.get("/tickets/{ticket_id}")
def get_ticket_details_test(ticket_id: int, db: Session = Depends(get_db)):
    """Get details for a specific ticket"""
    ticket = tickets_crud.get_ticket_details(db=db, ticket_id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status_test(
    ticket_id: int, 
    new_status: str, 
    db: Session = Depends(get_db)
):
    """Update ticket status"""
    ticket = tickets_crud.update_ticket_status(db=db, ticket_id=ticket_id, new_status=new_status)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.get("/tickets/bot/{bot_id}", response_model=List[schemas.Ticket])
def get_bot_tickets_test(bot_id: int, db: Session = Depends(get_db)):
    """Get tickets for a specific bot"""
    return tickets_crud.get_bot_tickets(db=db, bot_id=bot_id)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AILifeBotAssist Tickets Test Server...")
    print("📋 Available endpoints:")
    print("   GET  /                    - Root endpoint")
    print("   GET  /health              - Health check")
    print("   POST /tickets/            - Create ticket")
    print("   GET  /tickets/            - Get all tickets")
    print("   GET  /tickets/user/{id}   - Get user tickets")
    print("   GET  /tickets/{id}        - Get ticket details")
    print("   PATCH /tickets/{id}/status - Update ticket status")
    print("   GET  /tickets/bot/{id}    - Get bot tickets")
    print("\n📖 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
