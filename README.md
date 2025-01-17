# 0x Wallet Tracker
A Telegram Solana Address tracker integrated with Firebase and Helius Websocket to monitor and notify users of wallet activities such as swaps and transfers.

## Table of Contents
- Features
- Installation
- Usage & Configuration

## Features
- Realtime wallet activity tracking
- Firebase integration for storing user wallet data
- Telegram notifications for event triggers
- Concise commands for simplicity

## Installation

1. Clone repository

git clone https://github.com/Max17190/SOLWalletTracker.git
cd your-repo-name

3. Install Dependencies
pip install -r requirements.txt

4. Setup APIs
Telegram Bot via Botfather
Setup Firebase Realtime Databse
Webhook URL for hosting Helius Websocket
Helius API with Websocket

5. Setup Environment Variables
Create a ".env" file and use the example file as reference for adding API keys

## Usage & Configuration
- Receive real-time updates on wallet activity directly in your Telegram chat
- Event type (e.g., SWAP, TRANSFER)
- Wallet name and address
- Transaction signature and timestamp
- Dynamic latency in helius_helper.py
