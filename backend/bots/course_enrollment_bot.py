# course_enrollment_bot.py
from fastapi import APIRouter, HTTPException
from bots.base_bot import BaseBot, QueryRequest
from schemas import HumanAssistanceRequest
from sqlalchemy.orm import Session
from database.sessions import get_db
from fastapi import Depends

router = APIRouter()

course_enrollment_prompt = """
As a course enrollment assistant, your primary function is to help students register for courses. You can provide details about course schedules, prerequisites, and availability. You should also be able to guide users through the enrollment process step-by-step. If a course is full or a student does not meet the prerequisites, you should provide alternative suggestions or explain the process for joining a waitlist. For complex issues like financial aid or academic advising, you must escalate the conversation to the appropriate department.

Context: {context}
Question: {input}
"""

course_enrollment_bot = BaseBot(system_prompt=course_enrollment_prompt)

@router.post("/ask")
async def ask_course_enrollment_question(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        response = course_enrollment_bot.ask_question(request.question, request.user_id, db)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-human-assistance")
async def request_human_assistance(request: HumanAssistanceRequest, db: Session = Depends(get_db)):
    try:
        ticket = course_enrollment_bot.create_human_assistance_ticket(
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

