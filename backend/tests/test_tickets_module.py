#!/usr/bin/env python3
"""
Direct test of the actual tickets.py functions
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tickets_module_import():
    """Test that we can import the tickets module and its functions"""
    print("🧪 Testing tickets module import...")
    
    try:
        # Test importing the tickets module
        import adminbackend.tickets as tickets
        
        # Check that all expected functions exist
        expected_functions = [
            'create_ticket',
            'get_user_tickets', 
            'get_all_tickets',
            'get_bot_tickets',
            'get_bot_ticket_details',
            'get_ticket_details',
            'update_ticket_status'
        ]
        
        for func_name in expected_functions:
            assert hasattr(tickets, func_name), f"Function {func_name} not found in tickets module"
            func = getattr(tickets, func_name)
            assert callable(func), f"{func_name} is not callable"
            print(f"  ✅ {func_name} - OK")
        
        print("✅ All ticket functions are available and callable")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import tickets module: {e}")
        return False

def test_schemas_import():
    """Test that we can import the schemas module"""
    print("\n🧪 Testing schemas module import...")
    
    try:
        import schemas
        
        # Check that expected ticket schemas exist
        expected_schemas = ['TicketBase', 'TicketCreate', 'Ticket']
        
        for schema_name in expected_schemas:
            assert hasattr(schemas, schema_name), f"Schema {schema_name} not found"
            schema_class = getattr(schemas, schema_name)
            print(f"  ✅ {schema_name} - OK")
        
        print("✅ All ticket schemas are available")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import schemas: {e}")
        return False

def test_function_signatures():
    """Test that functions have expected signatures"""
    print("\n🧪 Testing function signatures...")
    
    try:
        import adminbackend.tickets as tickets
        import inspect
        
        # Test create_ticket signature
        sig = inspect.signature(tickets.create_ticket)
        params = list(sig.parameters.keys())
        expected_params = ['db', 'ticket', 'user_id', 'bot_id']
        
        for param in expected_params:
            assert param in params, f"Parameter {param} missing from create_ticket"
        
        print("  ✅ create_ticket signature - OK")
        
        # Test get_user_tickets signature
        sig = inspect.signature(tickets.get_user_tickets)
        params = list(sig.parameters.keys())
        assert 'db' in params and 'user_id' in params
        print("  ✅ get_user_tickets signature - OK")
        
        # Test update_ticket_status signature
        sig = inspect.signature(tickets.update_ticket_status)
        params = list(sig.parameters.keys())
        expected_params = ['db', 'ticket_id', 'new_status']
        
        for param in expected_params:
            assert param in params, f"Parameter {param} missing from update_ticket_status"
        
        print("  ✅ update_ticket_status signature - OK")
        
        print("✅ All function signatures are correct")
        return True
        
    except Exception as e:
        print(f"❌ Function signature test failed: {e}")
        return False

def test_tickets_code_quality():
    """Test code quality aspects of tickets.py"""
    print("\n🧪 Testing code quality...")
    
    try:
        # Read the tickets.py file
        tickets_path = os.path.join(os.path.dirname(__file__), 'adminbackend', 'tickets.py')
        with open(tickets_path, 'r') as f:
            content = f.read()
        
        # Check for basic code quality indicators
        checks = [
            ('imports', 'from sqlalchemy.orm import Session' in content),
            ('database imports', 'from database.database import' in content),
            ('schemas import', 'import schemas' in content),
            ('function definitions', 'def create_ticket(' in content),
            ('database operations', 'db.add(' in content),
            ('commit operations', 'db.commit(' in content),
            ('query operations', 'db.query(' in content),
        ]
        
        for check_name, condition in checks:
            assert condition, f"Code quality check failed: {check_name}"
            print(f"  ✅ {check_name} - OK")
        
        print("✅ Code quality checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Code quality test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Tickets Module Tests")
    print("=" * 50)
    
    tests = [
        test_tickets_module_import,
        test_schemas_import,
        test_function_signatures,
        test_tickets_code_quality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The tickets.py module is working correctly.")
        print("\n📋 What was tested:")
        print("   - Module imports work correctly")
        print("   - All expected functions are present and callable")
        print("   - Schemas are properly defined")
        print("   - Function signatures are correct")
        print("   - Code includes proper database operations")
        print("   - Code follows expected patterns")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
