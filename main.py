from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import sqlite3
import asyncio

# Telegram Bot Token
TOKEN = 'YOUR_BOT_TOKEN'

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
        # Generate referral link
        referral_link = f"https://t.me/{update.message.bot.username}?start={user_id}"

        # Register user
        cursor.execute("INSERT INTO users (id, username, referral_link) VALUES (?, ?, ?)",
                       (user_id, username, referral_link))
        conn.commit()
        await update.message.reply_text(f"Welcome, {username}! Your referral link is: {referral_link}")
    else:
        await update.message.reply_text(f"Welcome back, {username}! Your referral link is: {user[2]}")

    conn.close()

# Function to display the help command
async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Welcome to the Referral Bot!\n\n"
        "Available commands:\n"
        "/start - Register or get your referral link\n"
        "/help - Get a list of commands\n"
        "/myreferrals - See how many people you've referred\n"
        "/leaderboard - View the top referrers"
    )
    await update.message.reply_text(help_text)

# Function to show the number of referrals
async def myreferrals(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    conn = sqlite3.connect('referral_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (user_id,))
    referral_count = cursor.fetchone()[0]
    conn.close()

    await update.message.reply_text(f"You have referred {referral_count} people.")

# Function to show the leaderboard
async def leaderboard(update: Update, context: CallbackContext):
    conn = sqlite3.connect('referral_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, COUNT(*) as referrals FROM users GROUP BY referred_by ORDER BY referrals DESC LIMIT 10")
    top_referrers = cursor.fetchall()
    conn.close()

    leaderboard_text = "Leaderboard (Top 10 Referrers):\n\n"
    for index, (username, referrals) in enumerate(top_referrers, start=1):
        leaderboard_text += f"{index}. {username} - {referrals} referrals\n"

    await update.message.reply_text(leaderboard_text)

# Function to handle referrals using the referral link
async def referral(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    referred_by_user_id = None

    # Extract the referred_by_user_id from the "start" argument in the referral link
    if context.args:
        referred_by_user_id = context.args[0]

    if referred_by_user_id:
        # Check if the referral link is valid
        conn = sqlite3.connect('referral_bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (referred_by_user_id,))
        referrer = cursor.fetchone()

        if referrer:
            # Register the referral
            cursor.execute("UPDATE users SET referred_by=? WHERE id=?", (referrer[2], user_id))
            conn.commit()
            await update.message.reply_text(f"Referral successful! You were referred by {referrer[1]}")
        else:
            await update.message.reply_text("Invalid referral link. Please check again.")

        conn.close()
    else:
        await update.message.reply_text("Please provide a valid referral link.")

# Setup the bot
async def main():
    application = Application.builder().token(TOKEN).build()

    # Adding new command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myreferrals", myreferrals))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("referral", referral))  # Updated referral handler

    # Start polling for updates
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())

