# base_bot.py
import sys
import pickle

from dotenv import load_dotenv
import redis
from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.combine_documents import create_stuff_documents_chain

from auth.auth import SECRET_KEY, ALGORITHM
from database.sessions import get_db
from database.database import get_user_by_email, Conversation
from backend.knowledgebase import embeddings

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class QueryRequest(BaseModel):
    question: str

class HumanAssistanceRequest(BaseModel):
    topic: str
    description: Optional[str] = None

def get_current_user(request: Request, db: Session = Depends(get_db)):
    print("--- In get_current_user (base_bot) ---")
    sys.stdout.flush()

    auth_header = request.headers.get("Authorization")
    print(f"Authorization header: {auth_header}")
    sys.stdout.flush()

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = auth_header.split(" ")[1]
    print(f"Extracted token: {token}")
    sys.stdout.flush()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")
        sys.stdout.flush()
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        print(f"JWTError: {e}")
        sys.stdout.flush()
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

class BaseBot:
    def __init__(self, system_prompt: str, persist_directory: str = "chroma_db"):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            callbacks=[StreamingStdOutCallbackHandler()],
        )
        self.system_prompt = ChatPromptTemplate.from_template(system_prompt)
        self.vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        self.cache = self._init_redis()
        self.retrieval_chain = self._init_retrieval_chain()
        

    def _init_redis(self):
        try:
            cache = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)
            cache.ping()
            print("Redis connection successful")
            return cache
        except redis.ConnectionError:
            print("Redis connection failed, caching will be disabled")
            return None

    def _init_retrieval_chain(self):
        retriever = self.vectorstore.as_retriever(search_type="similarity")
        document_chain = create_stuff_documents_chain(self.model, self.system_prompt)
        return create_retrieval_chain(retriever, document_chain)

    def get_cached_answer(self, query: str):
        if not self.cache:
            return None
        try:
            cached = self.cache.get(query)
            if cached:
                return pickle.loads(cached)
        except Exception as e:
            print(f"Cache retrieval error: {e}")
        return None

    def set_cached_answer(self, query: str, answer: str):
        if not self.cache:
            return
        try:
            self.cache.set(query, pickle.dumps(answer), ex=3600)  # expires in 1 hour
        except Exception as e:
            print(f"Cache storage error: {e}")

    def detect_human_assistance_needed(self, question: str, answer: str) -> bool:
        """
        Detect if human assistance is needed based on the question and answer
        """
        print(f"DETECTION DEBUG: Question: {question}")
        print(f"DETECTION DEBUG: Answer: {answer}")
        
        # For testing - always return True if question contains "help"
        if "help" in question.lower():
            print("DETECTION DEBUG: Found 'help' keyword - returning True")
            return True
        
        # Keywords that suggest human assistance is needed
        human_assistance_keywords = [
            "human assistance", "speak to human", "talk to agent", "contact support",
            "human help", "real person", "live agent", "customer service",
            "escalate", "complaint", "urgent", "emergency", "help me", "assistance",
            "fraud", "dispute", "unauthorized", "problem", "issue", "error"
        ]
        
        # Check if user explicitly asks for human assistance
        question_lower = question.lower()
        for keyword in human_assistance_keywords:
            if keyword in question_lower:
                print(f"DETECTION DEBUG: Human assistance keyword '{keyword}' found in question: {question}")
                return True
        
        # Check if the answer indicates the bot couldn't help adequately
        uncertain_phrases = [
            "i don't know", "i'm not sure", "i cannot", "i can't help",
            "beyond my capabilities", "contact a human", "speak with",
            "recommend consulting", "suggest speaking"
        ]
        
        answer_lower = answer.lower()
        for phrase in uncertain_phrases:
            if phrase in answer_lower:
                print(f"DETECTION DEBUG: Uncertain phrase '{phrase}' found in answer: {answer}")
                return True
        
        print("DETECTION DEBUG: No human assistance needed")
        return False

    def create_human_assistance_response(self, original_answer: str) -> dict:
        """
        Create a response that includes human assistance option
        """
        return {
            "answer": f"{original_answer}\n\n🎯 Would you like to flag this for human assistance?",
            "needs_human_assistance": True,
            "human_assistance_message": "It seems like you might need additional help. Would you like to flag this query for human assistance?",
            "show_human_assistance_button": True
        }

    def ask_question(
        self,
        request: "QueryRequest",
        bot_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        question = request.question
        cached = self.get_cached_answer(question)

        if cached:
            answer = cached["answer"]
        else:
            result = self.retrieval_chain.invoke({"input": question})
            answer = result["answer"]
            self.set_cached_answer(question, result)

        # Save user question
        save_conversation(
            db=db,
            user_id=current_user.id,
            bot_id=bot_id,
            source="user",
            content=question,
            channel="web",
            resolved=False,
        )

        # Save bot answer
        save_conversation(
            db=db,
            user_id=current_user.id,
            bot_id=bot_id,
            source="bot",
            content=answer,
            channel="web",
            resolved=False,
        )

        # Check if human assistance is needed
        needs_assistance = self.detect_human_assistance_needed(question, answer)
        print(f"DEBUG: Question: {question}")
        print(f"DEBUG: Answer: {answer}")
        print(f"DEBUG: Needs assistance: {needs_assistance}")
        
        if needs_assistance:
            response = self.create_human_assistance_response(answer)
            print(f"DEBUG: Human assistance response: {response}")
            return response
        else:
            response = {"answer": answer, "needs_human_assistance": False}
            print(f"DEBUG: Normal response: {response}")
            return response

    def create_human_assistance_ticket(
        self,
        request,  # HumanAssistanceRequest object
        bot_id: int,
        current_user,
        db: Session,
    ):
        """
        Create a human assistance ticket for the user
        """
        from adminbackend import tickets as tickets_crud
        import schemas
        
        # Create full description combining query and context
        description = f"Query: {request.query}"
        if request.context:
            description += f"\n\nContext: {request.context}"
        
        # Create ticket data
        ticket_data = schemas.TicketCreate(
            topic="Human Assistance Request", 
            description=description
        )
        
        # Create the ticket
        ticket = tickets_crud.create_ticket(
            db=db, 
            ticket=ticket_data, 
            user_id=current_user.id,
            bot_id=bot_id  # Now properly set from the calling bot
        )
        
        # Save conversation about ticket creation
        save_conversation(
            db=db,
            user_id=current_user.id,
            bot_id=bot_id,
            source="system",
            content=f"Human assistance ticket created: {ticket_data.topic}",
            channel="web",
            resolved=False,
        )
        
        return {
            "success": True,
            "message": "Your query has been flagged for human assistance. Our support team will review it shortly.",
            "ticket_id": ticket.id,
            "status": ticket.status,
            "created_at": ticket.created_at
        }

def save_conversation(
    db: Session, user_id: int, bot_id: int, source: str, content: str, channel: str = "web", resolved: bool = False
):
    convo = Conversation(
        user_id=user_id,
        bot_id=bot_id,
        interaction={"source": source, "content": content, "channel": channel},
        resolved=resolved,
    )
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo
