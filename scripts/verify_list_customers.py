import requests
import sys

def verify_list_customers():
    url = "http://127.0.0.1:8000/customers/"
    print(f"Attempting to fetch customers list from {url}...")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Endpoint exists and returned data.")
            return True
        elif response.status_code == 405:
            print("FAILURE: Method Not Allowed. Endpoint likely exists but only for POST.")
            return False
        elif response.status_code == 404:
            print("FAILURE: Endpoint not found.")
            return False
        else:
            print(f"FAILURE: Unexpected status code {response.status_code}")
            return False
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    verify_list_customers()
