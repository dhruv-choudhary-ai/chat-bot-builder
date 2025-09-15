# banking_bot.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from bots.base_bot import BaseBot, QueryRequest, HumanAssistanceRequest, get_current_user
from database.sessions import get_db

banking_prompt = """
As a banking assistant, you are here to help customers with their everyday banking needs. You can provide account balances, transaction history, and information on banking products like loans and credit cards. You must prioritize security and verify the user's identity before providing any sensitive information. For transactions or issues that require manual authorization, you must escalate the query to a human banking representative. You should never ask for passwords or PINs.

If you cannot resolve a banking issue or if the user explicitly requests human assistance, you should suggest they flag their query for human assistance.

Context: {context}
Question: {input}
"""

class EnhancedBankingBot(BaseBot):
    def detect_banking_human_assistance_needed(self, question: str, answer: str) -> bool:
        """Enhanced detection for banking-specific issues that need human assistance"""
        
        # Banking-specific keywords that always need human assistance
        critical_banking_keywords = [
            "fraud", "unauthorized transaction", "dispute", "stolen card", "compromised account",
            "identity theft", "suspicious activity", "blocked account", "locked account",
            "error in transaction", "missing money", "incorrect charge", "refund request",
            "loan application", "mortgage", "credit application", "account opening",
            "large transfer", "wire transfer", "international transfer", "investment advice"
        ]
        
        # General human assistance keywords
        human_assistance_keywords = [
            "human assistance", "speak to human", "talk to agent", "contact support",
            "human help", "real person", "live agent", "customer service",
            "escalate", "complaint", "urgent", "emergency", "manager", "supervisor"
        ]
        
        question_lower = question.lower()
        
        # Check for critical banking issues
        for keyword in critical_banking_keywords:
            if keyword in question_lower:
                return True
        
        # Check for general human assistance requests
        for keyword in human_assistance_keywords:
            if keyword in question_lower:
                return True
        
        # Check if the answer indicates uncertainty
        uncertain_phrases = [
            "i don't know", "i'm not sure", "i cannot", "i can't help",
            "beyond my capabilities", "contact a human", "speak with",
            "recommend consulting", "suggest speaking", "unable to assist"
        ]
        
        answer_lower = answer.lower()
        for phrase in uncertain_phrases:
            if phrase in answer_lower:
                return True
                
        return False

    def ask_question(self, request, bot_id, current_user, db):
        """Enhanced ask_question that automatically creates tickets for banking issues"""
        question = request.question
        cached = self.get_cached_answer(question)

        if cached:
            answer = cached["answer"]
        else:
            result = self.retrieval_chain.invoke({"input": question})
            answer = result["answer"]
            self.set_cached_answer(question, result)

        # Save conversations
        from bots.base_bot import save_conversation
        save_conversation(
            db=db,
            user_id=current_user.id,
            bot_id=bot_id,
            source="user",
            content=question,
            channel="web",
            resolved=False,
        )

        save_conversation(
            db=db,
            user_id=current_user.id,
            bot_id=bot_id,
            source="bot",
            content=answer,
            channel="web",
            resolved=False,
        )

        # Enhanced human assistance detection
        needs_assistance = self.detect_banking_human_assistance_needed(question, answer)
        
        if needs_assistance:
            # Automatically create ticket for banking issues
            from adminbackend import tickets as tickets_crud
            import schemas
            
            # Create ticket automatically
            ticket_data = schemas.TicketCreate(
                topic="Banking Human Assistance Request",
                description=f"Query: {question}\n\nBot Response: {answer}\n\nAuto-flagged for human assistance."
            )
            
            ticket = tickets_crud.create_ticket(
                db=db,
                ticket=ticket_data,
                user_id=current_user.id,
                bot_id=bot_id
            )
            
            return {
                "answer": f"{answer}\n\n🎯 Your query has been automatically flagged for human assistance due to its complexity. A banking specialist will review your request. Ticket ID: {ticket.id}",
                "needs_human_assistance": True,
                "ticket_created": True,
                "ticket_id": ticket.id,
                "human_assistance_message": "A human assistance ticket has been automatically created for your banking query."
            }
        else:
            return {"answer": answer, "needs_human_assistance": False}

banking_bot = EnhancedBankingBot(system_prompt=banking_prompt)

# Create router for banking bot
router = APIRouter()

@router.post("/ask")
def ask_banking_question(
    request: QueryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a banking question"""
    return banking_bot.ask_question(
        request=request,
        bot_id=5,  # Banking bot ID (Bank Agent)
        current_user=current_user,
        db=db
    )

@router.post("/request-human-assistance")
def request_human_assistance(
    request: HumanAssistanceRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a human assistance ticket for banking"""
    print(f"DEBUG: Banking request-human-assistance called with query='{request.query}'")
    result = banking_bot.create_human_assistance_ticket(
        request=request,
        bot_id=5,  # Banking bot ID (Bank Agent)
        current_user=current_user,
        db=db
    )
    print(f"DEBUG: Banking assistance ticket created with ID={result.get('ticket_id', 'unknown')}")
    return result

