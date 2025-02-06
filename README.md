# Mystery Box Telegram Bot

A Telegram bot that sends daily mystery box links and manages prizes for the first 10 people who click.

## Features

- Sends daily mystery box links at random times between 2 PM and 6 PM (Lebanon time)
- First 10 people to click get prizes
- Automatic winner notification
- Works in both private chats and groups
- Admin-only controls in groups

## Setup Instructions

1. Install Python 3.8 or higher

2. Clone this repository:
   ```bash
   git clone [repository-url]
   cd telegram_bot
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Get a Telegram Bot Token:
   - Talk to [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot using `/newbot`
   - Copy the bot token

5. Edit `bot.py`:
   - Replace `BOT_TOKEN` with your token from BotFather

6. Start the servers:
   ```bash
   # Start the verification server
   python verify_server.py
   
   # In a new terminal, start the bot
   python bot.py
   ```

## Usage

### User Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/subscribe` - Subscribe to daily links
- `/unsubscribe` - Unsubscribe from daily links

### Group Admin Commands
- `/subscribe` - Subscribe the group to daily links
- `/unsubscribe` - Unsubscribe the group

## Prize System

- First 10 people to click the link win prizes
- Winners are automatically notified
- Winners should contact @CrypticKimo to claim their prize

## Technical Details

- Verification server runs on `http://localhost:5000`
- Bot uses timezone-aware scheduling
- Automatic daily reset at midnight
- Winner tracking and verification system

## Requirements

See `requirements.txt` for a full list of dependencies.

## Support

For support or questions, contact @CrypticKimo on Telegram.
