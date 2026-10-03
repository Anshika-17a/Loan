import requests
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

def verify_full_flow():
    # 1. Register a new user
    username = f"applicant_{int(time.time())}"
    print(f"\n--- 1. Registering User '{username}' ---")
    auth_payload = {
        "username": username,
        "password": "password123",
        "role": "applicant"
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json=auth_payload)
        if res.status_code != 200:
            print(f"Registration Failed: {res.text}")
            return False
        token = res.json()["access_token"]
        print("Registration Successful.")
    except Exception as e:
        print(f"Exception during registration: {e}")
        return False

    # 2. Submit Loan Application
    print(f"\n--- 2. Submitting Loan Application ---")
    app_payload = {
        "customer_token": username,
        "loan_amount": 500000,
        "annual_income": 1200000,
        "credit_score": 750,
        "date_of_birth": "1990-01-01",
        "years_employed": 5,
        "education_type": "Higher education",
        "pan_ssn": "ABCDE1234F",
        "phone_number": "9876543210",
        "email_address": f"{username}@example.com",
        "residential_status": "Rented",
        "months_at_address": 12,
        "phone_contract_type": "Prepaid"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/customers/", json=app_payload)
        if res.status_code != 201:
            print(f"Application Submission Failed: {res.text}")
            return False
        customer_id = res.json()["id"]
        print(f"Application Submitted. ID: {customer_id}")
    except Exception as e:
        print(f"Exception during submission: {e}")
        return False

    # 3. Verify Application appears in List (Banker View)
    print(f"\n--- 3. Verifying Application in List ---")
    try:
        res = requests.get(f"{BASE_URL}/customers/")
        if res.status_code != 200:
            print(f"Fetch Customers Failed: {res.text}")
            return False
        
        customers = res.json()
        found = False
        for c in customers:
            if c["id"] == customer_id:
                found = True
                print(f"SUCCESS: Found Application #{customer_id} in list.")
                break
        
        if not found:
            print(f"FAILURE: Application #{customer_id} NOT found in list.")
            return False
            
    except Exception as e:
        print(f"Exception during fetch: {e}")
        return False

    return True

if __name__ == "__main__":
    if verify_full_flow():
        sys.exit(0)
    else:
        sys.exit(1)
