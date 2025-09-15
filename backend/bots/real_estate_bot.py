# real_estate_bot.py
from fastapi import APIRouter, HTTPException
from bots.base_bot import BaseBot, QueryRequest
from schemas import HumanAssistanceRequest
from sqlalchemy.orm import Session
from database.sessions import get_db
from fastapi import Depends

router = APIRouter()

real_estate_prompt = """
As a real estate assistant, your purpose is to help clients find properties that match their criteria. You can search for listings based on location, price range, and property type. You should also be able to provide details about the properties, such as the number of bedrooms, amenities, and neighborhood information. Your goal is to connect potential buyers with suitable properties and schedule viewings. For negotiations, legal advice, or complex financial questions, you must refer the user to a licensed real estate agent.

Context: {context}
Question: {input}
"""

real_estate_bot = BaseBot(system_prompt=real_estate_prompt)

@router.post("/ask")
async def ask_real_estate_question(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        response = real_estate_bot.ask_question(request.question, request.user_id, db)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-human-assistance")
async def request_human_assistance(request: HumanAssistanceRequest, db: Session = Depends(get_db)):
    try:
        ticket = real_estate_bot.create_human_assistance_ticket(
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

