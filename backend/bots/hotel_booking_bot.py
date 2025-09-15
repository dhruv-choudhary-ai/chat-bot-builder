# hotel_booking_bot.py
from fastapi import APIRouter, HTTPException
from bots.base_bot import BaseBot, QueryRequest
from schemas import HumanAssistanceRequest
from sqlalchemy.orm import Session
from database.sessions import get_db
from fastapi import Depends

router = APIRouter()

hotel_booking_prompt = """
As a hotel booking assistant, your job is to help users find and book hotel rooms. You can search for available rooms based on location, dates, and user preferences. You should be able to provide details on hotel amenities, rates, and policies. Your goal is to make the booking process as smooth as possible. If a user has a special request or a problem with their booking, you should offer to connect them with hotel staff or a customer service representative.

Context: {context}
Question: {input}
"""

hotel_booking_bot = BaseBot(system_prompt=hotel_booking_prompt)

@router.post("/ask")
async def ask_hotel_booking_question(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        response = hotel_booking_bot.ask_question(request.question, request.user_id, db)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-human-assistance")
async def request_human_assistance(request: HumanAssistanceRequest, db: Session = Depends(get_db)):
    try:
        ticket = hotel_booking_bot.create_human_assistance_ticket(
            user_id=request.user_id,
            query=request.query,
            context=request.context,
            db=db
        )
        return {
            "message": "Your request has been escalated to human assistance. A support representative will contact you soon.",
            "ticket_id": ticket.id,
            "status": ticket.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

