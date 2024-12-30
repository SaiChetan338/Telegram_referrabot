from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import sqlite3
import asyncio

# Telegram Bot Token
TOKEN = 'YOUR_BOT_TOKEN'

# Initialize the database
def init_db():
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            referral_code TEXT UNIQUE,
            referrals INTEGER DEFAULT 0,
            referred_by INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Add a new user
def add_user(user_id, username, referral_code, referred_by=None):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, referral_code, referred_by)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, referral_code, referred_by))
    conn.commit()
    conn.close()

# Check if a referral code exists
def check_referral_code(referral_code):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE referral_code = ?", (referral_code,))
    user = cursor.fetchone()
    conn.close()
    return user

# Increment referral count for a user
def increment_referrals(user_id):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Get referral stats
def get_referrals(user_id):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT referrals FROM users WHERE id = ?", (user_id,))
    referrals = cursor.fetchone()
    conn.close()
    return referrals[0] if referrals else 0

# Function to start a conversation and register a user
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Check if user is already registered
    conn = sqlite3.connect('referral_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        referral_code = f"REF{user_id}"  # Generate a unique referral code based on user ID
        add_user(user_id, username, referral_code)
        await update.message.reply_text(f"Welcome, {username}! Your referral code is: {referral_code}")
    else:
        await update.message.reply_text(f"Welcome back, {username}! Your referral code is: {user[2]}")

    conn.close()

# Function to handle referrals
async def referral(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    referred_by_user_id = None

    if context.args:
        referred_by_user_id = context.args[0]

    if referred_by_user_id:
        # Check if the referral code is valid
        referral_code_check = check_referral_code(referred_by_user_id)

        if referral_code_check:
            # Register the referral
            increment_referrals(referred_by_user_id)
            add_user(user_id, update.message.from_user.username, f"REF{user_id}", referred_by=referred_by_user_id)
            await update.message.reply_text(f"Referral successful! You were referred by {referred_by_user_id}.")
        else:
            await update.message.reply_text("Invalid referral code.")
    else:
        await update.message.reply_text("Please provide a valid referral code.")

# Function to show the number of referrals
async def myreferrals(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    referral_count = get_referrals(user_id)
    await update.message.reply_text(f"You have referred {referral_count} people.")

# Function to display the leaderboard
async def leaderboard(update: Update, context: CallbackContext):
    conn = sqlite3.connect('referral_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, referrals FROM users ORDER BY referrals DESC LIMIT 10")
    top_referrers = cursor.fetchall()
    conn.close()

    leaderboard_text = "Leaderboard (Top 10 Referrers):\n\n"
    for index, (username, referrals) in enumerate(top_referrers, start=1):
        leaderboard_text += f"{index}. {username} - {referrals} referrals\n"

    await update.message.reply_text(leaderboard_text)

# Setup the bot
async def main():
    init_db()  # Initialize the database when starting the bot

    application = Application.builder().token(TOKEN).build()

    # Adding new command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("referral", referral))
    application.add_handler(CommandHandler("myreferrals", myreferrals))
    application.add_handler(CommandHandler("leaderboard", leaderboard))

    # Start polling for updates
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
