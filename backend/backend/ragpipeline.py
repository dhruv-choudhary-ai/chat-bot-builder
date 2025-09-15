# ragpipeline.py
import sys
import pickle

from dotenv import load_dotenv
import redis
from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.combine_documents import create_stuff_documents_chain

from auth.auth import SECRET_KEY, ALGORITHM
from database.sessions import get_db
from database.database import get_user_by_email, Conversation
from .knowledgebase import embeddings

load_dotenv()

# Initialize the language model
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    callbacks=[StreamingStdOutCallbackHandler()],
)
llm = model

# Define the system prompt template
system_prompt = ChatPromptTemplate.from_template(
    """
Answer the user's question based on the following context, whatever language they are typing decode the words well and try to answer it in english only.
If you don't know the answer, just say that you don't know and ask them that can you flag this for human assistance.

Context: {context}
Question: {input}
"""
)

# Initialize vector store
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

# Connect to Redis for caching
try:
    cache = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)
    cache.ping()  # Test the connection
    print("Redis connection successful")
except redis.ConnectionError:
    print("Redis connection failed, caching will be disabled")
    cache = None


def get_cached_answer(query):
    """Retrieve cached answer from Redis"""
    if not cache:
        return None
    try:
        cached = cache.get(query)
        if cached:
            return pickle.loads(cached)
    except Exception as e:
        print(f"Cache retrieval error: {e}")
    return None


def set_cached_answer(query, answer):
    """Store answer in Redis cache"""
    if not cache:
        return
    try:
        cache.set(query, pickle.dumps(answer), ex=3600)  # expires in 1 hour
    except Exception as e:
        print(f"Cache storage error: {e}")


# Initialize retrieval chain
retriever = vectorstore.as_retriever(search_type="similarity")
document_chain = create_stuff_documents_chain(llm, system_prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current user from Authorization header for API routes"""
    print("--- In get_current_user (ragpipeline) ---")
    sys.stdout.flush()

    # Get token from Authorization header
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


class QueryRequest(BaseModel):
    """Request model for user queries"""

    question: str


def save_conversation(
    db: Session, user_id: int, source: str, content: str, channel: str = "web", resolved: bool = False
):
    """Save a single interaction message to the database."""
    convo = Conversation(
        user_id=user_id,
        interaction={"source": source, "content": content, "channel": channel},
        resolved=resolved,
    )
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo



# Initialize router
router = APIRouter()


@router.post("/query")
def ask_question(
    request: QueryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle user questions and return AI-generated answers"""
    question = request.question
    cached = get_cached_answer(question)

    if cached:
        answer = cached["answer"]
    else:
        result = retrieval_chain.invoke({"input": question})
        answer = result["answer"]
        set_cached_answer(question, result)

    # Save the user's question
    save_conversation(
        db=db,
        user_id=current_user.id,
        source="user",
        content=question,
        channel="web",
        resolved=False,
    )

    # Save the bot's answer
    save_conversation(
        db=db,
        user_id=current_user.id,
        source="bot",
        content=answer,
        channel="web",
        resolved=False, # Or determine based on answer
    )

    return {"answer": answer}
