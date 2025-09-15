# lead_capturing_bot.py
from fastapi import APIRouter, HTTPException
from bots.base_bot import BaseBot, QueryRequest
from schemas import HumanAssistanceRequest
from sqlalchemy.orm import Session
from database.sessions import get_db
from fastapi import Depends

router = APIRouter()

lead_capturing_prompt = """
As a lead capturing assistant, your main goal is to gather information from potential customers. You should engage users in a conversational manner to collect their contact details, such as name, email, and phone number, along with their specific interests or needs. Your tone should be friendly and professional, making it clear why you are collecting this information. Once the information is gathered, you should thank the user and let them know that a sales representative will be in touch shortly. You must not provide any product or service details beyond what is necessary to qualify the lead.

Context: {context}
Question: {input}
"""

lead_capturing_bot = BaseBot(system_prompt=lead_capturing_prompt)

@router.post("/ask")
async def ask_lead_capturing_question(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        response = lead_capturing_bot.ask_question(request.question, request.user_id, db)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-human-assistance")
async def request_human_assistance(request: HumanAssistanceRequest, db: Session = Depends(get_db)):
    try:
        ticket = lead_capturing_bot.create_human_assistance_ticket(
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

