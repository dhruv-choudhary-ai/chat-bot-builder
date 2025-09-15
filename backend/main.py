# main.py
import sys
import os
from datetime import timedelta, date
from typing import List

# ... (rest of the code) ...
from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile
import shutil
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from database.sessions import session_local
from database.database import User, Admin, Bot, get_user_by_email, Conversation, Ticket
# from backend.ragpipeline import router as rag_router
from adminbackend.inbox import get_inbox_dates, get_users_by_date, get_user_conversation_by_date
from backend.knowledgebase import update_knowledge_base
import schemas
from adminbackend import tickets as tickets_crud
from schemas import UserResponse, ConversationResponse

# Import bot routers
from bots.banking_bot import router as banking_router
from bots.career_counselling_bot import router as career_router
from bots.retail_bot import router as retail_router
from bots.insurance_bot import router as insurance_router
from bots.hotel_booking_bot import router as hotel_booking_router
from bots.telecom_bot import router as telecom_router
from bots.real_estate_bot import router as real_estate_router
from bots.lead_capturing_bot import router as lead_capturing_router
from bots.course_enrollment_bot import router as course_enrollment_router

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Template setup
templates = Jinja2Templates(directory="templates")

# Serve static files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ALLOW_ADMIN_SIGNUP = os.getenv("ALLOW_ADMIN_SIGNUP", "False").lower() == "true"

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@app.get("/users/me/bots", response_model=List[schemas.Bot])
def get_user_bots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns a list of bots associated with the current user.
    """
    # Assuming a user can be associated with multiple bots, or all bots are available to all users.
    # For now, let's assume all created bots are available to any logged-in user.
    # If bots are user-specific, this query needs to be adjusted.
    return db.query(Bot).all() # Or filter by user_id if bots are assigned to users


# ---------- Serve UI ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def user_interface(request: Request):
    """Serve the dashboard - authentication is handled client-side"""
    return templates.TemplateResponse("userinterface.html", {"request": request})


# -------------------------
#  User Registration (Signup)
# -------------------------
class UserCreate(BaseModel):
    email: str
    password: str
    phone_number: str


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # check if user already exists by email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # check if phone number already exists
    existing_phone = db.query(User).filter(User.phone_number == user.phone_number).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # hash password
    hashed_pw = get_password_hash(user.password)

    # create user object with phone number
    new_user = User(
        email=user.email, 
        password=hashed_pw, 
        phone_number=user.phone_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # generate token for new user
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )

    # try:
    #     client.messages.create(
    #         from_=TWILIO_WHATSAPP_NUMBER,
    #         body=f"Hello {new_user.email}! 👋 Welcome to our platform.",
    #         to=f"whatsapp:{new_user.phone_number}"
    #     )
    # except Exception as e:
    #     print("Failed to send WhatsApp message:", e)
    return {
        "msg": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
    }


# -------------------------
#  User Login (Existing)
# -------------------------
@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# -------------------------
#  Protected Route (Profile)
# -------------------------
@app.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def test_dependency():
    print("--- In test_dependency ---")
    sys.stdout.flush()


@app.get("/test", dependencies=[Depends(test_dependency)])
def test_endpoint():
    return {"message": "Test endpoint works!"}


@app.get("/debug")
def debug_endpoint():
    """Debug endpoint to test server"""
    return {"message": "Debug endpoint works!", "routes": "ui route should work"}


@app.get("/favicon.ico")
def favicon():
    """Return empty response for favicon to prevent 404 errors"""
    return Response(content="", media_type="image/x-icon")


# -------------------------
#  Admin Registration & Login
# -------------------------
class AdminCreate(BaseModel):
    email: str
    password: str
    name: str = None
    phone_number: str = None


def get_admin_by_email(db: Session, email: str):
    return db.query(Admin).filter(Admin.email == email).first()


def get_current_admin(request: Request, db: Session = Depends(get_db)):
    """Get current admin from JWT token"""
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_type: str = payload.get("type")  # "admin" or "user"
        if email is None or user_type != "admin":
            raise HTTPException(status_code=401, detail="Invalid admin token")
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    admin = get_admin_by_email(db, email)
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")

    return admin


@app.post("/admin/register")
def admin_register(admin: AdminCreate, db: Session = Depends(get_db)):
    # Check if admin already exists by email
    existing_admin = get_admin_by_email(db, admin.email)
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin email already registered")
    
    # Check if phone number already exists (if provided)
    if admin.phone_number:
        existing_phone = db.query(Admin).filter(Admin.phone_number == admin.phone_number).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    # Hash password
    hashed_pw = get_password_hash(admin.password)

    # Create admin object
    new_admin = Admin(
        email=admin.email,
        password=hashed_pw,
        name=admin.name,
        phone_number=admin.phone_number
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    # Generate token for new admin
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": new_admin.email, "type": "admin"}, expires_delta=access_token_expires
    )

    return {
        "msg": "Admin registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.post("/admin/token")
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    admin = get_admin_by_email(db, form_data.username)
    if not admin or not verify_password(form_data.password, admin.password):
        raise HTTPException(status_code=400, detail="Invalid admin credentials")

    if not admin.is_active:
        raise HTTPException(status_code=400, detail="Admin account is deactivated")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": admin.email, "type": "admin"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/admin/me")
def read_admin_me(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return {
        "id": admin.id,
        "email": admin.email,
        "name": admin.name,
        "role": admin.role
    }


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, bot_id: int = None):
    """Serve the admin dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request, "bot_id": bot_id})


@app.get("/create-bot", response_class=HTMLResponse)
def create_bot_page(request: Request):
    """Serve the bot creation page"""
    return templates.TemplateResponse("create_bot.html", {"request": request})


@app.get("/bot/{bot_id}/dashboard", response_class=HTMLResponse)
def bot_dashboard_page(request: Request, bot_id: int):
    """Serve the bot-specific dashboard page"""
    return templates.TemplateResponse("bot_dashboard.html", {"request": request, "bot_id": bot_id})


@app.get("/admin/bots/{bot_id}", response_model=schemas.Bot)
def get_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.admin_id == current_admin.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot


# -------------------------
#  Admin Bot Management
# -------------------------
AVAILABLE_BOTS = [
    "Retail Bot",
    "Telecom bot",
    "Course Enrollment bot",
    "Career Counselling Bot",
    "Lead Capturing Bot",
    "Insurance Bot",
    "Hotel Booking Bot",
    "Banking Bot",
    "Real estate bot",
]

class BotCreate(BaseModel):
    name: str
    bot_type: str

@app.get("/admin/bots/available", response_model=List[str])
def get_available_bots():
    """
    Returns a list of available bot types. This endpoint is publicly accessible
    and does not require authentication.
    """
    return AVAILABLE_BOTS

@app.get("/public/bots/available", response_model=List[str])
def get_public_available_bots():
    """
    Returns a list of available bot types. This endpoint is explicitly public
    and does not require authentication.
    """
    return AVAILABLE_BOTS

@app.post("/admin/bots", response_model=schemas.Bot)
def create_bot(
    bot: BotCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    if bot.bot_type not in AVAILABLE_BOTS:
        raise HTTPException(status_code=400, detail="Invalid bot type")
    
    new_bot = Bot(
        name=bot.name,
        bot_type=bot.bot_type,
        admin_id=current_admin.id
    )
    db.add(new_bot)
    db.commit()
    db.refresh(new_bot)
    return new_bot

@app.get("/admin/bots", response_model=List[schemas.Bot])
def get_created_bots(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return db.query(Bot).filter(Bot.admin_id == current_admin.id).all()


@app.get("/admin/bots/{bot_id}/inbox/dates", response_model=List[date])
def get_bot_inbox_dates_route(bot_id: int, db: Session = Depends(get_db)):
    return get_inbox_dates(db, bot_id=bot_id)


@app.get("/admin/bots/{bot_id}/inbox/users", response_model=List[UserResponse])
def get_bot_users_by_date_route(bot_id: int, date: date, db: Session = Depends(get_db)):
    return get_users_by_date(db, date, bot_id=bot_id)


@app.get("/admin/bots/{bot_id}/inbox/conversations", response_model=List[ConversationResponse])
def get_bot_user_conversation_by_date_route(bot_id: int, user_id: int, date: date, db: Session = Depends(get_db)):
    return get_user_conversation_by_date(db, user_id, date, bot_id=bot_id)


@app.get("/admin/bots/{bot_id}/channels", response_model=List[str])
def list_bot_channels(bot_id: int, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.bot_id == bot_id).all()
    channel_set = {c.interaction.get("channel") for c in conversations if c.interaction.get("channel")}
    return sorted(list(channel_set))

@app.get("/admin/bots/{bot_id}/channels/{channel_name}/users", response_model=List[UserResponse])
def get_bot_users_by_channel(bot_id: int, channel_name: str, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.bot_id == bot_id, Conversation.interaction["channel"].astext == channel_name).all()
    if not conversations:
        return []
    
    user_ids = {c.user_id for c in conversations}
    
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    return users

@app.get("/admin/bots/{bot_id}/channels/{channel_name}/users/{user_id}/conversations", response_model=List[ConversationResponse])
def get_bot_user_conversations_by_channel(bot_id: int, channel_name: str, user_id: int, db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.bot_id == bot_id,
            Conversation.user_id == user_id,
            Conversation.interaction["channel"].astext == channel_name
        )
        .order_by(Conversation.created_at.asc())
        .all()
    )
    return conversations


# -------------------------
#  Admin Tickets Routes
# -------------------------

@app.get("/admin/bots/{bot_id}/tickets", response_model=List[schemas.Ticket])
def get_bot_tickets_route(
    bot_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return tickets_crud.get_bot_tickets(db=db, bot_id=bot_id)

@app.get("/admin/bots/{bot_id}/tickets/{ticket_id}")
def get_bot_ticket_details_route(
    bot_id: int, 
    ticket_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    ticket = tickets_crud.get_bot_ticket_details(db=db, bot_id=bot_id, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    user = db.query(User).filter(User.id == ticket.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "ticket": ticket,
        "user": {
            "id": user.id,
            "email": user.email,
            "phone_number": user.phone_number,
            "name": user.name
        }
    }


# -------------------------
#  Admin Inbox
# -------------------------




class UserResponse(BaseModel):
    id: int
    email: str
    phone_number: str | None
    name: str | None
    
    class Config:
        from_attributes = True

from datetime import datetime

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    interaction: dict
    resolved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# -------------------------
#  Admin Channels
# -------------------------

@app.get("/admin/channels", response_model=List[str])
def list_channels(db: Session = Depends(get_db)):
    """Return a list of unique channel names from conversations."""
    # This query is complex to do in pure SQLAlchemy, so we use a little trick.
    # We get all conversations, extract the channel name from the interaction JSON,
    # and then find the unique set.
    conversations = db.query(Conversation).all()
    channel_set = {c.interaction.get("channel") for c in conversations if c.interaction.get("channel")}
    return sorted(list(channel_set))

@app.get("/admin/channels/{channel_name}/users", response_model=List[UserResponse])
def get_users_by_channel(channel_name: str, db: Session = Depends(get_db)):
    """Return a list of users who have interacted on a specific channel."""
    # Find all conversations for the given channel
    conversations = db.query(Conversation).filter(Conversation.interaction["channel"].astext == channel_name).all()
    if not conversations:
        return []
    
    # Get the unique user IDs from those conversations
    user_ids = {c.user_id for c in conversations}
    
    # Get the user objects for those IDs
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    return users

@app.get("/admin/channels/{channel_name}/users/{user_id}/conversations", response_model=List[ConversationResponse])
def get_user_conversations_by_channel(channel_name: str, user_id: int, db: Session = Depends(get_db)):
    """Return all conversations for a specific user on a specific channel."""
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user_id,
            Conversation.interaction["channel"].astext == channel_name
        )
        .order_by(Conversation.created_at.asc())
        .all()
    )
    return conversations


@app.get("/admin/inbox/dates", response_model=List[date])
def get_inbox_dates_route(db: Session = Depends(get_db)):
    """
    Returns all distinct dates where interactions happened for any bot.
    """
    return get_inbox_dates(db)


@app.get("/admin/inbox/users", response_model=List[UserResponse])
def get_users_by_date_route(date: date, db: Session = Depends(get_db)):
    return get_users_by_date(db, date)


@app.get("/admin/inbox/conversations", response_model=List[ConversationResponse])
def get_user_conversation_by_date_route(user_id: int, date: date, db: Session = Depends(get_db)):
    return get_user_conversation_by_date(db, user_id, date)


@app.post("/create-admin")
def create_admin_user(admin: AdminCreate, db: Session = Depends(get_db)):
    if not ALLOW_ADMIN_SIGNUP:
        raise HTTPException(status_code=404, detail="Not Found")

    existing_admin = get_admin_by_email(db, admin.email)
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin email already registered")

    if admin.phone_number:
        existing_phone = db.query(Admin).filter(Admin.phone_number == admin.phone_number).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    hashed_pw = get_password_hash(admin.password)

    new_admin = Admin(
        email=admin.email,
        password=hashed_pw,
        name=admin.name,
        phone_number=admin.phone_number
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"msg": "Admin created successfully"}


# -------------------------
#  Omnichannel Webhooks
# -------------------------
from twilio.rest import Client
from bot_loader import get_bot_by_type
from channels.builders.web import WebMessageBuilder
from channels.builders.twilio import TwilioMessageBuilder
from channels.builders.sms import SmsMessageBuilder # New import
from channels.schemas import StandardizedMessage
from typing import Dict, Any

# --- Twilio Configuration ---
# It is strongly recommended to use environment variables for these
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER") # e.g., 'whatsapp:+14155238886'
TWILIO_SMS_NUMBER = os.getenv("TWILIO_SMS_NUMBER") # New SMS number env var

# Initialize the Twilio client if credentials are provided
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    print("WARNING: Twilio credentials not found. WhatsApp/SMS replies will be disabled.")


from bots.base_bot import QueryRequest, save_conversation

@app.post("/bots/{bot_id}/query")
def ask_question(
    bot_id: int,
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Handle user questions and return AI-generated answers"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    bot_instance = get_bot_by_type(bot.bot_type)
    if not bot_instance:
        raise HTTPException(status_code=500, detail="Bot implementation not found")

    question = request.question
    cached = bot_instance.get_cached_answer(question)

    if cached:
        answer = cached["answer"]
    else:
        result = bot_instance.retrieval_chain.invoke({"input": question})
        answer = result["answer"]
        bot_instance.set_cached_answer(question, result)

    # Save the user's question
    save_conversation(
        db=db,
        user_id=current_user.id,
        bot_id=bot_id,
        source="user",
        content=question,
        channel="web",
        resolved=False,
    )

    # Save the bot's answer
    save_conversation(
        db=db,
        user_id=current_user.id,
        bot_id=bot_id,
        source="bot",
        content=answer,
        channel="web",
        resolved=False, # Or determine based on answer
    )

    # Check if human assistance is needed using the bot's detection logic
    try:
        needs_assistance = bot_instance.detect_human_assistance_needed(question, answer)
        if needs_assistance:
            return bot_instance.create_human_assistance_response(answer)
        else:
            return {"answer": answer, "needs_human_assistance": False}
    except AttributeError:
        # Fallback if bot doesn't have human assistance detection
        return {"answer": answer, "needs_human_assistance": False}


@app.post("/hooks/web")
async def handle_web_message(payload: Dict[Any, Any], db: Session = Depends(get_db)):
    """
    Handles incoming messages from the web chat, gets an AI response, and returns it.
    """
    try:
        builder = WebMessageBuilder(payload)
        standardized_message = builder.build()
        question = standardized_message.content
        bot_id = payload.get("bot_id")

        if not bot_id:
            raise HTTPException(status_code=400, detail="bot_id is required")

        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        bot_instance = get_bot_by_type(bot.bot_type)
        if not bot_instance:
            raise HTTPException(status_code=500, detail="Bot implementation not found")

        # --- Find user and save their message ---
        user = db.query(User).filter(User.email == standardized_message.sender_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with email '{standardized_message.sender_id}' not found.")

        save_conversation(
            db=db, 
            user_id=user.id, 
            bot_id=bot_id,
            source="user", 
            content=question, 
            channel=standardized_message.channel_name
        )

        # --- Generate and Save AI Response ---
        result = bot_instance.retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        save_conversation(
            db=db, 
            user_id=user.id, 
            bot_id=bot_id,
            source="bot", 
            content=ai_response_text, 
            channel=standardized_message.channel_name
        )

        # Return the AI response to the frontend
        return {"answer": ai_response_text}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/hooks/twilio/{bot_id}")
async def handle_twilio_message(request: Request, bot_id: int, db: Session = Depends(get_db)):
    """
    Handles incoming SMS from Twilio, gets an AI response, and sends a reply.
    """
    try:
        payload = await request.form()
        builder = TwilioMessageBuilder(payload)
        standardized_message = builder.build()
        question = standardized_message.content

        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        bot_instance = get_bot_by_type(bot.bot_type)
        if not bot_instance:
            raise HTTPException(status_code=500, detail="Bot implementation not found")

        # --- Find user and save their message ---
        user = db.query(User).filter(User.phone_number == standardized_message.sender_id).first()
        if not user:
            print(f"User with phone number '{standardized_message.sender_id}' not found.")
            return Response(content="", media_type="application/xml")

        save_conversation(
            db=db, 
            user_id=user.id, 
            bot_id=bot_id,
            source="user", 
            content=question, 
            channel=standardized_message.channel_name
        )

        # --- Generate and Send AI Response ---
        result = bot_instance.retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        save_conversation(
            db=db, 
            user_id=user.id, 
            bot_id=bot_id,
            source="bot", 
            content=ai_response_text, 
            channel=standardized_message.channel_name
        )

        # --- Send Reply via Twilio ---
        if twilio_client and TWILIO_WHATSAPP_NUMBER:
            try:
                to_number = f"whatsapp:{standardized_message.sender_id}"
                twilio_client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    body=ai_response_text,
                    to=to_number
                )
            except Exception as e:
                print(f"ERROR: Failed to send Twilio message: {e}")
        
        return Response(content="", media_type="application/xml")

    except Exception as e:
        print(f"An unexpected error occurred in handle_twilio_message: {e}")
        return Response(content="", media_type="application/xml")


@app.post("/hooks/sms/{bot_id}")
async def handle_sms_message(request: Request, bot_id: int, db: Session = Depends(get_db)):
    """
    Handles incoming SMS from Twilio, gets an AI response, and sends a reply.
    """
    try:
        payload = await request.form()
        builder = SmsMessageBuilder(payload)
        standardized_message = builder.build()
        question = standardized_message.content

        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        bot_instance = get_bot_by_type(bot.bot_type)
        if not bot_instance:
            raise HTTPException(status_code=500, detail="Bot implementation not found")

        # --- Find user and save their message ---
        user = db.query(User).filter(User.phone_number == standardized_message.sender_id).first()
        if not user:
            print(f"User with phone number '{standardized_message.sender_id}' not found.")
            return Response(content="", media_type="application/xml")

        save_conversation(
            db=db, 
            user_id=user.id, 
            bot_id=bot_id,
            source="user", 
            content=question, 
            channel=standardized_message.channel_name
        )

        # --- Generate and Send AI Response ---
        result = bot_instance.retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        save_conversation(
            db=db, 
            user_id=user.id, 
            bot_id=bot_id,
            source="bot", 
            content=ai_response_text, 
            channel=standardized_message.channel_name
        )

        # --- Send Reply via Twilio ---
        if twilio_client and TWILIO_SMS_NUMBER:
            try:
                # For SMS, no special prefix is needed for the 'to' number
                twilio_client.messages.create(
                    from_=TWILIO_SMS_NUMBER,
                    body=ai_response_text,
                    to=standardized_message.sender_id
                )
            except Exception as e:
                print(f"ERROR: Failed to send SMS message: {e}")
        
        return Response(content="", media_type="application/xml")

    except Exception as e:
        print(f"An unexpected error occurred in handle_sms_message: {e}")
        return Response(content="", media_type="application/xml")


# Include the router from ragpipeline.py
# app.include_router(rag_router)

# Include bot routers
app.include_router(banking_router, prefix="/banking", tags=["Banking Bot"])
app.include_router(career_router, prefix="/career", tags=["Career Bot"])
app.include_router(retail_router, prefix="/retail", tags=["Retail Bot"])
app.include_router(insurance_router, prefix="/insurance", tags=["Insurance Bot"])
app.include_router(hotel_booking_router, prefix="/hotel-booking", tags=["Hotel Booking Bot"])
app.include_router(telecom_router, prefix="/telecom", tags=["Telecom Bot"])
app.include_router(real_estate_router, prefix="/real-estate", tags=["Real Estate Bot"])
app.include_router(lead_capturing_router, prefix="/lead-capturing", tags=["Lead Capturing Bot"])
app.include_router(course_enrollment_router, prefix="/course-enrollment", tags=["Course Enrollment Bot"])


@app.post("/admin/upload-document")
async def upload_document(file: UploadFile = File(...)):
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "uploaded_docs")
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Trigger knowledgebase update
    update_knowledge_base()
    return {"success": True, "filename": file.filename}

@app.get("/admin/get-documents")
async def get_documents():
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "uploaded_docs")
    documents = os.listdir(upload_dir)
    return documents

@app.get("/admin/bots/{bot_id}/knowledge-base", response_model=List[str])
def get_bot_knowledge_base(
    bot_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Returns a list of knowledge base documents for a specific bot.
    For now, it returns all documents in backend/uploaded_docs.
    In a real application, this would be filtered by bot_id.
    """
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "uploaded_docs")
    if not os.path.exists(upload_dir):
        return []
    documents = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    return documents


@app.post("/users/me/tickets", response_model=schemas.Ticket)
def create_ticket_for_user(
    ticket: schemas.TicketCreate,
    bot_id: int = None,  # Optional bot_id parameter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: Creating ticket with bot_id={bot_id}, topic='{ticket.topic}'")
    result = tickets_crud.create_ticket(db=db, ticket=ticket, user_id=current_user.id, bot_id=bot_id)
    print(f"DEBUG: Created ticket ID={result.id} with bot_id={result.bot_id}")
    return result


@app.get("/users/me/tickets", response_model=List[schemas.Ticket])
def read_tickets_for_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return tickets_crud.get_user_tickets(db=db, user_id=current_user.id)


@app.get("/admin/tickets", response_model=List[schemas.Ticket])
def read_all_tickets(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return tickets_crud.get_all_tickets(db=db)


@app.get("/admin/tickets/{ticket_id}")
def read_ticket_details(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    ticket = tickets_crud.get_ticket_details(db=db, ticket_id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    user = db.query(User).filter(User.id == ticket.user_id).first()
    
    return {
        "ticket": ticket,
        "user": {
            "email": user.email,
            "phone_number": user.phone_number,
        }
    }


@app.patch("/users/me/tickets/{ticket_id}/resolve", response_model=schemas.Ticket)
def resolve_user_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = tickets_crud.get_ticket_details(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to resolve this ticket")
    if ticket.status == "resolved":
        raise HTTPException(status_code=400, detail="Ticket is already resolved")

    return tickets_crud.update_ticket_status(db=db, ticket_id=ticket_id, new_status="resolved")


# Debug endpoint to test bot responses
@app.post("/debug/test-banking-response")
def debug_banking_response(db: Session = Depends(get_db)):
    """Debug endpoint to test banking bot human assistance detection"""
    try:
        from bots.banking_bot import banking_bot
        
        # Create a mock request object
        class MockRequest:
            def __init__(self, question):
                self.question = question
        
        # Create a mock user
        class MockUser:
            def __init__(self):
                self.id = 1
                self.email = "test@test.com"
        
        # Test queries that should trigger human assistance
        test_queries = [
            "I need human assistance with my account",
            "I have fraud on my account", 
            "Help me with unauthorized transaction",
            "I want to speak to a human agent"
        ]
        
        results = []
        for query in test_queries:
            try:
                mock_request = MockRequest(query)
                mock_user = MockUser()
                
                # Test the detection method directly
                needs_assistance = banking_bot.detect_banking_human_assistance_needed(query, "sample response")
                
                results.append({
                    "query": query,
                    "needs_assistance_detected": needs_assistance,
                    "test_status": "✅ Detected" if needs_assistance else "❌ Not detected"
                })
            except Exception as e:
                results.append({
                    "query": query,
                    "error": str(e),
                    "test_status": "❌ Error"
                })
        
        return {
            "message": "Banking bot human assistance detection test",
            "results": results,
            "banking_bot_type": str(type(banking_bot).__name__)
        }
        
    except Exception as e:
        return {"error": str(e), "details": "Failed to test banking bot"}


# Debug endpoint to check database contents
@app.get("/debug/database-status")
def debug_database_status(db: Session = Depends(get_db)):
    """Debug endpoint to check database status"""
    try:
        users = db.query(User).all()
        tickets = db.query(Ticket).all()
        bots = db.query(Bot).all()
        
        return {
            "users_count": len(users),
            "tickets_count": len(tickets),
            "bots_count": len(bots),
            "users": [{"id": u.id, "email": u.email} for u in users[:5]],
            "tickets": [{"id": t.id, "user_id": t.user_id, "bot_id": t.bot_id, "topic": t.topic, "description": t.description[:100] if t.description else None} for t in tickets[:5]],
            "bots": [{"id": b.id, "name": b.name, "bot_type": b.bot_type} for b in bots[:5]]
        }
    except Exception as e:
        return {"error": str(e)}


# Debug endpoint to test banking bot endpoint
@app.post("/debug/test-banking-endpoint")
def debug_banking_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Debug endpoint to test banking bot functionality"""
    try:
        from bots.banking_bot import banking_bot
        
        # Test query
        question = "I need help with fraud"
        result = banking_bot.retrieval_chain.invoke({"input": question})
        answer = result["answer"]
        
        # Test human assistance detection
        needs_assistance = banking_bot.detect_banking_human_assistance_needed(question, answer)
        
        # If needs assistance, create ticket
        if needs_assistance:
            from adminbackend import tickets as tickets_crud
            import schemas
            
            ticket_data = schemas.TicketCreate(
                topic="Debug Banking Test",
                description=f"Debug test - Query: {question}\n\nBot Response: {answer}"
            )
            
            ticket = tickets_crud.create_ticket(
                db=db,
                ticket=ticket_data,
                user_id=current_user.id,
                bot_id=5  # Banking bot ID
            )
            
            return {
                "success": True,
                "question": question,
                "answer": answer,
                "needs_assistance": needs_assistance,
                "ticket_created": True,
                "ticket_id": ticket.id,
                "ticket_bot_id": ticket.bot_id
            }
        else:
            return {
                "success": True,
                "question": question,
                "answer": answer,
                "needs_assistance": needs_assistance,
                "ticket_created": False
            }
            
    except Exception as e:
        return {"error": str(e), "details": "Failed to test banking endpoint"}



