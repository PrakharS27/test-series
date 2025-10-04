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
        # Test with the specific teacher userId mentioned: "97717e61-b920-4faa-9d2a-7a70961474f1"
        # First try to find this user or create a test teacher
        
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