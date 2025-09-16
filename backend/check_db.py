#!/usr/bin/env python3
"""
Check database tables script
"""
import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_tables():
    """Check what tables exist in the database"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    # Extract the path from the sqlite URL
    db_path = database_url.replace("sqlite:///", "")
    
    print(f"Checking tables in database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            print("📋 Tables found:")
            for table in tables:
                print(f"  - {table[0]}")
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table[0]});")
                columns = cursor.fetchall()
                print(f"    Columns:")
                for col in columns:
                    print(f"      {col[1]} ({col[2]})")
                print()
        else:
            print("❌ No tables found in the database")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_tables()