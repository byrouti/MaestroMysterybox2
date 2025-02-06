import requests
from telegram import Bot
import asyncio
import logging
import sys

# Set console to UTF-8 mode for emoji support
sys.stdout.reconfigure(encoding='utf-8')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token - using the same one from bot.py
BOT_TOKEN = "7963123621:AAE3iruUPGZh2shH50nk3cCvokKwvP8u7dA"

async def test_message():
    print("Testing Maestro Mystery Box message format...\n")
    
    # Create bot instance
    bot = Bot(token=BOT_TOKEN)
    
    # Get a test verification link
    base_url = "http://localhost:5000"
    test_user_id = 5001
    
    try:
        # Reset server first
        requests.post(f"{base_url}/reset")
        
        # Generate token
        response = requests.post(
            f"{base_url}/generate_token",
            json={'user_id': test_user_id}
        )
        
        if response.status_code == 200:
            verification_link = f"{base_url}/verify/{response.json()['token']}"
            
            # Create the message
            message = (
                "🎁 Click on [Maestro Mystery Box]({}) to win!\n\n"
                "⚠️ Important:\n"
                "• First 10 people to click will win exclusive prizes\n"
                "• You can only click once per day\n"
                "• Winners will be contacted with prize details\n\n"
                "Good luck! 🍀"
            ).format(verification_link)
            
            print("Message Preview (in Telegram, 'Maestro Mystery Box' will be a clickable link):")
            print("=" * 70)
            print(message)
            print("=" * 70)
            
            print("\nIn Telegram:")
            print("• The text 'Maestro Mystery Box' will be blue and clickable")
            print("• Clicking it will take you directly to the verification page")
            print("• The actual URL will be hidden for a cleaner look")
            
            print("\nTo test in Telegram, you need to:")
            print("1. Subscribe to the bot using /subscribe")
            print("2. Wait for the daily link (sent between 2 PM - 6 PM Lebanon time)")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(test_message())
