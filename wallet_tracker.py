from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import requests

# Load API Tokens from .env
load_dotenv("API.env")
TG_TOKEN: Final = os.getenv("TG_TOKEN")
HELIUS_TOKEN: Final = os.getenv("HELIUS_TOKEN")

# Bot name
BOT_USER: Final = '@OxSolBot'

# Check Valid Token
if not TG_TOKEN or HELIUS_TOKEN:
    raise ValueError('An API key is missing! Please check .env')

# SOL Addresses
wallet_addresses = {}

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Thank you for joining Ox Wallet Tracker!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please be patient, the tracker may be experiencing downtime')

async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Add a valid wallet address to track
    """
    if not context.args:
        await update.message.reply_text('Please provide SOL wallet address!')
        return
    sol_addy = str(context.args[0])

    if valid_address(sol_addy):
        wallet_addresses.add(sol_addy)
        await update.message.reply_text(f'Wallet {sol_addy} successfully added!')
    else:
        await update.message.reply_text(f'Wallet {sol_addy} is invalid!')

async def remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Remove a valid wallet from tracked list
    """
    if not context.args:
        await update.message.reply_text('Please provide a SOL wallet address!')
        return
    sol_addy = str(context.args[0])
    
    if sol_addy in wallet_addresses:
        wallet_addresses.remove(sol_addy)
        await update.message.reply_text(f'Successfuly removed wallet: {sol_addy}')
    else:
        await update.message.reply_text(f'Unable to remove wallet: {sol_addy}')


async def list_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display all tracked wallets, each on a seperate line
    """
    if not wallet_addresses:
        await update.message.reply_text('No wallets currently being tracked.')
    else:
        wallets = '\n'.join(wallet_addresses)
        await update.message.reply_text(f'Tracked Wallets:\n{wallets}')



# Verify Address
def valid_address(sol_addy):
    if 44 >= len(sol_addy) >= 32 and sol_addy not in wallet_addresses:
        return True
    return False

# Iterate Wallets
def get_wallets():
    for 

# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'
    if 'How are you' in processed:
        return 'Great, what about you?'
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USER in text:
            new_text: str = text.replace(BOT_USER, '').strip()
            response: str = handle_response(new_text)
        else:
            return 
    else:
        response: str = handle_response(text)

    print('Bot', response)
    await update.message.reply_text(response)    
    

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)