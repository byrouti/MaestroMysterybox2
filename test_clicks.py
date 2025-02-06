import requests

def test_multiple_clicks():
    # Base URL
    base_url = "http://localhost:5000"
    
    print("Testing click limitations...\n")
    
    # Reset the server first
    requests.post(f"{base_url}/reset")
    
    # Test case 1: Same user clicking multiple times
    print("Test Case 1: Same user clicking multiple times")
    print("-" * 50)
    
    # Generate token for user
    user_id = 1001
    response = requests.post(
        f"{base_url}/generate_token",
        json={'user_id': user_id}
    )
    
    if response.status_code == 200:
        token = response.json()['token']
        
        # Try clicking 3 times with the same token
        for i in range(3):
            print(f"\nClick attempt {i + 1}:")
            verify_response = requests.get(f"{base_url}/verify/{token}")
            result = verify_response.json()
            print(f"Response: {result}")
    
    # Test case 2: Different users clicking
    print("\nTest Case 2: Different users clicking")
    print("-" * 50)
    
    # Generate tokens for 3 different users
    for user_id in range(2001, 2004):
        response = requests.post(
            f"{base_url}/generate_token",
            json={'user_id': user_id}
        )
        
        if response.status_code == 200:
            token = response.json()['token']
            print(f"\nUser {user_id} clicking:")
            verify_response = requests.get(f"{base_url}/verify/{token}")
            result = verify_response.json()
            print(f"Response: {result}")
    
    # Test case 3: Invalid token
    print("\nTest Case 3: Invalid token")
    print("-" * 50)
    print("Trying to click with invalid token:")
    verify_response = requests.get(f"{base_url}/verify/invalid_token")
    result = verify_response.json()
    print(f"Response: {result}")

if __name__ == "__main__":
    test_multiple_clicks()
