from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3

# Import database-related functions
from database import initialize_database, get_referral_code, increment_referral_count, get_leaderboard

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = "YOUR_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the referral bot! Use /referral to get your referral code.")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_code = get_referral_code(user_id)
    referral_count = increment_referral_count(user_id, 0)  # Retrieve without incrementing
    await update.message.reply_text(
        f"Your Referral Code: {referral_code}\nTotal Referrals: {referral_count}"
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaderboard_data = get_leaderboard()
    leaderboard_text = "🏆 Leaderboard 🏆\n" + "\n".join(
        [f"{i+1}. {name} - {count} referrals" for i, (name, count) in enumerate(leaderboard_data)]
    )
    await update.message.reply_text(leaderboard_text)

def main():
    # Initialize the database
    initialize_database()

    # Create the application
    app = ApplicationBuilder().token(bot_token).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("leaderboard", leaderboard))

    # Run the bot
    app.run_polling()

if __name__ == "__main__":
    main()
