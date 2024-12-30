import logging
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters
from telegram.ext import ConversationHandler

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
users = {}
referrals = {}

# States for the conversation
REFERRAL = 1
JOINED = 2

# Command to start the bot and ask for referral code
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Please provide a referral code if you have one, or type /skip if you don't.")
    return REFERRAL

# Generate unique referral code
def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Handle the referral code entered by the new user
async def referral(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    referral_code = update.message.text.strip().upper()

    if referral_code == "/skip":
        # If no referral code is entered, skip and add the user
        referral_code = None
        await update.message.reply_text("No referral code entered, you will join without a referrer.")
    elif referral_code in referrals:
        # Valid referral code, add the user to the referrer's list
        referrals[referral_code].append(user_id)
        await update.message.reply_text(f"Referral code {referral_code} applied. You will be added to the group soon!")
    else:
        await update.message.reply_text("Invalid referral code! Please try again or type /skip to skip.")
        return REFERRAL  # Wait for the user to try again
    
    # Generate the new user's referral code
    user_referral_code = generate_referral_code()
    users[user_id] = user_referral_code
    referrals[user_referral_code] = []  # Initialize referral list for this user
    await update.message.reply_text(f"Your referral code is {user_referral_code}. Share it with others to earn rewards!")
    
    # Proceed with adding the user to the group after this
    await update.message.reply_text("You have been successfully registered! You will now be added to the group.")
    
    return JOINED

# Handle the /skip command if no referral code is entered
async def skip(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    # Generate the new user's referral code
    user_referral_code = generate_referral_code()
    users[user_id] = user_referral_code
    referrals[user_referral_code] = []  # Initialize referral list for this user
    await update.message.reply_text(f"You have been successfully registered without a referral code! Your referral code is {user_referral_code}. Share it with others to earn rewards!")
    
    # Proceed with adding the user to the group
    await update.message.reply_text("You will now be added to the group.")
    
    return JOINED

# Handle the /referrals command to show the number of referrals
async def referrals_count(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_referral_code = users.get(user_id)

    if user_referral_code:
        # Count how many users have used the current user's referral code
        referral_count = len(referrals[user_referral_code])
        await update.message.reply_text(f"You have referred {referral_count} user(s) using the code {user_referral_code}.")
    else:
        await update.message.reply_text("You haven't registered yet! Please start by typing /start.")

# To handle the user's successful joining
async def join_group(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the group!")
    # Here you can add code to invite the user to the actual Telegram group (manual or via invite link)

    return ConversationHandler.END

# Define the main function to set up the bot
def main():
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Set up the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REFERRAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, referral)],
            JOINED: [CommandHandler('skip', skip)],
        },
        fallbacks=[],
    )

    # Add the new /referrals command handler
    application.add_handler(CommandHandler('referrals', referrals_count))

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
