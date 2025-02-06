import secrets
import logging
from datetime import datetime, time
import pytz
import random
import sys
from telegram import Update, Chat
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue
from telegram.error import TelegramError

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def generate_url_token(length=16):
    """Generates a secure random URL-safe token."""
    return secrets.token_urlsafe(length)

# Bot token
BOT_TOKEN = "7963123621:AAE3iruUPGZh2shH50nk3cCvokKwvP8u7dA"

# Constants
MAX_WINNERS = 10
LEBANON_TIMEZONE = pytz.timezone('Asia/Beirut')
ADMIN_ID = 5754961056
GROUP_ID = None
is_bot_active = False

# Prize pool
available_prizes = [
    "1 Free Maestro Premium Account for 1 month",
    "1 Free Maestro Premium Account for 1 week",
    "1 Free Maestro Premium Account for 1 week",
    "1 Free Maestro Premium Account for 1 week",
    "1 Free Maestro Premium Account for 1 week",
    "1 Free Maestro Premium Account for 1 week",
    "1 Free Maestro Premium Account for 1 week",
    "1 Free Maestro Premium Account for 1 week",
    "1 Free Maestro Premium Account for 1 week",
    "1 Free Maestro Premium Account for 1 week"
]

# Store winners and clicked users
winners = {}  # Store winners
users_clicked = set()  # Track users who clicked
active_links = {}  # {token: {'prize': str, 'created_at': datetime}}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    global GROUP_ID, is_bot_active
    
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    GROUP_ID = update.effective_chat.id
    is_bot_active = True
    await update.message.reply_text("Bot started! Use /help to see available commands.")

async def start_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start sending mystery box links"""
    global GROUP_ID, is_bot_active
    
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    GROUP_ID = update.effective_chat.id
    is_bot_active = True
    await update.message.reply_text("MaestroMysteryBox started! Links will be sent every minute.")

async def stop_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop sending mystery box links"""
    global is_bot_active
    
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    is_bot_active = False
    await update.message.reply_text("Bot stopped! Use /start_mmb to start again.")

async def send_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually send a mystery box link"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    if not GROUP_ID:
        await update.message.reply_text("Please use /start first!")
        return

    if available_prizes and len(users_clicked) < MAX_WINNERS:
        prize = random.choice(available_prizes)
        available_prizes.remove(prize)  # Remove the prize from available ones
        
        # Record the winner immediately
        await add_winner(
            user_id=ADMIN_ID,  # Using admin ID
            username="CrypticKimo",  # Hardcoded for testing
            prize=prize
        )
        
        token = generate_url_token()
        link = f"https://maestromysterybox.netlify.app/prize.html?t={token}"
        
        message = f"🎁 <a href='{link}'>MaestroMysteryBox</a> 🎁\n\nClick fast to claim your prize! 🔥"

        try:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            await update.message.reply_text("✅ Link sent successfully!")
        except Exception as e:
            # Remove the winner if sending fails
            if ADMIN_ID in winners:
                del winners[ADMIN_ID]
            if ADMIN_ID in users_clicked:
                users_clicked.remove(ADMIN_ID)
            available_prizes.append(prize)  # Put the prize back
            await update.message.reply_text(f"❌ Failed to send link: {str(e)}")
    else:
        if len(users_clicked) >= MAX_WINNERS:
            await update.message.reply_text("❌ Maximum winners reached!")
        else:
            await update.message.reply_text("❌ No more prizes available!")

async def winners_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current winners"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    if not winners:
        await update.message.reply_text("🏆 No winners yet!")
        return

    message = "🏆 <b>Recent Winners:</b>\n\n"
    
    # Sort winners by date, most recent first
    sorted_winners = sorted(
        winners.items(),
        key=lambda x: datetime.strptime(x[1]['date'], '%Y-%m-%d %H:%M:%S'),
        reverse=True
    )
    
    for user_id, data in sorted_winners:
        message += f"👤 <b>{data['username']}</b>\n"
        message += f"🎁 {data['prize']}\n"
        message += f"📅 {data['date']}\n\n"

    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML
    )

async def reset_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset all winners and clicks"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return
        
    # Clear winners and clicks
    winners.clear()
    users_clicked.clear()
    
    # Reset available prizes
    available_prizes.clear()
    available_prizes.extend([
        "1 Free Maestro Premium Account for 1 month",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week"
    ])
    
    await update.message.reply_text("✅ All winners and clicks have been reset!")

async def restart_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "1 Free Maestro Premium Account for 1 month",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week",
        "1 Free Maestro Premium Account for 1 week"
    ])
    GROUP_ID = update.effective_chat.id
    is_bot_active = True
    await update.message.reply_text("Bot restarted successfully!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    help_text = """
Available Commands:

/start - Initialize the bot
/start_mmb - Start sending mystery box links
/stop_mmb - Stop sending links
/send_mmb - Send a link manually
/winners_mmb - Show current winners
/reset_mmb - Reset winners and clicks
/restart_mmb - Restart the bot
/help - Show this help message
/test_mmb - Show bot status

All commands are admin-only.
"""
    await update.message.reply_text(help_text)

async def send_prize_link(context: ContextTypes.DEFAULT_TYPE):
    """Automatic link sender"""
    if not GROUP_ID or not is_bot_active:
        return

    if available_prizes and len(users_clicked) < MAX_WINNERS:
        prize = random.choice(available_prizes)
        available_prizes.remove(prize)  # Remove the prize from available ones
        token = generate_url_token()
        link = f"https://maestromysterybox.netlify.app/prize.html?t={token}"
        
        message = f"🎁 <a href='{link}'>MaestroMysteryBox</a> 🎁\n\nClick fast to claim your prize! 🔥"

        try:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
        except Exception as e:
            available_prizes.append(prize)  # Put the prize back if sending failed
            logging.error(f"Failed to send automatic link: {str(e)}")

async def record_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Record when a user clicks a link"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    token = context.args[0] if context.args else None

    if not token or token not in active_links:
        await update.message.reply_text("Invalid or expired link!")
        return

    if user_id in users_clicked:
        await update.message.reply_text("You have already claimed a prize!")
        return

    if len(users_clicked) >= MAX_WINNERS:
        await update.message.reply_text("All prizes have been claimed!")
        return

    # Record the win
    link_data = active_links[token]
    users_clicked.add(user_id)
    winners[user_id] = {
        'username': username,
        'prize': link_data['prize'],
        'date': link_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    }

    # Remove the used token
    del active_links[token]

    await update.message.reply_text(f"Congratulations! You won: {link_data['prize']}")

async def clean_old_links(context: ContextTypes.DEFAULT_TYPE):
    """Clean old links"""
    now = datetime.now(LEBANON_TIMEZONE)
    expired_tokens = [
        token for token, data in active_links.items()
        if (now - data['created_at']).total_seconds() > 3600  # 1 hour
    ]
    for token in expired_tokens:
        link_data = active_links[token]
        available_prizes.append(link_data['prize'])  # Put prize back
        del active_links[token]

async def test_mmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Sorry, only admin can use this command.")
        return

    status_message = "🤖 *MaestroMysteryBot*\n\n"
    status_message += "📊 *Bot Status:*\n"
    status_message += f"🎯 Remaining Clicks: {MAX_WINNERS - len(users_clicked)}\n"
    status_message += f"🏆 Total Winners: {len(winners)}\n"
    status_message += f"🔵 Bot Active: {'Yes' if is_bot_active else 'No'}\n"

    await update.message.reply_text(
        status_message,
        parse_mode=ParseMode.MARKDOWN
    )

async def add_winner(user_id: int, username: str, prize: str):
    """Add a winner to the winners list"""
    current_time = datetime.now(LEBANON_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
    winners[user_id] = {
        'username': username,
        'prize': prize,
        'date': current_time
    }
    users_clicked.add(user_id)

def main():
    """Start the bot"""
    try:
        # Initialize bot
        application = Application.builder().token(BOT_TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("start_mmb", start_mmb))
        application.add_handler(CommandHandler("stop_mmb", stop_mmb))
        application.add_handler(CommandHandler("send_mmb", send_mmb))
        application.add_handler(CommandHandler("winners_mmb", winners_mmb))
        application.add_handler(CommandHandler("reset_mmb", reset_mmb))
        application.add_handler(CommandHandler("restart_mmb", restart_mmb))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("test_mmb", test_mmb))  # Add test command
        application.add_handler(CommandHandler("click", record_click))  # Add click handler

        # Set up job queue for automatic link sending
        if application.job_queue:
            application.job_queue.run_repeating(
                send_prize_link,
                interval=60,  # Send every minute
                first=10  # Wait 10 seconds before first send
            )

            # Reset at midnight
            lebanon_tz = pytz.timezone('Asia/Beirut')
            midnight = time(0, 0, tzinfo=lebanon_tz)
            application.job_queue.run_daily(
                lambda ctx: winners.clear() and users_clicked.clear() and available_prizes.extend([
                    "1 Free Maestro Premium Account for 1 month",
                    "1 Free Maestro Premium Account for 1 week",
                    "1 Free Maestro Premium Account for 1 week",
                    "1 Free Maestro Premium Account for 1 week",
                    "1 Free Maestro Premium Account for 1 week",
                    "1 Free Maestro Premium Account for 1 week",
                    "1 Free Maestro Premium Account for 1 week",
                    "1 Free Maestro Premium Account for 1 week",
                    "1 Free Maestro Premium Account for 1 week",
                    "1 Free Maestro Premium Account for 1 week"
                ]),
                time=midnight
            )

            # Clean old links every hour
            application.job_queue.run_repeating(
                clean_old_links,
                interval=3600,  # Clean every hour
                first=3600  # Start after 1 hour
            )

        # Start bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
