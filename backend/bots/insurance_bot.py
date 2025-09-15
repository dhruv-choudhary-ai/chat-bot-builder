# insurance_bot.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from bots.base_bot import BaseBot, QueryRequest, HumanAssistanceRequest, get_current_user
from database.sessions import get_db

insurance_prompt = """
As an insurance assistant, you are designed to help users with their insurance-related questions. You can provide quotes, explain policy details, and guide users through the process of filing a claim. Your responses must be accurate and comply with insurance regulations. You should avoid giving advice but provide clear and factual information. For complex claims or personalized advice, you must transfer the user to a licensed insurance agent.

If you cannot provide adequate help or if the user explicitly requests human assistance, you should suggest they flag their query for human assistance.

Context: {context}
Question: {input}
"""

insurance_bot = BaseBot(system_prompt=insurance_prompt)

# Create router for insurance bot
router = APIRouter(prefix="/insurance-bot", tags=["Insurance Bot"])

@router.post("/ask")
def ask_insurance_question(
    request: QueryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask an insurance question"""
    return insurance_bot.ask_question(
        request=request,
        bot_id=6,  # Insurance bot ID
        current_user=current_user,
        db=db
    )

@router.post("/request-human-assistance")
def request_human_assistance(
    request: HumanAssistanceRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a human assistance ticket for insurance"""
    return insurance_bot.create_human_assistance_ticket(
        request=request,
        bot_id=6,  # Insurance bot ID
        current_user=current_user,
        db=db
    )

