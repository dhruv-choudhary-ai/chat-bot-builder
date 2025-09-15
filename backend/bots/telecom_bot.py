# telecom_bot.py
from fastapi import APIRouter, HTTPException
from bots.base_bot import BaseBot, QueryRequest
from schemas import HumanAssistanceRequest
from sqlalchemy.orm import Session
from database.sessions import get_db
from fastapi import Depends

router = APIRouter()

telecom_prompt = """
As a telecom assistant, your role is to address customer inquiries regarding their mobile and internet services. You can provide information on billing, data usage, plan upgrades, and troubleshooting common network issues. Your responses should be clear, concise, and aimed at resolving the customer's problem efficiently. If a query is outside your scope, such as a major service outage, you should inform the user that you will escalate the issue to a human agent.

Context: {context}
Question: {input}
"""

telecom_bot = BaseBot(system_prompt=telecom_prompt)

@router.post("/ask")
async def ask_telecom_question(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        response = telecom_bot.ask_question(request.question, request.user_id, db)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-human-assistance")
async def request_human_assistance(request: HumanAssistanceRequest, db: Session = Depends(get_db)):
    try:
        ticket = telecom_bot.create_human_assistance_ticket(
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

