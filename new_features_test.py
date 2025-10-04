#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for NEW Test Series Platform Features
Tests all NEW functionality including:
1. Enhanced Authentication System (password reset, profile with photo)
2. Category Management System 
3. Teacher-Category Integration
4. File Upload System (photo and CSV uploads)
5. Enhanced Student Flow (category/teacher selection)
6. Enhanced Results System (student details, category filtering)
"""

import requests
import json
import time
import uuid
import io
import base64
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://testmate-portal.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

class NewFeaturesAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.teacher_token = None
        self.student_token = None
        self.category_id = None
        self.teacher_id = None
        self.test_series_id = None
        self.results = {
            "enhanced_auth": {"passed": 0, "failed": 0, "details": []},
            "category_management": {"passed": 0, "failed": 0, "details": []},
            "teacher_category_integration": {"passed": 0, "failed": 0, "details": []},
            "file_upload": {"passed": 0, "failed": 0, "details": []},
            "enhanced_student_flow": {"passed": 0, "failed": 0, "details": []},
            "enhanced_results": {"passed": 0, "failed": 0, "details": []}
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
    
    def make_request(self, method, endpoint, data=None, token=None, files=None):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/{endpoint}"
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
    
    def setup_admin_token(self):
        """Setup admin token for testing"""
        response = self.make_request("POST", "auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data["token"]
            print("✅ Admin token obtained successfully")
            return True
        else:
            print(f"❌ Failed to obtain admin token. Status: {response.status_code if response else 'No response'}")
            if response:
                print(f"Response: {response.text}")
            return False
    
    def test_enhanced_authentication(self):
        """Test enhanced authentication features"""
        print("\n=== TESTING ENHANCED AUTHENTICATION SYSTEM ===")
        
        # Create a test user for password reset testing
        test_email = f"reset.test.{uuid.uuid4().hex[:8]}@gmail.com"
        user_data = {
            "username": f"resetuser_{uuid.uuid4().hex[:8]}",
            "password": "original123",
            "name": "Reset Test User",
            "role": "teacher",
            "email": test_email
        }
        
        # Register user
        response = self.make_request("POST", "auth/register", user_data)
        if response and response.status_code == 200:
            print(f"✅ Test user created for password reset: {test_email}")
            
            # Test 1: Forgot Password Flow
            forgot_data = {"email": test_email}
            response = self.make_request("POST", "auth/forgot-password", forgot_data)
            if response and response.status_code == 200:
                data = response.json()
                if "resetToken" in data:
                    reset_token = data["resetToken"]
                    self.log_result("enhanced_auth", "Forgot Password Request", True, 
                                  "Password reset token generated successfully")
                    
                    # Test 2: Reset Password with Token
                    reset_data = {
                        "resetToken": reset_token,
                        "newPassword": "newpassword123"
                    }
                    response = self.make_request("POST", "auth/reset-password", reset_data)
                    if response and response.status_code == 200:
                        self.log_result("enhanced_auth", "Password Reset with Token", True, 
                                      "Password reset successfully completed")
                        
                        # Test 3: Login with New Password
                        login_data = {
                            "username": user_data["username"],
                            "password": "newpassword123"
                        }
                        response = self.make_request("POST", "auth/login", login_data)
                        if response and response.status_code == 200:
                            self.teacher_token = response.json()["token"]
                            self.log_result("enhanced_auth", "Login with New Password", True, 
                                          "Login successful with new password")
                        else:
                            self.log_result("enhanced_auth", "Login with New Password", False, 
                                          "Failed to login with new password")
                    else:
                        self.log_result("enhanced_auth", "Password Reset with Token", False, 
                                      f"Password reset failed: {response.status_code if response else 'No response'}")
                else:
                    self.log_result("enhanced_auth", "Forgot Password Request", False, 
                                  "Reset token not returned in response")
            else:
                self.log_result("enhanced_auth", "Forgot Password Request", False, 
                              f"Forgot password failed: {response.status_code if response else 'No response'}")
            
            # Test 4: Invalid Reset Token
            invalid_reset_data = {
                "resetToken": "invalid-token-12345",
                "newPassword": "shouldnotwork123"
            }
            response = self.make_request("POST", "auth/reset-password", invalid_reset_data)
            if response and response.status_code == 400:
                self.log_result("enhanced_auth", "Invalid Reset Token Rejection", True, 
                              "Invalid reset token properly rejected")
            else:
                self.log_result("enhanced_auth", "Invalid Reset Token Rejection", False, 
                              "Invalid reset token should be rejected")
        else:
            self.log_result("enhanced_auth", "Enhanced Auth Setup", False, 
                          "Could not create test user for password reset testing")
        
        # Test 5: Enhanced Profile Management
        if self.teacher_token:
            # Get current profile
            response = self.make_request("GET", "auth/profile", token=self.teacher_token)
            if response and response.status_code == 200:
                self.log_result("enhanced_auth", "Get Profile", True, 
                              "Profile retrieved successfully")
                
                # Update profile with enhanced fields
                profile_update = {
                    "name": "Updated Teacher Name",
                    "phone": "+1-555-0123",
                    "selectedCategory": "test-category-id",
                    "selectedTeacher": "test-teacher-id"
                }
                response = self.make_request("PUT", "auth/profile", profile_update, token=self.teacher_token)
                if response and response.status_code == 200:
                    self.log_result("enhanced_auth", "Update Profile with Enhanced Fields", True, 
                                  "Profile updated with enhanced fields successfully")
                else:
                    self.log_result("enhanced_auth", "Update Profile with Enhanced Fields", False, 
                                  f"Profile update failed: {response.status_code if response else 'No response'}")
            else:
                self.log_result("enhanced_auth", "Get Profile", False, 
                              f"Failed to get profile: {response.status_code if response else 'No response'}")
    
    def test_category_management(self):
        """Test category management system"""
        print("\n=== TESTING CATEGORY MANAGEMENT SYSTEM ===")
        
        if not self.admin_token:
            self.log_result("category_management", "Category Management Setup", False, 
                          "No admin token available")
            return
        
        # Test 1: Get All Categories
        response = self.make_request("GET", "categories")
        if response and response.status_code == 200:
            categories = response.json()
            if isinstance(categories, list):
                self.log_result("category_management", "Get All Categories", True, 
                              f"Retrieved {len(categories)} categories")
                
                # Check for default categories
                category_names = [cat.get("name", "") for cat in categories]
                expected_categories = ["JEE-Mains", "CUET PG", "NEET", "GATE", "CAT"]
                found_defaults = [cat for cat in expected_categories if cat in category_names]
                
                if len(found_defaults) >= 3:  # At least some default categories should exist
                    self.log_result("category_management", "Default Categories Verification", True, 
                                  f"Found default categories: {found_defaults}")
                else:
                    self.log_result("category_management", "Default Categories Verification", False, 
                                  f"Missing default categories. Found: {category_names}")
            else:
                self.log_result("category_management", "Get All Categories", False, 
                              "Categories response is not a list")
        else:
            self.log_result("category_management", "Get All Categories", False, 
                          f"Failed to get categories: {response.status_code if response else 'No response'}")
        
        # Test 2: Create New Category (Admin Only)
        new_category = {
            "name": f"Test Category {uuid.uuid4().hex[:8]}",
            "description": "A test category for API testing"
        }
        response = self.make_request("POST", "categories", new_category, token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if "categoryId" in data:
                self.category_id = data["categoryId"]
                self.log_result("category_management", "Create Category (Admin)", True, 
                              f"Category created successfully with ID: {self.category_id}")
            else:
                self.log_result("category_management", "Create Category (Admin)", False, 
                              "Category created but no ID returned")
        else:
            self.log_result("category_management", "Create Category (Admin)", False, 
                          f"Failed to create category: {response.status_code if response else 'No response'}")
        
        # Test 3: Non-Admin Cannot Create Category
        if self.teacher_token:
            response = self.make_request("POST", "categories", new_category, token=self.teacher_token)
            if response and response.status_code == 403:
                self.log_result("category_management", "Non-Admin Create Restriction", True, 
                              "Non-admin properly restricted from creating categories")
            else:
                self.log_result("category_management", "Non-Admin Create Restriction", False, 
                              "Non-admin should be restricted from creating categories")
        
        # Test 4: Delete Category (Admin Only)
        if self.category_id:
            response = self.make_request("DELETE", f"categories/{self.category_id}", token=self.admin_token)
            if response and response.status_code == 200:
                self.log_result("category_management", "Delete Category (Admin)", True, 
                              "Category deleted successfully")
            else:
                self.log_result("category_management", "Delete Category (Admin)", False, 
                              f"Failed to delete category: {response.status_code if response else 'No response'}")
        
        # Test 5: Non-Admin Cannot Delete Category
        if self.teacher_token and self.category_id:
            response = self.make_request("DELETE", f"categories/{self.category_id}", token=self.teacher_token)
            if response and response.status_code == 403:
                self.log_result("category_management", "Non-Admin Delete Restriction", True, 
                              "Non-admin properly restricted from deleting categories")
            else:
                self.log_result("category_management", "Non-Admin Delete Restriction", False, 
                              "Non-admin should be restricted from deleting categories")
    
    def test_teacher_category_integration(self):
        """Test teacher-category integration"""
        print("\n=== TESTING TEACHER-CATEGORY INTEGRATION ===")
        
        # Test 1: Get All Teachers
        response = self.make_request("GET", "teachers")
        if response and response.status_code == 200:
            teachers = response.json()
            if isinstance(teachers, list):
                self.log_result("teacher_category_integration", "Get All Teachers", True, 
                              f"Retrieved {len(teachers)} teachers")
                if teachers:
                    self.teacher_id = teachers[0].get("userId")
            else:
                self.log_result("teacher_category_integration", "Get All Teachers", False, 
                              "Teachers response is not a list")
        else:
            self.log_result("teacher_category_integration", "Get All Teachers", False, 
                          f"Failed to get teachers: {response.status_code if response else 'No response'}")
        
        # Test 2: Get Teachers by Category (when category has test series)
        # First create a test series in a category if we have tokens
        if self.teacher_token and self.admin_token:
            # Get a category to use
            categories_response = self.make_request("GET", "categories")
            if categories_response and categories_response.status_code == 200:
                categories = categories_response.json()
                if categories:
                    test_category = categories[0].get("categoryId") or categories[0].get("name")
                    
                    # Create a test series in this category
                    test_series_data = {
                        "title": "Category Integration Test",
                        "description": "Test series for category integration",
                        "category": test_category,
                        "duration": 30,
                        "questions": [
                            {
                                "questionId": str(uuid.uuid4()),
                                "question": "Test question for category integration?",
                                "options": ["A", "B", "C", "D"],
                                "correctAnswer": 0
                            }
                        ]
                    }
                    
                    response = self.make_request("POST", "test-series", test_series_data, token=self.teacher_token)
                    if response and response.status_code == 200:
                        # Now test getting teachers by category
                        response = self.make_request("GET", f"teachers?category={test_category}")
                        if response and response.status_code == 200:
                            filtered_teachers = response.json()
                            self.log_result("teacher_category_integration", "Get Teachers by Category", True, 
                                          f"Retrieved {len(filtered_teachers)} teachers for category {test_category}")
                        else:
                            self.log_result("teacher_category_integration", "Get Teachers by Category", False, 
                                          f"Failed to get teachers by category: {response.status_code if response else 'No response'}")
                    else:
                        self.log_result("teacher_category_integration", "Category Integration Setup", False, 
                                      "Could not create test series for category integration testing")
    
    def test_file_upload_system(self):
        """Test file upload system"""
        print("\n=== TESTING FILE UPLOAD SYSTEM ===")
        
        if not self.teacher_token:
            self.log_result("file_upload", "File Upload Setup", False, 
                          "No teacher token available for file upload testing")
            return
        
        # Test 1: Photo Upload (Valid)
        # Create a small test image (1x1 pixel PNG in base64)
        test_image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==")
        
        files = {
            'photo': ('test.png', io.BytesIO(test_image_data), 'image/png')
        }
        
        response = self.make_request("POST", "upload/photo", data={}, token=self.teacher_token, files=files)
        if response and response.status_code == 200:
            data = response.json()
            if "photoUrl" in data:
                self.log_result("file_upload", "Photo Upload (Valid)", True, 
                              "Photo uploaded successfully")
            else:
                self.log_result("file_upload", "Photo Upload (Valid)", False, 
                              "Photo uploaded but no URL returned")
        else:
            self.log_result("file_upload", "Photo Upload (Valid)", False, 
                          f"Photo upload failed: {response.status_code if response else 'No response'}")
        
        # Test 2: Photo Upload (Invalid File Type)
        files = {
            'photo': ('test.txt', io.BytesIO(b"This is not an image"), 'text/plain')
        }
        
        response = self.make_request("POST", "upload/photo", data={}, token=self.teacher_token, files=files)
        if response and response.status_code == 400:
            try:
                error_msg = response.json().get("error", "")
                if "invalid file type" in error_msg.lower():
                    self.log_result("file_upload", "Photo Upload (Invalid Type)", True, 
                                  "Invalid file type properly rejected")
                else:
                    self.log_result("file_upload", "Photo Upload (Invalid Type)", False, 
                                  f"Wrong error message: {error_msg}")
            except:
                # If JSON parsing fails, check response text
                if "invalid file type" in response.text.lower():
                    self.log_result("file_upload", "Photo Upload (Invalid Type)", True, 
                                  "Invalid file type properly rejected")
                else:
                    self.log_result("file_upload", "Photo Upload (Invalid Type)", False, 
                                  f"Unexpected response: {response.text}")
        else:
            self.log_result("file_upload", "Photo Upload (Invalid Type)", False, 
                          "Invalid file type should be rejected with 400")
        
        # Test 3: CSV Upload for Questions
        # First create a test series to upload questions to
        test_series_data = {
            "title": "CSV Upload Test Series",
            "description": "Test series for CSV upload testing",
            "category": "Mathematics",
            "duration": 60,
            "questions": []
        }
        
        response = self.make_request("POST", "test-series", test_series_data, token=self.teacher_token)
        if response and response.status_code == 200:
            test_series_id = response.json().get("testSeriesId")
            
            # Create CSV content
            csv_content = """Question,Option A,Option B,Option C,Option D,Correct Answer,Explanation
"What is 2+2?","3","4","5","6","2","Basic addition"
"What is 3*3?","6","9","12","15","2","Basic multiplication"
"What is 10/2?","4","5","6","7","2","Basic division"
"""
            
            files = {
                'csv': ('questions.csv', io.BytesIO(csv_content.encode()), 'text/csv')
            }
            data = {
                'testSeriesId': test_series_id
            }
            
            response = self.make_request("POST", "upload/csv", data=data, token=self.teacher_token, files=files)
            if response and response.status_code == 200:
                result = response.json()
                if "questionsCount" in result and result["questionsCount"] == 3:
                    self.log_result("file_upload", "CSV Upload (Valid)", True, 
                                  f"CSV uploaded successfully with {result['questionsCount']} questions")
                else:
                    self.log_result("file_upload", "CSV Upload (Valid)", False, 
                                  f"CSV uploaded but unexpected result: {result}")
            else:
                self.log_result("file_upload", "CSV Upload (Valid)", False, 
                              f"CSV upload failed: {response.status_code if response else 'No response'}")
        else:
            self.log_result("file_upload", "CSV Upload Setup", False, 
                          "Could not create test series for CSV upload testing")
        
        # Test 4: Unauthorized Photo Upload (Student)
        if self.student_token:
            files = {
                'photo': ('test.png', io.BytesIO(test_image_data), 'image/png')
            }
            
            response = self.make_request("POST", "upload/photo", data={}, token=self.student_token, files=files)
            if response and response.status_code == 403:
                self.log_result("file_upload", "Unauthorized Photo Upload", True, 
                              "Student properly restricted from photo upload")
            else:
                self.log_result("file_upload", "Unauthorized Photo Upload", False, 
                              "Student should be restricted from photo upload")
    
    def test_enhanced_student_flow(self):
        """Test enhanced student flow with category/teacher selection"""
        print("\n=== TESTING ENHANCED STUDENT FLOW ===")
        
        # Get available categories and teachers for testing
        categories_response = self.make_request("GET", "categories")
        teachers_response = self.make_request("GET", "teachers")
        
        if categories_response and categories_response.status_code == 200 and teachers_response and teachers_response.status_code == 200:
            categories = categories_response.json()
            teachers = teachers_response.json()
            
            if categories and teachers:
                selected_category = categories[0].get("categoryId") or categories[0].get("name")
                selected_teacher = teachers[0].get("userId")
                
                # Test 1: Student Registration with Category/Teacher Selection
                student_data = {
                    "username": f"enhanced_student_{uuid.uuid4().hex[:8]}",
                    "password": "student123",
                    "name": "Enhanced Student",
                    "role": "student",
                    "email": f"enhanced.student.{uuid.uuid4().hex[:8]}@gmail.com",
                    "selectedCategory": selected_category,
                    "selectedTeacher": selected_teacher
                }
                
                response = self.make_request("POST", "auth/register", student_data)
                if response and response.status_code == 200:
                    data = response.json()
                    if data.get("user", {}).get("selectedCategory") == selected_category:
                        self.log_result("enhanced_student_flow", "Student Registration with Selections", True, 
                                      "Student registered with category/teacher selection")
                        
                        # Login as enhanced student
                        login_response = self.make_request("POST", "auth/login", {
                            "username": student_data["username"],
                            "password": student_data["password"]
                        })
                        
                        if login_response and login_response.status_code == 200:
                            enhanced_student_token = login_response.json()["token"]
                            
                            # Test 2: Student Sees Filtered Test Series
                            response = self.make_request("GET", "test-series", token=enhanced_student_token)
                            if response and response.status_code == 200:
                                test_series = response.json()
                                self.log_result("enhanced_student_flow", "Filtered Test Series View", True, 
                                              f"Student sees {len(test_series)} filtered test series")
                            else:
                                self.log_result("enhanced_student_flow", "Filtered Test Series View", False, 
                                              f"Failed to get filtered test series: {response.status_code if response else 'No response'}")
                            
                            # Test 3: Update Student Profile with New Selections
                            profile_update = {
                                "selectedCategory": selected_category,
                                "selectedTeacher": selected_teacher,
                                "name": "Updated Enhanced Student"
                            }
                            
                            response = self.make_request("PUT", "auth/profile", profile_update, token=enhanced_student_token)
                            if response and response.status_code == 200:
                                self.log_result("enhanced_student_flow", "Update Student Profile Selections", True, 
                                              "Student profile updated with new selections")
                            else:
                                self.log_result("enhanced_student_flow", "Update Student Profile Selections", False, 
                                              f"Failed to update student profile: {response.status_code if response else 'No response'}")
                            
                            self.student_token = enhanced_student_token
                        else:
                            self.log_result("enhanced_student_flow", "Enhanced Student Login", False, 
                                          "Failed to login enhanced student")
                    else:
                        self.log_result("enhanced_student_flow", "Student Registration with Selections", False, 
                                      "Student registered but selections not saved properly")
                else:
                    self.log_result("enhanced_student_flow", "Student Registration with Selections", False, 
                                  f"Enhanced student registration failed: {response.status_code if response else 'No response'}")
            else:
                self.log_result("enhanced_student_flow", "Enhanced Student Flow Setup", False, 
                              "No categories or teachers available for testing")
        else:
            self.log_result("enhanced_student_flow", "Enhanced Student Flow Setup", False, 
                          "Could not retrieve categories and teachers for testing")
    
    def test_enhanced_results_system(self):
        """Test enhanced results system with student details"""
        print("\n=== TESTING ENHANCED RESULTS SYSTEM ===")
        
        if not self.teacher_token or not self.student_token:
            self.log_result("enhanced_results", "Enhanced Results Setup", False, 
                          "No teacher or student token available")
            return
        
        # Create a test series and have student take it
        test_series_data = {
            "title": "Enhanced Results Test",
            "description": "Test series for enhanced results testing",
            "category": "General",
            "duration": 30,
            "questions": [
                {
                    "questionId": str(uuid.uuid4()),
                    "question": "Enhanced results test question?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": 1,
                    "explanation": "Test explanation"
                }
            ]
        }
        
        response = self.make_request("POST", "test-series", test_series_data, token=self.teacher_token)
        if response and response.status_code == 200:
            test_series_id = response.json().get("testSeriesId")
            
            # Student starts test attempt
            attempt_data = {"testSeriesId": test_series_id}
            response = self.make_request("POST", "test-attempts", attempt_data, token=self.student_token)
            if response and response.status_code == 200:
                attempt_id = response.json().get("attemptId")
                
                # Student submits answer
                answer_data = {
                    "questionId": test_series_data["questions"][0]["questionId"],
                    "answer": 1,
                    "action": "submit_answer"
                }
                self.make_request("PUT", f"test-attempts/{attempt_id}", answer_data, token=self.student_token)
                
                # Student completes test
                complete_data = {"action": "complete_test"}
                self.make_request("PUT", f"test-attempts/{attempt_id}", complete_data, token=self.student_token)
                
                # Test 1: Teacher Views Enhanced Results with Student Details
                response = self.make_request("GET", "test-attempts", token=self.teacher_token)
                if response and response.status_code == 200:
                    attempts = response.json()
                    if attempts and isinstance(attempts, list):
                        attempt = attempts[0]
                        if "studentDetails" in attempt:
                            student_details = attempt["studentDetails"]
                            expected_fields = ["name", "email"]
                            if any(field in student_details for field in expected_fields):
                                self.log_result("enhanced_results", "Teacher Views Enhanced Results", True, 
                                              "Teacher can view test attempts with student details")
                            else:
                                self.log_result("enhanced_results", "Teacher Views Enhanced Results", False, 
                                              f"Student details missing expected fields: {student_details}")
                        else:
                            self.log_result("enhanced_results", "Teacher Views Enhanced Results", False, 
                                          "Test attempts missing student details")
                    else:
                        self.log_result("enhanced_results", "Teacher Views Enhanced Results", False, 
                                      "No test attempts found or invalid format")
                else:
                    self.log_result("enhanced_results", "Teacher Views Enhanced Results", False, 
                                  f"Failed to get enhanced results: {response.status_code if response else 'No response'}")
                
                # Test 2: Admin Views Enhanced Analytics
                if self.admin_token:
                    response = self.make_request("GET", "analytics", token=self.admin_token)
                    if response and response.status_code == 200:
                        analytics = response.json()
                        expected_fields = ["totalUsers", "totalTestSeries", "totalAttempts"]
                        if all(field in analytics for field in expected_fields):
                            self.log_result("enhanced_results", "Admin Enhanced Analytics", True, 
                                          f"Admin analytics working: {analytics['totalAttempts']} total attempts")
                        else:
                            self.log_result("enhanced_results", "Admin Enhanced Analytics", False, 
                                          f"Missing analytics fields: {analytics}")
                    else:
                        self.log_result("enhanced_results", "Admin Enhanced Analytics", False, 
                                      f"Failed to get admin analytics: {response.status_code if response else 'No response'}")
            else:
                self.log_result("enhanced_results", "Enhanced Results Test Setup", False, 
                              "Could not create test attempt for enhanced results testing")
        else:
            self.log_result("enhanced_results", "Enhanced Results Test Setup", False, 
                          "Could not create test series for enhanced results testing")
    
    def run_all_tests(self):
        """Run all new features test suites"""
        print("🚀 Starting NEW FEATURES Backend API Testing...")
        print(f"Base URL: {self.base_url}")
        print("Testing: Enhanced Auth, Category Management, Teacher-Category Integration, File Upload, Enhanced Student Flow, Enhanced Results")
        
        start_time = time.time()
        
        # Setup admin token first
        if not self.setup_admin_token():
            print("❌ Cannot proceed without admin token")
            return False
        
        # Run all test suites
        self.test_enhanced_authentication()
        self.test_category_management()
        self.test_teacher_category_integration()
        self.test_file_upload_system()
        self.test_enhanced_student_flow()
        self.test_enhanced_results_system()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "="*80)
        print("📊 NEW FEATURES TEST RESULTS SUMMARY")
        print("="*80)
        
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
        
        print("-" * 80)
        print(f"🎯 OVERALL: {total_passed} passed, {total_failed} failed")
        print(f"⏱️  Duration: {end_time - start_time:.2f} seconds")
        
        if total_failed == 0:
            print("🎉 ALL NEW FEATURES TESTS PASSED! New functionality is working correctly.")
        else:
            print(f"⚠️  {total_failed} tests failed. Please review the issues above.")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = NewFeaturesAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)