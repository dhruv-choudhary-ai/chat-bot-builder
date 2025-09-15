#!/usr/bin/env python3
"""
Test script to verify tickets API functionality
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing AILifeBotAssist Tickets API")
    print("=" * 50)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: Get all tickets (should be empty initially)
    try:
        response = requests.get(f"{base_url}/tickets/")
        tickets = response.json()
        print(f"✅ Get all tickets: {response.status_code} - Found {len(tickets)} tickets")
    except Exception as e:
        print(f"❌ Get all tickets failed: {e}")
    
    # Test 4: Create a test ticket (assuming user_id 1 exists)
    try:
        response = requests.post(f"{base_url}/tickets/?topic=Test Support Issue&user_id=1&bot_id=1")
        if response.status_code == 200:
            ticket = response.json()
            print(f"✅ Create ticket: {response.status_code} - Created ticket ID {ticket.get('id')}")
            ticket_id = ticket.get('id')
        else:
            print(f"⚠️  Create ticket: {response.status_code} - {response.text}")
            ticket_id = None
    except Exception as e:
        print(f"❌ Create ticket failed: {e}")
        ticket_id = None
    
    # Test 5: Get ticket details (if we created one)
    if ticket_id:
        try:
            response = requests.get(f"{base_url}/tickets/{ticket_id}")
            print(f"✅ Get ticket details: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Get ticket details failed: {e}")
        
        # Test 6: Update ticket status
        try:
            response = requests.patch(f"{base_url}/tickets/{ticket_id}/status?new_status=resolved")
            print(f"✅ Update ticket status: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Update ticket status failed: {e}")
    
    # Test 7: Get tickets for user 1
    try:
        response = requests.get(f"{base_url}/tickets/user/1")
        user_tickets = response.json()
        print(f"✅ Get user tickets: {response.status_code} - Found {len(user_tickets)} tickets for user 1")
    except Exception as e:
        print(f"❌ Get user tickets failed: {e}")
    
    # Test 8: Get tickets for bot 1
    try:
        response = requests.get(f"{base_url}/tickets/bot/1")
        bot_tickets = response.json()
        print(f"✅ Get bot tickets: {response.status_code} - Found {len(bot_tickets)} tickets for bot 1")
    except Exception as e:
        print(f"❌ Get bot tickets failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    return True

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(2)
    test_api()
