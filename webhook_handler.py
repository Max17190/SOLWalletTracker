from flask import Flask, request, jsonify
from telegram import Bot
import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, db
from firebase_helpers import get_user_wallets

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize Telegram bot
bot = Bot(token=os.getenv('TG_TOKEN'))

# Initialize Firebase Admin SDK
firebase_credentials_path = os.getenv('FIRE_JSON')
firebase_db_url = os.getenv('FIRE_PATH')

if not (firebase_credentials_path and firebase_db_url):
    raise ValueError("Firebase credentials or database URL is missing!")

cred = credentials.Certificate(firebase_credentials_path)
initialize_app(cred, {'databaseURL': firebase_db_url})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if data.get('type') == 'SWAP':
        account_address = data.get('accountAddress')

        # Get all users tracking this wallet
        all_users = db.reference('users').get() or {}

        for user_id, user_data in all_users.items():
            user_wallets = get_user_wallets(user_id)

            if account_address in user_wallets.values():
                wallet_name = next(name for name, addr in user_wallets.items() if addr == account_address)
                message = (
                    f"🔄 Swap Detected\n"
                    f"Wallet: {wallet_name}\n"
                    f"Address: {account_address}\n"
                    f"Transaction: {data.get('signature', 'Unknown')}"
                )
                bot.send_message(chat_id=user_id, text=message)

    return jsonify({'status': 'success'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
