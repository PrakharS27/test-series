#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Test Series Web App
Tests all major API endpoints and workflows including authentication, 
test series management, test attempts, user management, and analytics.
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://test-display-issue.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

class TestSeriesAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.teacher_token = None
        self.student_token = None
        self.test_series_id = None
        self.attempt_id = None
        self.results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "test_series": {"passed": 0, "failed": 0, "details": []},
            "test_attempts": {"passed": 0, "failed": 0, "details": []},
            "user_management": {"passed": 0, "failed": 0, "details": []},
            "analytics": {"passed": 0, "failed": 0, "details": []}
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
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        # Test 1: Admin Login
        response = self.make_request("POST", "auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                self.admin_token = data["token"]
                self.log_result("authentication", "Admin Login", True, 
                              f"Admin logged in successfully, role: {data['user']['role']}")
            else:
                self.log_result("authentication", "Admin Login", False, 
                              "Missing token or user in response", response.json())
        else:
            self.log_result("authentication", "Admin Login", False, 
                          f"Login failed with status {response.status_code if response else 'No response'}", 
                          response.json() if response else None)
        
        # Test 2: Teacher Registration
        teacher_data = {
            "username": f"teacher_{uuid.uuid4().hex[:8]}",
            "password": "teacher123",
            "name": "Test Teacher",
            "role": "teacher"
        }
        response = self.make_request("POST", "auth/register", teacher_data)
        if response and response.status_code == 200:
            self.log_result("authentication", "Teacher Registration", True, 
                          "Teacher registered successfully")
            
            # Login as teacher
            login_response = self.make_request("POST", "auth/login", {
                "username": teacher_data["username"],
                "password": teacher_data["password"]
            })
            if login_response and login_response.status_code == 200:
                self.teacher_token = login_response.json()["token"]
                self.log_result("authentication", "Teacher Login", True, "Teacher logged in successfully")
            else:
                self.log_result("authentication", "Teacher Login", False, 
                              "Teacher login failed after registration")
        else:
            self.log_result("authentication", "Teacher Registration", False, 
                          f"Registration failed with status {response.status_code if response else 'No response'}")
        
        # Test 3: Student Registration
        student_data = {
            "username": f"student_{uuid.uuid4().hex[:8]}",
            "password": "student123",
            "name": "Test Student",
            "role": "student"
        }
        response = self.make_request("POST", "auth/register", student_data)
        if response and response.status_code == 200:
            self.log_result("authentication", "Student Registration", True, 
                          "Student registered successfully")
            
            # Login as student
            login_response = self.make_request("POST", "auth/login", {
                "username": student_data["username"],
                "password": student_data["password"]
            })
            if login_response and login_response.status_code == 200:
                self.student_token = login_response.json()["token"]
                self.log_result("authentication", "Student Login", True, "Student logged in successfully")
            else:
                self.log_result("authentication", "Student Login", False, 
                              "Student login failed after registration")
        else:
            self.log_result("authentication", "Student Registration", False, 
                          f"Registration failed with status {response.status_code if response else 'No response'}")
        
        # Test 4: Invalid Login
        response = self.make_request("POST", "auth/login", {
            "username": "invalid_user",
            "password": "wrong_password"
        })
        if response and response.status_code == 401:
            self.log_result("authentication", "Invalid Login Rejection", True, 
                          "Invalid credentials properly rejected")
        else:
            self.log_result("authentication", "Invalid Login Rejection", False, 
                          "Invalid login should return 401")
        
        # Test 5: JWT Token Verification
        if self.admin_token:
            response = self.make_request("GET", "auth/me", token=self.admin_token)
            if response and response.status_code == 200:
                user_data = response.json()
                if user_data.get("role") == "admin":
                    self.log_result("authentication", "JWT Token Verification", True, 
                                  "JWT token verified successfully")
                else:
                    self.log_result("authentication", "JWT Token Verification", False, 
                                  "JWT token verification returned wrong user data")
            else:
                self.log_result("authentication", "JWT Token Verification", False, 
                              "JWT token verification failed")
        
        # Test 6: Unauthorized Access
        response = self.make_request("GET", "test-series")
        if response and response.status_code == 401:
            self.log_result("authentication", "Unauthorized Access Protection", True, 
                          "Unauthorized access properly blocked")
        else:
            self.log_result("authentication", "Unauthorized Access Protection", False, 
                          "Unauthorized access should return 401")
    
    def test_test_series_management(self):
        """Test test series CRUD operations"""
        print("\n=== TESTING TEST SERIES MANAGEMENT ===")
        
        if not self.teacher_token:
            self.log_result("test_series", "Test Series Tests", False, 
                          "No teacher token available for testing")
            return
        
        # Test 1: Create Test Series
        test_series_data = {
            "title": "Sample Math Test",
            "description": "A comprehensive math test for students",
            "category": "Mathematics",
            "duration": 60,
            "questions": [
                {
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correctAnswer": 1
                },
                {
                    "question": "What is 5 * 3?",
                    "options": ["12", "15", "18", "20"],
                    "correctAnswer": 1
                },
                {
                    "question": "What is 10 / 2?",
                    "options": ["4", "5", "6", "7"],
                    "correctAnswer": 1
                }
            ]
        }
        
        response = self.make_request("POST", "test-series", test_series_data, self.teacher_token)
        if response and response.status_code == 200:
            data = response.json()
            if "testSeriesId" in data:
                self.test_series_id = data["testSeriesId"]
                self.log_result("test_series", "Create Test Series", True, 
                              f"Test series created with ID: {self.test_series_id}")
            else:
                self.log_result("test_series", "Create Test Series", False, 
                              "Test series created but no ID returned")
        else:
            self.log_result("test_series", "Create Test Series", False, 
                          f"Failed to create test series: {response.status_code if response else 'No response'}")
        
        # Test 2: Get All Test Series (Teacher)
        response = self.make_request("GET", "test-series", token=self.teacher_token)
        if response and response.status_code == 200:
            test_series_list = response.json()
            if isinstance(test_series_list, list):
                self.log_result("test_series", "Get Test Series List", True, 
                              f"Retrieved {len(test_series_list)} test series")
            else:
                self.log_result("test_series", "Get Test Series List", False, 
                              "Response is not a list")
        else:
            self.log_result("test_series", "Get Test Series List", False, 
                          f"Failed to get test series: {response.status_code if response else 'No response'}")
        
        # Test 3: Get Single Test Series
        if self.test_series_id:
            response = self.make_request("GET", f"test-series/{self.test_series_id}", token=self.teacher_token)
            if response and response.status_code == 200:
                test_series = response.json()
                if test_series.get("testSeriesId") == self.test_series_id:
                    self.log_result("test_series", "Get Single Test Series", True, 
                                  "Retrieved test series successfully")
                else:
                    self.log_result("test_series", "Get Single Test Series", False, 
                                  "Retrieved test series has wrong ID")
            else:
                self.log_result("test_series", "Get Single Test Series", False, 
                              f"Failed to get test series: {response.status_code if response else 'No response'}")
        
        # Test 4: Update Test Series
        if self.test_series_id:
            update_data = {
                "title": "Updated Math Test",
                "description": "Updated description"
            }
            response = self.make_request("PUT", f"test-series/{self.test_series_id}", 
                                       update_data, self.teacher_token)
            if response and response.status_code == 200:
                self.log_result("test_series", "Update Test Series", True, 
                              "Test series updated successfully")
            else:
                self.log_result("test_series", "Update Test Series", False, 
                              f"Failed to update test series: {response.status_code if response else 'No response'}")
        
        # Test 5: Role-based Access (Student should see test series but not create)
        if self.student_token:
            response = self.make_request("GET", "test-series", token=self.student_token)
            if response and response.status_code == 200:
                self.log_result("test_series", "Student View Access", True, 
                              "Student can view test series")
            else:
                self.log_result("test_series", "Student View Access", False, 
                              "Student cannot view test series")
            
            # Student should not be able to create test series
            response = self.make_request("POST", "test-series", test_series_data, self.student_token)
            if response and response.status_code == 403:
                self.log_result("test_series", "Student Create Restriction", True, 
                              "Student properly restricted from creating test series")
            else:
                self.log_result("test_series", "Student Create Restriction", False, 
                              "Student should not be able to create test series")
    
    def test_test_attempts(self):
        """Test test taking workflow"""
        print("\n=== TESTING TEST ATTEMPTS ===")
        
        if not self.student_token or not self.test_series_id:
            self.log_result("test_attempts", "Test Attempts Tests", False, 
                          "No student token or test series ID available")
            return
        
        # Test 1: Start Test Attempt
        attempt_data = {"testSeriesId": self.test_series_id}
        response = self.make_request("POST", "test-attempts", attempt_data, self.student_token)
        if response and response.status_code == 200:
            data = response.json()
            if "attemptId" in data:
                self.attempt_id = data["attemptId"]
                self.log_result("test_attempts", "Start Test Attempt", True, 
                              f"Test attempt started with ID: {self.attempt_id}")
            else:
                self.log_result("test_attempts", "Start Test Attempt", False, 
                              "Test attempt started but no ID returned")
        else:
            self.log_result("test_attempts", "Start Test Attempt", False, 
                          f"Failed to start test attempt: {response.status_code if response else 'No response'}")
        
        # Test 2: Submit Answer
        if self.attempt_id:
            # Get the test series to find question IDs
            test_response = self.make_request("GET", f"test-series/{self.test_series_id}", token=self.student_token)
            if test_response and test_response.status_code == 200:
                test_data = test_response.json()
                questions = test_data.get("questions", [])
                
                if questions:
                    question_id = questions[0].get("questionId")
                    answer_data = {
                        "questionId": question_id,
                        "answer": 1,  # Correct answer for first question
                        "action": "submit_answer"
                    }
                    
                    response = self.make_request("PUT", f"test-attempts/{self.attempt_id}", 
                                               answer_data, self.student_token)
                    if response and response.status_code == 200:
                        self.log_result("test_attempts", "Submit Answer", True, 
                                      "Answer submitted successfully")
                    else:
                        self.log_result("test_attempts", "Submit Answer", False, 
                                      f"Failed to submit answer: {response.status_code if response else 'No response'}")
        
        # Test 3: Complete Test
        if self.attempt_id:
            complete_data = {"action": "complete_test"}
            response = self.make_request("PUT", f"test-attempts/{self.attempt_id}", 
                                       complete_data, self.student_token)
            if response and response.status_code == 200:
                data = response.json()
                if "score" in data and "totalQuestions" in data:
                    self.log_result("test_attempts", "Complete Test", True, 
                                  f"Test completed with score: {data['score']}/{data['totalQuestions']}")
                else:
                    self.log_result("test_attempts", "Complete Test", False, 
                                  "Test completed but missing score data")
            else:
                self.log_result("test_attempts", "Complete Test", False, 
                              f"Failed to complete test: {response.status_code if response else 'No response'}")
        
        # Test 4: Get Test Attempt Details
        if self.attempt_id:
            response = self.make_request("GET", f"test-attempts/{self.attempt_id}", token=self.student_token)
            if response and response.status_code == 200:
                attempt_data = response.json()
                if attempt_data.get("attemptId") == self.attempt_id:
                    self.log_result("test_attempts", "Get Attempt Details", True, 
                                  f"Retrieved attempt details, status: {attempt_data.get('status')}")
                else:
                    self.log_result("test_attempts", "Get Attempt Details", False, 
                                  "Retrieved attempt has wrong ID")
            else:
                self.log_result("test_attempts", "Get Attempt Details", False, 
                              f"Failed to get attempt details: {response.status_code if response else 'No response'}")
        
        # Test 5: Get Student's Attempt History
        response = self.make_request("GET", "test-attempts", token=self.student_token)
        if response and response.status_code == 200:
            attempts = response.json()
            if isinstance(attempts, list):
                self.log_result("test_attempts", "Get Attempt History", True, 
                              f"Retrieved {len(attempts)} attempts")
            else:
                self.log_result("test_attempts", "Get Attempt History", False, 
                              "Response is not a list")
        else:
            self.log_result("test_attempts", "Get Attempt History", False, 
                          f"Failed to get attempt history: {response.status_code if response else 'No response'}")
        
        # Test 6: Prevent Duplicate Attempts
        if self.test_series_id:
            duplicate_attempt = {"testSeriesId": self.test_series_id}
            response = self.make_request("POST", "test-attempts", duplicate_attempt, self.student_token)
            if response and response.status_code == 400:
                self.log_result("test_attempts", "Prevent Duplicate Attempts", True, 
                              "Duplicate attempt properly prevented")
            else:
                self.log_result("test_attempts", "Prevent Duplicate Attempts", False, 
                              "Should prevent duplicate attempts")
    
    def test_user_management(self):
        """Test user management endpoints (admin only)"""
        print("\n=== TESTING USER MANAGEMENT ===")
        
        if not self.admin_token:
            self.log_result("user_management", "User Management Tests", False, 
                          "No admin token available")
            return
        
        # Test 1: Get All Users (Admin)
        response = self.make_request("GET", "users", token=self.admin_token)
        if response and response.status_code == 200:
            users = response.json()
            if isinstance(users, list) and len(users) > 0:
                self.log_result("user_management", "Get All Users", True, 
                              f"Retrieved {len(users)} users")
            else:
                self.log_result("user_management", "Get All Users", False, 
                              "No users returned or invalid format")
        else:
            self.log_result("user_management", "Get All Users", False, 
                          f"Failed to get users: {response.status_code if response else 'No response'}")
        
        # Test 2: Create Admin User
        admin_data = {
            "username": f"admin_{uuid.uuid4().hex[:8]}",
            "password": "newadmin123",
            "name": "New Admin User"
        }
        response = self.make_request("POST", "users", admin_data, self.admin_token)
        if response and response.status_code == 200:
            self.log_result("user_management", "Create Admin User", True, 
                          "New admin user created successfully")
        else:
            self.log_result("user_management", "Create Admin User", False, 
                          f"Failed to create admin user: {response.status_code if response else 'No response'}")
        
        # Test 3: Non-admin Access Restriction
        if self.teacher_token:
            response = self.make_request("GET", "users", token=self.teacher_token)
            if response and response.status_code == 403:
                self.log_result("user_management", "Non-admin Access Restriction", True, 
                              "Non-admin properly restricted from user management")
            else:
                self.log_result("user_management", "Non-admin Access Restriction", False, 
                              "Non-admin should be restricted from user management")
    
    def test_analytics(self):
        """Test analytics endpoints"""
        print("\n=== TESTING ANALYTICS ===")
        
        # Test 1: Teacher Analytics
        if self.teacher_token:
            response = self.make_request("GET", "analytics", token=self.teacher_token)
            if response and response.status_code == 200:
                analytics = response.json()
                expected_fields = ["totalTestSeries", "totalAttempts", "averageScore", "testSeriesStats"]
                if all(field in analytics for field in expected_fields):
                    self.log_result("analytics", "Teacher Analytics", True, 
                                  f"Retrieved teacher analytics: {analytics['totalTestSeries']} test series, {analytics['totalAttempts']} attempts")
                else:
                    self.log_result("analytics", "Teacher Analytics", False, 
                                  "Missing required fields in analytics response")
            else:
                self.log_result("analytics", "Teacher Analytics", False, 
                              f"Failed to get teacher analytics: {response.status_code if response else 'No response'}")
        
        # Test 2: Admin Analytics
        if self.admin_token:
            response = self.make_request("GET", "analytics", token=self.admin_token)
            if response and response.status_code == 200:
                analytics = response.json()
                expected_fields = ["totalUsers", "totalTestSeries", "totalAttempts"]
                if all(field in analytics for field in expected_fields):
                    self.log_result("analytics", "Admin Analytics", True, 
                                  f"Retrieved admin analytics: {analytics['totalUsers']} users, {analytics['totalTestSeries']} test series")
                else:
                    self.log_result("analytics", "Admin Analytics", False, 
                                  "Missing required fields in admin analytics response")
            else:
                self.log_result("analytics", "Admin Analytics", False, 
                              f"Failed to get admin analytics: {response.status_code if response else 'No response'}")
        
        # Test 3: Student Analytics Access (should be restricted)
        if self.student_token:
            response = self.make_request("GET", "analytics", token=self.student_token)
            if response and response.status_code == 403:
                self.log_result("analytics", "Student Analytics Restriction", True, 
                              "Student properly restricted from analytics")
            else:
                self.log_result("analytics", "Student Analytics Restriction", False, 
                              "Student should be restricted from analytics")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Backend API Testing...")
        print(f"Base URL: {self.base_url}")
        
        start_time = time.time()
        
        # Run all test suites
        self.test_authentication()
        self.test_test_series_management()
        self.test_test_attempts()
        self.test_user_management()
        self.test_analytics()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "❌"
            print(f"{status_icon} {category.upper()}: {passed} passed, {failed} failed")
            
            # Show failed tests
            if failed > 0:
                for detail in results["details"]:
                    if "❌" in detail["status"]:
                        print(f"   - {detail['test']}: {detail['message']}")
        
        print("-" * 60)
        print(f"🎯 OVERALL: {total_passed} passed, {total_failed} failed")
        print(f"⏱️  Duration: {end_time - start_time:.2f} seconds")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED! Backend API is working correctly.")
        else:
            print(f"⚠️  {total_failed} tests failed. Please review the issues above.")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = TestSeriesAPITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)