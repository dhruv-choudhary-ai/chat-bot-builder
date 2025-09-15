#!/usr/bin/env python3
"""
Setup and environment test script for AILifeBotAssist
"""
import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if all required environment variables are set"""
    print("=== Environment Setup Test ===")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = [
        "SECRET_KEY",
        "DATABASE_URL", 
        "GOOGLE_API_KEY",  # For Gemini AI
    ]
    
    optional_vars = [
        "HUBSPOT_ACCESS_TOKEN",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "REDIS_URL"
    ]
    
    missing_required = []
    missing_optional = []
    
    print("\n--- Required Environment Variables ---")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10)}...")
        else:
            print(f"❌ {var}: Not set")
            missing_required.append(var)
    
    print("\n--- Optional Environment Variables ---")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10)}...")
        else:
            print(f"⚠️  {var}: Not set (optional)")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required variables: {missing_required}")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def test_dependencies():
    """Test if all required packages are installed"""
    print("\n=== Dependencies Test ===")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "alembic",
        "langchain",
        "chromadb",
        "redis",
        "python-jose",
        "passlib",
        "python-multipart"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages are installed!")
        return True

def test_file_structure():
    """Test if all required files and directories exist"""
    print("\n=== File Structure Test ===")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "alembic.ini",
        "auth/auth.py",
        "database/database.py",
        "database/sessions.py",
        "backend/knowledgebase.py",
        "backend/ragpipeline.py",
        "bots/base_bot.py",
        "schemas.py"
    ]
    
    required_dirs = [
        "templates",
        "static", 
        "alembic/versions",
        "bots",
        "backend",
        "chroma_db"
    ]
    
    missing_files = []
    missing_dirs = []
    
    print("\n--- Required Files ---")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    print("\n--- Required Directories ---")
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/")
            missing_dirs.append(dir_path)
    
    if missing_files or missing_dirs:
        print(f"\n❌ Missing files: {missing_files}")
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("\n✅ All required files and directories exist!")
        return True

if __name__ == "__main__":
    print("AILifeBotAssist - Setup and Environment Test")
    print("=" * 50)
    
    env_ok = test_environment()
    deps_ok = test_dependencies()
    files_ok = test_file_structure()
    
    print("\n" + "=" * 50)
    if env_ok and deps_ok and files_ok:
        print("🎉 All setup tests passed! Ready to start testing the application.")
    else:
        print("❌ Some setup tests failed. Please fix the issues above before proceeding.")
        sys.exit(1)
