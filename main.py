import logging
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
users = {}  # Store user data, including referral link and referrer
referrals = {}  # Track referrals for each user
leaderboard = {}  # Track the number of referrals for each user

# States for the conversation
REFERRAL = 1
JOINED = 2

# Command to start the bot
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in users:
        await update.message.reply_text("Welcome! Please provide a referral link from a friend, or type /skip to skip.")
        return REFERRAL
    else:
        await update.message.reply_text(f"Welcome back! Your referral link is: {users[user_id]['referral_link']}")
        return JOINED

# Generate a unique referral link
def generate_referral_link(user_id):
    return f"https://t.me/your_bot_username?start={user_id}"

# Handle the referral link entered by the new user
async def referral(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    referrer_id = None

    # Extract the referrer user_id from the "start" argument (after ?start=)
    if update.message.text.startswith("/start"):
        referrer_id = update.message.text.split('=')[-1]

    if referrer_id:
        if referrer_id in referrals:
            referrals[referrer_id].append(user_id)
            await update.message.reply_text(f"Referral link applied! You will be added to the group soon!")
        else:
            await update.message.reply_text("Invalid referral link! Please try again.")
            return REFERRAL  # Ask the user to try again

    # Generate a unique referral link for the new user
    user_referral_link = generate_referral_link(user_id)

    # Save the user's data (including their referral link)
    users[user_id] = {
        'referral_link': user_referral_link
    }
    referrals[user_id] = []  # Initialize empty referral list for this user
    leaderboard[user_id] = 0  # Initialize leaderboard count for this user

    await update.message.reply_text(f"Your referral link is: {user_referral_link}")
    await update.message.reply_text("You have been successfully registered and will now be added to the group.")
    return JOINED

# Handle the /skip command if no referral link is entered
async def skip(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Generate a unique referral link for the new user
    user_referral_link = generate_referral_link(user_id)

    # Save the user's data (including their referral link)
    users[user_id] = {
        'referral_link': user_referral_link
    }
    referrals[user_id] = []  # Initialize empty referral list for this user
    leaderboard[user_id] = 0  # Initialize leaderboard count for this user
    
    await update.message.reply_text(f"You have been successfully registered without a referral link. Your referral link is: {user_referral_link}. Share it with others to earn rewards!")
    await update.message.reply_text("You will now be added to the group.")
    return JOINED

# Handle the /referrals command to show the number of referrals
async def referrals_count(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in referrals:
        referral_count = len(referrals[user_id])
        await update.message.reply_text(f"You have referred {referral_count} user(s) using your referral link.")
    else:
        await update.message.reply_text("You haven't registered yet! Please start by typing /start.")

# Show the referral leaderboard
async def leaderboard_command(update: Update, context: CallbackContext):
    leaderboard_text = "Referral Leaderboard:\n"
    for user_id, count in leaderboard.items():
        leaderboard_text += f"User ID: {user_id} - {count} referral(s)\n"
    
    await update.message.reply_text(leaderboard_text)

# To handle the user's successful joining
async def join_group(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the group!")
    # Here you can add code to invite the user to the actual Telegram group (manual or via invite link)
    return ConversationHandler.END

# Define the main function to set up the bot
def main():
    application = Application.builder().token("TELEGRAM_TOKEN").build()

    # Set up the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REFERRAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, referral)],
            JOINED: [CommandHandler('skip', skip)],
        },
        fallbacks=[],
    )

    # Add the /referrals command handler
    application.add_handler(CommandHandler('referrals', referrals_count))
    application.add_handler(CommandHandler('leaderboard', leaderboard_command))

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()

