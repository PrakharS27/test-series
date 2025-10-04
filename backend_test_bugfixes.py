#!/usr/bin/env python3
"""
Backend Testing for Specific Bug Fixes
Testing only the 3 specific bug fixes implemented:
1. Admin Edit Permissions for Teacher Tests
2. Teacher Test Visibility After Creation  
3. Test Status Publish/Unpublish Functionality
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'http://localhost:3000')
API_BASE = f"{BASE_URL}/api"

class TestRunner:
    def __init__(self):
        self.admin_token = None
        self.teacher_token = None
        self.teacher_user_id = None
        self.admin_user_id = None
        self.test_series_id = None
        self.results = []
        
    def log_result(self, test_name, success, message):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        self.results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        
    def login_admin(self):
        """Login as admin"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "username": "admin",
                "password": "admin123"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['token']
                self.admin_user_id = data['user']['userId']
                self.log_result("Admin Login", True, f"Admin logged in successfully (ID: {self.admin_user_id})")
                return True
            else:
                self.log_result("Admin Login", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception: {str(e)}")
            return False
            
    def login_teacher(self):
        """Login as teacher (using existing teacher account)"""
        try:
            # First try to get existing teacher accounts
            if not self.admin_token:
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{API_BASE}/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                teachers = [u for u in users if u.get('role') == 'teacher']
                
                if teachers:
                    teacher = teachers[0]
                    # Try to login with this teacher (assuming password is same as username for test data)
                    login_response = requests.post(f"{API_BASE}/auth/login", json={
                        "username": teacher['username'],
                        "password": teacher['username']  # Common test pattern
                    })
                    
                    if login_response.status_code == 200:
                        data = login_response.json()
                        self.teacher_token = data['token']
                        self.teacher_user_id = data['user']['userId']
                        self.log_result("Teacher Login", True, f"Teacher logged in: {teacher['username']} (ID: {self.teacher_user_id})")
                        return True
                    else:
                        # Create a new teacher for testing
                        return self.create_test_teacher()
                else:
                    return self.create_test_teacher()
            else:
                return self.create_test_teacher()
                
        except Exception as e:
            self.log_result("Teacher Login", False, f"Exception: {str(e)}")
            return False
            
    def create_test_teacher(self):
        """Create a test teacher account"""
        try:
            response = requests.post(f"{API_BASE}/auth/register", json={
                "username": "testteacher_bugfix",
                "password": "testteacher_bugfix",
                "name": "Test Teacher for Bug Fixes",
                "role": "teacher",
                "email": "testteacher_bugfix@example.com",
                "phone": "1234567890"
            })
            
            if response.status_code == 200:
                # Now login
                login_response = requests.post(f"{API_BASE}/auth/login", json={
                    "username": "testteacher_bugfix",
                    "password": "testteacher_bugfix"
                })
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.teacher_token = data['token']
                    self.teacher_user_id = data['user']['userId']
                    self.log_result("Teacher Creation & Login", True, f"Created and logged in teacher (ID: {self.teacher_user_id})")
                    return True
                    
            self.log_result("Teacher Creation", False, f"Failed to create teacher: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("Teacher Creation", False, f"Exception: {str(e)}")
            return False

    def test_teacher_creates_test_series(self):
        """Test: Teacher creates a test series and it appears immediately (Bug Fix #2)"""
        try:
            if not self.teacher_token:
                self.log_result("Teacher Test Creation", False, "No teacher token available")
                return False
                
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            
            # Create test series
            test_data = {
                "title": "Bug Fix Test Series - Teacher Created",
                "description": "Test series created by teacher to verify immediate visibility",
                "category": "Mathematics",
                "duration": 60,
                "questions": [
                    {
                        "question": "What is 2 + 2?",
                        "options": ["3", "4", "5", "6"],
                        "correctAnswer": 1,
                        "explanation": "Basic addition: 2 + 2 = 4"
                    }
                ]
            }
            
            response = requests.post(f"{API_BASE}/test-series", json=test_data, headers=headers)
            
            if response.status_code == 200:
                created_test = response.json()
                self.test_series_id = created_test['testSeriesId']
                
                # Verify status is 'published' by default (Bug Fix #2)
                if created_test.get('status') == 'published':
                    self.log_result("Teacher Test Creation - Default Status", True, f"Test created with 'published' status by default (ID: {self.test_series_id})")
                else:
                    self.log_result("Teacher Test Creation - Default Status", False, f"Test created with status '{created_test.get('status')}' instead of 'published'")
                
                # Immediately check if teacher can see their own test
                get_response = requests.get(f"{API_BASE}/test-series", headers=headers)
                
                if get_response.status_code == 200:
                    teacher_tests = get_response.json()
                    created_test_visible = any(t['testSeriesId'] == self.test_series_id for t in teacher_tests)
                    
                    if created_test_visible:
                        self.log_result("Teacher Test Visibility After Creation", True, "Teacher can see newly created test immediately in their list")
                    else:
                        self.log_result("Teacher Test Visibility After Creation", False, "Teacher cannot see newly created test in their list")
                        
                    return True
                else:
                    self.log_result("Teacher Test Visibility Check", False, f"Failed to get teacher tests: {get_response.status_code}")
                    return False
                    
            else:
                self.log_result("Teacher Test Creation", False, f"Failed to create test: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Teacher Test Creation", False, f"Exception: {str(e)}")
            return False

    def test_admin_edit_permissions_for_teacher_tests(self):
        """Test: Admin can edit/delete teacher-created tests (Bug Fix #1)"""
        try:
            if not self.admin_token or not self.test_series_id:
                self.log_result("Admin Edit Permissions", False, "Missing admin token or test series ID")
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test 1: Admin can view teacher-created test
            get_response = requests.get(f"{API_BASE}/test-series", headers=headers)
            
            if get_response.status_code == 200:
                admin_tests = get_response.json()
                teacher_test_visible = any(t['testSeriesId'] == self.test_series_id for t in admin_tests)
                
                if teacher_test_visible:
                    self.log_result("Admin View Teacher Tests", True, "Admin can see teacher-created tests")
                else:
                    self.log_result("Admin View Teacher Tests", False, "Admin cannot see teacher-created tests")
                    return False
            else:
                self.log_result("Admin View Teacher Tests", False, f"Failed to get tests as admin: {get_response.status_code}")
                return False
            
            # Test 2: Admin can edit teacher-created test (Bug Fix #1)
            update_data = {
                "title": "Bug Fix Test Series - EDITED BY ADMIN",
                "description": "This test was edited by admin to verify permissions"
            }
            
            edit_response = requests.put(f"{API_BASE}/test-series/{self.test_series_id}", 
                                       json=update_data, headers=headers)
            
            if edit_response.status_code == 200:
                self.log_result("Admin Edit Teacher Test", True, "Admin successfully edited teacher-created test")
                
                # Verify the edit was applied
                get_updated = requests.get(f"{API_BASE}/test-series", headers=headers)
                if get_updated.status_code == 200:
                    updated_tests = get_updated.json()
                    updated_test = next((t for t in updated_tests if t['testSeriesId'] == self.test_series_id), None)
                    
                    if updated_test and updated_test['title'] == update_data['title']:
                        self.log_result("Admin Edit Verification", True, "Admin edit was successfully applied")
                    else:
                        self.log_result("Admin Edit Verification", False, "Admin edit was not applied correctly")
                        
            else:
                self.log_result("Admin Edit Teacher Test", False, f"Admin failed to edit teacher test: {edit_response.status_code} - {edit_response.text}")
                return False
                
            return True
            
        except Exception as e:
            self.log_result("Admin Edit Permissions", False, f"Exception: {str(e)}")
            return False

    def test_publish_unpublish_functionality(self):
        """Test: Test status publish/unpublish functionality (Bug Fix #3)"""
        try:
            if not self.admin_token or not self.test_series_id:
                self.log_result("Publish/Unpublish Test", False, "Missing admin token or test series ID")
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test 1: Change status to draft (unpublish)
            unpublish_data = {"status": "draft"}
            
            unpublish_response = requests.put(f"{API_BASE}/test-series/{self.test_series_id}", 
                                            json=unpublish_data, headers=headers)
            
            if unpublish_response.status_code == 200:
                self.log_result("Unpublish Test", True, "Successfully changed test status to 'draft'")
                
                # Verify status change in database
                get_response = requests.get(f"{API_BASE}/test-series", headers=headers)
                if get_response.status_code == 200:
                    tests = get_response.json()
                    updated_test = next((t for t in tests if t['testSeriesId'] == self.test_series_id), None)
                    
                    if updated_test and updated_test.get('status') == 'draft':
                        self.log_result("Unpublish Verification", True, "Test status correctly updated to 'draft' in database")
                    else:
                        self.log_result("Unpublish Verification", False, f"Test status not updated correctly. Current status: {updated_test.get('status') if updated_test else 'Not found'}")
                        
            else:
                self.log_result("Unpublish Test", False, f"Failed to unpublish test: {unpublish_response.status_code} - {unpublish_response.text}")
                return False
            
            # Test 2: Change status back to published
            publish_data = {"status": "published"}
            
            publish_response = requests.put(f"{API_BASE}/test-series/{self.test_series_id}", 
                                          json=publish_data, headers=headers)
            
            if publish_response.status_code == 200:
                self.log_result("Publish Test", True, "Successfully changed test status to 'published'")
                
                # Verify status change in database
                get_response = requests.get(f"{API_BASE}/test-series", headers=headers)
                if get_response.status_code == 200:
                    tests = get_response.json()
                    updated_test = next((t for t in tests if t['testSeriesId'] == self.test_series_id), None)
                    
                    if updated_test and updated_test.get('status') == 'published':
                        self.log_result("Publish Verification", True, "Test status correctly updated to 'published' in database")
                    else:
                        self.log_result("Publish Verification", False, f"Test status not updated correctly. Current status: {updated_test.get('status') if updated_test else 'Not found'}")
                        
            else:
                self.log_result("Publish Test", False, f"Failed to publish test: {publish_response.status_code} - {publish_response.text}")
                return False
                
            return True
            
        except Exception as e:
            self.log_result("Publish/Unpublish Test", False, f"Exception: {str(e)}")
            return False

    def test_admin_delete_teacher_test(self):
        """Test: Admin can delete teacher-created tests (Bug Fix #1)"""
        try:
            if not self.admin_token or not self.test_series_id:
                self.log_result("Admin Delete Teacher Test", False, "Missing admin token or test series ID")
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Admin deletes teacher-created test
            delete_response = requests.delete(f"{API_BASE}/test-series/{self.test_series_id}", headers=headers)
            
            if delete_response.status_code == 200:
                self.log_result("Admin Delete Teacher Test", True, "Admin successfully deleted teacher-created test")
                
                # Verify test is deleted
                get_response = requests.get(f"{API_BASE}/test-series", headers=headers)
                if get_response.status_code == 200:
                    tests = get_response.json()
                    deleted_test = next((t for t in tests if t['testSeriesId'] == self.test_series_id), None)
                    
                    if not deleted_test:
                        self.log_result("Admin Delete Verification", True, "Test successfully removed from database")
                    else:
                        self.log_result("Admin Delete Verification", False, "Test still exists in database after deletion")
                        
            else:
                self.log_result("Admin Delete Teacher Test", False, f"Admin failed to delete teacher test: {delete_response.status_code} - {delete_response.text}")
                return False
                
            return True
            
        except Exception as e:
            self.log_result("Admin Delete Teacher Test", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all bug fix tests"""
        print("=" * 80)
        print("BACKEND TESTING - SPECIFIC BUG FIXES")
        print("Testing 3 specific bug fixes:")
        print("1. Admin Edit Permissions for Teacher Tests")
        print("2. Teacher Test Visibility After Creation")
        print("3. Test Status Publish/Unpublish Functionality")
        print("=" * 80)
        
        # Setup
        if not self.login_admin():
            print("❌ Cannot proceed without admin login")
            return False
            
        if not self.login_teacher():
            print("❌ Cannot proceed without teacher login")
            return False
        
        # Run bug fix tests
        print("\n--- BUG FIX #2: Teacher Test Visibility After Creation ---")
        self.test_teacher_creates_test_series()
        
        print("\n--- BUG FIX #1: Admin Edit Permissions for Teacher Tests ---")
        self.test_admin_edit_permissions_for_teacher_tests()
        
        print("\n--- BUG FIX #3: Test Status Publish/Unpublish Functionality ---")
        self.test_publish_unpublish_functionality()
        
        print("\n--- BUG FIX #1: Admin Delete Permissions for Teacher Tests ---")
        self.test_admin_delete_teacher_test()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFAILED TESTS:")
            for r in self.results:
                if not r['success']:
                    print(f"❌ {r['test']}: {r['message']}")
        
        return passed == total

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)