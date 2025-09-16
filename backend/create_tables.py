#!/usr/bin/env python3
"""
Create database tables script
"""
import os
from sqlalchemy import create_engine
from database.database import Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables():
    """Create all database tables"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    print(f"Creating tables for database: {database_url}")
    
    # Create engine
    engine = create_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    create_tables()