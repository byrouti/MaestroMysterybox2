from flask import Flask, request
from flask_cors import CORS
import logging
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Track winners and last reset
winner_count = 0
winners = set()  # Store unique winners
MAX_WINNERS = 10
last_reset = datetime.now(pytz.timezone('Asia/Beirut'))

def should_reset_winners():
    """Check if we should reset the winners (at midnight Lebanon time)"""
    global last_reset
    now = datetime.now(pytz.timezone('Asia/Beirut'))
    
    # If it's a new day
    if now.date() > last_reset.date():
        last_reset = now
        return True
    return False

@app.route('/')
def home():
    """Home page with status"""
    return f"""
    <html>
        <head>
            <title>Prize Bot Status</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding-top: 50px;
                    background-color: #f0f0f0;
                }}
                .status {{
                    font-size: 24px;
                    margin: 20px;
                    padding: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <div class="status">
                <h1>🎁 Prize Bot Status</h1>
                <p>Prizes Remaining Today: {MAX_WINNERS - winner_count} of {MAX_WINNERS}</p>
            </div>
        </body>
    </html>
    """

@app.route('/claim')
def claim_prize():
    global winner_count, winners
    
    # Check if we need to reset winners
    if should_reset_winners():
        winner_count = 0
        winners.clear()
        logger.info("Reset winners for new day")
    
    # Get user's IP or some identifier
    user_id = request.remote_addr
    
    # Check if this user already won
    if user_id in winners:
        return f"""
        <html>
            <head>
                <title>Already Claimed</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 20px;
                        background-color: #f0f0f0;
                        max-width: 600px;
                        margin: 0 auto;
                    }}
                    .message {{
                        color: #ffa500;
                        font-size: 24px;
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="message">
                    <h1>⚠️ Already Claimed</h1>
                    <p>You have already claimed a prize today!</p>
                </div>
            </body>
        </html>
        """
    
    # Check if we still have prizes available
    if winner_count < MAX_WINNERS:
        winner_count += 1
        winners.add(user_id)
        logger.info(f"New winner: {user_id} (#{winner_count})")
        
        return f"""
        <html>
            <head>
                <title>Congratulations!</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 20px;
                        background-color: #f0f0f0;
                        max-width: 600px;
                        margin: 0 auto;
                    }}
                    .success {{
                        color: #28a745;
                        font-size: 32px;
                        margin-bottom: 20px;
                    }}
                    .message {{
                        font-size: 24px;
                        color: #333;
                        margin: 20px 0;
                        padding: 20px;
                        background: white;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .contact {{
                        color: #007bff;
                        font-weight: bold;
                        text-decoration: none;
                    }}
                    .contact:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <h1 class="success">🎉 Congratulations!</h1>
                <div class="message">
                    <p>You are winner #{winner_count} of {MAX_WINNERS}!</p>
                    <p>Contact <a href="https://t.me/cryptickimo" class="contact">@cryptickimo</a> to claim your prize!</p>
                </div>
            </body>
        </html>
        """
    else:
        return f"""
        <html>
            <head>
                <title>Sorry</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 20px;
                        background-color: #f0f0f0;
                        max-width: 600px;
                        margin: 0 auto;
                    }}
                    .message {{
                        color: #dc3545;
                        font-size: 24px;
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="message">
                    <h1>Sorry!</h1>
                    <p>All prizes have been claimed for today.<br>Try again tomorrow!</p>
                </div>
            </body>
        </html>
        """

@app.route('/status')
def get_status():
    """Get current winners status"""
    return {
        'winner_count': winner_count,
        'max_winners': MAX_WINNERS,
        'prizes_left': MAX_WINNERS - winner_count
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
