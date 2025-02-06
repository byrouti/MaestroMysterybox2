# Maestro Mystery Box Bot - Setup Instructions

## Prerequisites
1. Python 3.8 or higher
2. Internet connection
3. A Telegram account

## Step 1: Create a Telegram Bot
1. Open Telegram and search for "@BotFather"
2. Start a chat with BotFather and send `/newbot`
3. Follow the instructions to:
   - Set a name for your bot
   - Set a username for your bot (must end in 'bot')
4. **Save the API token** BotFather gives you - you'll need it later

## Step 2: Setup the Files
1. Unzip `maestro_mystery_box_bot.zip` to a folder
2. Open a terminal/command prompt in that folder
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Step 3: Configure the Bot
1. Open `bot.py` in a text editor
2. Find this line near the top:
   ```python
   BOT_TOKEN = "7963123621:AAE3iruUPGZh2shH50nk3cCvokKwvP8u7dA"
   ```
3. Replace it with your bot token from Step 1:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```

## Step 4: Run the Bot
1. First, start the verification server:
   ```bash
   python verify_server.py
   ```
2. Open a new terminal window in the same folder
3. Start the bot:
   ```bash
   python bot.py
   ```

## How the Bot Works
1. The bot sends daily links between 2 PM and 6 PM (Lebanon time)
2. 10 people can win prizes each day:
   - 1 person: 1 account for 1 month
   - 1 person: 2 accounts for 1 week
   - 1 person: 3 accounts for 1 week
   - 1 person: 4 accounts for 1 week
   - 1 person: 5 accounts for 1 week
   - 1 person: 6 accounts for 1 week
   - 1 person: 7 accounts for 3 days
   - 1 person: 8 accounts for 3 days
   - 1 person: 1 account for 1 day
   - 1 person: 2 accounts for 1 day

## User Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/subscribe` - Subscribe to daily links
- `/unsubscribe` - Unsubscribe from daily links

## Important Notes
1. Both `verify_server.py` and `bot.py` must be running for the bot to work
2. The system resets at midnight (Lebanon time)
3. Each user can only click once per day
4. Prizes are distributed randomly to the first 10 clickers

## Troubleshooting
1. If the bot doesn't respond:
   - Check that both scripts are running
   - Verify your bot token is correct
   - Make sure you have internet connection

2. If users can't click links:
   - Check that verify_server.py is running
   - Verify the server is running on port 5000

3. If you need to restart:
   - Stop both scripts (Ctrl+C)
   - Start verify_server.py first
   - Then start bot.py

For additional help or issues, contact the bot administrator.
