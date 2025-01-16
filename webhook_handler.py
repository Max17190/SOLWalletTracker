import asyncio
import json
from telegram import Bot
import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, db
from firebase_helpers import get_user_wallets
from helius_helpers import mock_start_server, mock_generate_event
import websockets

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

async def process_event(event_data):
    data = json.loads(event_data)
    if data.get('type') in ['SWAP', 'TRANSFER']:
        account_address = data.get('accountAddress')
        all_users = db.reference('users').get() or {}
        for user_id, user_data in all_users.items():
            user_wallets = get_user_wallets(user_id)
            if account_address in user_wallets.values():
                wallet_name = next(name for name, addr in user_wallets.items() if addr == account_address)
                message = (
                    f"🔔 Event Detected: {data['type']}\n"
                    f"Wallet: {wallet_name}\n"
                    f"Address: {account_address}\n"
                    f"Transaction: {data.get('signature', 'Unknown')}\n"
                    f"Timestamp: {data.get('timestamp', 'Unknown')}"
                )
                await bot.send_message(chat_id=user_id, text=message)

async def connect_to_mock_websocket():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            await process_event(message)

async def main():
    await asyncio.gather(
        mock_start_server(),
        connect_to_mock_websocket()
    )

if __name__ == '__main__':
    asyncio.run(main())
