import requests
import time

def print_separator(title):
    print(f"\n{'=' * 60}")
    print(title)
    print('=' * 60)

def test_comprehensive():
    base_url = "http://localhost:5000"
    
    # Test 1: System Reset
    print_separator("Test 1: System Reset Behavior")
    
    # First, let's have some users click
    print("Before Reset:")
    test_users = [3001, 3002]
    tokens = {}
    
    for user_id in test_users:
        response = requests.post(
            f"{base_url}/generate_token",
            json={'user_id': user_id}
        )
        if response.status_code == 200:
            token = response.json()['token']
            tokens[user_id] = token
            verify_response = requests.get(f"{base_url}/verify/{token}")
            print(f"User {user_id} first click: {verify_response.json()}")
    
    # Reset the system
    print("\nResetting system...")
    reset_response = requests.post(f"{base_url}/reset")
    print(f"Reset response: {reset_response.status_code}")
    
    # Try clicking with the same tokens after reset
    print("\nAfter Reset - Using old tokens:")
    for user_id, token in tokens.items():
        verify_response = requests.get(f"{base_url}/verify/{token}")
        print(f"User {user_id} using old token: {verify_response.json()}")
    
    # Get new tokens and click again
    print("\nAfter Reset - Getting new tokens:")
    for user_id in test_users:
        response = requests.post(
            f"{base_url}/generate_token",
            json={'user_id': user_id}
        )
        if response.status_code == 200:
            token = response.json()['token']
            verify_response = requests.get(f"{base_url}/verify/{token}")
            print(f"User {user_id} with new token: {verify_response.json()}")
    
    # Test 2: Edge Cases
    print_separator("Test 2: Edge Cases")
    
    # Case 1: Invalid user ID
    print("\nTesting invalid user ID:")
    response = requests.post(
        f"{base_url}/generate_token",
        json={'user_id': "invalid"}
    )
    print(f"Invalid user ID response: {response.json() if response.status_code == 200 else response.status_code}")
    
    # Case 2: Missing user ID
    print("\nTesting missing user ID:")
    response = requests.post(
        f"{base_url}/generate_token",
        json={}
    )
    print(f"Missing user ID response: {response.json() if response.status_code == 200 else response.status_code}")
    
    # Case 3: Rapid clicks
    print("\nTesting rapid clicks:")
    response = requests.post(
        f"{base_url}/generate_token",
        json={'user_id': 3003}
    )
    if response.status_code == 200:
        token = response.json()['token']
        for i in range(3):
            verify_response = requests.get(f"{base_url}/verify/{token}")
            print(f"Rapid click {i+1}: {verify_response.json()}")
            time.sleep(0.1)  # Small delay between clicks
    
    # Case 4: Fill up winners and test additional clicks
    print("\nTesting after all prizes are taken:")
    # Reset first
    requests.post(f"{base_url}/reset")
    
    # Fill up all prize slots
    print("\nFilling all prize slots:")
    for i in range(12):  # Try with 12 users (more than MAX_USERS)
        user_id = 4000 + i
        response = requests.post(
            f"{base_url}/generate_token",
            json={'user_id': user_id}
        )
        if response.status_code == 200:
            token = response.json()['token']
            verify_response = requests.get(f"{base_url}/verify/{token}")
            print(f"User {user_id}: {verify_response.json()}")

if __name__ == "__main__":
    test_comprehensive()
