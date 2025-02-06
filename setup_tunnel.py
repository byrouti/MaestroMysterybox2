import subprocess
import sys
import time
import re
import requests

def get_ngrok_url():
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except:
        return None

def setup_tunnel():
    print("Setting up secure tunnel for the verification server...")
    
    # Check if ngrok is running
    url = get_ngrok_url()
    if url:
        print(f"Tunnel is already running at: {url}")
        return url

    # Start ngrok
    try:
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", "5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        url = get_ngrok_url()
        if url:
            print(f"Tunnel created successfully!")
            print(f"Public URL: {url}")
            
            # Update the bot.py file with the new URL
            with open('bot.py', 'r') as file:
                content = file.read()
            
            # Replace the VERIFY_SERVER URL
            content = re.sub(
                r'VERIFY_SERVER = ".*"',
                f'VERIFY_SERVER = "{url}"',
                content
            )
            
            with open('bot.py', 'w') as file:
                file.write(content)
            
            print("\nUpdated bot.py with the new URL")
            print("\nInstructions:")
            print("1. Start the verify_server.py")
            print("2. Start the bot.py")
            print("3. The links will now work for all users!")
            
            return url
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTo fix this:")
        print("1. Download ngrok from https://ngrok.com/download")
        print("2. Extract ngrok.exe to this folder")
        print("3. Run 'ngrok config add-authtoken YOUR_TOKEN' with your ngrok token")
        print("4. Run this script again")
        return None

if __name__ == "__main__":
    setup_tunnel()
