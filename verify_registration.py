import requests
import sys

def verify_registration():
    url = "http://127.0.0.1:8000/auth/register"
    payload = {
        "username": "anshika3",
        "password": "password123",
        "role": "applicant"
    }
    
    print(f"Attempting registration at {url}...")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Registration successful.")
            return True
        else:
            print("FAILURE: Registration failed.")
            return False
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    verify_registration()
