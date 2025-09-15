#!/usr/bin/env python3
"""
Comprehensive API testing script for AILifeBotAssist
Tests all major endpoints and functionality
"""
import requests
import json
import time
import sys
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.test_user_email = "test_user@example.com"
        self.test_user_password = "testpassword123"
        self.test_user_phone = "+1234567890"

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

    def test_server_health(self) -> bool:
        """Test if the server is running"""
        self.print_section("SERVER HEALTH CHECK")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            success = response.status_code == 200
            self.print_test("Server Running", success, f"Status: {response.status_code}")
            return success
        except requests.exceptions.ConnectionError:
            self.print_test("Server Running", False, "Connection failed - is the server running?")
            return False
        except Exception as e:
            self.print_test("Server Running", False, f"Error: {str(e)}")
            return False

    def test_user_registration(self) -> bool:
        """Test user registration"""
        self.print_section("USER REGISTRATION")
        
        url = f"{self.base_url}/register"
        data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "phone_number": self.test_user_phone
        }
        
        try:
            response = requests.post(url, json=data)
            success = response.status_code in [200, 400]  # 400 if user already exists
            
            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data.get('access_token')
                self.print_test("User Registration", True, "New user registered successfully")
            elif response.status_code == 400:
                self.print_test("User Registration", True, "User already exists (expected)")
            else:
                self.print_test("User Registration", False, f"Status: {response.status_code}")
            
            return success
            
        except Exception as e:
            self.print_test("User Registration", False, f"Error: {str(e)}")
            return False

    def test_user_login(self) -> bool:
        """Test user login"""
        self.print_section("USER LOGIN")
        
        url = f"{self.base_url}/token"
        data = {
            "username": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            response = requests.post(url, data=data)  # form data for OAuth2
            success = response.status_code == 200
            
            if success:
                response_data = response.json()
                self.access_token = response_data.get('access_token')
                self.print_test("User Login", True, f"Token received: {self.access_token[:20]}...")
            else:
                self.print_test("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
            
            return success
            
        except Exception as e:
            self.print_test("User Login", False, f"Error: {str(e)}")
            return False

    def test_protected_endpoints(self) -> bool:
        """Test protected endpoints with authentication"""
        self.print_section("PROTECTED ENDPOINTS")
        
        if not self.access_token:
            self.print_test("Protected Endpoints", False, "No access token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Test /users/me endpoint
        try:
            response = requests.get(f"{self.base_url}/users/me", headers=headers)
            success_me = response.status_code == 200
            self.print_test("Get Current User", success_me, f"Status: {response.status_code}")
            
            if success_me:
                user_data = response.json()
                self.print_test("User Data Validation", "email" in user_data, f"Email: {user_data.get('email', 'N/A')}")
        except Exception as e:
            self.print_test("Get Current User", False, f"Error: {str(e)}")
            success_me = False
        
        # Test /users/me/bots endpoint
        try:
            response = requests.get(f"{self.base_url}/users/me/bots", headers=headers)
            success_bots = response.status_code == 200
            self.print_test("Get User Bots", success_bots, f"Status: {response.status_code}")
            
            if success_bots:
                bots_data = response.json()
                self.print_test("Bots Data Validation", isinstance(bots_data, list), f"Found {len(bots_data)} bots")
        except Exception as e:
            self.print_test("Get User Bots", False, f"Error: {str(e)}")
            success_bots = False
        
        return success_me and success_bots

    def test_chat_functionality(self) -> bool:
        """Test chat/query functionality"""
        self.print_section("CHAT FUNCTIONALITY")
        
        if not self.access_token:
            self.print_test("Chat Functionality", False, "No access token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        test_queries = [
            "Hello, what can you help me with?",
            "What services do you offer?",
            "Can you tell me about your banking services?"
        ]
        
        results = []
        for query in test_queries:
            try:
                data = {"question": query}
                response = requests.post(f"{self.base_url}/query", json=data, headers=headers)
                success = response.status_code == 200
                results.append(success)
                
                if success:
                    response_data = response.json()
                    answer = response_data.get("answer", "No answer")
                    self.print_test(f"Query: '{query[:30]}...'", True, f"Answer length: {len(answer)} chars")
                else:
                    self.print_test(f"Query: '{query[:30]}...'", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.print_test(f"Query: '{query[:30]}...'", False, f"Error: {str(e)}")
                results.append(False)
        
        return all(results)

    def test_admin_functionality(self) -> bool:
        """Test admin-related endpoints"""
        self.print_section("ADMIN FUNCTIONALITY")
        
        if not self.access_token:
            self.print_test("Admin Functionality", False, "No access token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Test inbox dates
        try:
            response = requests.get(f"{self.base_url}/admin/inbox/dates", headers=headers)
            success_dates = response.status_code in [200, 401, 403]  # 401/403 if not admin
            self.print_test("Get Inbox Dates", success_dates, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Inbox Dates", False, f"Error: {str(e)}")
            success_dates = False
        
        # Test tickets
        try:
            response = requests.get(f"{self.base_url}/tickets", headers=headers)
            success_tickets = response.status_code in [200, 401, 403]
            self.print_test("Get Tickets", success_tickets, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Tickets", False, f"Error: {str(e)}")
            success_tickets = False
        
        return success_dates and success_tickets

    def test_knowledge_base(self) -> bool:
        """Test knowledge base functionality"""
        self.print_section("KNOWLEDGE BASE")
        
        if not self.access_token:
            self.print_test("Knowledge Base", False, "No access token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        # Test knowledge base status
        try:
            response = requests.get(f"{self.base_url}/knowledge-base/status", headers=headers)
            success = response.status_code in [200, 404]  # 404 if endpoint doesn't exist
            self.print_test("Knowledge Base Status", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test("Knowledge Base Status", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self) -> bool:
        """Run all tests in sequence"""
        print("AILifeBotAssist - Comprehensive API Testing")
        print("=" * 60)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Protected Endpoints", self.test_protected_endpoints),
            ("Chat Functionality", self.test_chat_functionality),
            ("Admin Functionality", self.test_admin_functionality),
            ("Knowledge Base", self.test_knowledge_base)
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
        self.print_section("TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} | {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        success_rate = (passed / total) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Testing completed successfully!")
        else:
            print("⚠️  Some critical tests failed. Please review the issues above.")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    tester = APITester(base_url)
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
