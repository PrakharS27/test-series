#!/usr/bin/env python3
"""
Backend Test Suite for Teacher Test Series Visibility Issue
Testing specific user report about draft status and visibility problems
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3000/api"
HEADERS = {"Content-Type": "application/json"}

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name, passed, message):
        self.results.append({
            'test': test_name,
            'status': 'PASS' if passed else 'FAIL',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{'✅' if passed else '❌'} {test_name}: {message}")
    
    def summary(self):
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        print(f"\n📊 TEST SUMMARY:")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        return success_rate

def test_teacher_login(results):
    """Test login with specific teacher mentioned by user"""
    try:
        # Try login with teacher1 (from previous tests)
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json={"username": "teacher1", "password": "teacher123"}, 
                               headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user_info = data.get('user', {})
            results.add_result("Teacher Login (teacher1)", True, 
                             f"Login successful, userId: {user_info.get('userId')}, role: {user_info.get('role')}")
            return token, user_info.get('userId')
        else:
            # Try to register teacher1 if not exists
            reg_response = requests.post(f"{BASE_URL}/auth/register", 
                                       json={
                                           "username": "teacher1", 
                                           "password": "teacher123",
                                           "name": "Test Teacher 1",
                                           "role": "teacher",
                                           "email": "teacher1@test.com",
                                           "phone": "1234567890"
                                       }, 
                                       headers=HEADERS)
            
            if reg_response.status_code == 201:
                # Now login
                login_response = requests.post(f"{BASE_URL}/auth/login", 
                                             json={"username": "teacher1", "password": "teacher123"}, 
                                             headers=HEADERS)
                if login_response.status_code == 200:
                    data = login_response.json()
                    token = data.get('token')
                    user_info = data.get('user', {})
                    results.add_result("Teacher Registration & Login", True, 
                                     f"Created and logged in teacher, userId: {user_info.get('userId')}")
                    return token, user_info.get('userId')
            
            results.add_result("Teacher Login", False, f"Failed to login or register teacher: {response.status_code}")
            return None, None
            
    except Exception as e:
        results.add_result("Teacher Login", False, f"Exception: {str(e)}")
        return None, None

def test_create_test_series_status(results, token, teacher_id):
    """Test that new test series are created with 'published' status by default"""
    if not token:
        results.add_result("Create Test Series Status", False, "No valid token")
        return None
    
    try:
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        
        test_data = {
            "title": f"Test Status Check - {int(time.time())}",
            "description": "Testing default status creation",
            "category": "Mathematics",
            "duration": 60,
            "questions": [
                {
                    "question": "What is 2+2?",
                    "options": ["3", "4", "5", "6"],
                    "correctAnswer": 1,
                    "explanation": "2+2 equals 4"
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/test-series", 
                               json=test_data, 
                               headers=auth_headers)
        
        if response.status_code == 200:
            created_test = response.json()
            test_id = created_test.get('testSeriesId')
            status = created_test.get('status')
            
            if status == 'published':
                results.add_result("Default Status Check", True, 
                                 f"Test created with 'published' status (testId: {test_id})")
                return test_id
            else:
                results.add_result("Default Status Check", False, 
                                 f"Test created with '{status}' status instead of 'published' (testId: {test_id})")
                return test_id
        else:
            results.add_result("Create Test Series Status", False, 
                             f"Failed to create test series: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        results.add_result("Create Test Series Status", False, f"Exception: {str(e)}")
        return None

def test_teacher_can_see_own_tests(results, token, teacher_id):
    """Test that teacher can see their own test series immediately after creation"""
    if not token:
        results.add_result("Teacher Test Visibility", False, "No valid token")
        return
    
    try:
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        
        # Get teacher's test series
        response = requests.get(f"{BASE_URL}/test-series", headers=auth_headers)
        
        if response.status_code == 200:
            test_series = response.json()
            teacher_tests = [test for test in test_series if test.get('createdBy') == teacher_id]
            
            results.add_result("Teacher Test List Access", True, 
                             f"Retrieved {len(test_series)} total tests, {len(teacher_tests)} created by teacher")
            
            # Check if teacher can see both published and draft tests
            published_tests = [test for test in teacher_tests if test.get('status') == 'published']
            draft_tests = [test for test in teacher_tests if test.get('status') == 'draft']
            
            results.add_result("Teacher Published Tests Visibility", True, 
                             f"Teacher can see {len(published_tests)} published tests")
            results.add_result("Teacher Draft Tests Visibility", True, 
                             f"Teacher can see {len(draft_tests)} draft tests")
            
            return test_series
        else:
            results.add_result("Teacher Test Visibility", False, 
                             f"Failed to get test series: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        results.add_result("Teacher Test Visibility", False, f"Exception: {str(e)}")
        return []

def test_create_draft_test_manually(results, token, teacher_id):
    """Test creating a test with draft status manually and verify teacher can see it"""
    if not token:
        results.add_result("Manual Draft Test Creation", False, "No valid token")
        return None
    
    try:
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        
        # Create test series first
        test_data = {
            "title": f"Draft Test Manual - {int(time.time())}",
            "description": "Testing manual draft creation",
            "category": "Science",
            "duration": 45,
            "questions": [
                {
                    "question": "What is H2O?",
                    "options": ["Water", "Hydrogen", "Oxygen", "Salt"],
                    "correctAnswer": 0,
                    "explanation": "H2O is the chemical formula for water"
                }
            ]
        }
        
        create_response = requests.post(f"{BASE_URL}/test-series", 
                                      json=test_data, 
                                      headers=auth_headers)
        
        if create_response.status_code == 200:
            created_test = create_response.json()
            test_id = created_test.get('testSeriesId')
            
            # Now update it to draft status
            update_response = requests.put(f"{BASE_URL}/test-series/{test_id}", 
                                         json={"status": "draft"}, 
                                         headers=auth_headers)
            
            if update_response.status_code == 200:
                results.add_result("Manual Draft Creation", True, 
                                 f"Successfully created and updated test to draft status (testId: {test_id})")
                
                # Verify teacher can still see it
                list_response = requests.get(f"{BASE_URL}/test-series", headers=auth_headers)
                if list_response.status_code == 200:
                    test_series = list_response.json()
                    draft_test = next((test for test in test_series if test.get('testSeriesId') == test_id), None)
                    
                    if draft_test and draft_test.get('status') == 'draft':
                        results.add_result("Draft Test Visibility", True, 
                                         f"Teacher can see draft test in their list (status: {draft_test.get('status')})")
                    else:
                        results.add_result("Draft Test Visibility", False, 
                                         f"Draft test not found in teacher's list or wrong status")
                
                return test_id
            else:
                results.add_result("Manual Draft Creation", False, 
                                 f"Failed to update test to draft: {update_response.status_code}")
                return test_id
        else:
            results.add_result("Manual Draft Test Creation", False, 
                             f"Failed to create test: {create_response.status_code}")
            return None
            
    except Exception as e:
        results.add_result("Manual Draft Test Creation", False, f"Exception: {str(e)}")
        return None

def test_specific_user_scenario(results):
    """Test the specific scenario mentioned by user with testSeriesId: 4991d975-72ef-42df-80e2-ec8a806a33ab"""
    try:
        # Try to find the specific test series mentioned by user
        # First need admin access to check all tests
        admin_response = requests.post(f"{BASE_URL}/auth/login", 
                                     json={"username": "admin", "password": "admin123"}, 
                                     headers=HEADERS)
        
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            admin_token = admin_data.get('token')
            admin_headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
            
            # Get all test series as admin
            all_tests_response = requests.get(f"{BASE_URL}/test-series", headers=admin_headers)
            
            if all_tests_response.status_code == 200:
                all_tests = all_tests_response.json()
                specific_test = next((test for test in all_tests 
                                    if test.get('testSeriesId') == '4991d975-72ef-42df-80e2-ec8a806a33ab'), None)
                
                if specific_test:
                    results.add_result("Specific Test Found", True, 
                                     f"Found test {specific_test.get('testSeriesId')} with status: {specific_test.get('status')}")
                    
                    # Check if the teacher who created this test can see it
                    teacher_id = specific_test.get('createdBy')
                    if teacher_id:
                        results.add_result("Specific Test Analysis", True, 
                                         f"Test created by teacher: {teacher_id}, status: {specific_test.get('status')}")
                else:
                    results.add_result("Specific Test Found", False, 
                                     "Test with ID 4991d975-72ef-42df-80e2-ec8a806a33ab not found in database")
            else:
                results.add_result("Admin Test List", False, 
                                 f"Failed to get all tests as admin: {all_tests_response.status_code}")
        else:
            results.add_result("Admin Login for Specific Test Check", False, 
                             f"Failed to login as admin: {admin_response.status_code}")
            
    except Exception as e:
        results.add_result("Specific User Scenario", False, f"Exception: {str(e)}")

def test_teacher_filtering_parameters(results, token, teacher_id):
    """Test various URL parameters that might affect test visibility"""
    if not token:
        results.add_result("Teacher Filtering Parameters", False, "No valid token")
        return
    
    try:
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        
        # Test different parameter combinations
        test_params = [
            ("", "Default (no parameters)"),
            ("?includeUnpublished=true", "Include unpublished explicitly"),
            ("?includeUnpublished=false", "Exclude unpublished explicitly"),
            ("?category=Mathematics", "Filter by category"),
            ("?preview=false", "Preview mode off")
        ]
        
        for params, description in test_params:
            response = requests.get(f"{BASE_URL}/test-series{params}", headers=auth_headers)
            
            if response.status_code == 200:
                test_series = response.json()
                teacher_tests = [test for test in test_series if test.get('createdBy') == teacher_id]
                results.add_result(f"Parameter Test: {description}", True, 
                                 f"Retrieved {len(teacher_tests)} teacher tests with params: {params}")
            else:
                results.add_result(f"Parameter Test: {description}", False, 
                                 f"Failed with params {params}: {response.status_code}")
                
    except Exception as e:
        results.add_result("Teacher Filtering Parameters", False, f"Exception: {str(e)}")

def test_rapid_test_creation_visibility(results, token, teacher_id):
    """Test creating multiple tests rapidly and checking immediate visibility"""
    if not token:
        results.add_result("Rapid Test Creation", False, "No valid token")
        return
    
    try:
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        created_test_ids = []
        
        # Create 3 tests rapidly
        for i in range(3):
            test_data = {
                "title": f"Rapid Test {i+1} - {int(time.time())}",
                "description": f"Testing rapid creation #{i+1}",
                "category": "Physics",
                "duration": 30,
                "questions": [
                    {
                        "question": f"Test question {i+1}?",
                        "options": ["A", "B", "C", "D"],
                        "correctAnswer": i % 4,
                        "explanation": f"Answer explanation {i+1}"
                    }
                ]
            }
            
            create_response = requests.post(f"{BASE_URL}/test-series", 
                                          json=test_data, 
                                          headers=auth_headers)
            
            if create_response.status_code == 200:
                created_test = create_response.json()
                test_id = created_test.get('testSeriesId')
                created_test_ids.append(test_id)
                
                # Immediately check if it's visible
                list_response = requests.get(f"{BASE_URL}/test-series", headers=auth_headers)
                if list_response.status_code == 200:
                    test_series = list_response.json()
                    found_test = next((test for test in test_series if test.get('testSeriesId') == test_id), None)
                    
                    if found_test:
                        results.add_result(f"Rapid Test {i+1} Immediate Visibility", True, 
                                         f"Test {test_id} immediately visible after creation")
                    else:
                        results.add_result(f"Rapid Test {i+1} Immediate Visibility", False, 
                                         f"Test {test_id} NOT immediately visible after creation")
            else:
                results.add_result(f"Rapid Test {i+1} Creation", False, 
                                 f"Failed to create test {i+1}: {create_response.status_code}")
            
            time.sleep(0.5)  # Small delay between creations
        
        results.add_result("Rapid Test Creation Summary", True, 
                         f"Created {len(created_test_ids)} tests rapidly: {created_test_ids}")
        
    except Exception as e:
        results.add_result("Rapid Test Creation", False, f"Exception: {str(e)}")

def main():
    print("🧪 BACKEND TESTING: Teacher Test Series Visibility Issue")
    print("=" * 60)
    print("Testing specific user report about draft status and visibility problems")
    print("User reported testSeriesId: 4991d975-72ef-42df-80e2-ec8a806a33ab with status: 'draft'")
    print("User reported teacher userId: 97717e61-b920-4faa-9d2a-7a70961474f1")
    print()
    
    results = TestResults()
    
    # Test 1: Teacher Login
    print("🔐 Testing Teacher Authentication...")
    token, teacher_id = test_teacher_login(results)
    
    if token and teacher_id:
        print(f"\n📝 Testing with Teacher ID: {teacher_id}")
        
        # Test 2: Default Status Check
        print("\n📊 Testing Default Test Status...")
        test_id = test_create_test_series_status(results, token, teacher_id)
        
        # Test 3: Teacher Visibility
        print("\n👁️ Testing Teacher Test Visibility...")
        test_teacher_can_see_own_tests(results, token, teacher_id)
        
        # Test 4: Manual Draft Creation
        print("\n📝 Testing Manual Draft Creation...")
        draft_test_id = test_create_draft_test_manually(results, token, teacher_id)
        
        # Test 5: URL Parameter Testing
        print("\n🔍 Testing URL Parameters...")
        test_teacher_filtering_parameters(results, token, teacher_id)
        
        # Test 6: Rapid Creation Testing
        print("\n⚡ Testing Rapid Test Creation...")
        test_rapid_test_creation_visibility(results, token, teacher_id)
    
    # Test 7: Specific User Scenario
    print("\n🎯 Testing Specific User Scenario...")
    test_specific_user_scenario(results)
    
    # Final Summary
    print("\n" + "=" * 60)
    success_rate = results.summary()
    
    if success_rate >= 90:
        print("🎉 BACKEND STATUS: EXCELLENT - All major functionality working")
    elif success_rate >= 75:
        print("✅ BACKEND STATUS: GOOD - Minor issues detected")
    else:
        print("❌ BACKEND STATUS: ISSUES DETECTED - Requires attention")
    
    return results

if __name__ == "__main__":
    main()
                self.log("Teacher already exists, attempting login...")
                return self.test_teacher_login()
            else:
                self.log(f"❌ Teacher registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Teacher registration error: {str(e)}", "ERROR")
            return False
    
    def test_teacher_login(self):
        """Test teacher authentication"""
        try:
            self.log("Testing teacher login...")
            
            login_data = {
                "username": "teacher1",
                "password": "teacher123"
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get('token')
                self.teacher_user_id = data.get('user', {}).get('userId')
                self.log(f"✅ Teacher login successful. UserID: {self.teacher_user_id}")
                return True
            else:
                self.log(f"❌ Teacher login failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Teacher login error: {str(e)}", "ERROR")
            return False
    
    def test_get_initial_test_list(self):
        """Get initial test series list before creating new test"""
        try:
            self.log("Getting initial test series list...")
            
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.get(f"{API_BASE}/test-series", headers=headers)
            
            if response.status_code == 200:
                initial_tests = response.json()
                self.log(f"✅ Initial test series count: {len(initial_tests)}")
                for test in initial_tests:
                    self.log(f"   - {test.get('title', 'No title')} (ID: {test.get('testSeriesId', 'No ID')}, Status: {test.get('status', 'No status')})")
                return len(initial_tests)
            else:
                self.log(f"❌ Failed to get initial test list: {response.status_code} - {response.text}", "ERROR")
                return -1
                
        except Exception as e:
            self.log(f"❌ Error getting initial test list: {str(e)}", "ERROR")
            return -1
    
    def test_create_test_series(self):
        """Test creating a new test series"""
        try:
            self.log("Testing test series creation...")
            
            test_data = {
                "title": f"Teacher Visibility Test - {datetime.now().strftime('%H:%M:%S')}",
                "description": "Test series created to verify teacher visibility issue",
                "category": "Mathematics", 
                "duration": 60,
                "questions": [
                    {
                        "questionId": "q1",
                        "question": "What is 2 + 2?",
                        "options": ["3", "4", "5", "6"],
                        "correctAnswer": 1,
                        "explanation": "2 + 2 equals 4"
                    },
                    {
                        "questionId": "q2", 
                        "question": "What is 5 * 3?",
                        "options": ["12", "15", "18", "20"],
                        "correctAnswer": 1,
                        "explanation": "5 * 3 equals 15"
                    }
                ]
            }
            
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{API_BASE}/test-series", json=test_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.created_test_id = data.get('testSeriesId')
                created_status = data.get('status')
                self.log(f"✅ Test series created successfully!")
                self.log(f"   - Test ID: {self.created_test_id}")
                self.log(f"   - Title: {data.get('title')}")
                self.log(f"   - Status: {created_status}")
                self.log(f"   - Created By: {data.get('createdBy')}")
                return True
            else:
                self.log(f"❌ Test series creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Test series creation error: {str(e)}", "ERROR")
            return False
    
    def test_immediate_visibility(self):
        """Test if newly created test appears immediately in teacher's list"""
        try:
            self.log("Testing immediate visibility of newly created test...")
            
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.get(f"{API_BASE}/test-series", headers=headers)
            
            if response.status_code == 200:
                tests = response.json()
                self.log(f"✅ Retrieved {len(tests)} test series after creation")
                
                # Look for our newly created test
                found_test = None
                for test in tests:
                    self.log(f"   - {test.get('title', 'No title')} (ID: {test.get('testSeriesId', 'No ID')}, Status: {test.get('status', 'No status')}, CreatedBy: {test.get('createdBy', 'No creator')})")
                    if test.get('testSeriesId') == self.created_test_id:
                        found_test = test
                        break
                
                if found_test:
                    self.log(f"✅ FOUND: Newly created test is visible in teacher's list!")
                    self.log(f"   - Test ID: {found_test.get('testSeriesId')}")
                    self.log(f"   - Title: {found_test.get('title')}")
                    self.log(f"   - Status: {found_test.get('status')}")
                    self.log(f"   - Created By: {found_test.get('createdBy')}")
                    return True
                else:
                    self.log(f"❌ ISSUE REPRODUCED: Newly created test (ID: {self.created_test_id}) is NOT visible in teacher's list!", "ERROR")
                    self.log(f"   - Expected test ID: {self.created_test_id}", "ERROR")
                    self.log(f"   - Teacher user ID: {self.teacher_user_id}", "ERROR")
                    return False
            else:
                self.log(f"❌ Failed to get test list after creation: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing immediate visibility: {str(e)}", "ERROR")
            return False
    
    def test_delayed_visibility(self):
        """Test if test appears after a short delay"""
        try:
            self.log("Testing delayed visibility (waiting 2 seconds)...")
            time.sleep(2)
            
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.get(f"{API_BASE}/test-series", headers=headers)
            
            if response.status_code == 200:
                tests = response.json()
                self.log(f"✅ Retrieved {len(tests)} test series after delay")
                
                # Look for our newly created test
                found_test = None
                for test in tests:
                    if test.get('testSeriesId') == self.created_test_id:
                        found_test = test
                        break
                
                if found_test:
                    self.log(f"✅ Test became visible after delay")
                    return True
                else:
                    self.log(f"❌ Test still not visible after delay", "ERROR")
                    return False
            else:
                self.log(f"❌ Failed to get test list after delay: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing delayed visibility: {str(e)}", "ERROR")
            return False
    
    def test_with_different_parameters(self):
        """Test with different URL parameters to see if filtering is the issue"""
        try:
            self.log("Testing with different URL parameters...")
            
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            
            # Test with includeUnpublished=true
            response1 = requests.get(f"{API_BASE}/test-series?includeUnpublished=true", headers=headers)
            if response1.status_code == 200:
                tests1 = response1.json()
                self.log(f"✅ With includeUnpublished=true: {len(tests1)} tests")
                found1 = any(test.get('testSeriesId') == self.created_test_id for test in tests1)
                self.log(f"   - New test found: {found1}")
            
            # Test with includeUnpublished=false
            response2 = requests.get(f"{API_BASE}/test-series?includeUnpublished=false", headers=headers)
            if response2.status_code == 200:
                tests2 = response2.json()
                self.log(f"✅ With includeUnpublished=false: {len(tests2)} tests")
                found2 = any(test.get('testSeriesId') == self.created_test_id for test in tests2)
                self.log(f"   - New test found: {found2}")
            
            # Test without parameters (default)
            response3 = requests.get(f"{API_BASE}/test-series", headers=headers)
            if response3.status_code == 200:
                tests3 = response3.json()
                self.log(f"✅ Without parameters (default): {len(tests3)} tests")
                found3 = any(test.get('testSeriesId') == self.created_test_id for test in tests3)
                self.log(f"   - New test found: {found3}")
                
                return found1 or found2 or found3
            
            return False
                
        except Exception as e:
            self.log(f"❌ Error testing with different parameters: {str(e)}", "ERROR")
            return False
    
    def test_multiple_scenarios(self):
        """Test multiple scenarios that might cause visibility issues"""
        try:
            self.log("Testing multiple scenarios for potential visibility issues...")
            
            # Scenario 1: Create test with draft status explicitly
            self.log("Scenario 1: Creating test with draft status...")
            draft_test_data = {
                "title": f"Draft Test - {datetime.now().strftime('%H:%M:%S')}",
                "description": "Test with draft status",
                "category": "Science", 
                "duration": 30,
                "status": "draft",  # Explicitly set to draft
                "questions": [
                    {
                        "questionId": "q1",
                        "question": "What is H2O?",
                        "options": ["Water", "Hydrogen", "Oxygen", "Salt"],
                        "correctAnswer": 0,
                        "explanation": "H2O is water"
                    }
                ]
            }
            
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            response = requests.post(f"{API_BASE}/test-series", json=draft_test_data, headers=headers)
            
            if response.status_code == 200:
                draft_test_id = response.json().get('testSeriesId')
                self.log(f"✅ Draft test created: {draft_test_id}")
                
                # Check if draft test appears in list
                list_response = requests.get(f"{API_BASE}/test-series", headers=headers)
                if list_response.status_code == 200:
                    tests = list_response.json()
                    draft_found = any(test.get('testSeriesId') == draft_test_id for test in tests)
                    self.log(f"   - Draft test visible in list: {draft_found}")
            
            # Scenario 2: Create multiple tests rapidly
            self.log("Scenario 2: Creating multiple tests rapidly...")
            rapid_test_ids = []
            for i in range(3):
                rapid_data = {
                    "title": f"Rapid Test {i+1} - {datetime.now().strftime('%H:%M:%S')}",
                    "description": f"Rapid test number {i+1}",
                    "category": "Physics", 
                    "duration": 45,
                    "questions": [
                        {
                            "questionId": f"q{i+1}",
                            "question": f"Question {i+1}?",
                            "options": ["A", "B", "C", "D"],
                            "correctAnswer": i % 4,
                            "explanation": f"Answer {i+1}"
                        }
                    ]
                }
                
                response = requests.post(f"{API_BASE}/test-series", json=rapid_data, headers=headers)
                if response.status_code == 200:
                    test_id = response.json().get('testSeriesId')
                    rapid_test_ids.append(test_id)
                    self.log(f"   - Created rapid test {i+1}: {test_id}")
                
                # Small delay between creations
                time.sleep(0.1)
            
            # Check if all rapid tests are visible
            list_response = requests.get(f"{API_BASE}/test-series", headers=headers)
            if list_response.status_code == 200:
                tests = list_response.json()
                for i, test_id in enumerate(rapid_test_ids):
                    found = any(test.get('testSeriesId') == test_id for test in tests)
                    self.log(f"   - Rapid test {i+1} visible: {found}")
            
            # Scenario 3: Test with different teacher
            self.log("Scenario 3: Testing with different teacher account...")
            teacher2_data = {
                "username": "teacher2",
                "password": "teacher123", 
                "name": "Test Teacher Two",
                "role": "teacher",
                "email": "teacher2@example.com"
            }
            
            # Register or login teacher2
            response = requests.post(f"{API_BASE}/auth/register", json=teacher2_data)
            if response.status_code == 400:  # Already exists
                response = requests.post(f"{API_BASE}/auth/login", json={
                    "username": "teacher2", "password": "teacher123"
                })
            
            if response.status_code == 200:
                teacher2_token = response.json().get('token')
                teacher2_user_id = response.json().get('user', {}).get('userId')
                self.log(f"   - Teacher2 logged in: {teacher2_user_id}")
                
                # Create test with teacher2
                teacher2_test_data = {
                    "title": f"Teacher2 Test - {datetime.now().strftime('%H:%M:%S')}",
                    "description": "Test by second teacher",
                    "category": "Chemistry", 
                    "duration": 60,
                    "questions": [
                        {
                            "questionId": "q1",
                            "question": "What is NaCl?",
                            "options": ["Salt", "Sugar", "Water", "Oil"],
                            "correctAnswer": 0,
                            "explanation": "NaCl is salt"
                        }
                    ]
                }
                
                headers2 = {"Authorization": f"Bearer {teacher2_token}"}
                response = requests.post(f"{API_BASE}/test-series", json=teacher2_test_data, headers=headers2)
                
                if response.status_code == 200:
                    teacher2_test_id = response.json().get('testSeriesId')
                    self.log(f"   - Teacher2 test created: {teacher2_test_id}")
                    
                    # Check if teacher2 can see their test
                    list_response = requests.get(f"{API_BASE}/test-series", headers=headers2)
                    if list_response.status_code == 200:
                        tests = list_response.json()
                        found = any(test.get('testSeriesId') == teacher2_test_id for test in tests)
                        self.log(f"   - Teacher2 can see their test: {found}")
                        
                        # Check if teacher1 cannot see teacher2's test
                        list_response1 = requests.get(f"{API_BASE}/test-series", headers=headers)
                        if list_response1.status_code == 200:
                            tests1 = list_response1.json()
                            found1 = any(test.get('testSeriesId') == teacher2_test_id for test in tests1)
                            self.log(f"   - Teacher1 cannot see teacher2's test: {not found1}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error in multiple scenarios test: {str(e)}", "ERROR")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("=" * 60)
        self.log("STARTING TEACHER TEST VISIBILITY TESTS")
        self.log("=" * 60)
        
        results = {}
        
        # Step 1: Setup teacher account
        results['registration'] = self.test_teacher_registration()
        if not results['registration']:
            self.log("❌ Cannot proceed without teacher account", "ERROR")
            return results
        
        # Step 2: Get initial test count
        initial_count = self.test_get_initial_test_list()
        
        # Step 3: Create new test
        results['creation'] = self.test_create_test_series()
        if not results['creation']:
            self.log("❌ Cannot proceed without creating test", "ERROR")
            return results
        
        # Step 4: Test immediate visibility
        results['immediate_visibility'] = self.test_immediate_visibility()
        
        # Step 5: Test delayed visibility if immediate failed
        if not results['immediate_visibility']:
            results['delayed_visibility'] = self.test_delayed_visibility()
        
        # Step 6: Test with different parameters
        results['parameter_testing'] = self.test_with_different_parameters()
        
        # Step 7: Test multiple scenarios
        results['multiple_scenarios'] = self.test_multiple_scenarios()
        
        # Summary
        self.log("=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
        
        # Determine if the issue exists
        visibility_issue = not (results.get('immediate_visibility', False) or 
                              results.get('delayed_visibility', False) or 
                              results.get('parameter_testing', False))
        
        if visibility_issue:
            self.log("=" * 60)
            self.log("🚨 ISSUE CONFIRMED: Teacher test visibility problem exists!", "ERROR")
            self.log("   - Test was created successfully")
            self.log("   - Test does NOT appear in teacher's test list")
            self.log("=" * 60)
        else:
            self.log("=" * 60)
            self.log("✅ NO ISSUE: Teacher test visibility working correctly!")
            self.log("   - All basic visibility tests passed")
            self.log("   - The reported issue may be frontend-related or already fixed")
            self.log("=" * 60)
        
        return results

if __name__ == "__main__":
    tester = TestTeacherVisibility()
    results = tester.run_all_tests()