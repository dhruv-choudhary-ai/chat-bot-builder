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
    allow_origins=["*"],  # Allows all origins for embedded chatbot functionality
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
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

@app.get("/users/conversations", response_model=List[ConversationResponse])
def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns a list of conversations for the current user across all bots.
    Groups user questions with bot answers.
    """
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.created_at.desc()).all()
    
    # Group conversations by pairing user questions with bot answers
    conversation_responses = []
    grouped_conversations = {}
    
    for conv in conversations:
        interaction_data = conv.interaction if isinstance(conv.interaction, dict) else {}
        source = interaction_data.get("source", "unknown")
        content = interaction_data.get("content", "")
        channel = interaction_data.get("channel", "web")
        
        # Use bot_id and rough timestamp grouping to match questions with answers
        # Group by bot_id and time window (within 1 minute)
        time_key = conv.created_at.replace(second=0, microsecond=0)  # Round to minute
        group_key = f"{conv.bot_id}_{time_key}"
        
        if group_key not in grouped_conversations:
            grouped_conversations[group_key] = {
                "id": conv.id,
                "user_id": conv.user_id,
                "bot_id": conv.bot_id,
                "question": "",
                "answer": "",
                "channel": channel,
                "resolved": conv.resolved,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
        
        if source == "user":
            grouped_conversations[group_key]["question"] = content
        elif source == "bot":
            grouped_conversations[group_key]["answer"] = content
    
    # Convert grouped conversations to response format
    for group in grouped_conversations.values():
        if group["question"] or group["answer"]:  # Only include if there's actual content
            conversation_responses.append(ConversationResponse(
                id=group["id"],
                user_id=group["user_id"],
                interaction={
                    "question": group["question"],
                    "answer": group["answer"],
                    "channel": group["channel"]
                },
                resolved=group["resolved"],
                created_at=group["created_at"],
                updated_at=group["updated_at"]
            ))
    
    return conversation_responses
    
    # Process to group questions with their answers
    grouped_conversations = {}
    for conv in conversations:
        # Use a simple grouping strategy - group by timestamp proximity
        time_key = conv.created_at.strftime("%Y-%m-%d %H:%M")
        if time_key not in grouped_conversations:
            grouped_conversations[time_key] = {"question": "", "answer": "", "conv_obj": conv}
        
        if conv.source == "user":
            grouped_conversations[time_key]["question"] = conv.content
        else:
            grouped_conversations[time_key]["answer"] = conv.content
    
    # Convert grouped conversations back to response format
    final_responses = []
    for time_key, data in grouped_conversations.items():
        if data["question"]:  # Only include if there's a question
            final_responses.append(ConversationResponse(
                id=data["conv_obj"].id,
                user_id=data["conv_obj"].user_id,
                interaction={
                    "question": data["question"],
                    "answer": data["answer"],
                    "channel": data["conv_obj"].channel
                },
                resolved=data["conv_obj"].resolved,
                created_at=data["conv_obj"].created_at,
                updated_at=data["conv_obj"].updated_at
            ))
    
    return final_responses


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

class ChatMessage(BaseModel):
    message: str

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

@app.get("/admin/bots/{bot_id}/embed-script")
def generate_embed_script(
    bot_id: int,
    primary_color: str = "#3B82F6",
    position: str = "bottom-right",
    greeting: str = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Generate a JavaScript embed script for the chatbot
    """
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.admin_id == current_admin.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    if not greeting:
        greeting = f"Hi! I'm {bot.name}, your {bot.bot_type.lower()} assistant. How can I help you today?"
    
    # Generate position CSS
    if position == "bottom-right":
        position_css = "bottom: 20px; right: 20px;"
    else:  # bottom-left
        position_css = "bottom: 20px; left: 20px;"
    
    # Generate the embed script
    embed_script = f"""
(function() {{
    // LifeBot Configuration
    window.LifeBotConfig = {{
        botId: {bot.id},
        botName: "{bot.name}",
        botType: "{bot.bot_type}",
        primaryColor: "{primary_color}",
        position: "{position}",
        greeting: "{greeting}",
        apiUrl: "http://localhost:8000"
    }};
    
    // Create typing indicator
    const createTypingIndicator = () => {{
        return `
            <div id="lifebot-typing" style="
                display: flex;
                justify-content: flex-start;
                margin: 8px 0;
                clear: both;
            ">
                <div style="
                    background: white;
                    padding: 16px;
                    border-radius: 18px;
                    max-width: 80%;
                    width: fit-content;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    animation: slideInLeft 0.3s ease-out;
                ">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="display: flex; gap: 4px; align-items: center;">
                            <div style="
                                width: 8px;
                                height: 8px;
                                background-color: #cbd5e0;
                                border-radius: 50%;
                                animation: typing 1.4s infinite;
                            "></div>
                            <div style="
                                width: 8px;
                                height: 8px;
                                background-color: #cbd5e0;
                                border-radius: 50%;
                                animation: typing 1.4s infinite 0.2s;
                            "></div>
                            <div style="
                                width: 8px;
                                height: 8px;
                                background-color: #cbd5e0;
                                border-radius: 50%;
                                animation: typing 1.4s infinite 0.4s;
                            "></div>
                        </div>
                        <span style="color: #718096; font-size: 12px; margin-left: 4px;">
                            {bot.name} is typing...
                        </span>
                    </div>
                </div>
            </div>
        `;
    }};
    
    // Add CSS animations
    const addAnimations = () => {{
        const style = document.createElement('style');
        style.textContent = `
            @keyframes typing {{
                0%, 60%, 100% {{
                    transform: translateY(0);
                    opacity: 0.4;
                }}
                30% {{
                    transform: translateY(-10px);
                    opacity: 1;
                }}
            }}
            
            @keyframes slideInLeft {{
                from {{
                    opacity: 0;
                    transform: translateX(-20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateX(0);
                }}
            }}
            
            @keyframes slideInRight {{
                from {{
                    opacity: 0;
                    transform: translateX(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateX(0);
                }}
            }}
            
            @keyframes pulse {{
                0% {{
                    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
                }}
                70% {{
                    box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
                }}
                100% {{
                    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
                }}
            }}
            
            #lifebot-button:hover {{
                animation: pulse 1.5s infinite;
            }}
            
            .lifebot-message-user {{
                animation: slideInRight 0.3s ease-out;
            }}
            
            .lifebot-message-bot {{
                animation: slideInLeft 0.3s ease-out;
            }}
        `;
        document.head.appendChild(style);
    }};
    
    // Create chatbot container
    const createChatbot = () => {{
        addAnimations();
        
        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'lifebot-chatbot';
        chatbotContainer.innerHTML = `
            <div id="lifebot-widget" style="
                position: fixed;
                {position_css}
                z-index: 9999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            ">
                <div id="lifebot-button" style="
                    width: 64px;
                    height: 64px;
                    background: linear-gradient(135deg, {primary_color}, #1e40af);
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    border: 3px solid rgba(255,255,255,0.2);
                    backdrop-filter: blur(10px);
                " onmouseover="this.style.transform='scale(1.1) translateY(-2px)'" onmouseout="this.style.transform='scale(1) translateY(0)'">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round">
                        <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
                    </svg>
                </div>
                <div id="lifebot-chat" style="
                    display: none;
                    width: 360px;
                    height: 500px;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.15), 0 8px 32px rgba(0,0,0,0.1);
                    position: absolute;
                    bottom: 80px;
                    {'right: 0;' if position == 'bottom-right' else 'left: 0;'}
                    overflow: hidden;
                    border: 1px solid rgba(255,255,255,0.2);
                    backdrop-filter: blur(20px);
                ">
                    <div style="
                        background: linear-gradient(135deg, {primary_color}, #1e40af);
                        color: white;
                        padding: 20px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        border-bottom: 1px solid rgba(255,255,255,0.1);
                    ">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="
                                width: 40px; 
                                height: 40px; 
                                background: rgba(255,255,255,0.15); 
                                border-radius: 50%; 
                                display: flex; 
                                align-items: center; 
                                justify-content: center;
                                border: 2px solid rgba(255,255,255,0.2);
                            ">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                                    <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
                                </svg>
                            </div>
                            <div>
                                <div style="font-weight: 600; font-size: 16px; letter-spacing: -0.5px;">{bot.name}</div>
                                <div style="font-size: 13px; opacity: 0.9; display: flex; align-items: center; gap: 6px;">
                                    <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                                    Online
                                </div>
                            </div>
                        </div>
                        <button id="lifebot-close" style="
                            background: rgba(255,255,255,0.1);
                            border: none;
                            color: white;
                            cursor: pointer;
                            padding: 8px;
                            border-radius: 8px;
                            transition: all 0.2s;
                            width: 32px;
                            height: 32px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        " onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                    <div id="lifebot-messages" style="
                        height: 360px;
                        overflow-y: auto;
                        padding: 20px;
                        background: linear-gradient(to bottom, #f8fafc, #f1f5f9);
                        scroll-behavior: smooth;
                    ">
                        <div class="lifebot-message-bot" style="
                            display: flex;
                            justify-content: flex-start;
                            margin: 8px 0;
                            clear: both;
                        ">
                            <div style="
                                background: white;
                                padding: 16px;
                                border-radius: 18px;
                                max-width: 85%;
                                width: fit-content;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                                font-size: 14px;
                                line-height: 1.5;
                                border: 1px solid rgba(0,0,0,0.05);
                            ">
                                {greeting}
                            </div>
                        </div>
                    </div>
                    <div style="
                        padding: 20px;
                        border-top: 1px solid #e2e8f0;
                        background: white;
                        display: flex;
                        gap: 12px;
                        align-items: flex-end;
                    ">
                        <input id="lifebot-input" type="text" placeholder="Type your message..." style="
                            flex: 1;
                            padding: 12px 16px;
                            border: 2px solid #e2e8f0;
                            border-radius: 24px;
                            outline: none;
                            font-size: 14px;
                            transition: all 0.2s;
                            background: #f8fafc;
                        " onfocus="this.style.border='2px solid {primary_color}'; this.style.background='white';" onblur="this.style.border='2px solid #e2e8f0'; this.style.background='#f8fafc';">
                        <button id="lifebot-send" style="
                            background: linear-gradient(135deg, {primary_color}, #1e40af);
                            color: white;
                            border: none;
                            border-radius: 50%;
                            width: 44px;
                            height: 44px;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            transition: all 0.2s;
                            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22,2 15,22 11,13 2,9"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(chatbotContainer);

        // Event listeners
        const button = document.getElementById('lifebot-button');
        const chat = document.getElementById('lifebot-chat');
        const closeBtn = document.getElementById('lifebot-close');
        const input = document.getElementById('lifebot-input');
        const sendBtn = document.getElementById('lifebot-send');
        const messages = document.getElementById('lifebot-messages');

        button.addEventListener('click', () => {{
            chat.style.display = chat.style.display === 'none' ? 'block' : 'none';
            if (chat.style.display === 'block') {{
                input.focus();
            }}
        }});

        closeBtn.addEventListener('click', () => {{
            chat.style.display = 'none';
        }});

        // Show typing indicator
        const showTypingIndicator = () => {{
            const typingHtml = createTypingIndicator();
            messages.insertAdjacentHTML('beforeend', typingHtml);
            messages.scrollTop = messages.scrollHeight;
        }};

        // Hide typing indicator
        const hideTypingIndicator = () => {{
            const typingElement = document.getElementById('lifebot-typing');
            if (typingElement) {{
                typingElement.remove();
            }}
        }};

        const sendMessage = () => {{
            const message = input.value.trim();
            if (!message) return;

            // Disable input while processing
            input.disabled = true;
            sendBtn.disabled = true;
            sendBtn.style.opacity = '0.6';

            // Add user message
            const userMsg = document.createElement('div');
            userMsg.className = 'lifebot-message-user';
            userMsg.style.cssText = `
                display: flex;
                justify-content: flex-end;
                margin: 8px 0;
                clear: both;
            `;
            
            const userMsgContent = document.createElement('div');
            userMsgContent.style.cssText = `
                background: linear-gradient(135deg, {primary_color}, #1e40af);
                color: white;
                padding: 12px 16px;
                border-radius: 18px;
                max-width: 80%;
                width: fit-content;
                font-size: 14px;
                line-height: 1.4;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
                word-wrap: break-word;
            `;
            userMsgContent.textContent = message;
            userMsg.appendChild(userMsgContent);
            messages.appendChild(userMsg);

            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            // Show typing indicator
            showTypingIndicator();

            // Send message to LifeBot API
            fetch('http://localhost:8000/chat/{bot.id}', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ message: message }})
            }})
            .then(response => response.json())
            .then(data => {{
                // Hide typing indicator
                hideTypingIndicator();
                
                // Add bot response
                const botMsg = document.createElement('div');
                botMsg.className = 'lifebot-message-bot';
                botMsg.style.cssText = `
                    display: flex;
                    justify-content: flex-start;
                    margin: 8px 0;
                    clear: both;
                `;
                
                const botMsgContent = document.createElement('div');
                botMsgContent.style.cssText = `
                    background: white;
                    padding: 16px;
                    border-radius: 18px;
                    max-width: 85%;
                    width: fit-content;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    font-size: 14px;
                    line-height: 1.5;
                    border: 1px solid rgba(0,0,0,0.05);
                    word-wrap: break-word;
                `;
                botMsgContent.textContent = data.response || "Thanks for your message! I'm processing your request.";
                botMsg.appendChild(botMsgContent);
                messages.appendChild(botMsg);
                messages.scrollTop = messages.scrollHeight;
                
                // Re-enable input
                input.disabled = false;
                sendBtn.disabled = false;
                sendBtn.style.opacity = '1';
                input.focus();
            }})
            .catch(error => {{
                console.error('Error:', error);
                
                // Hide typing indicator
                hideTypingIndicator();
                
                const botMsg = document.createElement('div');
                botMsg.className = 'lifebot-message-bot';
                botMsg.style.cssText = `
                    display: flex;
                    justify-content: flex-start;
                    margin: 8px 0;
                    clear: both;
                `;
                
                const botMsgContent = document.createElement('div');
                botMsgContent.style.cssText = `
                    background: #fee2e2;
                    color: #dc2626;
                    padding: 16px;
                    border-radius: 18px;
                    max-width: 85%;
                    width: fit-content;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    font-size: 14px;
                    line-height: 1.5;
                    border: 1px solid #fecaca;
                `;
                botMsgContent.textContent = "Sorry, I'm having trouble connecting. Please try again later.";
                botMsg.appendChild(botMsgContent);
                messages.appendChild(botMsg);
                messages.scrollTop = messages.scrollHeight;
                
                // Re-enable input
                input.disabled = false;
                sendBtn.disabled = false;
                sendBtn.style.opacity = '1';
                input.focus();
            }});
        }};

        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter' && !input.disabled) {{
                sendMessage();
            }}
        }});
    }};

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', createChatbot);
    }} else {{
        createChatbot();
    }}
}})();
"""
    
    return Response(
        content=embed_script,
        media_type="application/javascript",
        headers={
            "Content-Disposition": f"attachment; filename=lifebot-{bot.id}-embed.js"
        }
    )

@app.post("/chat/{bot_id}")
def chat_with_bot(
    bot_id: int,
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Handle chat messages for embedded chatbots
    This endpoint is public to allow embedded chatbots to work on external websites
    """
    # Verify bot exists
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    try:
        # Route to the appropriate bot based on bot type
        if bot.bot_type == "Lead Capturing Bot":
            from bots.lead_capturing_bot import lead_capturing_bot
            from bots.base_bot import QueryRequest
            request = QueryRequest(question=message.message)
            # For embedded bots, we'll simulate a simple user session without authentication
            response = lead_capturing_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        elif bot.bot_type == "Banking Bot":
            from bots.banking_bot import banking_bot
            response = banking_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        elif bot.bot_type == "Retail Bot":
            from bots.retail_bot import retail_bot
            response = retail_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        elif bot.bot_type == "Insurance Bot":
            from bots.insurance_bot import insurance_bot
            response = insurance_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        elif bot.bot_type == "Hotel Booking Bot":
            from bots.hotel_booking_bot import hotel_booking_bot
            response = hotel_booking_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        elif bot.bot_type == "Telecom bot":
            from bots.telecom_bot import telecom_bot
            response = telecom_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        elif bot.bot_type == "Course Enrollment bot":
            from bots.course_enrollment_bot import course_enrollment_bot
            response = course_enrollment_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        elif bot.bot_type == "Career Counselling Bot":
            from bots.career_counselling_bot import career_counselling_bot
            response = career_counselling_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        elif bot.bot_type == "Real estate bot":
            from bots.real_estate_bot import real_estate_bot
            response = real_estate_bot.retrieval_chain.invoke({"input": message.message})
            return {
                "response": response["answer"],
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
        else:
            # Fallback for unknown bot types
            return {
                "response": f"Hello! I'm {bot.name}. Thanks for your message: '{message.message}'. How can I assist you further?",
                "bot_name": bot.name,
                "bot_type": bot.bot_type
            }
    except Exception as e:
        # Fallback if there's an error with the AI processing
        print(f"Error processing message with AI: {e}")
        return {
            "response": f"Hello! I'm {bot.name}. I received your message about '{message.message}'. Let me help you with that!",
            "bot_name": bot.name,
            "bot_type": bot.bot_type,
            "error": "AI processing temporarily unavailable"
        }


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


@app.get("/admin/bots/{bot_id}/conversations", response_model=List[ConversationResponse])
def get_bot_all_conversations(
    bot_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Get all conversations for a specific bot with grouped question/answer pairs.
    Returns conversations with user details for admin dashboard.
    """
    conversations = db.query(Conversation).filter(Conversation.bot_id == bot_id).order_by(Conversation.created_at.desc()).all()
    
    # Group conversations by pairing user questions with bot answers
    conversation_responses = []
    grouped_conversations = {}
    
    for conv in conversations:
        interaction_data = conv.interaction if isinstance(conv.interaction, dict) else {}
        source = interaction_data.get("source", "unknown")
        content = interaction_data.get("content", "")
        channel = interaction_data.get("channel", "web")
        
        # Use user_id and rough timestamp grouping to match questions with answers
        time_key = conv.created_at.replace(second=0, microsecond=0)  # Round to minute
        group_key = f"{conv.user_id}_{time_key}"
        
        if group_key not in grouped_conversations:
            grouped_conversations[group_key] = {
                "id": conv.id,
                "user_id": conv.user_id,
                "bot_id": conv.bot_id,
                "question": "",
                "answer": "",
                "channel": channel,
                "resolved": conv.resolved,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
        
        if source == "user":
            grouped_conversations[group_key]["question"] = content
        elif source == "bot":
            grouped_conversations[group_key]["answer"] = content
    
    # Convert grouped conversations to response format
    for group in grouped_conversations.values():
        if group["question"] or group["answer"]:  # Only include if there's actual content
            conversation_responses.append(ConversationResponse(
                id=group["id"],
                user_id=group["user_id"],
                interaction={
                    "question": group["question"],
                    "answer": group["answer"],
                    "channel": group["channel"]
                },
                resolved=group["resolved"],
                created_at=group["created_at"],
                updated_at=group["updated_at"]
            ))
    
    return conversation_responses


@app.get("/admin/bots/{bot_id}/users/{user_id}", response_model=UserResponse)
def get_bot_user_details(
    bot_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Get user details for admin dashboard.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        phone_number=user.phone_number,
        name=user.name
    )


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
from bot_loader import get_bot_by_type
from twilio.rest import Client
from backend.ragpipeline import retrieval_chain, save_conversation
from channels.builders.web import WebMessageBuilder
from channels.builders.twilio import TwilioMessageBuilder
from channels.builders.sms import SmsMessageBuilder # New import
from channels.builders.email import EmailMessageBuilder # Email import
from channels.builders.telegram import TelegramMessageBuilder # Telegram import
from channels.builders.instagram import InstagramMessageBuilder # Instagram import
from channels.builders.messenger import MessengerMessageBuilder # Messenger import
from channels.schemas import StandardizedMessage
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
import threading
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent
import requests
import json

# --- Twilio Configuration ---
# It is strongly recommended to use environment variables for these
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER") # e.g., 'whatsapp:+14155238886'
TWILIO_SMS_NUMBER = os.getenv("TWILIO_SMS_NUMBER") # New SMS number env var

# --- Telegram Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")

# --- Instagram Configuration ---
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_VERIFY_TOKEN = os.getenv("INSTAGRAM_VERIFY_TOKEN")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")
INSTAGRAM_PAGE_ID = os.getenv("INSTAGRAM_PAGE_ID")

# --- Messenger Configuration ---
MESSENGER_ACCESS_TOKEN = os.getenv("MESSENGER_ACCESS_TOKEN")
MESSENGER_VERIFY_TOKEN = os.getenv("MESSENGER_VERIFY_TOKEN")
MESSENGER_APP_SECRET = os.getenv("MESSENGER_APP_SECRET")
MESSENGER_PAGE_ID = os.getenv("MESSENGER_PAGE_ID")

# --- Email Configuration ---
# SendGrid Configuration (Primary)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM_ADDRESS = os.getenv("EMAIL_FROM_ADDRESS")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "AI Assistant")

# Legacy SMTP Configuration (Backup)
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")  # Your email address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Your email password or app password
EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
EMAIL_IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", "993"))

# Debug: Print Twilio configuration at startup
print("=== TWILIO CONFIGURATION ===")
print(f"TWILIO_ACCOUNT_SID: {TWILIO_ACCOUNT_SID}")
print(f"TWILIO_AUTH_TOKEN: {'*' * len(TWILIO_AUTH_TOKEN) if TWILIO_AUTH_TOKEN else 'Not set'}")
print(f"TWILIO_WHATSAPP_NUMBER: {TWILIO_WHATSAPP_NUMBER}")
print(f"TWILIO_SMS_NUMBER: {TWILIO_SMS_NUMBER}")
print("=== END CONFIGURATION ===")

# Debug: Print Telegram configuration at startup
print("=== TELEGRAM CONFIGURATION ===")
print(f"TELEGRAM_BOT_TOKEN: {'*' * len(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else 'Not set'}")
print(f"TELEGRAM_WEBHOOK_URL: {TELEGRAM_WEBHOOK_URL}")
print("=== END TELEGRAM CONFIGURATION ===")

# Debug: Print Email configuration at startup
print("=== EMAIL CONFIGURATION ===")
print(f"SENDGRID_API_KEY: {'*' * len(SENDGRID_API_KEY) if SENDGRID_API_KEY else 'Not set'}")
print(f"EMAIL_FROM_ADDRESS: {EMAIL_FROM_ADDRESS}")
print(f"EMAIL_FROM_NAME: {EMAIL_FROM_NAME}")
print(f"EMAIL_SMTP_SERVER: {EMAIL_SMTP_SERVER}")
print(f"EMAIL_SMTP_PORT: {EMAIL_SMTP_PORT}")
print(f"EMAIL_USERNAME: {EMAIL_USERNAME}")
print(f"EMAIL_PASSWORD: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'Not set'}")
print(f"EMAIL_IMAP_SERVER: {EMAIL_IMAP_SERVER}")
print(f"EMAIL_IMAP_PORT: {EMAIL_IMAP_PORT}")
print("=== END EMAIL CONFIGURATION ===")

# Initialize SendGrid client
sendgrid_client = None
if SENDGRID_API_KEY:
    sendgrid_client = SendGridAPIClient(api_key=SENDGRID_API_KEY)
    print("SendGrid client initialized successfully")
else:
    print("WARNING: SendGrid API key not found. Email sending will use SMTP fallback.")

# Initialize the Twilio client if credentials are provided
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    print("WARNING: Twilio credentials not found. WhatsApp/SMS replies will be disabled.")

# Email sending function using SendGrid
def send_email_reply(to_email: str, subject: str, body: str, reply_to_subject: str = None):
    """Send email reply using SendGrid (primary) or SMTP (fallback)"""
    
    # Prepare subject
    final_subject = subject
    if reply_to_subject and not reply_to_subject.lower().startswith('re:'):
        final_subject = f"Re: {reply_to_subject}"
    elif reply_to_subject:
        final_subject = reply_to_subject
    
    # Try SendGrid first
    if sendgrid_client and EMAIL_FROM_ADDRESS:
        try:
            from_email = From(EMAIL_FROM_ADDRESS, EMAIL_FROM_NAME)
            to_email_obj = To(to_email)
            subject_obj = Subject(final_subject)
            plain_text_content = PlainTextContent(body)
            html_content = HtmlContent(f"<p>{body.replace(chr(10), '<br>')}</p>")
            
            mail = Mail(
                from_email=from_email,
                to_emails=to_email_obj,
                subject=subject_obj,
                plain_text_content=plain_text_content,
                html_content=html_content
            )
            
            response = sendgrid_client.send(mail)
            print(f"SendGrid email sent successfully to: {to_email} (Status: {response.status_code})")
            return True
            
        except Exception as e:
            print(f"ERROR: SendGrid failed: {e}")
            print("Falling back to SMTP...")
    
    # Fallback to SMTP
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        print("ERROR: No email credentials configured (neither SendGrid nor SMTP)")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_USERNAME}>"
        msg['To'] = to_email
        msg['Subject'] = final_subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, to_email, text)
        server.quit()
        
        print(f"SMTP email sent successfully to: {to_email}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to send email via SMTP: {e}")
        return False


# Telegram sending functions
def send_telegram_message(chat_id: str, text: str):
    """Send message via Telegram Bot API"""
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: Telegram bot token not configured")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"  # Enable HTML formatting
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"Telegram message sent successfully to chat_id: {chat_id}")
            return True
        else:
            print(f"ERROR: Failed to send Telegram message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to send Telegram message: {e}")
        return False


def set_telegram_webhook():
    """Set up Telegram webhook"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_WEBHOOK_URL:
        print("WARNING: Telegram credentials not configured, skipping webhook setup")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
        payload = {
            "url": TELEGRAM_WEBHOOK_URL
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"Telegram webhook set successfully: {TELEGRAM_WEBHOOK_URL}")
                return True
            else:
                print(f"ERROR: Failed to set Telegram webhook: {result.get('description')}")
                return False
        else:
            print(f"ERROR: Failed to set webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to set Telegram webhook: {e}")
        return False


# Instagram sending functions
def send_instagram_message(recipient_id: str, text: str):
    """Send message via Instagram Graph API"""
    if not INSTAGRAM_ACCESS_TOKEN:
        print("ERROR: Instagram access token not configured")
        return False
    
    try:
        url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_PAGE_ID}/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"Instagram message sent successfully to recipient_id: {recipient_id}")
            return True
        else:
            print(f"ERROR: Failed to send Instagram message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to send Instagram message: {e}")
        return False


# Messenger sending functions
def send_messenger_message(recipient_id: str, text: str):
    """Send message via Messenger Graph API"""
    if not MESSENGER_ACCESS_TOKEN:
        print("ERROR: Messenger access token not configured")
        return False
    
    try:
        url = f"https://graph.facebook.com/v18.0/{MESSENGER_PAGE_ID}/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "access_token": MESSENGER_ACCESS_TOKEN
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"Messenger message sent successfully to recipient_id: {recipient_id}")
            return True
        else:
            print(f"ERROR: Failed to send Messenger message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to send Messenger message: {e}")
        return False


def verify_facebook_webhook(hub_mode: str, hub_challenge: str, hub_verify_token: str, platform: str):
    """Verify Facebook webhook for Instagram or Messenger"""
    expected_token = INSTAGRAM_VERIFY_TOKEN if platform == "instagram" else MESSENGER_VERIFY_TOKEN
    
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        print(f"{platform.capitalize()} webhook verified successfully")
        return hub_challenge
    else:
        print(f"ERROR: {platform.capitalize()} webhook verification failed")
        return None


# IMAP email checking function
# Commented out temporarily due to IMAP authentication issues
# def check_email_inbox():
#     """Check IMAP inbox for new emails and process them"""
#     if not EMAIL_USERNAME or not EMAIL_PASSWORD or EMAIL_USERNAME == "your-email@gmail.com":
#         print("IMAP credentials not properly configured, skipping email check")
#         return
    
    # try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER, EMAIL_IMAP_PORT)
        mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        mail.select("inbox")
        
        # Search for unread emails
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        print(f"Found {len(email_ids)} unread emails")
        
        for email_id in email_ids:
            try:
                # Fetch email
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Extract email details
                from_header = email_message["From"]
                subject = email_message["Subject"]
                
                # Decode subject if needed
                if subject:
                    decoded_subject = decode_header(subject)[0]
                    if decoded_subject[1]:
                        subject = decoded_subject[0].decode(decoded_subject[1])
                    else:
                        subject = str(decoded_subject[0])
                
                # Extract email body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = email_message.get_payload(decode=True).decode()
                
                # Create payload for processing
                email_payload = {
                    "from": from_header,
                    "subject": subject,
                    "text": body,
                    "body": body
                }
                
                print(f"Processing email from: {from_header}")
                
                # Process email through our handler
                # Note: This is a synchronous call, you might want to make it async
                # For now, we'll create a simple processing function
                process_incoming_email(email_payload)
                
                # Mark email as read
                mail.store(email_id, '+FLAGS', '\\Seen')
                
            except Exception as e:
                print(f"Error processing email {email_id}: {e}")
                continue
        
#         mail.close()
#         mail.logout()
        
#     except Exception as e:
#         print(f"Error checking email inbox: {e}")
#         print("Note: If using SendGrid, consider disabling IMAP and using webhooks instead")
    pass  # Placeholder since function is commented out


def process_incoming_email(email_payload):
    """Process incoming email synchronously"""
    try:
        from database.sessions import session_local
        db = session_local()
        
        builder = EmailMessageBuilder(email_payload)
        standardized_message = builder.build()
        question = standardized_message.content

        # Find user
        user = db.query(User).filter(User.email == standardized_message.sender_id).first()
        if not user:
            print(f"User with email '{standardized_message.sender_id}' not found.")
            db.close()
            return

        # Generate AI response
        result = retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        # Save conversation in the same format as web chat (question + answer together)
        conversation = Conversation(
            user_id=user.id,
            interaction={
                "question": question, 
                "answer": ai_response_text,
                "channel": "email"
            },
            resolved=False,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Send email reply
        original_subject = standardized_message.metadata.get("subject", "")
        send_email_reply(
            to_email=standardized_message.sender_id,
            subject="AI Assistant Response",
            body=ai_response_text,
            reply_to_subject=original_subject
        )
        
        db.close()
        print(f"Email processed and reply sent to: {standardized_message.sender_id}")
        
    except Exception as e:
        print(f"Error in process_incoming_email: {e}")


# Email polling function
def start_email_polling():
    """Start email polling in background thread"""
    def email_polling_loop():
        while True:
            try:
                # check_email_inbox()  # Commented out temporarily
                print("Email polling disabled - using SendGrid webhooks instead")
                time.sleep(300)  # Check every 5 minutes instead of 30 seconds
            except Exception as e:
                print(f"Error in email polling loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    # Only start IMAP polling if SMTP credentials are properly configured
    if EMAIL_USERNAME and EMAIL_PASSWORD and EMAIL_USERNAME != "your-email@gmail.com":
        thread = threading.Thread(target=email_polling_loop, daemon=True)
        thread.start()
        print("Email IMAP polling started")
    else:
        print("Email IMAP polling disabled - using SendGrid webhooks for incoming emails")

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

        # --- Find user and save their message ---
        user = db.query(User).filter(User.email == standardized_message.sender_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with email '{standardized_message.sender_id}' not found.")

        save_conversation(
            db=db, 
            user_id=user.id, 
            source="user", 
            content=question, 
            channel=standardized_message.channel_name
        )

        # --- Generate and Save AI Response ---
        result = retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        save_conversation(
            db=db, 
            user_id=user.id, 
            source="bot", 
            content=ai_response_text, 
            channel=standardized_message.channel_name
        )

        # Return the AI response to the frontend
        return {"answer": ai_response_text}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/hooks/twilio")
async def handle_twilio_message(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming WhatsApp and SMS messages from Twilio, gets an AI response, and sends a reply.
    """
    try:
        payload = await request.form()
        
        # Debug: Print all payload data
        print("=== TWILIO WEBHOOK DEBUG ===")
        for key, value in payload.items():
            print(f"{key}: {value}")
        
        # Check if this is a WhatsApp message by examining the 'From' field
        from_number = payload.get("From", "")
        to_number = payload.get("To", "")
        is_whatsapp = from_number.startswith("whatsapp:")
        
        print(f"From: {from_number}")
        print(f"To: {to_number}")
        print(f"Is WhatsApp: {is_whatsapp}")
        print("=== END DEBUG ===")
        
        builder = TwilioMessageBuilder(payload)
        standardized_message = builder.build()
        question = standardized_message.content

        # --- Find user and save their message ---
        user = db.query(User).filter(User.phone_number == standardized_message.sender_id).first()
        if not user:
            print(f"User with phone number '{standardized_message.sender_id}' not found.")
            return Response(content="", media_type="application/xml")

        # --- Generate and Send AI Response ---
        result = retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        # Save conversation in the same format as web chat (question + answer together)
        conversation = Conversation(
            user_id=user.id,
            interaction={
                "question": question, 
                "answer": ai_response_text,
                "channel": "whatsapp" if is_whatsapp else "sms"
            },
            resolved=False,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # --- Send Reply via Twilio (Channel-specific) ---
        if twilio_client:
            try:
                if is_whatsapp:
                    # WhatsApp message - reply via WhatsApp
                    if not TWILIO_WHATSAPP_NUMBER:
                        print("ERROR: TWILIO_WHATSAPP_NUMBER not configured")
                        return Response(content="", media_type="application/xml")
                    
                    reply_to = f"whatsapp:{standardized_message.sender_id}"
                    print(f"Sending WhatsApp reply FROM: {TWILIO_WHATSAPP_NUMBER} TO: {reply_to}")
                    
                    twilio_client.messages.create(
                        from_=TWILIO_WHATSAPP_NUMBER,
                        body=ai_response_text,
                        to=reply_to
                    )
                    print(f"WhatsApp reply sent successfully")
                else:
                    # SMS message - reply via SMS
                    if not TWILIO_SMS_NUMBER:
                        print("ERROR: TWILIO_SMS_NUMBER not configured")
                        return Response(content="", media_type="application/xml")
                    
                    reply_to = standardized_message.sender_id
                    print(f"Sending SMS reply FROM: {TWILIO_SMS_NUMBER} TO: {reply_to}")
                    
                    twilio_client.messages.create(
                        from_=TWILIO_SMS_NUMBER,
                        body=ai_response_text,
                        to=reply_to
                    )
                    print(f"SMS reply sent successfully")
                    
            except Exception as e:
                print(f"ERROR: Failed to send Twilio message: {e}")
        else:
            print("ERROR: Twilio client not initialized")
        
        return Response(content="", media_type="application/xml")

    except Exception as e:
        print(f"An unexpected error occurred in handle_twilio_message: {e}")
        return Response(content="", media_type="application/xml")


@app.post("/hooks/sms")
async def handle_sms_message(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming SMS from Twilio, gets an AI response, and sends a reply.
    """
    try:
        payload = await request.form()
        
        builder = SmsMessageBuilder(payload)
        standardized_message = builder.build()
        question = standardized_message.content

        # --- Find user and save their message ---
        user = db.query(User).filter(User.phone_number == standardized_message.sender_id).first()
        if not user:
            print(f"User with phone number '{standardized_message.sender_id}' not found.")
            return Response(content="", media_type="application/xml")

        # --- Generate and Send AI Response ---
        result = retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        # Save conversation in the same format as web chat (question + answer together)
        conversation = Conversation(
            user_id=user.id,
            interaction={
                "question": question, 
                "answer": ai_response_text,
                "channel": "sms"
            },
            resolved=False,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # --- Send Reply via Twilio SMS ---
        if twilio_client and TWILIO_SMS_NUMBER:
            try:
                # For SMS, no special prefix is needed for the 'to' number
                twilio_client.messages.create(
                    from_=TWILIO_SMS_NUMBER,
                    body=ai_response_text,
                    to=standardized_message.sender_id
                )
                print(f"SMS reply sent to: {standardized_message.sender_id}")
            except Exception as e:
                print(f"ERROR: Failed to send SMS message: {e}")
        else:
            print("WARNING: SMS number not configured or Twilio client not available")
        
        return Response(content="", media_type="application/xml")

    except Exception as e:
        print(f"An unexpected error occurred in handle_sms_message: {e}")
        return Response(content="", media_type="application/xml")


@app.post("/hooks/email")
async def handle_email_message(payload: Dict[Any, Any], db: Session = Depends(get_db)):
    """
    Handles incoming emails (from email webhooks like SendGrid, Mailgun, etc.), 
    gets an AI response, and sends a reply.
    """
    try:
        print("=== EMAIL WEBHOOK DEBUG ===")
        print(f"Received email payload: {payload}")
        print("=== END EMAIL DEBUG ===")
        
        builder = EmailMessageBuilder(payload)
        standardized_message = builder.build()
        question = standardized_message.content

        # --- Find user and save their message ---
        user = db.query(User).filter(User.email == standardized_message.sender_id).first()
        if not user:
            print(f"User with email '{standardized_message.sender_id}' not found.")
            # For email, we might want to send a response anyway or create a guest conversation
            return {"status": "user_not_found", "message": "User not registered"}

        # --- Generate and Send AI Response ---
        result = retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        # Save conversation in the same format as web chat (question + answer together)
        conversation = Conversation(
            user_id=user.id,
            interaction={
                "question": question, 
                "answer": ai_response_text,
                "channel": "email"
            },
            resolved=False,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # --- Send Reply via Email ---
        original_subject = standardized_message.metadata.get("subject", "")
        success = send_email_reply(
            to_email=standardized_message.sender_id,
            subject="AI Assistant Response",
            body=ai_response_text,
            reply_to_subject=original_subject
        )
        
        if success:
            return {"status": "success", "message": "Email reply sent"}
        else:
            return {"status": "error", "message": "Failed to send email reply"}

    except Exception as e:
        print(f"An unexpected error occurred in handle_email_message: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/hooks/sendgrid")
async def handle_sendgrid_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle SendGrid Inbound Parse webhook
    SendGrid sends form data, not JSON
    """
    try:
        form_data = await request.form()
        
        # Extract email data from SendGrid format
        payload = {
            "from": form_data.get("from"),
            "to": form_data.get("to"),
            "subject": form_data.get("subject"),
            "text": form_data.get("text"),
            "html": form_data.get("html")
        }
        
        print("=== SENDGRID WEBHOOK DEBUG ===")
        print(f"Received SendGrid payload: {payload}")
        print("=== END SENDGRID DEBUG ===")
        
        # Process through the standard email handler
        return await handle_email_message(payload, db)
        
    except Exception as e:
        print(f"Error in SendGrid webhook handler: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/hooks/telegram")
async def handle_telegram_message(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming Telegram messages, gets an AI response, and sends a reply.
    """
    try:
        payload = await request.json()
        
        print("=== TELEGRAM WEBHOOK DEBUG ===")
        print(f"Received Telegram payload: {payload}")
        print("=== END TELEGRAM DEBUG ===")
        
        builder = TelegramMessageBuilder(payload)
        standardized_message = builder.build()
        question = standardized_message.content

        # Extract Telegram chat ID for replies
        telegram_chat_id = standardized_message.sender_id
        
        # --- Find user by Telegram ID or create a mapping ---
        # Note: You might want to store telegram_user_id in User table
        # For now, we'll try to find by phone number if available
        user = None
        
        # Try to find user by stored telegram_user_id (if you add this field)
        # user = db.query(User).filter(User.telegram_user_id == telegram_chat_id).first()
        
        # For demo purposes, let's use a default user or create a guest system
        # In production, you'd want users to register their Telegram ID
        user = db.query(User).first()  # Use first user for demo
        
        if not user:
            # Send registration message
            send_telegram_message(
                telegram_chat_id, 
                "👋 Welcome! Please register on our platform first to use this service.\n\nVisit: https://yourdomain.com/register"
            )
            return {"status": "user_not_found", "message": "User not registered"}

        # --- Generate and Send AI Response ---
        result = retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        # Save conversation in the same format as other channels
        conversation = Conversation(
            user_id=user.id,
            interaction={
                "question": question, 
                "answer": ai_response_text,
                "channel": "telegram"
            },
            resolved=False,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # --- Send Reply via Telegram ---
        success = send_telegram_message(telegram_chat_id, ai_response_text)
        
        if success:
            return {"status": "success", "message": "Telegram reply sent"}
        else:
            return {"status": "error", "message": "Failed to send Telegram reply"}

    except Exception as e:
        print(f"An unexpected error occurred in handle_telegram_message: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/hooks/instagram")
async def verify_instagram_webhook(request: Request):
    """Verify Instagram webhook"""
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")
    
    challenge = verify_facebook_webhook(hub_mode, hub_challenge, hub_verify_token, "instagram")
    if challenge:
        return Response(content=challenge, media_type="text/plain")
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/hooks/instagram")
async def handle_instagram_message(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming Instagram messages, gets an AI response, and sends a reply.
    """
    try:
        payload = await request.json()
        
        print("=== INSTAGRAM WEBHOOK DEBUG ===")
        print(f"Received Instagram payload: {payload}")
        print("=== END INSTAGRAM DEBUG ===")
        
        # Skip if it's a test webhook
        if payload.get("object") == "instagram" and not payload.get("entry"):
            return {"status": "test_webhook", "message": "Test webhook received"}
        
        builder = InstagramMessageBuilder(payload)
        standardized_message = builder.build()
        question = standardized_message.content

        # Extract Instagram sender ID for replies
        instagram_sender_id = standardized_message.sender_id
        
        # Find user - Instagram integration typically requires user registration
        user = db.query(User).first()  # Use first user for demo
        
        if not user:
            # Send registration message
            send_instagram_message(
                instagram_sender_id, 
                "👋 Welcome! Please register on our platform first to use this service."
            )
            return {"status": "user_not_found", "message": "User not registered"}

        # Generate AI Response
        result = retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        # Save conversation
        conversation = Conversation(
            user_id=user.id,
            interaction={
                "question": question, 
                "answer": ai_response_text,
                "channel": "instagram"
            },
            resolved=False,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Send Reply via Instagram
        success = send_instagram_message(instagram_sender_id, ai_response_text)
        
        if success:
            return {"status": "success", "message": "Instagram reply sent"}
        else:
            return {"status": "error", "message": "Failed to send Instagram reply"}

    except Exception as e:
        print(f"An unexpected error occurred in handle_instagram_message: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/hooks/messenger")
async def verify_messenger_webhook(request: Request):
    """Verify Messenger webhook"""
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")
    
    challenge = verify_facebook_webhook(hub_mode, hub_challenge, hub_verify_token, "messenger")
    if challenge:
        return Response(content=challenge, media_type="text/plain")
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/hooks/messenger")
async def handle_messenger_message(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming Messenger messages, gets an AI response, and sends a reply.
    """
    try:
        payload = await request.json()
        
        print("=== MESSENGER WEBHOOK DEBUG ===")
        print(f"Received Messenger payload: {payload}")
        print("=== END MESSENGER DEBUG ===")
        
        # Skip if it's a test webhook
        if payload.get("object") == "page" and not payload.get("entry"):
            return {"status": "test_webhook", "message": "Test webhook received"}
        
        builder = MessengerMessageBuilder(payload)
        
        # Handle postback events differently
        if builder.is_postback():
            postback_payload = builder.get_postback_payload()
            question = f"User clicked: {postback_payload}"
        else:
            standardized_message = builder.build()
            question = standardized_message.content

        # Extract Messenger sender ID for replies  
        messenger_sender_id = builder.get_sender_psid()
        
        # Find user - Messenger integration typically requires user registration
        user = db.query(User).first()  # Use first user for demo
        
        if not user:
            # Send registration message
            send_messenger_message(
                messenger_sender_id, 
                "👋 Welcome! Please register on our platform first to use this service."
            )
            return {"status": "user_not_found", "message": "User not registered"}

        # Generate AI Response
        result = retrieval_chain.invoke({"input": question})
        ai_response_text = result.get("answer", "I could not find an answer.")

        # Save conversation
        conversation = Conversation(
            user_id=user.id,
            interaction={
                "question": question, 
                "answer": ai_response_text,
                "channel": "messenger"
            },
            resolved=False,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Send Reply via Messenger
        success = send_messenger_message(messenger_sender_id, ai_response_text)
        
        if success:
            return {"status": "success", "message": "Messenger reply sent"}
        else:
            return {"status": "error", "message": "Failed to send Messenger reply"}

    except Exception as e:
        print(f"An unexpected error occurred in handle_messenger_message: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/hooks/email-manual")
async def handle_manual_email(request: Request, db: Session = Depends(get_db)):
    """
    Manual email endpoint for testing or direct email processing.
    Expects JSON with 'from', 'subject', and 'body' fields.
    """
    try:
        payload = await request.json()
        
        # Validate required fields
        required_fields = ['from', 'body']
        for field in required_fields:
            if field not in payload:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        return await handle_email_message(payload, db)
        
    except Exception as e:
        print(f"Error in manual email handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/test-email")
async def test_email_functionality(request: Request, db: Session = Depends(get_db)):
    """Test email functionality - admin only"""
    try:
        current_admin = get_current_admin(request, db)
        
        # Test sending an email
        test_subject = "AI Assistant Test Email"
        test_body = "This is a test email from your AI Assistant. If you receive this, email functionality is working correctly!"
        
        success = send_email_reply(
            to_email=current_admin.email,
            subject=test_subject,
            body=test_body
        )
        
        if success:
            return {"status": "success", "message": f"Test email sent to {current_admin.email}"}
        else:
            return {"status": "error", "message": "Failed to send test email"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test email error: {str(e)}")


@app.post("/admin/check-email-inbox")
async def manual_email_check(request: Request, db: Session = Depends(get_db)):
    """Manually trigger email inbox check - admin only"""
    try:
        current_admin = get_current_admin(request, db)
        
        # Trigger email check
        # check_email_inbox()  # Commented out temporarily
        return {"status": "success", "message": "Email inbox check disabled - using SendGrid webhooks"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email check error: {str(e)}")

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



from fastapi import Form

@app.post("/admin/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    bot_id: int = Form(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    # Get bot name for folder
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        return {"success": False, "error": "Bot not found"}
    folder_name = f"{bot.name.replace(' ', '_').lower()}_knowledge_base"
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "uploaded_docs", folder_name)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Trigger knowledgebase update
    update_knowledge_base()
    return {"success": True, "filename": file.filename, "folder": folder_name}

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
    Now returns only documents in the bot's knowledge base folder.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        return []
    folder_name = f"{bot.name.replace(' ', '_').lower()}_knowledge_base"
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "uploaded_docs", folder_name)
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