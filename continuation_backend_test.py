#!/usr/bin/env python3
"""
Backend API Testing for Test Series App - Continuation Enhancements
Testing the new API enhancements for category navigation, teacher metadata, 
detailed results, and enhanced permissions.
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:3000/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}
TEACHER_CREDENTIALS = {"username": "teacher_jee", "password": "teacher123"}
STUDENT_CREDENTIALS = {"username": "test_student", "password": "student123"}

class APITester:
    def __init__(self):
        self.admin_token = None
        self.teacher_token = None
        self.student_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
    def authenticate_users(self):
        """Authenticate all user types and get tokens"""
        print("\n🔐 AUTHENTICATION TESTS")
        print("=" * 50)
        
        # Admin authentication
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.log_result("Admin Authentication", True, f"Token received for user: {data.get('user', {}).get('username')}")
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Error: {str(e)}")
            return False
            
        # Teacher authentication
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=TEACHER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get('token')
                self.log_result("Teacher Authentication", True, f"Token received for user: {data.get('user', {}).get('username')}")
            else:
                self.log_result("Teacher Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Teacher Authentication", False, f"Error: {str(e)}")
            
        # Create and authenticate student
        try:
            # Try to register a new student
            student_data = {
                "username": "test_student",
                "password": "student123",
                "name": "Test Student",
                "role": "student",
                "email": "student@test.com"
            }
            response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('token')
                self.log_result("Student Registration & Authentication", True, f"Student created and authenticated")
            else:
                # Try to login if already exists
                response = requests.post(f"{BASE_URL}/auth/login", json=STUDENT_CREDENTIALS)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data.get('token')
                    self.log_result("Student Authentication", True, f"Existing student authenticated")
                else:
                    self.log_result("Student Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Student Authentication", False, f"Error: {str(e)}")
            
        return self.admin_token and self.teacher_token and self.student_token
        
    def test_categories_with_teachers(self):
        """Test GET /api/categories?withTeachers=true"""
        print("\n📚 CATEGORY API WITH TEACHERS TESTS")
        print("=" * 50)
        
        try:
            # Test categories with teachers aggregation
            response = requests.get(f"{BASE_URL}/categories?withTeachers=true")
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list) and len(categories) > 0:
                    # Check if categories have teachers
                    has_teachers = any('teachers' in cat for cat in categories)
                    if has_teachers:
                        # Check teacher metadata structure
                        sample_category = next((cat for cat in categories if 'teachers' in cat and len(cat['teachers']) > 0), None)
                        if sample_category:
                            teacher = sample_category['teachers'][0]
                            required_fields = ['userId', 'name', 'photo', 'rating', 'experience']
                            has_all_fields = all(field in teacher for field in required_fields)
                            self.log_result("Categories with Teachers API", True, 
                                          f"Found {len(categories)} categories with teacher aggregation")
                            self.log_result("Teacher Metadata Structure", has_all_fields, 
                                          f"Teacher fields: {list(teacher.keys())}")
                        else:
                            self.log_result("Categories with Teachers API", False, "No teachers found in categories")
                    else:
                        self.log_result("Categories with Teachers API", False, "Teachers field missing in response")
                else:
                    self.log_result("Categories with Teachers API", False, "No categories returned")
            else:
                self.log_result("Categories with Teachers API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Categories with Teachers API", False, f"Error: {str(e)}")
            
        # Test regular categories endpoint
        try:
            response = requests.get(f"{BASE_URL}/categories")
            if response.status_code == 200:
                categories = response.json()
                self.log_result("Regular Categories API", True, f"Found {len(categories)} categories")
            else:
                self.log_result("Regular Categories API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Regular Categories API", False, f"Error: {str(e)}")
            
    def test_enhanced_test_series_api(self):
        """Test enhanced test series API with filtering and metadata"""
        print("\n📝 ENHANCED TEST SERIES API TESTS")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Test student sees ALL published test series
            response = requests.get(f"{BASE_URL}/test-series", headers=headers)
            if response.status_code == 200:
                test_series = response.json()
                if isinstance(test_series, list):
                    self.log_result("Student All Test Series Access", True, 
                                  f"Student can see {len(test_series)} test series")
                    
                    # Check for enhanced metadata
                    if len(test_series) > 0:
                        test = test_series[0]
                        metadata_fields = ['createdByName', 'createdByPhoto', 'createdByRating', 
                                         'createdByExperience', 'totalAttempts', 'averageScore', 'averagePercentage']
                        has_metadata = all(field in test for field in metadata_fields)
                        self.log_result("Enhanced Test Metadata", has_metadata, 
                                      f"Metadata fields present: {[f for f in metadata_fields if f in test]}")
                else:
                    self.log_result("Student All Test Series Access", False, "Invalid response format")
            else:
                self.log_result("Student All Test Series Access", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Student All Test Series Access", False, f"Error: {str(e)}")
            
        # Test category filtering
        try:
            response = requests.get(f"{BASE_URL}/test-series?category=JEE-Mains", headers=headers)
            if response.status_code == 200:
                filtered_tests = response.json()
                self.log_result("Category Filtering", True, 
                              f"Category filter returned {len(filtered_tests)} tests")
            else:
                self.log_result("Category Filtering", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Category Filtering", False, f"Error: {str(e)}")
            
        # Test teacher filtering
        try:
            # Get a teacher ID first
            teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.get(f"{BASE_URL}/test-series", headers=teacher_headers)
            if response.status_code == 200:
                teacher_tests = response.json()
                if len(teacher_tests) > 0:
                    teacher_id = teacher_tests[0]['createdBy']
                    # Test filtering by teacher
                    response = requests.get(f"{BASE_URL}/test-series?teacher={teacher_id}", headers=headers)
                    if response.status_code == 200:
                        teacher_filtered = response.json()
                        self.log_result("Teacher Filtering", True, 
                                      f"Teacher filter returned {len(teacher_filtered)} tests")
                    else:
                        self.log_result("Teacher Filtering", False, f"Status: {response.status_code}")
                else:
                    self.log_result("Teacher Filtering", False, "No teacher tests found for filtering test")
        except Exception as e:
            self.log_result("Teacher Filtering", False, f"Error: {str(e)}")
            
        # Test teacher preview functionality
        try:
            teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.get(f"{BASE_URL}/test-series?preview=true", headers=teacher_headers)
            if response.status_code == 200:
                preview_tests = response.json()
                self.log_result("Teacher Preview Functionality", True, 
                              f"Preview mode returned {len(preview_tests)} tests")
            else:
                self.log_result("Teacher Preview Functionality", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Teacher Preview Functionality", False, f"Error: {str(e)}")
            
    def test_detailed_results_storage(self):
        """Test detailed results storage with explanations"""
        print("\n📊 DETAILED RESULTS STORAGE TESTS")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Get available test series
            response = requests.get(f"{BASE_URL}/test-series", headers=headers)
            if response.status_code != 200:
                self.log_result("Get Test Series for Results Test", False, f"Status: {response.status_code}")
                return
                
            test_series = response.json()
            if len(test_series) == 0:
                self.log_result("Get Test Series for Results Test", False, "No test series available")
                return
                
            test_id = test_series[0]['testSeriesId']
            
            # Start a test attempt
            response = requests.post(f"{BASE_URL}/test-attempts", 
                                   json={"testSeriesId": test_id}, headers=headers)
            if response.status_code == 200:
                attempt_data = response.json()
                attempt_id = attempt_data.get('attemptId')
                self.log_result("Start Test Attempt", True, f"Attempt ID: {attempt_id}")
                
                # Submit some answers
                questions = test_series[0].get('questions', [])
                if len(questions) > 0:
                    question_id = questions[0]['questionId']
                    # Submit an answer
                    response = requests.put(f"{BASE_URL}/test-attempts/{attempt_id}",
                                          json={"questionId": question_id, "answer": 0, "action": "submit_answer"},
                                          headers=headers)
                    if response.status_code == 200:
                        self.log_result("Submit Answer", True, "Answer submitted successfully")
                        
                        # Complete the test
                        response = requests.put(f"{BASE_URL}/test-attempts/{attempt_id}",
                                              json={"action": "complete_test"}, headers=headers)
                        if response.status_code == 200:
                            result_data = response.json()
                            # Check for detailed results
                            if 'detailedResults' in result_data:
                                detailed_results = result_data['detailedResults']
                                if len(detailed_results) > 0:
                                    result = detailed_results[0]
                                    required_fields = ['questionId', 'question', 'options', 'studentAnswer', 
                                                     'correctAnswer', 'isCorrect', 'explanation']
                                    has_all_fields = all(field in result for field in required_fields)
                                    self.log_result("Detailed Results Structure", has_all_fields,
                                                  f"Fields present: {list(result.keys())}")
                                    self.log_result("Complete Test with Detailed Results", True,
                                                  f"Score: {result_data.get('score')}/{result_data.get('totalQuestions')}")
                                else:
                                    self.log_result("Detailed Results Structure", False, "No detailed results found")
                            else:
                                self.log_result("Detailed Results Structure", False, "detailedResults field missing")
                        else:
                            self.log_result("Complete Test", False, f"Status: {response.status_code}")
                    else:
                        self.log_result("Submit Answer", False, f"Status: {response.status_code}")
                else:
                    self.log_result("Test Questions Available", False, "No questions found in test series")
            else:
                self.log_result("Start Test Attempt", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Detailed Results Storage Test", False, f"Error: {str(e)}")
            
    def test_teacher_results_privacy(self):
        """Test that teachers only see student names, not email/phone"""
        print("\n🔒 TEACHER RESULTS PRIVACY TESTS")
        print("=" * 50)
        
        teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get test attempts as teacher
            response = requests.get(f"{BASE_URL}/test-attempts", headers=teacher_headers)
            if response.status_code == 200:
                teacher_attempts = response.json()
                if len(teacher_attempts) > 0:
                    attempt = teacher_attempts[0]
                    if 'studentDetails' in attempt:
                        student_details = attempt['studentDetails']
                        # Teacher should only see name
                        has_name = 'name' in student_details
                        has_email = 'email' in student_details
                        has_phone = 'phone' in student_details
                        
                        privacy_correct = has_name and not has_email and not has_phone
                        self.log_result("Teacher Privacy - Student Name Only", privacy_correct,
                                      f"Fields visible to teacher: {list(student_details.keys())}")
                    else:
                        self.log_result("Teacher Results Access", False, "No student details found")
                else:
                    self.log_result("Teacher Results Access", True, "No attempts found (expected for new test)")
            else:
                self.log_result("Teacher Results Access", False, f"Status: {response.status_code}")
                
            # Get test attempts as admin
            response = requests.get(f"{BASE_URL}/test-attempts", headers=admin_headers)
            if response.status_code == 200:
                admin_attempts = response.json()
                if len(admin_attempts) > 0:
                    attempt = admin_attempts[0]
                    if 'studentDetails' in attempt:
                        student_details = attempt['studentDetails']
                        # Admin should see full details
                        has_name = 'name' in student_details
                        has_email = 'email' in student_details
                        has_phone = 'phone' in student_details
                        
                        admin_access_correct = has_name and has_email and has_phone
                        self.log_result("Admin Full Access - All Student Details", admin_access_correct,
                                      f"Fields visible to admin: {list(student_details.keys())}")
                    else:
                        self.log_result("Admin Results Access", False, "No student details found")
                else:
                    self.log_result("Admin Results Access", True, "No attempts found")
            else:
                self.log_result("Admin Results Access", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Teacher Results Privacy Test", False, f"Error: {str(e)}")
            
    def test_edit_delete_permissions(self):
        """Test teacher edit/delete permissions for their own test series"""
        print("\n✏️ EDIT/DELETE PERMISSIONS TESTS")
        print("=" * 50)
        
        teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            # Create a test series as teacher
            test_data = {
                "title": "Test Edit/Delete Permissions",
                "description": "Test series for permission testing",
                "category": "JEE-Mains",
                "duration": 60,
                "questions": [{
                    "questionId": "test-q1",
                    "question": "Test question?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": 0,
                    "explanation": "Test explanation"
                }]
            }
            
            response = requests.post(f"{BASE_URL}/test-series", json=test_data, headers=teacher_headers)
            if response.status_code == 200:
                created_test = response.json()
                test_id = created_test['testSeriesId']
                self.log_result("Teacher Create Test Series", True, f"Created test: {test_id}")
                
                # Test teacher can edit their own test
                update_data = {"title": "Updated Test Title", "description": "Updated description"}
                response = requests.put(f"{BASE_URL}/test-series/{test_id}", 
                                      json=update_data, headers=teacher_headers)
                if response.status_code == 200:
                    self.log_result("Teacher Edit Own Test", True, "Successfully updated test series")
                else:
                    self.log_result("Teacher Edit Own Test", False, f"Status: {response.status_code}")
                
                # Test teacher can delete their own test
                response = requests.delete(f"{BASE_URL}/test-series/{test_id}", headers=teacher_headers)
                if response.status_code == 200:
                    self.log_result("Teacher Delete Own Test", True, "Successfully deleted test series")
                else:
                    self.log_result("Teacher Delete Own Test", False, f"Status: {response.status_code}")
                    
            else:
                self.log_result("Teacher Create Test Series", False, f"Status: {response.status_code}")
                
            # Test teacher cannot edit/delete other teacher's tests
            # Get all test series and find one not created by current teacher
            response = requests.get(f"{BASE_URL}/test-series", headers=teacher_headers)
            if response.status_code == 200:
                all_tests = response.json()
                # Find a test not created by current teacher
                other_test = None
                for test in all_tests:
                    # Get teacher profile to compare
                    profile_response = requests.get(f"{BASE_URL}/auth/profile", headers=teacher_headers)
                    if profile_response.status_code == 200:
                        teacher_profile = profile_response.json()
                        if test['createdBy'] != teacher_profile['userId']:
                            other_test = test
                            break
                
                if other_test:
                    # Try to edit other teacher's test
                    response = requests.put(f"{BASE_URL}/test-series/{other_test['testSeriesId']}", 
                                          json={"title": "Unauthorized Edit"}, headers=teacher_headers)
                    if response.status_code == 404:  # Should be unauthorized
                        self.log_result("Teacher Cannot Edit Others' Tests", True, "Correctly blocked unauthorized edit")
                    else:
                        self.log_result("Teacher Cannot Edit Others' Tests", False, 
                                      f"Should be blocked but got status: {response.status_code}")
                        
                    # Try to delete other teacher's test
                    response = requests.delete(f"{BASE_URL}/test-series/{other_test['testSeriesId']}", 
                                             headers=teacher_headers)
                    if response.status_code == 404:  # Should be unauthorized
                        self.log_result("Teacher Cannot Delete Others' Tests", True, "Correctly blocked unauthorized delete")
                    else:
                        self.log_result("Teacher Cannot Delete Others' Tests", False, 
                                      f"Should be blocked but got status: {response.status_code}")
                else:
                    self.log_result("Find Other Teacher's Test", False, "No other teacher's tests found for permission test")
                    
        except Exception as e:
            self.log_result("Edit/Delete Permissions Test", False, f"Error: {str(e)}")
            
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 STARTING BACKEND API ENHANCEMENT TESTS")
        print("=" * 60)
        
        # Authenticate users first
        if not self.authenticate_users():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
            
        # Run all test suites
        self.test_categories_with_teachers()
        self.test_enhanced_test_series_api()
        self.test_detailed_results_storage()
        self.test_teacher_results_privacy()
        self.test_edit_delete_permissions()
        
        # Summary
        print("\n📋 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
                    
        return failed_tests == 0

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)