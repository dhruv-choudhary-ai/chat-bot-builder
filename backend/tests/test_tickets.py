#!/usr/bin/env python3
"""
Test script for tickets functionality
"""

import sys
import os
from datetime import datetime
xfrom sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import StaticPool

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create simplified models for testing (without JSONB dependency)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bot_id = Column(Integer, nullable=True)
    topic = Column(String, nullable=False)
    status = Column(String, default='open')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

# Import required modules
from adminbackend.tickets import (
    create_ticket, 
    get_user_tickets, 
    get_all_tickets, 
    get_bot_tickets, 
    get_bot_ticket_details, 
    get_ticket_details, 
    update_ticket_status
)
import schemas

class TestTickets:
    def __init__(self):
        # Create in-memory SQLite database for testing
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
        
        # Create test user
        self.test_user = User(
            username="testuser",
            email="test@example.com",
            password="hashed_password"
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)
        
        print("✅ Test database setup complete")
        
    def test_create_ticket(self):
        """Test creating a new ticket"""
        print("\n🧪 Testing ticket creation...")
        
        ticket_data = schemas.TicketCreate(topic="Test Support Issue")
        
        # Create ticket
        ticket = create_ticket(
            db=self.db, 
            ticket=ticket_data, 
            user_id=self.test_user.id,
            bot_id=1
        )
        
        assert ticket.id is not None
        assert ticket.topic == "Test Support Issue"
        assert ticket.user_id == self.test_user.id
        assert ticket.status == "open"  # default status
        assert ticket.created_at is not None
        
        print(f"✅ Ticket created successfully with ID: {ticket.id}")
        return ticket
        
    def test_get_user_tickets(self):
        """Test retrieving tickets for a specific user"""
        print("\n🧪 Testing get user tickets...")
        
        # Create multiple tickets for the user
        ticket1_data = schemas.TicketCreate(topic="First Issue")
        ticket2_data = schemas.TicketCreate(topic="Second Issue")
        
        create_ticket(self.db, ticket1_data, self.test_user.id)
        create_ticket(self.db, ticket2_data, self.test_user.id)
        
        # Get user tickets
        user_tickets = get_user_tickets(self.db, self.test_user.id)
        
        assert len(user_tickets) >= 2
        print(f"✅ Found {len(user_tickets)} tickets for user")
        
    def test_get_all_tickets(self):
        """Test retrieving all tickets"""
        print("\n🧪 Testing get all tickets...")
        
        all_tickets = get_all_tickets(self.db)
        assert len(all_tickets) > 0
        print(f"✅ Found {len(all_tickets)} total tickets")
        
    def test_get_bot_tickets(self):
        """Test retrieving tickets for a specific bot"""
        print("\n🧪 Testing get bot tickets...")
        
        # Create ticket with specific bot_id
        ticket_data = schemas.TicketCreate(topic="Bot Specific Issue")
        bot_id = 5
        create_ticket(self.db, ticket_data, self.test_user.id, bot_id=bot_id)
        
        # Get bot tickets
        bot_tickets = get_bot_tickets(self.db, bot_id)
        assert len(bot_tickets) > 0
        assert all(ticket.bot_id == bot_id for ticket in bot_tickets if ticket.bot_id is not None)
        print(f"✅ Found {len(bot_tickets)} tickets for bot {bot_id}")
        
    def test_get_ticket_details(self):
        """Test retrieving specific ticket details"""
        print("\n🧪 Testing get ticket details...")
        
        # Create a ticket first
        ticket_data = schemas.TicketCreate(topic="Detailed Issue")
        created_ticket = create_ticket(self.db, ticket_data, self.test_user.id)
        
        # Get ticket details
        ticket_details = get_ticket_details(self.db, created_ticket.id)
        
        assert ticket_details is not None
        assert ticket_details.id == created_ticket.id
        assert ticket_details.topic == "Detailed Issue"
        print(f"✅ Retrieved ticket details for ticket ID: {ticket_details.id}")
        
    def test_get_bot_ticket_details(self):
        """Test retrieving specific ticket details for a bot"""
        print("\n🧪 Testing get bot ticket details...")
        
        # Create a ticket with bot_id
        ticket_data = schemas.TicketCreate(topic="Bot Detailed Issue")
        bot_id = 10
        created_ticket = create_ticket(self.db, ticket_data, self.test_user.id, bot_id=bot_id)
        
        # Get bot ticket details
        ticket_details = get_bot_ticket_details(self.db, bot_id, created_ticket.id)
        
        assert ticket_details is not None
        assert ticket_details.id == created_ticket.id
        assert ticket_details.bot_id == bot_id
        print(f"✅ Retrieved bot ticket details for bot {bot_id}, ticket ID: {ticket_details.id}")
        
    def test_update_ticket_status(self):
        """Test updating ticket status"""
        print("\n🧪 Testing update ticket status...")
        
        # Create a ticket first
        ticket_data = schemas.TicketCreate(topic="Status Update Issue")
        created_ticket = create_ticket(self.db, ticket_data, self.test_user.id)
        
        # Update status
        updated_ticket = update_ticket_status(self.db, created_ticket.id, "resolved")
        
        assert updated_ticket is not None
        assert updated_ticket.status == "resolved"
        assert updated_ticket.id == created_ticket.id
        print(f"✅ Updated ticket {updated_ticket.id} status to: {updated_ticket.status}")
        
    def test_update_nonexistent_ticket(self):
        """Test updating a ticket that doesn't exist"""
        print("\n🧪 Testing update non-existent ticket...")
        
        # Try to update a ticket that doesn't exist
        result = update_ticket_status(self.db, 99999, "resolved")
        
        assert result is None
        print("✅ Correctly handled non-existent ticket update")
        
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Tickets Functionality Tests")
        print("=" * 50)
        
        try:
            self.test_create_ticket()
            self.test_get_user_tickets()
            self.test_get_all_tickets()
            self.test_get_bot_tickets()
            self.test_get_ticket_details()
            self.test_get_bot_ticket_details()
            self.test_update_ticket_status()
            self.test_update_nonexistent_ticket()
            
            print("\n" + "=" * 50)
            print("🎉 All tests passed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            raise
        finally:
            self.db.close()

if __name__ == "__main__":
    test_suite = TestTickets()
    test_suite.run_all_tests()
