import requests
import time
import sys

def verify_login():
    url = "http://127.0.0.1:8000/auth/login"
    payload = {
        "username": "anh",
        "password": "password"
    }
    
    print(f"Attempting login at {url}...")
    
    # Retry a few times in case server is reloading
    for i in range(5):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print("SUCCESS: Login successful. Access token received.")
                    return True
                else:
                    print(f"FAILURE: Login successful but no access token. Response: {data}")
                    return False
            else:
                print(f"Attempt {i+1}: Login failed with status {response.status_code}. Response: {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"Attempt {i+1}: Connection failed. Server might be reloading...")
        
        time.sleep(2)
        
    print("FAILURE: Could not log in after multiple attempts.")
    return False

if __name__ == "__main__":
    if verify_login():
        sys.exit(0)
    else:
        sys.exit(1)
