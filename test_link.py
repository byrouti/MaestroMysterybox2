import requests
import json
import sys

# Set console to UTF-8 mode
sys.stdout.reconfigure(encoding='utf-8')

def test_link():
    base_url = "http://localhost:5000"
    test_user_id = 12345

    print("Testing link functionality...")
    print("=" * 50)

    # Step 1: Reset the server
    print("\n1. Resetting server...")
    try:
        response = requests.post(f"{base_url}/reset")
        print("[OK] Server reset successful")
    except Exception as e:
        print(f"[ERROR] Server reset failed: {str(e)}")
        return

    # Step 2: Generate a token
    print("\n2. Generating verification token...")
    try:
        response = requests.post(
            f"{base_url}/generate_token",
            json={'user_id': test_user_id}
        )
        if response.status_code == 200:
            token = response.json()['token']
            print("[OK] Token generated successfully")
            print(f"[OK] Verification link would be: {base_url}/verify/{token}")
        else:
            print(f"[ERROR] Failed to generate token: {response.text}")
            return
    except Exception as e:
        print(f"[ERROR] Token generation failed: {str(e)}")
        return

    # Step 3: Test clicking the link
    print("\n3. Testing link click...")
    try:
        response = requests.get(f"{base_url}/verify/{token}")
        if response.status_code == 200:
            result = response.json()
            print("[OK] Link click successful!")
            if 'prize' in result:
                prize = result['prize']
                print(f"[OK] Won prize: {prize['accounts']} account(s) for {prize['duration']}")
            else:
                print(f"[OK] Response: {result['message']}")
        else:
            print(f"[ERROR] Link click failed: {response.text}")
    except Exception as e:
        print(f"[ERROR] Link click failed: {str(e)}")
        return

    # Step 4: Test clicking the same link again
    print("\n4. Testing clicking the same link again (should fail)...")
    try:
        response = requests.get(f"{base_url}/verify/{token}")
        if response.status_code == 200:
            result = response.json()
            print("[OK] Server responded correctly")
            print(f"[OK] Message: {result.get('message', result)}")
        else:
            print(f"[ERROR] Unexpected response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Request failed: {str(e)}")

    # Step 5: Test invalid token
    print("\n5. Testing invalid token...")
    try:
        response = requests.get(f"{base_url}/verify/invalid_token")
        if response.status_code != 200:
            print("[OK] Server correctly rejected invalid token")
        else:
            print("[ERROR] Server unexpectedly accepted invalid token")
    except Exception as e:
        print(f"[ERROR] Request failed: {str(e)}")

    print("\nTest complete!")

if __name__ == "__main__":
    test_link()
