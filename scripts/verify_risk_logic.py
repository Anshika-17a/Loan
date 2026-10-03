import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_15l_limit():
    print("\n--- Testing 15L Limit ---")
    # 1. Create a user with 10L loan (Approved)
    pan = "ABCDE1234L"
    token = f"user_limit_test_{int(time.time())}"
    
    payload = {
        "customer_token": token,
        "loan_amount": 1000000, # 10L
        "annual_income": 2000000,
        "credit_score": 750,
        "date_of_birth": "1990-01-01",
        "years_employed": 5,
        "education_type": "Higher education",
        "pan_ssn": pan,
        "phone_number": "9999999999",
        "email_address": f"{token}@example.com",
        "residential_status": "Owned",
        "months_at_address": 24,
        "phone_contract_type": "Postpaid"
    }
    
    # Register
    res = requests.post(f"{BASE_URL}/customers/", json=payload)
    if res.status_code != 201:
        print(f"Failed to register base user: {res.text}")
        return
    
    cust_id = res.json()["id"]
    print(f"Registered User 1 (10L): ID {cust_id}")
    
    # Score & Approve (Mocking approval by updating DB directly would be cheating, 
    # but our logic auto-approves low risk. 750 score should be low risk.)
    res = requests.post(f"{BASE_URL}/customers/score/{cust_id}")
    if res.status_code != 200:
        print(f"Failed to score: {res.text}")
        return
    
    print(f"User 1 Status: {res.json()['customer']['review_status']}")
    
    # 2. Try to create another user with same PAN and 6L loan (Total 16L > 15L)
    # Note: The limit check sums 'Approved' loans. If User 1 is not 'Approved', this won't trigger.
    # Let's assume User 1 got Approved.
    
    token2 = f"user_limit_test_2_{int(time.time())}"
    payload2 = payload.copy()
    payload2["customer_token"] = token2
    payload2["loan_amount"] = 600000 # 6L
    payload2["email_address"] = f"{token2}@example.com" # Unique email to avoid fraud ring check
    payload2["phone_number"] = "8888888888"
    
    res = requests.post(f"{BASE_URL}/customers/", json=payload2)
    if res.status_code == 400 and "Loan Limit Exceeded" in res.text:
        print("SUCCESS: 15L Limit Check Passed! (Rejected as expected)")
    elif res.status_code == 201:
        print("FAILURE: 15L Limit Check Failed (Accepted unexpectedly)")
        # Clean up or check why User 1 wasn't approved?
    else:
        print(f"Unexpected response: {res.status_code} {res.text}")

def test_cibil_override():
    print("\n--- Testing CIBIL Override ---")
    # Create user with Low CIBIL (e.g. 550) but high income (so model might think it's fine)
    token = f"user_cibil_test_{int(time.time())}"
    payload = {
        "customer_token": token,
        "loan_amount": 100000, # Small loan
        "annual_income": 2000000, # High income
        "credit_score": 550, # LOW CIBIL
        "date_of_birth": "1990-01-01",
        "years_employed": 5,
        "education_type": "Higher education",
        "pan_ssn": "ABCDE1234C",
        "phone_number": "7777777777",
        "email_address": f"{token}@example.com",
        "residential_status": "Owned",
        "months_at_address": 24,
        "phone_contract_type": "Postpaid"
    }
    
    res = requests.post(f"{BASE_URL}/customers/", json=payload)
    cust_id = res.json()["id"]
    
    # Score
    res = requests.post(f"{BASE_URL}/customers/score/{cust_id}")
    data = res.json()
    risk_level = data["prediction_details"]["risk_level"]
    explanation = data["prediction_details"]["explanation"]
    
    print(f"CIBIL: 550 -> Risk Level: {risk_level}")
    
    override_found = any(e['feature'] == 'CIBIL_OVERRIDE' for e in explanation)
    if override_found and risk_level in ["Medium", "High", "Rejected"]:
        print("SUCCESS: CIBIL Override Logic Passed!")
    else:
        print("FAILURE: CIBIL Override Logic Failed.")

if __name__ == "__main__":
    try:
        test_15l_limit()
        test_cibil_override()
    except Exception as e:
        print(f"Test Execution Failed: {e}")
