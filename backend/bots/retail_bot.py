# retail_bot.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from bots.base_bot import BaseBot, QueryRequest, HumanAssistanceRequest, get_current_user
from database.sessions import get_db

retail_prompt = """
Answer the user's question based on the following context, whatever language they are typing decode the words well and try to answer it in english only.
If you don't know the answer, just say that you don't know and ask them that can you flag this for human assistance.

If you cannot provide adequate help or if the user explicitly requests human assistance, you should suggest they flag their query for human assistance.

Context: {context}
Question: {input}
"""

retail_bot = BaseBot(system_prompt=retail_prompt)

# Create router for retail bot
router = APIRouter(prefix="/retail-bot", tags=["Retail Bot"])

@router.post("/ask")
def ask_retail_question(
    request: QueryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a retail question"""
    return retail_bot.ask_question(
        request=request,
        bot_id=5,  # Retail bot ID
        current_user=current_user,
        db=db
    )

@router.post("/request-human-assistance")
def request_human_assistance(
    request: HumanAssistanceRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a human assistance ticket for retail"""
    return retail_bot.create_human_assistance_ticket(
        request=request,
        bot_id=5,  # Retail bot ID
        current_user=current_user,
        db=db
    )
