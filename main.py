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
users = {}  # Store user data, including referral link and referral code
referrals = {}  # Track referrals for each user
leaderboard = {}  # Track the number of referrals for each user
referral_codes = {}  # Track generated referral codes

# States for the conversation
GENERATE_LINK = 1
GENERATE_CODE = 2
ENTER_REFERRAL_CODE = 3

# Command to start the bot
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in users:
        await update.message.reply_text("Welcome! Type /generate_referral_link to generate a referral link or /generate_referral_code to generate a referral code.")
        return GENERATE_LINK
    else:
        await update.message.reply_text(f"Welcome back! You already have a referral link: {users[user_id]['referral_link']}")
        return ENTER_REFERRAL_CODE

# Generate a unique referral link
def generate_referral_link(user_id):
    return f"https://t.me/testing1339?start={user_id}"

# Generate a unique referral code
def generate_referral_code(user_id):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    referral_codes[user_id] = code
    return code

# Handle generating a referral link
async def generate_referral_link_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in users:
        await update.message.reply_text(f"Your referral link is: {users[user_id]['referral_link']}")
    else:
        user_referral_link = generate_referral_link(user_id)
        users[user_id] = {'referral_link': user_referral_link}
        referrals[user_id] = []  # Initialize empty referral list for this user
        leaderboard[user_id] = 0  # Initialize leaderboard count for this user
        await update.message.reply_text(f"Your referral link is: {user_referral_link}")
    return GENERATE_LINK

# Handle generating a referral code
async def generate_referral_code_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in referral_codes:
        await update.message.reply_text(f"Your referral code is: {referral_codes[user_id]}")
    else:
        user_referral_code = generate_referral_code(user_id)
        await update.message.reply_text(f"Your referral code is: {user_referral_code}")
    return GENERATE_CODE

# Handle entering a referral code
async def enter_referral_code(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    referral_code = update.message.text.split()[-1]  # Get referral code from message
    
    # Check if the code is valid
    for referrer_id, code in referral_codes.items():
        if referral_code == code:
            # If valid, associate the referrer with the new user
            referrals[referrer_id].append(user_id)
            leaderboard[referrer_id] += 1  # Increment the referral count
            await update.message.reply_text(f"Referral successful! You have been referred by user {referrer_id}.")
            break
    else:
        await update.message.reply_text("Invalid referral code. Please try again.")
    return ENTER_REFERRAL_CODE

# Show the referral leaderboard
async def leaderboard_command(update: Update, context: CallbackContext):
    leaderboard_text = "Referral Leaderboard:\n"
    for user_id, count in leaderboard.items():
        leaderboard_text += f"User ID: {user_id} - {count} referral(s)\n"
    
    await update.message.reply_text(leaderboard_text)

# Define the main function to set up the bot
def main():
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('generate_referral_link', generate_referral_link_command))
    application.add_handler(CommandHandler('generate_referral_code', generate_referral_code_command))
    application.add_handler(CommandHandler('enter_referral_code', enter_referral_code))
    application.add_handler(CommandHandler('leaderboard', leaderboard_command))

    application.run_polling()

if __name__ == '__main__':
    main()

