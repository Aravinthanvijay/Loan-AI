"""
Detailed diagnostic for user registration/login issues
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

# Generate unique test data
TEST_EMAIL = f"testuser_{int(time.time())}@test.com"
TEST_PASSWORD = "TestPassword123!"
# Valid PAN format: AAA[PCHABGJLFTE]A9999A
# Example: ABCPA1234Z
import random
pan_chars_4 = "PCHABGJLFTE"  # 4th character must be one of these
TEST_PAN = f"ABC{random.choice(pan_chars_4)}A{int(time.time()) % 10000:04d}Z"
TEST_PHONE = "9876543210"

print("="*60)
print("USER REGISTRATION DIAGNOSTIC")
print("="*60)
print(f"\nTest Data:")
print(f"  Email: {TEST_EMAIL}")
print(f"  PAN: {TEST_PAN}")
print(f"  Phone: {TEST_PHONE}")
print(f"  Password: {TEST_PASSWORD}\n")

# Step 1: Try registration
print("STEP 1: User Registration")
print("-" * 60)

registration_payload = {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD,
    "full_name": "Test User",
    "phone": TEST_PHONE,
    "pan_number": TEST_PAN
}

print(f"Payload: {json.dumps(registration_payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=registration_payload,
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code in [200, 201]:
        print("\n✅ Registration SUCCESSFUL")
        user_id = response.json().get("data", {}).get("user_id")
        user_token = response.json().get("data", {}).get("access_token")
        print(f"   User ID: {user_id}")
        print(f"   Token: {user_token[:30]}...")
        
        # Step 2: Try login with registered email/password
        print("\n" + "="*60)
        print("STEP 2: User Login (with registered credentials)")
        print("-" * 60)
        
        login_payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        print(f"Payload: {json.dumps(login_payload, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_payload,
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Login SUCCESSFUL")
        else:
            print(f"\n❌ Login FAILED: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            
    else:
        print(f"\n❌ Registration FAILED: {response.status_code}")
        error_detail = response.json().get("detail", "Unknown error")
        print(f"   Error: {error_detail}")
        
        # Try to understand the error
        if "already registered" in str(error_detail).lower():
            print(f"   → PAN number '{TEST_PAN}' is already in database")
            print(f"   → Try with a completely different PAN")
        elif "invalid" in str(error_detail).lower():
            print(f"   → Validation error - check field formats")
        elif "pan" in str(error_detail).lower():
            print(f"   → PAN validation issue")
            print(f"   → PAN format required: 10 characters")
            
except Exception as e:
    print(f"\n❌ Request Error: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
