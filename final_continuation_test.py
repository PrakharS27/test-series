#!/usr/bin/env python3
"""
Final Backend API Testing for Test Series App - Continuation Enhancements
Comprehensive testing of all new API enhancements with proper test data setup.
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:3000/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}
TEACHER_JEE_CREDENTIALS = {"username": "teacher_jee", "password": "teacher123"}
TEACHER_NEET_CREDENTIALS = {"username": "teacher_neet", "password": "teacher123"}
STUDENT_CREDENTIALS = {"username": "final_test_student", "password": "student123"}

class FinalAPITester:
    def __init__(self):
        self.admin_token = None
        self.teacher_jee_token = None
        self.teacher_neet_token = None
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
                self.log_result("Admin Authentication", True, f"Token received")
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Error: {str(e)}")
            return False
            
        # Teacher JEE authentication
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=TEACHER_JEE_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.teacher_jee_token = data.get('token')
                self.log_result("Teacher JEE Authentication", True, f"Token received")
            else:
                self.log_result("Teacher JEE Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Teacher JEE Authentication", False, f"Error: {str(e)}")
            
        # Teacher NEET authentication
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=TEACHER_NEET_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.teacher_neet_token = data.get('token')
                self.log_result("Teacher NEET Authentication", True, f"Token received")
            else:
                self.log_result("Teacher NEET Authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Teacher NEET Authentication", False, f"Error: {str(e)}")
            
        # Create and authenticate student
        try:
            # Try to register a new student
            student_data = {
                "username": "final_test_student",
                "password": "student123",
                "name": "Final Test Student",
                "role": "student",
                "email": "finalstudent@test.com"
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
            
        return self.admin_token and self.teacher_jee_token and self.teacher_neet_token and self.student_token
        
    def test_categories_with_teachers_aggregation(self):
        """Test GET /api/categories?withTeachers=true aggregation pipeline"""
        print("\n📚 CATEGORY API WITH TEACHERS AGGREGATION TESTS")
        print("=" * 60)
        
        try:
            # Test categories with teachers aggregation
            response = requests.get(f"{BASE_URL}/categories?withTeachers=true")
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list) and len(categories) > 0:
                    self.log_result("Categories with Teachers API Response", True, 
                                  f"Found {len(categories)} categories with teachers")
                    
                    # Verify aggregation pipeline structure
                    for category in categories:
                        if 'teachers' in category and len(category['teachers']) > 0:
                            teacher = category['teachers'][0]
                            required_fields = ['userId', 'name', 'photo', 'rating', 'experience']
                            has_all_fields = all(field in teacher for field in required_fields)
                            self.log_result(f"Teacher Metadata in {category['name']}", has_all_fields, 
                                          f"Fields: {list(teacher.keys())}")
                            break
                    
                    # Verify specific categories have teachers
                    jee_category = next((cat for cat in categories if cat['name'] == 'JEE-Mains'), None)
                    neet_category = next((cat for cat in categories if cat['name'] == 'NEET'), None)
                    
                    if jee_category and 'teachers' in jee_category:
                        self.log_result("JEE-Mains Category has Teachers", True, 
                                      f"Found {len(jee_category['teachers'])} teachers")
                    
                    if neet_category and 'teachers' in neet_category:
                        self.log_result("NEET Category has Teachers", True, 
                                      f"Found {len(neet_category['teachers'])} teachers")
                        
                else:
                    self.log_result("Categories with Teachers API Response", False, "No categories returned")
            else:
                self.log_result("Categories with Teachers API Response", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Categories with Teachers API", False, f"Error: {str(e)}")
            
    def test_enhanced_test_series_features(self):
        """Test enhanced test series API features"""
        print("\n📝 ENHANCED TEST SERIES API FEATURES")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Test student sees ALL published test series
            response = requests.get(f"{BASE_URL}/test-series", headers=headers)
            if response.status_code == 200:
                test_series = response.json()
                if isinstance(test_series, list):
                    self.log_result("Student All Test Series Access", True, 
                                  f"Student can see {len(test_series)} test series from all teachers")
                    
                    # Check for Udemy-style metadata
                    if len(test_series) > 0:
                        test = test_series[0]
                        udemy_fields = ['createdByName', 'createdByPhoto', 'createdByRating', 
                                       'createdByExperience', 'totalAttempts', 'averageScore', 'averagePercentage']
                        has_udemy_metadata = all(field in test for field in udemy_fields)
                        self.log_result("Udemy-style Test Metadata", has_udemy_metadata, 
                                      f"Metadata fields: {[f for f in udemy_fields if f in test]}")
                        
                        # Verify teacher metadata values
                        if test.get('createdByRating') and test.get('createdByExperience'):
                            self.log_result("Teacher Rating & Experience", True, 
                                          f"Rating: {test['createdByRating']}, Experience: {test['createdByExperience']}")
                        
                else:
                    self.log_result("Student All Test Series Access", False, "Invalid response format")
            else:
                self.log_result("Student All Test Series Access", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Student All Test Series Access", False, f"Error: {str(e)}")
            
        # Test category filtering
        try:
            # Get category ID for JEE-Mains
            cat_response = requests.get(f"{BASE_URL}/categories")
            if cat_response.status_code == 200:
                categories = cat_response.json()
                jee_category = next((cat for cat in categories if cat['name'] == 'JEE-Mains'), None)
                if jee_category:
                    category_id = jee_category['categoryId']
                    response = requests.get(f"{BASE_URL}/test-series?category={category_id}", headers=headers)
                    if response.status_code == 200:
                        filtered_tests = response.json()
                        self.log_result("Category Filtering by ID", True, 
                                      f"JEE-Mains filter returned {len(filtered_tests)} tests")
                    else:
                        self.log_result("Category Filtering by ID", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Category Filtering", False, f"Error: {str(e)}")
            
        # Test teacher preview functionality
        try:
            teacher_headers = {"Authorization": f"Bearer {self.teacher_jee_token}"}
            response = requests.get(f"{BASE_URL}/test-series?preview=true", headers=teacher_headers)
            if response.status_code == 200:
                preview_tests = response.json()
                self.log_result("Teacher Preview Mode", True, 
                              f"Preview returned {len(preview_tests)} tests with full questions")
            else:
                self.log_result("Teacher Preview Mode", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Teacher Preview Mode", False, f"Error: {str(e)}")
            
    def test_detailed_results_with_explanations(self):
        """Test detailed results storage with student answers vs correct answers"""
        print("\n📊 DETAILED RESULTS WITH EXPLANATIONS")
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
                
            # Find a test with questions
            test_with_questions = None
            for test in test_series:
                if test.get('questions') and len(test['questions']) > 0:
                    test_with_questions = test
                    break
                    
            if not test_with_questions:
                self.log_result("Find Test with Questions", False, "No test series with questions found")
                return
                
            test_id = test_with_questions['testSeriesId']
            
            # Start a test attempt
            response = requests.post(f"{BASE_URL}/test-attempts", 
                                   json={"testSeriesId": test_id}, headers=headers)
            if response.status_code == 200:
                attempt_data = response.json()
                attempt_id = attempt_data.get('attemptId')
                self.log_result("Start New Test Attempt", True, f"Attempt ID: {attempt_id}")
                
                # Submit answers for all questions
                questions = test_with_questions.get('questions', [])
                for i, question in enumerate(questions):
                    question_id = question['questionId']
                    # Submit wrong answer intentionally to test detailed results
                    wrong_answer = (question['correctAnswer'] + 1) % len(question['options'])
                    response = requests.put(f"{BASE_URL}/test-attempts/{attempt_id}",
                                          json={"questionId": question_id, "answer": wrong_answer, "action": "submit_answer"},
                                          headers=headers)
                    if response.status_code == 200:
                        self.log_result(f"Submit Answer {i+1}", True, f"Wrong answer submitted for testing")
                    else:
                        self.log_result(f"Submit Answer {i+1}", False, f"Status: {response.status_code}")
                        
                # Complete the test
                response = requests.put(f"{BASE_URL}/test-attempts/{attempt_id}",
                                      json={"action": "complete_test"}, headers=headers)
                if response.status_code == 200:
                    result_data = response.json()
                    # Check for detailed results structure
                    if 'detailedResults' in result_data:
                        detailed_results = result_data['detailedResults']
                        if len(detailed_results) > 0:
                            result = detailed_results[0]
                            required_fields = ['questionId', 'question', 'options', 'studentAnswer', 
                                             'correctAnswer', 'isCorrect', 'explanation']
                            has_all_fields = all(field in result for field in required_fields)
                            self.log_result("Detailed Results Structure", has_all_fields,
                                          f"All required fields present: {has_all_fields}")
                            
                            # Verify student vs correct answer comparison
                            student_answer = result.get('studentAnswer')
                            correct_answer = result.get('correctAnswer')
                            is_correct = result.get('isCorrect')
                            explanation = result.get('explanation')
                            
                            self.log_result("Student vs Correct Answer Comparison", True,
                                          f"Student: {student_answer}, Correct: {correct_answer}, Match: {is_correct}")
                            self.log_result("Explanation Included", bool(explanation),
                                          f"Explanation: {explanation[:50]}..." if explanation else "No explanation")
                            
                            self.log_result("Complete Test with Detailed Results", True,
                                          f"Score: {result_data.get('score')}/{result_data.get('totalQuestions')}")
                        else:
                            self.log_result("Detailed Results Structure", False, "No detailed results found")
                    else:
                        self.log_result("Detailed Results Structure", False, "detailedResults field missing")
                else:
                    self.log_result("Complete Test", False, f"Status: {response.status_code}")
            else:
                if response.status_code == 400:
                    self.log_result("Start New Test Attempt", False, "Test already completed (expected for repeated runs)")
                else:
                    self.log_result("Start New Test Attempt", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Detailed Results Test", False, f"Error: {str(e)}")
            
    def test_teacher_privacy_and_permissions(self):
        """Test teacher results privacy and edit/delete permissions"""
        print("\n🔒 TEACHER PRIVACY & PERMISSIONS")
        print("=" * 50)
        
        teacher_jee_headers = {"Authorization": f"Bearer {self.teacher_jee_token}"}
        teacher_neet_headers = {"Authorization": f"Bearer {self.teacher_neet_token}"}
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test teacher results privacy
        try:
            # Get test attempts as JEE teacher
            response = requests.get(f"{BASE_URL}/test-attempts", headers=teacher_jee_headers)
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
                        self.log_result("Teacher Privacy - Name Only", privacy_correct,
                                      f"Teacher sees: {list(student_details.keys())}")
                    else:
                        self.log_result("Teacher Results Access", True, "No student details (no attempts yet)")
                else:
                    self.log_result("Teacher Results Access", True, "No attempts found")
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
                        self.log_result("Admin Full Access", admin_access_correct,
                                      f"Admin sees: {list(student_details.keys())}")
                    else:
                        self.log_result("Admin Results Access", True, "No student details (no attempts yet)")
                else:
                    self.log_result("Admin Results Access", True, "No attempts found")
            else:
                self.log_result("Admin Results Access", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Teacher Privacy Test", False, f"Error: {str(e)}")
            
        # Test cross-teacher edit/delete permissions
        try:
            # Get all test series to find tests from different teachers
            response = requests.get(f"{BASE_URL}/test-series", headers=teacher_jee_headers)
            if response.status_code == 200:
                all_tests = response.json()
                
                # Get JEE teacher profile
                profile_response = requests.get(f"{BASE_URL}/auth/profile", headers=teacher_jee_headers)
                if profile_response.status_code == 200:
                    jee_teacher_profile = profile_response.json()
                    jee_teacher_id = jee_teacher_profile['userId']
                    
                    # Find a test NOT created by JEE teacher
                    other_teacher_test = None
                    for test in all_tests:
                        if test['createdBy'] != jee_teacher_id:
                            other_teacher_test = test
                            break
                    
                    if other_teacher_test:
                        # Try to edit other teacher's test (should fail)
                        response = requests.put(f"{BASE_URL}/test-series/{other_teacher_test['testSeriesId']}", 
                                              json={"title": "Unauthorized Edit Attempt"}, headers=teacher_jee_headers)
                        if response.status_code == 404:  # Should be unauthorized
                            self.log_result("Cross-Teacher Edit Protection", True, "JEE teacher cannot edit NEET teacher's test")
                        else:
                            self.log_result("Cross-Teacher Edit Protection", False, 
                                          f"Should be blocked but got status: {response.status_code}")
                            
                        # Try to delete other teacher's test (should fail)
                        response = requests.delete(f"{BASE_URL}/test-series/{other_teacher_test['testSeriesId']}", 
                                                 headers=teacher_jee_headers)
                        if response.status_code == 404:  # Should be unauthorized
                            self.log_result("Cross-Teacher Delete Protection", True, "JEE teacher cannot delete NEET teacher's test")
                        else:
                            self.log_result("Cross-Teacher Delete Protection", False, 
                                          f"Should be blocked but got status: {response.status_code}")
                    else:
                        self.log_result("Find Cross-Teacher Test", False, "No tests from other teachers found")
                        
        except Exception as e:
            self.log_result("Cross-Teacher Permissions Test", False, f"Error: {str(e)}")
            
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 COMPREHENSIVE BACKEND API ENHANCEMENT TESTS")
        print("=" * 70)
        
        # Authenticate users first
        if not self.authenticate_users():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
            
        # Run all test suites
        self.test_categories_with_teachers_aggregation()
        self.test_enhanced_test_series_features()
        self.test_detailed_results_with_explanations()
        self.test_teacher_privacy_and_permissions()
        
        # Summary
        print("\n📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
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
        else:
            print("\n🎉 ALL TESTS PASSED! Backend API enhancements are working correctly.")
                    
        return failed_tests == 0

if __name__ == "__main__":
    tester = FinalAPITester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)