#!/usr/bin/env python3
"""
Test script to debug authentication issues
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_register():
    """Test user registration"""
    url = f"{BASE_URL}/register"
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    print("Testing user registration...")
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_login():
    """Test user login"""
    url = f"{BASE_URL}/token"
    data = {
        "username": "test@example.com",  # Note: OAuth2 uses 'username' field
        "password": "testpassword123"
    }
    
    print("\nTesting user login...")
    response = requests.post(url, data=data)  # Note: using data, not json for form data
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_query_with_token(token):
    """Test protected query endpoint"""
    url = f"{BASE_URL}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "question": "What is your name?"
    }
    
    print(f"\nTesting query with token...")
    print(f"Token: {token}")
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    print("=== Authentication Test Script ===")
    
    # Test registration
    token = test_register()
    
    if not token:
        print("\nRegistration failed, trying login...")
        token = test_login()
    
    if token:
        print(f"\nAuthentication successful! Token: {token[:50]}...")
        test_query_with_token(token)
    else:
        print("\nAuthentication failed!")

if __name__ == "__main__":
    main()
