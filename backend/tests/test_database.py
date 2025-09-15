#!/usr/bin/env python3
"""
Database testing script for AILifeBotAssist
Tests database connections, models, and migrations
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import Base, User, Admin, Bot, Conversation, Ticket
from auth.auth import get_password_hash

load_dotenv()

class DatabaseTester:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.engine = None
        self.SessionLocal = None
        
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

    def print_test(self, test_name: str, success: bool, details: str = ""):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")

    def test_database_connection(self) -> bool:
        """Test database connection"""
        self.print_section("DATABASE CONNECTION")
        
        if not self.database_url:
            self.print_test("Database URL", False, "DATABASE_URL not set in environment")
            return False
        
        try:
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Test connection
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                success = result.fetchone()[0] == 1
            
            self.print_test("Database Connection", success, f"URL: {self.database_url[:50]}...")
            return success
            
        except Exception as e:
            self.print_test("Database Connection", False, f"Error: {str(e)}")
            return False

    def test_table_creation(self) -> bool:
        """Test if all tables can be created"""
        self.print_section("TABLE CREATION")
        
        if not self.engine:
            self.print_test("Table Creation", False, "No database connection")
            return False
        
        try:
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Check if tables exist
            inspector = self.engine.dialect.get_inspector(self.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users', 'admins', 'bots', 'conversations', 'tickets']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                self.print_test("Table Creation", False, f"Missing tables: {missing_tables}")
                return False
            else:
                self.print_test("Table Creation", True, f"All tables created: {expected_tables}")
                return True
                
        except Exception as e:
            self.print_test("Table Creation", False, f"Error: {str(e)}")
            return False

    def test_user_operations(self) -> bool:
        """Test user CRUD operations"""
        self.print_section("USER OPERATIONS")
        
        if not self.SessionLocal:
            self.print_test("User Operations", False, "No database session")
            return False
        
        db = self.SessionLocal()
        try:
            # Create test user
            test_email = "test_db@example.com"
            
            # Delete existing test user if exists
            existing_user = db.query(User).filter(User.email == test_email).first()
            if existing_user:
                db.delete(existing_user)
                db.commit()
            
            # Create new user
            hashed_password = get_password_hash("testpassword123")
            test_user = User(
                email=test_email,
                password=hashed_password,
                phone_number="+1234567890",
                name="Test User"
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            self.print_test("User Creation", True, f"User ID: {test_user.id}")
            
            # Read user
            retrieved_user = db.query(User).filter(User.email == test_email).first()
            read_success = retrieved_user is not None and retrieved_user.email == test_email
            self.print_test("User Read", read_success, f"Retrieved: {retrieved_user.email if retrieved_user else 'None'}")
            
            # Update user
            if retrieved_user:
                retrieved_user.name = "Updated Test User"
                db.commit()
                
                updated_user = db.query(User).filter(User.email == test_email).first()
                update_success = updated_user.name == "Updated Test User"
                self.print_test("User Update", update_success, f"New name: {updated_user.name}")
            else:
                update_success = False
            
            # Delete user
            if retrieved_user:
                db.delete(retrieved_user)
                db.commit()
                
                deleted_user = db.query(User).filter(User.email == test_email).first()
                delete_success = deleted_user is None
                self.print_test("User Delete", delete_success, "User successfully deleted")
            else:
                delete_success = False
            
            return read_success and update_success and delete_success
            
        except Exception as e:
            self.print_test("User Operations", False, f"Error: {str(e)}")
            return False
        finally:
            db.close()

    def test_bot_operations(self) -> bool:
        """Test bot CRUD operations"""
        self.print_section("BOT OPERATIONS")
        
        if not self.SessionLocal:
            self.print_test("Bot Operations", False, "No database session")
            return False
        
        db = self.SessionLocal()
        try:
            # Create test admin first
            test_admin_email = "admin_test@example.com"
            existing_admin = db.query(Admin).filter(Admin.email == test_admin_email).first()
            
            if not existing_admin:
                test_admin = Admin(
                    email=test_admin_email,
                    password=get_password_hash("adminpass123"),
                    name="Test Admin"
                )
                db.add(test_admin)
                db.commit()
                db.refresh(test_admin)
            else:
                test_admin = existing_admin
            
            # Create test bot
            test_bot = Bot(
                name="Test Banking Bot",
                bot_type="banking",
                admin_id=test_admin.id
            )
            
            db.add(test_bot)
            db.commit()
            db.refresh(test_bot)
            
            self.print_test("Bot Creation", True, f"Bot ID: {test_bot.id}, Type: {test_bot.bot_type}")
            
            # Read bot
            retrieved_bot = db.query(Bot).filter(Bot.id == test_bot.id).first()
            read_success = retrieved_bot is not None
            self.print_test("Bot Read", read_success, f"Retrieved: {retrieved_bot.name if retrieved_bot else 'None'}")
            
            # Clean up
            if retrieved_bot:
                db.delete(retrieved_bot)
            db.delete(test_admin)
            db.commit()
            
            return read_success
            
        except Exception as e:
            self.print_test("Bot Operations", False, f"Error: {str(e)}")
            return False
        finally:
            db.close()

    def test_conversation_operations(self) -> bool:
        """Test conversation CRUD operations"""
        self.print_section("CONVERSATION OPERATIONS")
        
        if not self.SessionLocal:
            self.print_test("Conversation Operations", False, "No database session")
            return False
        
        db = self.SessionLocal()
        try:
            # Create test user for conversation
            test_user = User(
                email="conv_test@example.com",
                password=get_password_hash("testpass123"),
                phone_number="+9876543210"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            # Create test conversation
            test_conversation = Conversation(
                user_id=test_user.id,
                interaction={"question": "Test question", "answer": "Test answer"},
                resolved=False
            )
            
            db.add(test_conversation)
            db.commit()
            db.refresh(test_conversation)
            
            self.print_test("Conversation Creation", True, f"Conversation ID: {test_conversation.id}")
            
            # Read conversation
            retrieved_conv = db.query(Conversation).filter(Conversation.id == test_conversation.id).first()
            read_success = retrieved_conv is not None
            self.print_test("Conversation Read", read_success, f"Interaction: {retrieved_conv.interaction if retrieved_conv else 'None'}")
            
            # Clean up
            if retrieved_conv:
                db.delete(retrieved_conv)
            db.delete(test_user)
            db.commit()
            
            return read_success
            
        except Exception as e:
            self.print_test("Conversation Operations", False, f"Error: {str(e)}")
            return False
        finally:
            db.close()

    def test_relationships(self) -> bool:
        """Test database relationships"""
        self.print_section("DATABASE RELATIONSHIPS")
        
        if not self.SessionLocal:
            self.print_test("Database Relationships", False, "No database session")
            return False
        
        db = self.SessionLocal()
        try:
            # Create admin
            admin = Admin(
                email="rel_admin@example.com",
                password=get_password_hash("adminpass"),
                name="Relationship Test Admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            # Create user
            user = User(
                email="rel_user@example.com",
                password=get_password_hash("userpass"),
                phone_number="+1111111111"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create bot linked to admin
            bot = Bot(
                name="Relationship Test Bot",
                bot_type="test",
                admin_id=admin.id
            )
            db.add(bot)
            db.commit()
            db.refresh(bot)
            
            # Create conversation linked to user and bot
            conversation = Conversation(
                user_id=user.id,
                bot_id=bot.id,
                interaction={"question": "Relationship test", "answer": "Working"}
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            # Test relationships
            # Bot -> Admin relationship
            bot_admin = db.query(Bot).filter(Bot.id == bot.id).first()
            admin_relation_success = bot_admin.admin.email == admin.email
            self.print_test("Bot-Admin Relationship", admin_relation_success, f"Bot admin: {bot_admin.admin.email}")
            
            # Conversation -> User relationship
            conv_user = db.query(Conversation).filter(Conversation.id == conversation.id).first()
            user_relation_success = conv_user.user.email == user.email
            self.print_test("Conversation-User Relationship", user_relation_success, f"Conversation user: {conv_user.user.email}")
            
            # Conversation -> Bot relationship
            bot_relation_success = conv_user.bot.name == bot.name
            self.print_test("Conversation-Bot Relationship", bot_relation_success, f"Conversation bot: {conv_user.bot.name}")
            
            # Clean up
            db.delete(conversation)
            db.delete(bot)
            db.delete(user)
            db.delete(admin)
            db.commit()
            
            return admin_relation_success and user_relation_success and bot_relation_success
            
        except Exception as e:
            self.print_test("Database Relationships", False, f"Error: {str(e)}")
            return False
        finally:
            db.close()

    def run_all_tests(self) -> bool:
        """Run all database tests"""
        print("AILifeBotAssist - Database Testing")
        print("=" * 60)
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("Table Creation", self.test_table_creation),
            ("User Operations", self.test_user_operations),
            ("Bot Operations", self.test_bot_operations),
            ("Conversation Operations", self.test_conversation_operations),
            ("Database Relationships", self.test_relationships)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ CRITICAL ERROR in {test_name}: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        self.print_section("DATABASE TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} | {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        success_rate = (passed / total) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Database testing completed successfully!")
        else:
            print("⚠️  Some database tests failed. Please review the issues above.")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = DatabaseTester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
