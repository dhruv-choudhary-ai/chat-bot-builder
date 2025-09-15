
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from src.core.config import settings
from dotenv import load_dotenv
import os
# Load environment variables from .env
load_dotenv()

# Get the URL
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
