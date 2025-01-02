from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from database import init_db, add_or_get_user, increment_referrals, get_referrals
import asyncio

# Generate referral link for the user
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    try:
        referral_code = add_or_get_user(user_id, username)
        referral_link = f"https://t.me/{context.bot.username}?start={referral_code}"
        await update.message.reply_text(f"Here is your referral link:\n{referral_link}")
    except Exception as e:
        await update.message.reply_text("An error occurred while generating your referral link.")
        print(f"Error in /referral: {e}")

# Show referral count for the user
async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        count = get_referrals(user_id)
        await update.message.reply_text(f"You have {count} referrals.")
    except Exception as e:
        await update.message.reply_text("An error occurred while retrieving your referral stats.")
        print(f"Error in /referrals: {e}")

# Handle new users joining via referral link
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args  # Capture arguments passed via the link
    if args:
        referral_code = args[0]
        try:
            increment_referrals(referral_code)
            await update.message.reply_text("Thanks for joining via a referral link!")
        except Exception as e:
            await update.message.reply_text("An error occurred while processing the referral.")
            print(f"Error in /start: {e}")
    else:
        await update.message.reply_text("Welcome to the bot! Use /referral to get your referral link.")

# Initialize and run the bot
async def main():
    init_db()  # Initialize the database

    # Set your bot token here
    TOKEN = "YOUR_BOT_TOKEN"

    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("referral", referral))
    application.add_handler(CommandHandler("referrals", referrals))

    # Set bot commands (optional but recommended)
    commands = [
        BotCommand("referral", "Generate your referral link"),
        BotCommand("referrals", "Show your referral count"),
    ]
    await application.bot.set_my_commands(commands)

    # Run the bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

