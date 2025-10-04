#!/usr/bin/env python3
"""
Final Comprehensive Backend API Testing for ALL NEW Test Series Platform Features
This test ensures all new features are working correctly with proper test sequencing.
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

class FinalComprehensiveAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.teacher_token = None
        self.student_token = None
        self.category_id = None
        self.teacher_id = None
        self.test_series_id = None
        self.results = {
            "setup": {"passed": 0, "failed": 0, "details": []},
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
    
    def setup_tokens(self):
        """Setup all required tokens for testing"""
        print("\n=== SETTING UP TEST TOKENS ===")
        
        # Get admin token
        response = self.make_request("POST", "auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            self.admin_token = response.json()["token"]
            self.log_result("setup", "Admin Token Setup", True, "Admin token obtained successfully")
        else:
            self.log_result("setup", "Admin Token Setup", False, "Failed to obtain admin token")
            return False
        
        # Create and login teacher
        teacher_data = {
            "username": f"comprehensive_teacher_{uuid.uuid4().hex[:8]}",
            "password": "teacher123",
            "name": "Comprehensive Test Teacher",
            "role": "teacher",
            "email": f"comprehensive.teacher.{uuid.uuid4().hex[:8]}@gmail.com"
        }
        
        response = self.make_request("POST", "auth/register", teacher_data)
        if response and response.status_code == 200:
            # Login as teacher
            login_response = self.make_request("POST", "auth/login", {
                "username": teacher_data["username"],
                "password": teacher_data["password"]
            })
            
            if login_response and login_response.status_code == 200:
                self.teacher_token = login_response.json()["token"]
                self.teacher_id = login_response.json()["user"]["userId"]
                self.log_result("setup", "Teacher Token Setup", True, "Teacher token obtained successfully")
            else:
                self.log_result("setup", "Teacher Token Setup", False, "Failed to login teacher")
                return False
        else:
            self.log_result("setup", "Teacher Token Setup", False, "Failed to create teacher")
            return False
        
        # Create and login student
        student_data = {
            "username": f"comprehensive_student_{uuid.uuid4().hex[:8]}",
            "password": "student123",
            "name": "Comprehensive Test Student",
            "role": "student",
            "email": f"comprehensive.student.{uuid.uuid4().hex[:8]}@gmail.com"
        }
        
        response = self.make_request("POST", "auth/register", student_data)
        if response and response.status_code == 200:
            # Login as student
            login_response = self.make_request("POST", "auth/login", {
                "username": student_data["username"],
                "password": student_data["password"]
            })
            
            if login_response and login_response.status_code == 200:
                self.student_token = login_response.json()["token"]
                self.log_result("setup", "Student Token Setup", True, "Student token obtained successfully")
            else:
                self.log_result("setup", "Student Token Setup", False, "Failed to login student")
                return False
        else:
            self.log_result("setup", "Student Token Setup", False, "Failed to create student")
            return False
        
        return True
    
    def test_enhanced_authentication(self):
        """Test enhanced authentication features"""
        print("\n=== TESTING ENHANCED AUTHENTICATION SYSTEM ===")
        
        # Test 1: Password Reset Flow
        test_email = f"reset.comprehensive.{uuid.uuid4().hex[:8]}@gmail.com"
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
            # Test forgot password
            forgot_data = {"email": test_email}
            response = self.make_request("POST", "auth/forgot-password", forgot_data)
            if response and response.status_code == 200:
                data = response.json()
                if "resetToken" in data:
                    reset_token = data["resetToken"]
                    self.log_result("enhanced_auth", "Password Reset Flow", True, 
                                  "Password reset flow working correctly")
                    
                    # Test reset password with token
                    reset_data = {
                        "resetToken": reset_token,
                        "newPassword": "newpassword123"
                    }
                    response = self.make_request("POST", "auth/reset-password", reset_data)
                    if response and response.status_code == 200:
                        self.log_result("enhanced_auth", "Password Reset Completion", True, 
                                      "Password reset completed successfully")
                    else:
                        self.log_result("enhanced_auth", "Password Reset Completion", False, 
                                      "Password reset completion failed")
                else:
                    self.log_result("enhanced_auth", "Password Reset Flow", False, 
                                  "Reset token not returned")
            else:
                self.log_result("enhanced_auth", "Password Reset Flow", False, 
                              "Forgot password request failed")
        else:
            self.log_result("enhanced_auth", "Password Reset Flow", False, 
                          "Could not create test user for password reset")
        
        # Test 2: Invalid Reset Token Rejection
        invalid_reset_data = {
            "resetToken": "invalid-token-12345",
            "newPassword": "shouldnotwork123"
        }
        response = self.make_request("POST", "auth/reset-password", invalid_reset_data)
        if response and response.status_code == 400:
            try:
                error_msg = response.json().get("error", "")
                if "invalid" in error_msg.lower() or "expired" in error_msg.lower():
                    self.log_result("enhanced_auth", "Invalid Reset Token Rejection", True, 
                                  "Invalid reset token properly rejected")
                else:
                    self.log_result("enhanced_auth", "Invalid Reset Token Rejection", False, 
                                  f"Wrong error message: {error_msg}")
            except:
                self.log_result("enhanced_auth", "Invalid Reset Token Rejection", True, 
                              "Invalid reset token properly rejected (400 status)")
        else:
            self.log_result("enhanced_auth", "Invalid Reset Token Rejection", False, 
                          "Invalid reset token should be rejected with 400")
        
        # Test 3: Enhanced Profile Management
        if self.teacher_token:
            response = self.make_request("GET", "auth/profile", token=self.teacher_token)
            if response and response.status_code == 200:
                self.log_result("enhanced_auth", "Enhanced Profile Retrieval", True, 
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
                    self.log_result("enhanced_auth", "Enhanced Profile Update", True, 
                                  "Profile updated with enhanced fields")
                else:
                    self.log_result("enhanced_auth", "Enhanced Profile Update", False, 
                                  "Profile update failed")
            else:
                self.log_result("enhanced_auth", "Enhanced Profile Retrieval", False, 
                              "Failed to retrieve profile")
    
    def test_category_management(self):
        """Test category management system"""
        print("\n=== TESTING CATEGORY MANAGEMENT SYSTEM ===")
        
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
                
                if len(found_defaults) >= 3:
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
                          "Failed to get categories")
        
        # Test 2: Create Category (Admin Only)
        new_category = {
            "name": f"Test Category {uuid.uuid4().hex[:8]}",
            "description": "A test category for comprehensive testing"
        }
        response = self.make_request("POST", "categories", new_category, token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if "categoryId" in data:
                self.category_id = data["categoryId"]
                self.log_result("category_management", "Admin Create Category", True, 
                              f"Category created successfully with ID: {self.category_id}")
            else:
                self.log_result("category_management", "Admin Create Category", False, 
                              "Category created but no ID returned")
        else:
            self.log_result("category_management", "Admin Create Category", False, 
                          "Failed to create category as admin")
        
        # Test 3: Non-Admin Cannot Create Category
        response = self.make_request("POST", "categories", new_category, token=self.teacher_token)
        if response and response.status_code == 403:
            try:
                error_msg = response.json().get("error", "")
                if "unauthorized" in error_msg.lower():
                    self.log_result("category_management", "Non-Admin Create Restriction", True, 
                                  "Non-admin properly restricted from creating categories")
                else:
                    self.log_result("category_management", "Non-Admin Create Restriction", True, 
                                  "Non-admin restricted (403 status)")
            except:
                self.log_result("category_management", "Non-Admin Create Restriction", True, 
                              "Non-admin properly restricted (403 status)")
        else:
            self.log_result("category_management", "Non-Admin Create Restriction", False, 
                          f"Non-admin should be restricted, got status: {response.status_code if response else 'No response'}")
        
        # Test 4: Delete Category (Admin Only)
        if self.category_id:
            response = self.make_request("DELETE", f"categories/{self.category_id}", token=self.admin_token)
            if response and response.status_code == 200:
                self.log_result("category_management", "Admin Delete Category", True, 
                              "Category deleted successfully")
                
                # Test 5: Non-Admin Cannot Delete Category (create another category first)
                another_category = {
                    "name": f"Another Test Category {uuid.uuid4().hex[:8]}",
                    "description": "Another test category"
                }
                create_response = self.make_request("POST", "categories", another_category, token=self.admin_token)
                if create_response and create_response.status_code == 200:
                    another_category_id = create_response.json().get("categoryId")
                    
                    response = self.make_request("DELETE", f"categories/{another_category_id}", token=self.teacher_token)
                    if response and response.status_code == 403:
                        self.log_result("category_management", "Non-Admin Delete Restriction", True, 
                                      "Non-admin properly restricted from deleting categories")
                    else:
                        self.log_result("category_management", "Non-Admin Delete Restriction", False, 
                                      f"Non-admin should be restricted, got status: {response.status_code if response else 'No response'}")
                    
                    # Clean up
                    self.make_request("DELETE", f"categories/{another_category_id}", token=self.admin_token)
            else:
                self.log_result("category_management", "Admin Delete Category", False, 
                              "Failed to delete category as admin")
    
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
            else:
                self.log_result("teacher_category_integration", "Get All Teachers", False, 
                              "Teachers response is not a list")
        else:
            self.log_result("teacher_category_integration", "Get All Teachers", False, 
                          "Failed to get teachers")
        
        # Test 2: Get Teachers by Category
        # First get categories
        categories_response = self.make_request("GET", "categories")
        if categories_response and categories_response.status_code == 200:
            categories = categories_response.json()
            if categories:
                test_category = categories[0].get("categoryId") or categories[0].get("name")
                
                # Create a test series in this category to ensure there are teachers with test series
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
                
                create_response = self.make_request("POST", "test-series", test_series_data, token=self.teacher_token)
                if create_response and create_response.status_code == 200:
                    # Now test getting teachers by category
                    response = self.make_request("GET", f"teachers?category={test_category}")
                    if response and response.status_code == 200:
                        filtered_teachers = response.json()
                        self.log_result("teacher_category_integration", "Get Teachers by Category", True, 
                                      f"Retrieved {len(filtered_teachers)} teachers for category")
                    else:
                        self.log_result("teacher_category_integration", "Get Teachers by Category", False, 
                                      f"Failed to get teachers by category: {response.status_code if response else 'No response'}")
                else:
                    self.log_result("teacher_category_integration", "Get Teachers by Category", False, 
                                  "Could not create test series for category integration testing")
            else:
                self.log_result("teacher_category_integration", "Get Teachers by Category", False, 
                              "No categories available for testing")
        else:
            self.log_result("teacher_category_integration", "Get Teachers by Category", False, 
                          "Could not retrieve categories for testing")
    
    def test_file_upload_system(self):
        """Test file upload system"""
        print("\n=== TESTING FILE UPLOAD SYSTEM ===")
        
        # Test 1: Valid Photo Upload
        test_image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==")
        
        files = {
            'photo': ('test.png', io.BytesIO(test_image_data), 'image/png')
        }
        
        response = self.make_request("POST", "upload/photo", data={}, token=self.teacher_token, files=files)
        if response and response.status_code == 200:
            data = response.json()
            if "photoUrl" in data:
                self.log_result("file_upload", "Valid Photo Upload", True, 
                              "Photo uploaded successfully")
            else:
                self.log_result("file_upload", "Valid Photo Upload", False, 
                              "Photo uploaded but no URL returned")
        else:
            self.log_result("file_upload", "Valid Photo Upload", False, 
                          f"Photo upload failed: {response.status_code if response else 'No response'}")
        
        # Test 2: Invalid Photo Upload (Wrong File Type)
        files = {
            'photo': ('test.txt', io.BytesIO(b"This is not an image"), 'text/plain')
        }
        
        response = self.make_request("POST", "upload/photo", data={}, token=self.teacher_token, files=files)
        if response and response.status_code == 400:
            try:
                error_msg = response.json().get("error", "")
                if "invalid file type" in error_msg.lower():
                    self.log_result("file_upload", "Invalid Photo Upload Rejection", True, 
                                  "Invalid file type properly rejected")
                else:
                    self.log_result("file_upload", "Invalid Photo Upload Rejection", True, 
                                  "Invalid file upload rejected (400 status)")
            except:
                self.log_result("file_upload", "Invalid Photo Upload Rejection", True, 
                              "Invalid file upload rejected (400 status)")
        else:
            self.log_result("file_upload", "Invalid Photo Upload Rejection", False, 
                          f"Invalid file should be rejected, got status: {response.status_code if response else 'No response'}")
        
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
                    self.log_result("file_upload", "CSV Upload Success", True, 
                                  f"CSV uploaded successfully with {result['questionsCount']} questions")
                else:
                    self.log_result("file_upload", "CSV Upload Success", False, 
                                  f"CSV uploaded but unexpected result: {result}")
            else:
                self.log_result("file_upload", "CSV Upload Success", False, 
                              f"CSV upload failed: {response.status_code if response else 'No response'}")
        else:
            self.log_result("file_upload", "CSV Upload Success", False, 
                          "Could not create test series for CSV upload testing")
        
        # Test 4: Unauthorized Upload (Student)
        files = {
            'photo': ('test.png', io.BytesIO(test_image_data), 'image/png')
        }
        
        response = self.make_request("POST", "upload/photo", data={}, token=self.student_token, files=files)
        if response and response.status_code == 403:
            self.log_result("file_upload", "Unauthorized Upload Restriction", True, 
                          "Student properly restricted from photo upload")
        else:
            self.log_result("file_upload", "Unauthorized Upload Restriction", False, 
                          f"Student should be restricted, got status: {response.status_code if response else 'No response'}")
    
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
                                              "Failed to get filtered test series")
                            
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
                                              "Failed to update student profile")
                        else:
                            self.log_result("enhanced_student_flow", "Enhanced Student Login", False, 
                                          "Failed to login enhanced student")
                    else:
                        self.log_result("enhanced_student_flow", "Student Registration with Selections", False, 
                                      "Student registered but selections not saved properly")
                else:
                    self.log_result("enhanced_student_flow", "Student Registration with Selections", False, 
                                  "Enhanced student registration failed")
            else:
                self.log_result("enhanced_student_flow", "Enhanced Student Flow Setup", False, 
                              "No categories or teachers available for testing")
        else:
            self.log_result("enhanced_student_flow", "Enhanced Student Flow Setup", False, 
                          "Could not retrieve categories and teachers for testing")
    
    def test_enhanced_results_system(self):
        """Test enhanced results system with student details"""
        print("\n=== TESTING ENHANCED RESULTS SYSTEM ===")
        
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
                        # Find our test attempt
                        our_attempt = None
                        for attempt in attempts:
                            if attempt.get("testSeriesId") == test_series_id:
                                our_attempt = attempt
                                break
                        
                        if our_attempt and "studentDetails" in our_attempt:
                            student_details = our_attempt["studentDetails"]
                            if "name" in student_details:
                                self.log_result("enhanced_results", "Teacher Views Enhanced Results", True, 
                                              "Teacher can view test attempts with student details")
                            else:
                                self.log_result("enhanced_results", "Teacher Views Enhanced Results", False, 
                                              f"Student details missing expected fields: {student_details}")
                        else:
                            self.log_result("enhanced_results", "Teacher Views Enhanced Results", False, 
                                          "Test attempts missing student details or attempt not found")
                    else:
                        self.log_result("enhanced_results", "Teacher Views Enhanced Results", False, 
                                      "No test attempts found or invalid format")
                else:
                    self.log_result("enhanced_results", "Teacher Views Enhanced Results", False, 
                                  "Failed to get enhanced results")
                
                # Test 2: Admin Views Enhanced Analytics
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
                                  "Failed to get admin analytics")
            else:
                self.log_result("enhanced_results", "Enhanced Results Test Setup", False, 
                              "Could not create test attempt for enhanced results testing")
        else:
            self.log_result("enhanced_results", "Enhanced Results Test Setup", False, 
                          "Could not create test series for enhanced results testing")
    
    def run_all_tests(self):
        """Run all comprehensive test suites"""
        print("🚀 Starting FINAL COMPREHENSIVE Backend API Testing...")
        print(f"Base URL: {self.base_url}")
        print("Testing ALL NEW FEATURES with proper test sequencing")
        
        start_time = time.time()
        
        # Setup tokens first
        if not self.setup_tokens():
            print("❌ Cannot proceed without proper token setup")
            return False
        
        # Run all test suites in proper order
        self.test_enhanced_authentication()
        self.test_category_management()
        self.test_teacher_category_integration()
        self.test_file_upload_system()
        self.test_enhanced_student_flow()
        self.test_enhanced_results_system()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "="*90)
        print("📊 FINAL COMPREHENSIVE TEST RESULTS SUMMARY")
        print("="*90)
        
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
        
        print("-" * 90)
        print(f"🎯 OVERALL: {total_passed} passed, {total_failed} failed")
        print(f"⏱️  Duration: {end_time - start_time:.2f} seconds")
        
        if total_failed == 0:
            print("🎉 ALL NEW FEATURES TESTS PASSED! All new functionality is working correctly.")
        else:
            print(f"⚠️  {total_failed} tests failed. Please review the issues above.")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = FinalComprehensiveAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)