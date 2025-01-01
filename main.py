from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from database import init_db, add_or_get_user, get_referrals
import asyncio



async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    referral_code = add_or_get_user(user_id, username)
    referral_link = f"https://t.me/{context.bot.username}?start={referral_code}"
    await update.message.reply_text(f"Here is your referral link:\n{referral_link}")

# Command to show the referral count
async def referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    count = get_referrals(user_id)
    await update.message.reply_text(f"You have {count} referrals.")

# Initialize and run the bot
async def main():
    init_db()  # Initialize the database

    # Set your bot token here
    TOKEN = "YOUR_BOT_TOKEN"

    application = Application.builder().token(TOKEN).build()

    # Add command handlers
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
