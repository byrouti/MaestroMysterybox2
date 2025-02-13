import os
import json
import random
import string
import logging
import secrets
import urllib.parse
from datetime import datetime, timedelta, time
import pytz
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import re
import sys
from telegram.error import TelegramError
import asyncio
import psutil
import uuid

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "7963123621:AAE3iruUPGZh2shH50nk3cCvokKwvP8u7dA"

# Constants
MAX_WINNERS = 10
ADMIN_ID = 5754961056
GROUP_ID = None
is_bot_active = False

# Lebanon timezone
LEBANON_TIMEZONE = pytz.timezone('Asia/Beirut')

# Initialize global variables
winners = {}
users_clicked = set()
active_links = {}
available_prizes = [
    "Maestro premium account for 1 month",
    "Maestro premium account for 1 week",
    "Maestro premium account for 3 days",
    "Maestro premium account for 1 day"
]

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WINNERS_FILE = os.path.join(SCRIPT_DIR, 'winners.json')
ARCHIVE_FILE = os.path.join(SCRIPT_DIR, 'winners_archive.json')

# Load winners at startup
def load_winners():
    """Load winners from file"""
    global winners, users_clicked
    try:
        if os.path.exists(WINNERS_FILE):
            with open(WINNERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                winners = data.get('winners', {})
                users_clicked = set(data.get('users_clicked', []))
                
            logger.info(f"Loaded winners from {WINNERS_FILE}: {winners}")
            logger.info(f"Loaded users_clicked: {users_clicked}")
        else:
            logger.info(f"No winners file found at {WINNERS_FILE}")
            winners = {}
            users_clicked = set()
    except Exception as e:
        logger.error(f"Error loading winners: {e}")
        winners = {}
        users_clicked = set()

load_winners()

def save_winners():
    """Save winners to file"""
    try:
        # Create data to save
        data = {
            'winners': winners,
            'users_clicked': list(users_clicked)
        }
        
        # Save to file with absolute path
        with open(WINNERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Saved winners to {WINNERS_FILE}: {winners}")
        logger.info(f"Saved users_clicked: {users_clicked}")
    except Exception as e:
        logger.error(f"Error saving winners: {e}")
        raise  # Re-raise to see the full error

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id
    print(f"Start command called by user {user_id} with args: {context.args}")

    # Check if this is a click command
    if context.args and len(context.args) > 0:
        token = context.args[0]
        print(f"Found token: {token}")
        print(f"Active links: {active_links}")
        
        # Check if token exists
        if token not in active_links:
            print(f"Token {token} not found in active_links")
            await update.message.reply_text("Sorry, this link is no longer valid!")
            return

        # Get the prize
        prize = active_links[token]
        print(f"Found prize: {prize}")
        
        # Add to winners list
        winners[str(user_id)] = {
            'username': update.effective_user.username or "Unknown",
            'prize': prize,
            'date': datetime.now(LEBANON_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
        }
        print(f"Added to winners: {winners}")
        
        # Save winners immediately
        try:
            with open(WINNERS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'winners': winners, 'users_clicked': list(users_clicked)}, f)
            print(f"Saved winners to file: {WINNERS_FILE}")
        except Exception as e:
            print(f"Error saving winners: {e}")
        
        # Remove the token
        del active_links[token]
        
        await update.message.reply_text(
            f"🎉 Congratulations! You won: {prize}\n\n"
            f"Please contact @CrypticKimo to claim your prize!\n"
            f"👉 https://t.me/CrypticKimo"
        )
        return

    # Only admin can use regular start command
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    await update.message.reply_text("Welcome to MaestroMysteryBox Bot!")

async def start_mmb(update, context):
    """Start sending mystery box links"""
    global is_bot_active, GROUP_ID

    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    GROUP_ID = update.effective_chat.id
    is_bot_active = True

    # Start the job queue
    if context.job_queue:
        # First stop any existing jobs
        for job in context.job_queue.jobs():
            job.schedule_removal()
        
        # Schedule one random time between 2 PM and 6 PM
        lebanon_tz = pytz.timezone('Asia/Beirut')
        
        # Generate a random minute between 0-59
        random_minute = random.randint(0, 59)
        # Generate a random hour between 14-17 (2 PM - 5:59 PM)
        random_hour = random.randint(14, 17)
        
        # Create time object for the random time
        random_time = time(random_hour, random_minute, tzinfo=lebanon_tz)
        
        # Schedule daily link at random time
        context.job_queue.run_daily(send_prize_link, time=random_time)

        # Reset at midnight
        midnight = time(0, 0, tzinfo=lebanon_tz)
        context.job_queue.run_daily(
            lambda ctx: (
                winners.clear(),
                users_clicked.clear(),
                save_winners(),  # Save empty winners list
                available_prizes.extend([
                    "Maestro premium account for 1 month",
                    "Maestro premium account for 1 week",
                    "Maestro premium account for 3 days",
                    "Maestro premium account for 1 day"
                ])
            ),
            time=midnight
        )

    await update.message.reply_text("MaestroMysteryBox started!")

async def send_prize_link(context):
    """Send a prize link at scheduled time"""
    if not is_bot_active:
        return

    try:
        # Generate a random token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # Get a random prize
        prize = random.choice(available_prizes)
        available_prizes.remove(prize)
        
        # Store the token and prize
        active_links[token] = prize
        
        # Create the mystery box link with the prize
        encoded_prize = urllib.parse.quote(prize)
        link = f"https://byrouti.github.io/MaestroMysterybox2/prize.html?token={token}&prize={encoded_prize}"
        
        # Send the message with the link - adding blue color
        message = f'🎁 <a href="{link}" style="color: #0088cc; text-decoration: underline;">MaestroMysteryBox</a> 🎁'
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Prize link sent with prize: {prize}")
        
    except Exception as e:
        logger.error(f"Error sending prize link: {e}")

async def stop_mmb(update, context):
    """Stop sending mystery box links"""
    global is_bot_active
    
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    is_bot_active = False
    
    # Remove all jobs from queue
    if context.job_queue:
        # Stop all current jobs
        for job in context.job_queue.jobs():
            job.schedule_removal()
        context.job_queue.stop()
    
    await update.message.reply_text("Bot stopped! Use /start_mmb to start again.")

async def send_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send mystery box link"""
    if not update.effective_user or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    try:
        # Generate unique token
        token = str(uuid.uuid4())
        print(f"Generated token: {token}")

        # Get random prize
        prize = random.choice(available_prizes)
        print(f"Selected prize: {prize}")

        # Store token and prize
        active_links[token] = prize
        print(f"Active links after adding: {active_links}")

        # Create mystery box link
        bot_username = (await context.bot.get_me()).username
        mystery_box_link = f"https://t.me/{bot_username}?start={token}"

        await update.message.reply_text(
            f"🎁 New Mystery Box!\n\n"
            f"🔗 Link: {mystery_box_link}"
        )
        print("Sent mystery box link")

    except Exception as e:
        print(f"Error in send_mmb: {e}")
        await update.message.reply_text(
            text="Error sending mystery box"
        )

async def winners_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current winners"""
    if not update.effective_user or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    try:
        print(f"Current winners in memory: {winners}")
        print(f"Looking for winners file at: {WINNERS_FILE}")
        
        # Try to read winners file
        try:
            with open(WINNERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                current_winners = data.get('winners', {})
            print(f"Winners from file: {current_winners}")
        except FileNotFoundError:
            print(f"Winners file not found at {WINNERS_FILE}")
            current_winners = {}
        except Exception as e:
            print(f"Error reading winners file: {e}")
            current_winners = {}

        if not current_winners:
            print("No winners found")
            await update.message.reply_text("No winners yet!")
            return

        message = "🏆 Recent Winners:\n\n"
        
        # Sort winners by date, most recent first
        sorted_winners = sorted(
            current_winners.items(),
            key=lambda x: datetime.strptime(x[1]['date'], '%Y-%m-%d %H:%M:%S'),
            reverse=True
        )
        
        for user_id, data in sorted_winners:
            message += f"👤 Username: {data['username']}\n"
            message += f"🎁 Prize: {data['prize']}\n"
            message += f"⏰ Date: {data['date']}\n"
            message += "─────────────\n"

        await update.message.reply_text(message)
        print("Sent winners message")
        
    except Exception as e:
        print(f"Error in winners_mmb: {e}")
        await update.message.reply_text("Error displaying winners. Please try again.")

async def record_winner(user_id, username, prize):
    """Record a winner"""
    now = datetime.now(LEBANON_TIMEZONE)
    winners[user_id] = {
        'username': username,
        'prize': prize,
        'date': now.strftime('%Y-%m-%d %H:%M:%S')
    }
    users_clicked.add(user_id)
    save_winners()

async def reset_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset bot state"""
    if not update.effective_user or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    try:
        # Clear all data
        winners.clear()
        users_clicked.clear()
        active_links.clear()
        
        # Reset available prizes
        available_prizes.clear()
        available_prizes.extend([
            "Maestro premium account for 1 month",
            "Maestro premium account for 1 week",
            "Maestro premium account for 3 days",
            "Maestro premium account for 1 day"
        ])
        
        # Save empty winners file
        save_winners()
        
        await update.message.reply_text("Bot has been reset! All data cleared.")
        logger.info("Bot reset successfully")
        
    except Exception as e:
        logger.error(f"Error resetting bot: {e}")
        await update.message.reply_text("Error resetting bot. Please try again.")

async def restart_mmb(update, context):
    """Restart the bot"""
    global GROUP_ID, is_bot_active
    
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    winners.clear()
    users_clicked.clear()
    available_prizes.clear()
    available_prizes.extend([
        "Maestro premium account for 1 month",
        "Maestro premium account for 1 week",
        "Maestro premium account for 3 days",
        "Maestro premium account for 1 day"
    ])
    GROUP_ID = update.effective_chat.id
    is_bot_active = True
    await update.message.reply_text("Bot restarted successfully!")

async def help_command(update, context):
    """Show help message"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    help_text = """
Available Commands:

/start - Initialize the bot
/help - Show this help message
/start_mmb - Start sending mystery box links
/stop_mmb - Stop sending mystery box links
/send_mmb - Send a mystery box link manually
/winners_mmb - Show current winners
/reset_mmb - Reset winners and clicks
/restart_mmb - Restart the bot
/test_mmb - Show bot status
/archive_mmb - Show archived winners

All commands are admin-only.
"""
    await update.message.reply_text(help_text)

async def test_mmb(update, context):
    """Show bot status"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    status_message = "*MaestroMysteryBot*\n\n"
    status_message += "*Bot Status:*\n"
    status_message += f"Remaining Clicks: {MAX_WINNERS - len(users_clicked)}\n"
    status_message += f"Total Winners: {len(winners)}\n"
    status_message += f"Bot Active: {'Yes' if is_bot_active else 'No'}\n"

    await update.message.reply_text(
        text=status_message,
        parse_mode=ParseMode.MARKDOWN
    )

async def show_archive(update, context):
    """Show archived winners"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    try:
        with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
            archive = json.load(f)
    except FileNotFoundError:
        await update.message.reply_text("No archived winners found.")
        return
    except Exception as e:
        logger.error(f"Error reading archive: {e}")
        await update.message.reply_text("Error reading archive file.")
        return

    if not archive.get('archives'):
        await update.message.reply_text("No archived winners found.")
        return

    message = "📜 Winners Archive:\n\n"
    for entry in archive['archives']:
        message += f"🗓 Archive from {entry['date']}:\n"
        for user_id, data in entry['winners'].items():
            message += f"👤 {data['username']}\n"
            message += f"🎁 {data['prize']}\n"
            message += f"⏰ {data['date']}\n\n"
        message += "─────────────\n"

    # Split message if it's too long
    if len(message) > 4000:
        messages = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for msg in messages:
            await update.message.reply_text(msg)
    else:
        await update.message.reply_text(message)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    # Don't try to send messages if update is None
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, something went wrong. Please try again later."
        )

def reset_prizes(context):
    """Reset available prizes and clear winners at midnight"""
    logger.info("Running daily prize reset")
    
    try:
        # Archive current winners before reset
        archive_winners()
        
        # Clear winners and clicked users
        global winners, users_clicked, available_prizes, active_links
        winners.clear()
        users_clicked.clear()
        active_links.clear()
        
        # Reset available prizes
        available_prizes.clear()
        available_prizes.extend([
            "Maestro premium account for 1 month",
            "Maestro premium account for 1 week",
            "Maestro premium account for 3 days",
            "Maestro premium account for 1 day"
        ])
        
        # Save empty winners
        save_winners()
        
        logger.info("Daily prize reset completed successfully")
        
        if GROUP_ID:
            context.bot.send_message(
                chat_id=GROUP_ID,
                text="🔄 A new day has begun! All prizes have been reset. Good luck everyone! 🍀"
            )
    except Exception as e:
        logger.error(f"Error in daily prize reset: {e}")

def archive_winners():
    """Archive current winners and save to a file"""
    try:
        # Get current date for filename
        current_date = datetime.now(LEBANON_TIMEZONE).strftime('%Y-%m-%d')
        archive_filename = f'winners_archive_{current_date}.json'
        
        # Create archive data
        archive_data = {
            'date': current_date,
            'winners': winners,
            'users_clicked': list(users_clicked)  # Convert set to list for JSON
        }
        
        # Save to archive file
        with open(archive_filename, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, indent=4, ensure_ascii=False)
        
        # Clear current winners and users
        winners.clear()
        users_clicked.clear()
        
        # Save empty winners file
        save_winners()
        
        logger.info(f"Winners archived to {archive_filename}")
        
    except Exception as e:
        logger.error(f"Error archiving winners: {e}")

async def archive_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Archive current winners and save to a file"""
    if not update.effective_user or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    try:
        # Get current date for filename
        current_date = datetime.now(LEBANON_TIMEZONE).strftime('%Y-%m-%d')
        archive_filename = f'winners_archive_{current_date}.json'
        
        # Create archive data
        archive_data = {
            'date': current_date,
            'winners': winners,
            'users_clicked': list(users_clicked)  # Convert set to list for JSON
        }
        
        # Save to archive file
        with open(archive_filename, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, indent=4, ensure_ascii=False)
        
        # Clear current winners and users
        winners.clear()
        users_clicked.clear()
        
        # Save empty winners file
        save_winners()
        
        await update.message.reply_text(f"Winners archived to {archive_filename}!")
        logger.info(f"Winners archived to {archive_filename}")
        
    except Exception as e:
        logger.error(f"Error archiving winners: {e}")
        await update.message.reply_text("Error archiving winners. Please try again.")

def main():
    """Start the bot"""
    # Initialize bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Add error handler
    application.add_error_handler(error_handler)

    # Add handlers
    application.add_handler(CommandHandler("start", start))  # Handle both start and clicks
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start_mmb", start_mmb))
    application.add_handler(CommandHandler("stop_mmb", stop_mmb))
    application.add_handler(CommandHandler("send_mmb", send_mmb))
    application.add_handler(CommandHandler("winners_mmb", winners_mmb))
    application.add_handler(CommandHandler("archive_mmb", archive_mmb))
    application.add_handler(CommandHandler("reset_mmb", reset_mmb))
    application.add_handler(CommandHandler("restart_mmb", restart_mmb))
    application.add_handler(CommandHandler("test_mmb", test_mmb))

    # Set up job queue for automatic link sending
    if application.job_queue:
        lebanon_tz = pytz.timezone('Asia/Beirut')
        
        # Schedule daily prize reset at midnight Lebanon time
        midnight = time(0, 0, tzinfo=lebanon_tz)
        application.job_queue.run_daily(reset_prizes, time=midnight)

    logger.info("Bot started! Press Ctrl+C to stop.")
    
    return application

if __name__ == '__main__':
    # First kill any existing Python processes
    try:
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'python.exe' and proc.info['pid'] != current_pid:
                try:
                    psutil.Process(proc.info['pid']).terminate()
                except:
                    pass
    except:
        pass

    try:
        app2 = main()
        app2.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
