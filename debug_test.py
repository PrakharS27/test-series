#!/usr/bin/env python3
"""
Debug specific failing tests
"""

import requests
import json
import uuid
import io

BASE_URL = "https://testmate-portal.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

def make_request(method, endpoint, data=None, token=None, files=None):
    """Make HTTP request with proper headers"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if files is None and data is not None:
        headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files, headers=headers, timeout=30)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def debug_tests():
    # Get admin token
    response = make_request("POST", "auth/login", ADMIN_CREDENTIALS)
    if response and response.status_code == 200:
        admin_token = response.json()["token"]
        print("✅ Admin token obtained")
    else:
        print("❌ Failed to get admin token")
        return
    
    # Create a teacher for testing
    teacher_data = {
        "username": f"debug_teacher_{uuid.uuid4().hex[:8]}",
        "password": "teacher123",
        "name": "Debug Teacher",
        "role": "teacher",
        "email": f"debug.teacher.{uuid.uuid4().hex[:8]}@gmail.com"
    }
    
    response = make_request("POST", "auth/register", teacher_data)
    if response and response.status_code == 200:
        print("✅ Teacher created")
        
        # Login as teacher
        login_response = make_request("POST", "auth/login", {
            "username": teacher_data["username"],
            "password": teacher_data["password"]
        })
        
        if login_response and login_response.status_code == 200:
            teacher_token = login_response.json()["token"]
            print("✅ Teacher token obtained")
            
            # Test 1: Invalid reset token
            print("\n=== Testing Invalid Reset Token ===")
            invalid_reset_data = {
                "resetToken": "invalid-token-12345",
                "newPassword": "shouldnotwork123"
            }
            response = make_request("POST", "auth/reset-password", invalid_reset_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json() if response else 'No response'}")
            
            # Test 2: Teacher trying to create category
            print("\n=== Testing Teacher Category Creation ===")
            new_category = {
                "name": f"Debug Category {uuid.uuid4().hex[:8]}",
                "description": "Debug category"
            }
            response = make_request("POST", "categories", new_category, token=teacher_token)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json() if response else 'No response'}")
            
            # Test 3: Invalid file upload
            print("\n=== Testing Invalid File Upload ===")
            files = {
                'photo': ('test.txt', io.BytesIO(b"This is not an image"), 'text/plain')
            }
            response = make_request("POST", "upload/photo", data={}, token=teacher_token, files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json() if response else 'No response'}")
            
            # Test 4: Teachers by category
            print("\n=== Testing Teachers by Category ===")
            # First get categories
            categories_response = make_request("GET", "categories")
            if categories_response and categories_response.status_code == 200:
                categories = categories_response.json()
                if categories:
                    category_id = categories[0].get("categoryId")
                    print(f"Testing with category: {category_id}")
                    
                    response = make_request("GET", f"teachers?category={category_id}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.json() if response else 'No response'}")
                else:
                    print("No categories found")
            else:
                print("Failed to get categories")
        else:
            print("❌ Failed to login teacher")
    else:
        print("❌ Failed to create teacher")

if __name__ == "__main__":
    debug_tests()