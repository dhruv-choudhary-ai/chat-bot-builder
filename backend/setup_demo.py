#!/usr/bin/env python3
"""
Lead Management Agent Demo Setup and Runner
Quick setup script for tomorrow's demo
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "lead_agent_requirements.txt"
        ])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def setup_environment():
    """Setup environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("""# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Demo Configuration
DEMO_MODE=true
LOG_LEVEL=INFO

# For production, you would add:
# DATABASE_URL=postgresql://user:pass@localhost/leaddb
# REDIS_URL=redis://localhost:6379
""")
        print("✅ .env file created. Please add your OpenAI API key!")
        return False
    return True

def run_demo():
    """Run the demo application"""
    print("🚀 Starting Lead Management Agent Demo...")
    print("📊 Dashboard will be available at: http://localhost:8001")
    print("🔄 Press Ctrl+C to stop the demo")
    
    try:
        # Run the FastAPI application
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "lead_agent_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8001", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Demo stopped. Thanks for trying the Lead Management Agent!")

def main():
    """Main setup and run function"""
    print("🤖 Lead Management Agent - Demo Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("lead_management_agent.py").exists():
        print("❌ Please run this script from the project directory")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("⚠️  Please edit the .env file and add your OpenAI API key before running the demo")
        return
    
    # Check if OpenAI API key is set
    if "your_openai_api_key_here" in open(".env").read():
        print("⚠️  Please edit the .env file and add your real OpenAI API key")
        print("💡 You can get one from: https://platform.openai.com/api-keys")
        return
    
    # Run the demo
    run_demo()

if __name__ == "__main__":
    main()
