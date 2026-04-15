"""
Comprehensive backend API testing script.
Tests all major endpoints for user and admin functionality.
Usage: python test_backend.py
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}{RESET}")

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ️  {msg}{RESET}")

# Test Data
TEST_USER_EMAIL = f"testuser_{int(time.time())}@test.com"
TEST_USER_PASSWORD = "TestPassword123!"
# Valid PAN format: AAA[PCHABGJLFTE]A9999A
# Example: ABCPA1234Z
import random
pan_chars_4 = "PCHABGJLFTE"  # 4th character must be one of these
TEST_USER_PAN = f"ABC{random.choice(pan_chars_4)}A{int(time.time()) % 10000:04d}Z"
TEST_ADMIN_EMAIL = "admin@loanai.com"
TEST_ADMIN_PASSWORD = "admin123"

user_token = None
admin_token = None
application_id = None

# ============================================
# 1. HEALTH CHECK
# ============================================
def test_health():
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"Health check passed: {response.json()}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Could not reach backend: {e}")
        return False

# ============================================
# 2. USER AUTHENTICATION
# ============================================
def test_user_registration():
    print_test("User Registration")
    global user_token
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": "Test User",
        "phone": "9876543210",
        "pan_number": TEST_USER_PAN
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 201]:
            print_success(f"User registered: {TEST_USER_EMAIL}")
            return True
        else:
            print_error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False

def test_user_login():
    print_test("User Login")
    global user_token
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            user_token = data.get("data", {}).get("access_token")
            if not user_token:
                user_token = data.get("access_token")
            print_success(f"User login successful, token: {user_token[:20]}...")
            return True
        else:
            print_error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False

# ============================================
# 3. ADMIN AUTHENTICATION
# ============================================
def test_admin_login():
    print_test("Admin Login")
    global admin_token
    
    payload = {
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin/login", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get("data", {}).get("access_token")
            if not admin_token:
                admin_token = data.get("access_token")
            print_success(f"Admin login successful, token: {admin_token[:20]}...")
            return True
        else:
            print_error(f"Admin login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Admin login error: {e}")
        return False

# ============================================
# 4. USER - LOAN APPLICATION SUBMISSION
# ============================================
def test_loan_application():
    print_test("Submit Loan Application (User)")
    global application_id, user_token
    
    if not user_token:
        print_error("No user token available")
        return False
    
    # Create dummy image data (1x1 pixel PNG)
    dummy_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    files = {
        'full_name': (None, 'Test User'),
        'age': (None, '30'),
        'pan_number': (None, TEST_USER_PAN),
        'phone': (None, '9876543210'),
        'email': (None, TEST_USER_EMAIL),
        'monthly_income': (None, '50000'),
        'employment_type': (None, 'Salaried'),
        'employer_name': (None, 'Tech Company'),
        'loan_amount': (None, '500000'),
        'loan_purpose': (None, 'Home'),
        'loan_tenure_months': (None, '60'),
        'pan_document': ('pan_card.png', dummy_image, 'image/png'),
        'salary_document': ('salary_slip.png', dummy_image, 'image/png'),
    }
    
    headers = {
        'Authorization': f'Bearer {user_token}'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/user/apply",
            files=files,
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 201, 202]:
            data = response.json()
            application_id = data.get("application_id") or data.get("data", {}).get("application_id")
            print_success(f"Loan application submitted: {application_id}")
            return True
        else:
            print_error(f"Loan application failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Loan application error: {e}")
        return False

# ============================================
# 5. USER - GET MY APPLICATIONS
# ============================================
def test_user_get_applications():
    print_test("Get My Applications (User)")
    global user_token
    
    if not user_token:
        print_error("No user token available")
        return False
    
    headers = {
        'Authorization': f'Bearer {user_token}'
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/user/applications",
            headers=headers,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")  # Show raw response for debugging
        
        if response.status_code == 200:
            try:
                data = response.json()
                apps = data.get("data", data.get("applications", []))
                print_success(f"Retrieved {len(apps)} application(s)")
                return True
            except ValueError as e:
                print_error(f"Failed to parse JSON: {e}")
                print_error(f"Raw response: {response.text}")
                return False
        elif response.status_code == 500:
            print_error(f"Server error (500): {response.text[:200]}")
            return False
        else:
            print_error(f"Failed to get applications: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get applications error: {e}")
        return False

# ============================================
# 6. ADMIN - GET ALL APPLICATIONS
# ============================================
def test_admin_get_applications():
    print_test("Get All Applications (Admin)")
    global admin_token
    
    if not admin_token:
        print_error("No admin token available")
        return False
    
    headers = {
        'Authorization': f'Bearer {admin_token}'
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/applications?page=1&per_page=10",
            headers=headers,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")  # Show raw response for debugging
        
        if response.status_code == 200:
            try:
                data = response.json()
                apps = data.get("data", data.get("applications", []))
                print_success(f"Admin retrieved {len(apps)} application(s)")
                return True
            except ValueError as e:
                print_error(f"Failed to parse JSON: {e}")
                print_error(f"Raw response: {response.text}")
                return False
        elif response.status_code == 500:
            print_error(f"Server error (500): {response.text[:200]}")
            return False
        else:
            print_error(f"Failed to get applications: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get applications error: {e}")
        return False

# ============================================
# 7. ADMIN - GET DASHBOARD STATS
# ============================================
def test_admin_dashboard():
    print_test("Get Dashboard Stats (Admin)")
    global admin_token
    
    if not admin_token:
        print_error("No admin token available")
        return False
    
    headers = {
        'Authorization': f'Bearer {admin_token}'
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/stats",
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Dashboard stats retrieved")
            print(f"  - Total applications: {data.get('total_applications', 'N/A')}")
            print(f"  - Approved: {data.get('approved_count', 'N/A')}")
            print(f"  - Rejected: {data.get('rejected_count', 'N/A')}")
            print(f"  - Pending: {data.get('pending_count', 'N/A')}")
            return True
        else:
            print_error(f"Failed to get stats: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Dashboard stats error: {e}")
        return False

# ============================================
# 8. ADMIN - ADD TO BLACKLIST
# ============================================
def test_admin_add_blacklist():
    print_test("Add to Blacklist (Admin)")
    global admin_token
    
    if not admin_token:
        print_error("No admin token available")
        return False
    
    payload = {
        "pan_number": f"TEST{int(time.time())}",
        "reason": "Test blacklist entry",
        "name": "Test Fraudster"
    }
    
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/blacklist",
            json=payload,
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 201]:
            print_success("Added to blacklist successfully")
            return True
        else:
            print_error(f"Failed to add to blacklist: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Add blacklist error: {e}")
        return False

# ============================================
# MAIN TEST RUNNER
# ============================================
def run_all_tests():
    print(f"\n{BLUE}")
    print("="*60)
    print("LOAN UNDERWRITING AI - BACKEND TEST SUITE")
    print("="*60)
    print(f"URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{RESET}")
    
    results = {}
    
    # Health check
    results['health'] = test_health()
    if not results['health']:
        print_error("Backend is not running!")
        return
    
    # User tests
    results['user_registration'] = test_user_registration()
    results['user_login'] = test_user_login()
    results['loan_application'] = test_loan_application()
    results['user_applications'] = test_user_get_applications()
    
    # Admin tests
    results['admin_login'] = test_admin_login()
    results['admin_applications'] = test_admin_get_applications()
    results['admin_dashboard'] = test_admin_dashboard()
    results['admin_blacklist'] = test_admin_add_blacklist()
    
    # Summary
    print(f"\n{BLUE}")
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"{RESET}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test_name.upper()}: {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"{GREEN}✅ ALL TESTS PASSED!{RESET}")
    else:
        print(f"{RED}⚠️  Some tests failed. Check output above.{RESET}")

if __name__ == "__main__":
    run_all_tests()
