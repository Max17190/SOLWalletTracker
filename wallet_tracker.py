from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import requests
import firebase_admin
from firebase_admin import credentials, db
import asyncio

# Load Environment Variables
load_dotenv("API.env")

# Load Firebase API
FIREBASE_CREDENTIALS: Final = os.getenv('FIRE_JSON')
FIREBASE_DB: Final = os.getenv('FIRE_URL')

# Initialize Firebase
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_DB
})

# Load TG BOT AND HELIUS API
TG_TOKEN: Final = os.getenv("TG_TOKEN")
HELIUS_TOKEN: Final = os.getenv("HELIUS_TOKEN")

# Bot name
BOT_USER: Final = '@OxSolBot'

# Check Valid Token
if not (TG_TOKEN and HELIUS_TOKEN and FIREBASE_CREDENTIALS and FIREBASE_DB):
    raise ValueError('An API key is missing! Please check .env')

# Global State
user_states = {}

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Thank you for joining Ox Wallet Tracker!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please be patient, the tracker may be experiencing downtime')

async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Add a valid wallet address to track
    """
    user_id = str(update.message.chat.id)
    user_states[user_id] = {"state": "waiting_for_wallet_name"}
    await update.message.reply_text('Please provide a name for your wallet')
    
async def remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Remove a wallet by its name.
    """
    user_id = str(update.message.chat.id)

    if not context.args:
        await update.message.reply_text('Please provide the name of the wallet to remove!')
        return

    wallet_name = context.args[0]

    # Fetch wallets from Firebase
    user_ref = db.reference(f'users/{user_id}/wallets')
    user_wallets = user_ref.get() or {}

    if wallet_name in user_wallets:
        # Remove the wallet by its name
        del user_wallets[wallet_name]
        user_ref.set(user_wallets)
        await update.message.reply_text(f'Successfully removed wallet: "{wallet_name}"')
    else:
        await update.message.reply_text(f'No wallet found with the name "{wallet_name}".')

async def list_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display all tracked wallets with their names and addresses.
    """
    user_id = str(update.message.chat.id)

    # Fetch wallets from Firebase
    user_ref = db.reference(f'users/{user_id}/wallets')
    user_wallets = user_ref.get() or {}

    if not user_wallets:
        await update.message.reply_text('No wallets are currently being tracked.')
    else:
        # Format the list of wallets
        wallets_list = '\n'.join([f'{name}: {address}' for name, address in user_wallets.items()])
        await update.message.reply_text(f'Tracked Wallets:\n{wallets_list}')

# Verify Address
def valid_address(sol_addy):
    if 44 >= len(sol_addy) >= 32:
        return True
    return False

# Reset User State
async def timeout_user_state(user_id: str, timeout: int = 120):
    await asyncio.sleep(timeout)
    if user_id in user_states:
        del user_states[user_id]

# Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'
    if 'How are you' in processed:
        return 'Great, what about you?'
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle user inputs based on current state
    """
    user_id = str(update.message.chat.id)
    user_input = update.message.text.strip()

    message_type: str = update.message.chat.type
    text: str = update.message.text

    # State 1: Wallet Name
    if user_id in user_states:
        state_info = user_states[user_id]

        # Save Wallet Name
        if state_info['state'] == 'waiting_for_wallet_name':
            user_states[user_id] = {
                'state': 'waiting_for_wallet_address',
                'wallet_name': user_input
            }

            await update.message.reply_text(f'Got it! Now provide the wallet address for {user_input}')
            return
        
    # State 2: Wallet Address
    elif state_info['state'] == 'waiting_for_wallet_address':
        wallet_name = state_info['wallet_name']
        sol_addy = user_input

        # Save to Firebase
        if valid_address(sol_addy):
            user_ref = db.reference(f'users/{user_id}/wallets')
            user_wallets = user_ref.get() or {}

            if wallet_name not in user_wallets:
                user_wallets[wallet_name] = sol_addy
                user_ref.set(user_wallets)
                await update.message.reply_text(f'Wallet {wallet_name} successfully added: {sol_addy}')
            else:
                await update.message.reply_text(f'A wallet with name {wallet_name} already exists!')

        else: 
            await update.message.reply_text(f'Provided address is invalid: {sol_addy}')
        
        # Clear state
        del user_states[user_id]
        return
    
    await update.message.reply_text(f'Please add a new wallet :D')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    app = Application.builder().token(TG_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('add_wallet', add_wallet))
    app.add_handler(CommandHandler('remove_wallet', remove_wallet))  
    app.add_handler(CommandHandler('list_wallet', list_wallet))

    # Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error Handler
    app.add_error_handler(error)

    # Start polling
    print('Polling...')
    app.run_polling(poll_interval=3)
