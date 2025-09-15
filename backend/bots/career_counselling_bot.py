# career_counselling_bot.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from bots.base_bot import BaseBot, QueryRequest, HumanAssistanceRequest, get_current_user
from database.sessions import get_db

career_counselling_prompt = """
As a career counseling assistant, your purpose is to provide guidance to individuals seeking career advice. You can offer information on different career paths, suggest relevant courses, and provide tips on resume building and interview skills. Your responses should be encouraging and informative, helping users to explore their options and make well-informed decisions. You should not give definitive advice but rather suggestions and resources. For in-depth personal counseling, you should recommend speaking with a certified human career counselor.

If you cannot provide adequate help or if the user explicitly requests human assistance, you should suggest they flag their query for human assistance.

Context: {context}
Question: {input}
"""

career_counselling_bot = BaseBot(system_prompt=career_counselling_prompt)

# Create router for career counselling bot
router = APIRouter(prefix="/career-bot", tags=["Career Counselling Bot"])

@router.post("/ask")
def ask_career_question(
    request: QueryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a career counselling question"""
    return career_counselling_bot.ask_question(
        request=request,
        bot_id=3,  # Career counselling bot ID
        current_user=current_user,
        db=db
    )

@router.post("/request-human-assistance")
def request_human_assistance(
    request: HumanAssistanceRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a human assistance ticket for career counselling"""
    return career_counselling_bot.create_human_assistance_ticket(
        request=request,
        bot_id=3,  # Career counselling bot ID
        current_user=current_user,
        db=db
    )

