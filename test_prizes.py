import requests
import random

def test_prize_distribution():
    # Base URL
    base_url = "http://localhost:5000"
    winners = []
    
    print("Testing prize distribution...\n")
    
    # Generate tokens for 15 users (more than MAX_USERS to test limits)
    for i in range(15):
        # Generate token
        user_id = 1000 + i  # Fake user IDs starting from 1000
        response = requests.post(
            f"{base_url}/generate_token",
            json={'user_id': user_id}
        )
        
        if response.status_code == 200:
            token = response.json()['token']
            
            # Verify token (simulate clicking)
            verify_response = requests.get(f"{base_url}/verify/{token}")
            
            if verify_response.status_code == 200:
                result = verify_response.json()
                if 'prize' in result:
                    winners.append({
                        'user_id': user_id,
                        'prize': result['prize']
                    })
                    print(f"User {user_id} won: {result['prize']['accounts']} account(s) for {result['prize']['duration']}")
                else:
                    print(f"User {user_id}: No prize (response: {result['message']})")
    
    print("\nSummary of winners:")
    print("-" * 50)
    for winner in winners:
        print(f"User {winner['user_id']}: {winner['prize']['accounts']} account(s) for {winner['prize']['duration']}")
    
    print(f"\nTotal winners: {len(winners)}")

if __name__ == "__main__":
    # Reset the server first
    requests.post("http://localhost:5000/reset")
    test_prize_distribution()
