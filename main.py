import os
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from database import init_db, add_user, check_referral_code, increment_referrals, get_referrals

# Load environment variables
load_dotenv()

# Telegram Bot Token
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Initialize the database
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username or "Anonymous"
    
    # Generate a unique referral code
    referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Add user to the database
    add_user(user_id, username, referral_code)
    
    await update.message.reply_text(
        f"Welcome, {username}!\n"
        f"Your referral code is: `{referral_code}`\n"
        f"Share this code with your friends to earn rewards!",
        parse_mode="Markdown"
    )

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) == 1:
        referred_code = args[0]
        user_id = update.effective_user.id
        
        # Check if the referral code exists and avoid self-referral
        referred_user = check_referral_code(referred_code)
        if referred_user and referred_user[0] != user_id:
            increment_referrals(referred_user[0])
            await update.message.reply_text("Referral successful!")
        else:
            await update.message.reply_text("Invalid or self-referral code!")
    else:
        await update.message.reply_text("Please provide a valid referral code.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    referrals = get_referrals(user_id)
    await update.message.reply_text(f"You have {referrals} successful referrals.")

def main():
    # Create the Application instance
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("referral", referral))
    application.add_handler(CommandHandler("stats", stats))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
