#!/usr/bin/env python3
"""
Enhanced Backend API Testing for Test Series Web App
Tests all new features including:
1. Custom Admin Login with new credentials
2. Email Validation & Temp Mail Restriction
3. Profile Management System
4. Bulk Question Import System
5. Enhanced Test Series Creation with bulk imported questions
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://test-display-issue.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}
NEW_ADMIN_CREDENTIALS = {"username": "prakharshivam0@gmail.com", "password": "Admin!@Super@19892005"}

class EnhancedTestSeriesAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.new_admin_token = None
        self.teacher_token = None
        self.student_token = None
        self.test_series_id = None
        self.attempt_id = None
        self.imported_questions = []
        self.results = {
            "new_admin_login": {"passed": 0, "failed": 0, "details": []},
            "email_validation": {"passed": 0, "failed": 0, "details": []},
            "profile_management": {"passed": 0, "failed": 0, "details": []},
            "bulk_import": {"passed": 0, "failed": 0, "details": []},
            "enhanced_test_series": {"passed": 0, "failed": 0, "details": []},
            "backward_compatibility": {"passed": 0, "failed": 0, "details": []}
        }
    
    def log_result(self, category, test_name, success, message, response_data=None):
        """Log test result"""
        if success:
            self.results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.results[category]["failed"] += 1
            status = "❌ FAIL"
        
        detail = {
            "test": test_name,
            "status": status,
            "message": message,
            "response": response_data if not success else None
        }
        self.results[category]["details"].append(detail)
        print(f"{status}: {test_name} - {message}")
    
    def make_request(self, method, endpoint, data=None, token=None):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def test_new_admin_login(self):
        """Test new admin credentials"""
        print("\n=== TESTING NEW ADMIN LOGIN ===")
        
        # Test 1: Original Admin Login (should still work)
        response = self.make_request("POST", "auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                self.admin_token = data["token"]
                self.log_result("new_admin_login", "Original Admin Login", True, 
                              f"Original admin logged in successfully, role: {data['user']['role']}")
            else:
                self.log_result("new_admin_login", "Original Admin Login", False, 
                              "Missing token or user in response", response.json())
        else:
            self.log_result("new_admin_login", "Original Admin Login", False, 
                          f"Login failed with status {response.status_code if response else 'No response'}", 
                          response.json() if response else None)
        
        # Test 2: New Admin Login (prakharshivam0@gmail.com / Admin!@Super@19892005)
        response = self.make_request("POST", "auth/login", NEW_ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data and data["user"]["role"] == "admin":
                self.new_admin_token = data["token"]
                self.log_result("new_admin_login", "New Admin Login", True, 
                              f"New admin logged in successfully, role: {data['user']['role']}")
            else:
                self.log_result("new_admin_login", "New Admin Login", False, 
                              "Login successful but user data incorrect", response.json())
        else:
            self.log_result("new_admin_login", "New Admin Login", False, 
                          f"New admin login failed with status {response.status_code if response else 'No response'}", 
                          response.json() if response else None)
        
        # Test 3: Verify new admin has admin privileges
        if self.new_admin_token:
            response = self.make_request("GET", "users", token=self.new_admin_token)
            if response and response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    self.log_result("new_admin_login", "New Admin Privileges", True, 
                                  f"New admin can access user management (found {len(users)} users)")
                else:
                    self.log_result("new_admin_login", "New Admin Privileges", False, 
                                  "New admin cannot access user management properly")
            else:
                self.log_result("new_admin_login", "New Admin Privileges", False, 
                              "New admin cannot access admin endpoints")
    
    def test_email_validation(self):
        """Test email validation and temporary email restrictions"""
        print("\n=== TESTING EMAIL VALIDATION & TEMP MAIL RESTRICTION ===")
        
        # Test 1: Invalid email format
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@missinglocal.com",
            "spaces in@email.com",
            "double@@domain.com"
        ]
        
        for invalid_email in invalid_emails:
            user_data = {
                "username": invalid_email,
                "password": "password123",
                "name": "Test User",
                "role": "student"
            }
            response = self.make_request("POST", "auth/register", user_data)
            if response and response.status_code == 400:
                error_msg = response.json().get("error", "")
                if "valid email" in error_msg.lower():
                    self.log_result("email_validation", f"Invalid Email Rejection ({invalid_email})", True, 
                                  "Invalid email format properly rejected")
                else:
                    self.log_result("email_validation", f"Invalid Email Rejection ({invalid_email})", False, 
                                  f"Wrong error message: {error_msg}")
            else:
                self.log_result("email_validation", f"Invalid Email Rejection ({invalid_email})", False, 
                              f"Invalid email should be rejected with 400, got {response.status_code if response else 'No response'}")
        
        # Test 2: Temporary email domains
        temp_emails = [
            "test@10minutemail.com",
            "user@guerrillamail.com", 
            "temp@mailinator.com",
            "fake@tempmail.org",
            "throwaway@yopmail.com"
        ]
        
        for temp_email in temp_emails:
            user_data = {
                "username": temp_email,
                "password": "password123",
                "name": "Test User",
                "role": "student"
            }
            response = self.make_request("POST", "auth/register", user_data)
            if response and response.status_code == 400:
                error_msg = response.json().get("error", "")
                if "temporary email" in error_msg.lower() or "permanent email" in error_msg.lower():
                    self.log_result("email_validation", f"Temp Email Rejection ({temp_email})", True, 
                                  "Temporary email properly rejected")
                else:
                    self.log_result("email_validation", f"Temp Email Rejection ({temp_email})", False, 
                                  f"Wrong error message: {error_msg}")
            else:
                self.log_result("email_validation", f"Temp Email Rejection ({temp_email})", False, 
                              f"Temp email should be rejected with 400, got {response.status_code if response else 'No response'}")
        
        # Test 3: Valid email should work
        valid_email = f"valid.user.{uuid.uuid4().hex[:8]}@gmail.com"
        user_data = {
            "username": valid_email,
            "password": "password123",
            "name": "Valid User",
            "role": "student"
        }
        response = self.make_request("POST", "auth/register", user_data)
        if response and response.status_code == 200:
            self.log_result("email_validation", "Valid Email Acceptance", True, 
                          f"Valid email {valid_email} accepted successfully")
        else:
            self.log_result("email_validation", "Valid Email Acceptance", False, 
                          f"Valid email should be accepted, got {response.status_code if response else 'No response'}")
    
    def test_profile_management(self):
        """Test profile management endpoints"""
        print("\n=== TESTING PROFILE MANAGEMENT SYSTEM ===")
        
        # First create a test user for profile testing
        test_email = f"profile.test.{uuid.uuid4().hex[:8]}@gmail.com"
        user_data = {
            "username": test_email,
            "password": "password123",
            "name": "Profile Test User",
            "role": "teacher"
        }
        
        # Register user
        response = self.make_request("POST", "auth/register", user_data)
        if response and response.status_code == 200:
            # Login to get token
            login_response = self.make_request("POST", "auth/login", {
                "username": test_email,
                "password": "password123"
            })
            
            if login_response and login_response.status_code == 200:
                profile_token = login_response.json()["token"]
                
                # Test 1: GET /api/profile
                response = self.make_request("GET", "profile", token=profile_token)
                if response and response.status_code == 200:
                    profile_data = response.json()
                    expected_fields = ["userId", "username", "name", "role", "profile"]
                    if all(field in profile_data for field in expected_fields):
                        profile_info = profile_data.get("profile", {})
                        profile_fields = ["bio", "phone", "institution", "experience", "subjects", "profileImage"]
                        if all(field in profile_info for field in profile_fields):
                            self.log_result("profile_management", "GET Profile", True, 
                                          "Profile retrieved with all required fields")
                        else:
                            self.log_result("profile_management", "GET Profile", False, 
                                          f"Missing profile fields: {[f for f in profile_fields if f not in profile_info]}")
                    else:
                        self.log_result("profile_management", "GET Profile", False, 
                                      f"Missing user fields: {[f for f in expected_fields if f not in profile_data]}")
                else:
                    self.log_result("profile_management", "GET Profile", False, 
                                  f"Failed to get profile: {response.status_code if response else 'No response'}")
                
                # Test 2: PUT /api/profile (update profile)
                update_data = {
                    "name": "Updated Profile Test User",
                    "profile": {
                        "bio": "I am a passionate educator with 5 years of experience",
                        "phone": "+1-555-0123",
                        "institution": "Test University",
                        "experience": "5 years",
                        "subjects": ["Mathematics", "Physics"],
                        "profileImage": "https://example.com/profile.jpg"
                    }
                }
                
                response = self.make_request("PUT", "profile", update_data, token=profile_token)
                if response and response.status_code == 200:
                    self.log_result("profile_management", "PUT Profile Update", True, 
                                  "Profile updated successfully")
                    
                    # Verify the update by getting profile again
                    verify_response = self.make_request("GET", "profile", token=profile_token)
                    if verify_response and verify_response.status_code == 200:
                        updated_profile = verify_response.json()
                        if (updated_profile.get("name") == update_data["name"] and 
                            updated_profile.get("profile", {}).get("bio") == update_data["profile"]["bio"]):
                            self.log_result("profile_management", "Profile Update Verification", True, 
                                          "Profile changes persisted correctly")
                        else:
                            self.log_result("profile_management", "Profile Update Verification", False, 
                                          "Profile changes not persisted correctly")
                else:
                    self.log_result("profile_management", "PUT Profile Update", False, 
                                  f"Failed to update profile: {response.status_code if response else 'No response'}")
                
                # Test 3: Security - cannot update sensitive fields
                security_update = {
                    "userId": "malicious-id",
                    "username": "hacker@evil.com",
                    "role": "admin",
                    "password": "hacked",
                    "name": "Legitimate Update"
                }
                
                response = self.make_request("PUT", "profile", security_update, token=profile_token)
                if response and response.status_code == 200:
                    # Check that sensitive fields weren't updated
                    verify_response = self.make_request("GET", "profile", token=profile_token)
                    if verify_response and verify_response.status_code == 200:
                        profile = verify_response.json()
                        if (profile.get("username") == test_email and 
                            profile.get("role") == "teacher" and
                            profile.get("name") == "Legitimate Update"):
                            self.log_result("profile_management", "Security - Sensitive Fields Protection", True, 
                                          "Sensitive fields properly protected from updates")
                        else:
                            self.log_result("profile_management", "Security - Sensitive Fields Protection", False, 
                                          "Sensitive fields were improperly updated")
                else:
                    self.log_result("profile_management", "Security - Sensitive Fields Protection", False, 
                                  "Profile update should succeed but protect sensitive fields")
            else:
                self.log_result("profile_management", "Profile Management Setup", False, 
                              "Could not login test user for profile testing")
        else:
            self.log_result("profile_management", "Profile Management Setup", False, 
                          "Could not create test user for profile testing")
    
    def test_bulk_question_import(self):
        """Test bulk question import system"""
        print("\n=== TESTING BULK QUESTION IMPORT SYSTEM ===")
        
        # Create a teacher for testing
        teacher_email = f"import.teacher.{uuid.uuid4().hex[:8]}@gmail.com"
        teacher_data = {
            "username": teacher_email,
            "password": "teacher123",
            "name": "Import Test Teacher",
            "role": "teacher"
        }
        
        # Register and login teacher
        response = self.make_request("POST", "auth/register", teacher_data)
        if response and response.status_code == 200:
            login_response = self.make_request("POST", "auth/login", {
                "username": teacher_email,
                "password": "teacher123"
            })
            
            if login_response and login_response.status_code == 200:
                import_token = login_response.json()["token"]
                
                # Test 1: CSV format import
                csv_content = '''Question,Option1,Option2,Option3,Option4,CorrectAnswer
"What is the capital of France?","London","Berlin","Paris","Madrid",2
"What is 2 + 2?","3","4","5","6",1
"Which planet is closest to the Sun?","Venus","Mercury","Earth","Mars",1'''
                
                csv_data = {
                    "content": csv_content,
                    "format": "csv"
                }
                
                response = self.make_request("POST", "import-questions", csv_data, token=import_token)
                if response and response.status_code == 200:
                    result = response.json()
                    if ("questions" in result and "count" in result and 
                        result["count"] == 3 and len(result["questions"]) == 3):
                        self.imported_questions = result["questions"]
                        # Verify questions have questionIds
                        if all("questionId" in q for q in result["questions"]):
                            self.log_result("bulk_import", "CSV Format Import", True, 
                                          f"Successfully imported {result['count']} questions from CSV with questionIds")
                        else:
                            self.log_result("bulk_import", "CSV Format Import", False, 
                                          "Questions imported but missing questionIds")
                    else:
                        self.log_result("bulk_import", "CSV Format Import", False, 
                                      f"Unexpected import result: {result}")
                else:
                    self.log_result("bulk_import", "CSV Format Import", False, 
                                  f"CSV import failed: {response.status_code if response else 'No response'}")
                
                # Test 2: Text format import
                text_content = '''What is the largest ocean on Earth?
Pacific Ocean
Atlantic Ocean
Indian Ocean
Arctic Ocean
0

What is the chemical symbol for gold?
Au
Ag
Cu
Fe
0

What year did World War II end?
1944
1945
1946
1947
1'''
                
                text_data = {
                    "content": text_content,
                    "format": "text"
                }
                
                response = self.make_request("POST", "import-questions", text_data, token=import_token)
                if response and response.status_code == 200:
                    result = response.json()
                    if ("questions" in result and "count" in result and 
                        result["count"] == 3 and len(result["questions"]) == 3):
                        self.log_result("bulk_import", "Text Format Import", True, 
                                      f"Successfully imported {result['count']} questions from text format")
                    else:
                        self.log_result("bulk_import", "Text Format Import", False, 
                                      f"Unexpected text import result: {result}")
                else:
                    self.log_result("bulk_import", "Text Format Import", False, 
                                  f"Text import failed: {response.status_code if response else 'No response'}")
                
                # Test 3: Invalid content handling
                invalid_data = {
                    "content": "This is not valid question format",
                    "format": "csv"
                }
                
                response = self.make_request("POST", "import-questions", invalid_data, token=import_token)
                if response and response.status_code == 400:
                    error_msg = response.json().get("error", "")
                    if "no valid questions" in error_msg.lower():
                        self.log_result("bulk_import", "Invalid Content Handling", True, 
                                      "Invalid content properly rejected")
                    else:
                        self.log_result("bulk_import", "Invalid Content Handling", False, 
                                      f"Wrong error message: {error_msg}")
                else:
                    self.log_result("bulk_import", "Invalid Content Handling", False, 
                                  "Invalid content should be rejected with 400")
                
                # Test 4: Empty content handling
                empty_data = {
                    "content": "",
                    "format": "csv"
                }
                
                response = self.make_request("POST", "import-questions", empty_data, token=import_token)
                if response and response.status_code == 400:
                    self.log_result("bulk_import", "Empty Content Handling", True, 
                                  "Empty content properly rejected")
                else:
                    self.log_result("bulk_import", "Empty Content Handling", False, 
                                  "Empty content should be rejected with 400")
                
                # Test 5: Role-based access (student should not be able to import)
                if hasattr(self, 'student_token') and self.student_token:
                    response = self.make_request("POST", "import-questions", csv_data, token=self.student_token)
                    if response and response.status_code == 403:
                        self.log_result("bulk_import", "Student Import Restriction", True, 
                                      "Student properly restricted from importing questions")
                    else:
                        self.log_result("bulk_import", "Student Import Restriction", False, 
                                      "Student should be restricted from importing questions")
                
                # Store teacher token for next test
                self.teacher_token = import_token
            else:
                self.log_result("bulk_import", "Bulk Import Setup", False, 
                              "Could not login teacher for import testing")
        else:
            self.log_result("bulk_import", "Bulk Import Setup", False, 
                          "Could not create teacher for import testing")
    
    def test_enhanced_test_series_creation(self):
        """Test enhanced test series creation with bulk imported questions"""
        print("\n=== TESTING ENHANCED TEST SERIES CREATION ===")
        
        if not self.teacher_token or not self.imported_questions:
            self.log_result("enhanced_test_series", "Enhanced Test Series Setup", False, 
                          "No teacher token or imported questions available")
            return
        
        # Test 1: Create test series with bulk imported questions
        test_series_data = {
            "title": "Imported Questions Test Series",
            "description": "Test series created using bulk imported questions",
            "category": "General Knowledge",
            "duration": 45,
            "questions": self.imported_questions  # Use imported questions
        }
        
        response = self.make_request("POST", "test-series", test_series_data, self.teacher_token)
        if response and response.status_code == 200:
            data = response.json()
            if "testSeriesId" in data:
                self.test_series_id = data["testSeriesId"]
                self.log_result("enhanced_test_series", "Create Test Series with Imported Questions", True, 
                              f"Test series created with imported questions, ID: {self.test_series_id}")
                
                # Verify the test series contains the imported questions with questionIds
                verify_response = self.make_request("GET", f"test-series/{self.test_series_id}", token=self.teacher_token)
                if verify_response and verify_response.status_code == 200:
                    test_series = verify_response.json()
                    questions = test_series.get("questions", [])
                    if (len(questions) == len(self.imported_questions) and 
                        all("questionId" in q for q in questions)):
                        self.log_result("enhanced_test_series", "Verify Imported Questions in Test Series", True, 
                                      f"Test series contains {len(questions)} questions with proper questionIds")
                    else:
                        self.log_result("enhanced_test_series", "Verify Imported Questions in Test Series", False, 
                                      "Test series questions don't match imported questions or missing questionIds")
            else:
                self.log_result("enhanced_test_series", "Create Test Series with Imported Questions", False, 
                              "Test series created but no ID returned")
        else:
            self.log_result("enhanced_test_series", "Create Test Series with Imported Questions", False, 
                          f"Failed to create test series: {response.status_code if response else 'No response'}")
        
        # Test 2: Mixed questions (some imported, some manual)
        mixed_questions = []
        if self.imported_questions:
            # Add first imported question
            mixed_questions.append(self.imported_questions[0])
        
        # Add manual question
        mixed_questions.append({
            "question": "What is the square root of 16?",
            "options": ["2", "4", "6", "8"],
            "correctAnswer": 1,
            "questionId": str(uuid.uuid4())
        })
        
        mixed_test_data = {
            "title": "Mixed Questions Test Series",
            "description": "Test series with both imported and manual questions",
            "category": "Mathematics",
            "duration": 30,
            "questions": mixed_questions
        }
        
        response = self.make_request("POST", "test-series", mixed_test_data, self.teacher_token)
        if response and response.status_code == 200:
            self.log_result("enhanced_test_series", "Create Test Series with Mixed Questions", True, 
                          "Test series created with mixed imported and manual questions")
        else:
            self.log_result("enhanced_test_series", "Create Test Series with Mixed Questions", False, 
                          f"Failed to create mixed test series: {response.status_code if response else 'No response'}")
    
    def test_backward_compatibility(self):
        """Test that existing functionality still works"""
        print("\n=== TESTING BACKWARD COMPATIBILITY ===")
        
        # Test 1: Original admin login still works
        response = self.make_request("POST", "auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            self.log_result("backward_compatibility", "Original Admin Login", True, 
                          "Original admin credentials still work")
        else:
            self.log_result("backward_compatibility", "Original Admin Login", False, 
                          "Original admin login broken")
        
        # Test 2: Regular user registration still works
        regular_user = {
            "username": f"regular.{uuid.uuid4().hex[:8]}@example.com",
            "password": "password123",
            "name": "Regular User",
            "role": "student"
        }
        
        response = self.make_request("POST", "auth/register", regular_user)
        if response and response.status_code == 200:
            self.log_result("backward_compatibility", "Regular User Registration", True, 
                          "Regular user registration still works")
            
            # Test login
            login_response = self.make_request("POST", "auth/login", {
                "username": regular_user["username"],
                "password": regular_user["password"]
            })
            if login_response and login_response.status_code == 200:
                self.student_token = login_response.json()["token"]
                self.log_result("backward_compatibility", "Regular User Login", True, 
                              "Regular user login still works")
            else:
                self.log_result("backward_compatibility", "Regular User Login", False, 
                              "Regular user login broken")
        else:
            self.log_result("backward_compatibility", "Regular User Registration", False, 
                          "Regular user registration broken")
        
        # Test 3: Test series creation without imported questions still works
        if self.teacher_token:
            manual_test_data = {
                "title": "Manual Test Series",
                "description": "Test series created manually",
                "category": "Science",
                "duration": 60,
                "questions": [
                    {
                        "question": "What is H2O?",
                        "options": ["Water", "Hydrogen", "Oxygen", "Salt"],
                        "correctAnswer": 0
                    }
                ]
            }
            
            response = self.make_request("POST", "test-series", manual_test_data, self.teacher_token)
            if response and response.status_code == 200:
                self.log_result("backward_compatibility", "Manual Test Series Creation", True, 
                              "Manual test series creation still works")
            else:
                self.log_result("backward_compatibility", "Manual Test Series Creation", False, 
                              "Manual test series creation broken")
    
    def run_all_tests(self):
        """Run all enhanced test suites"""
        print("🚀 Starting Enhanced Backend API Testing...")
        print(f"Base URL: {self.base_url}")
        print("Testing new features: Custom Admin Login, Email Validation, Profile Management, Bulk Import, Enhanced Test Series")
        
        start_time = time.time()
        
        # Run all test suites
        self.test_new_admin_login()
        self.test_email_validation()
        self.test_profile_management()
        self.test_bulk_question_import()
        self.test_enhanced_test_series_creation()
        self.test_backward_compatibility()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "="*70)
        print("📊 ENHANCED TEST RESULTS SUMMARY")
        print("="*70)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "❌"
            print(f"{status_icon} {category.upper().replace('_', ' ')}: {passed} passed, {failed} failed")
            
            # Show failed tests
            if failed > 0:
                for detail in results["details"]:
                    if "❌" in detail["status"]:
                        print(f"   - {detail['test']}: {detail['message']}")
        
        print("-" * 70)
        print(f"🎯 OVERALL: {total_passed} passed, {total_failed} failed")
        print(f"⏱️  Duration: {end_time - start_time:.2f} seconds")
        
        if total_failed == 0:
            print("🎉 ALL ENHANCED TESTS PASSED! New features are working correctly.")
        else:
            print(f"⚠️  {total_failed} tests failed. Please review the issues above.")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = EnhancedTestSeriesAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)