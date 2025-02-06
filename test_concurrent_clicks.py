import requests
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import random

async def click_link(session, user_id, token):
    """Simulate a user clicking the verification link"""
    url = f"http://localhost:5000/verify/{token}"
    try:
        async with session.get(url) as response:
            result = await response.json()
            return {
                'user_id': user_id,
                'status': response.status,
                'result': result
            }
    except Exception as e:
        return {
            'user_id': user_id,
            'status': 'error',
            'result': str(e)
        }

async def generate_token(session, user_id):
    """Generate a token for a user"""
    url = "http://localhost:5000/generate_token"
    try:
        async with session.post(url, json={'user_id': user_id}) as response:
            result = await response.json()
            return result.get('token')
    except Exception as e:
        print(f"Error generating token for user {user_id}: {str(e)}")
        return None

async def test_concurrent_clicks():
    """Test many users clicking at almost the same time"""
    # Reset the server first
    try:
        requests.post("http://localhost:5000/reset")
    except Exception as e:
        print(f"Error resetting server: {str(e)}")
        return

    print("\nTesting concurrent clicks...")
    print("=" * 50)

    # Number of simultaneous users
    num_users = 20  # More than MAX_USERS to test overflow

    async with aiohttp.ClientSession() as session:
        # Generate tokens for all users first
        print("Generating tokens for users...")
        tokens = []
        for user_id in range(1000, 1000 + num_users):
            token = await generate_token(session, user_id)
            if token:
                tokens.append((user_id, token))
        
        if not tokens:
            print("Failed to generate tokens!")
            return

        print(f"\nSimulating {len(tokens)} users clicking simultaneously...")
        
        # Create tasks for all users to click at almost the same time
        tasks = []
        for user_id, token in tokens:
            task = click_link(session, user_id, token)
            tasks.append(task)

        # Execute all clicks concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Analyze results
        print(f"\nResults (took {end_time - start_time:.2f} seconds):")
        print("-" * 50)
        
        winners = []
        non_winners = []
        errors = []

        for result in results:
            user_id = result['user_id']
            if result['status'] == 200:
                if 'prize' in result['result']:
                    winners.append((user_id, result['result']['prize']))
                else:
                    non_winners.append((user_id, result['result']['message']))
            else:
                errors.append((user_id, result['result']))

        # Print winners
        print("\nWinners:")
        for user_id, prize in winners:
            if isinstance(prize, dict):
                print(f"User {user_id}: {prize['accounts']} account(s) for {prize['duration']}")
            else:
                print(f"User {user_id}: {prize}")

        # Print non-winners
        print("\nNon-winners:")
        for user_id, message in non_winners:
            print(f"User {user_id}: {message}")

        # Print errors if any
        if errors:
            print("\nErrors:")
            for user_id, error in errors:
                print(f"User {user_id}: {error}")

        # Summary
        print("\nSummary:")
        print(f"Total users: {num_users}")
        print(f"Winners: {len(winners)}")
        print(f"Non-winners: {len(non_winners)}")
        print(f"Errors: {len(errors)}")

if __name__ == "__main__":
    print("Starting concurrent click test...")
    asyncio.run(test_concurrent_clicks())
