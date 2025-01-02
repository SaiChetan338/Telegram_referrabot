from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from database import init_db, add_or_get_user, increment_referrals, get_referrals

# Command: Start
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    referral_code = add_or_get_user(user.id, user.username or "Anonymous")
    update.message.reply_text(f"Welcome {user.first_name}!\nYour referral code is: {referral_code}\n"
                              f"Share it to earn rewards!")

# Command: Referral
def referral(update: Update, context: CallbackContext):
    if context.args:
        referred_code = context.args[0]
        increment_referrals(referred_code)
        update.message.reply_text("Thanks for using a referral code!")
    else:
        update.message.reply_text("Please provide a valid referral code after the /referral command.")

# Command: Stats
def stats(update: Update, context: CallbackContext):
    user = update.effective_user
    referral_count = get_referrals(user.id)
    update.message.reply_text(f"You have referred {referral_count} users!")

# Main function
def main():
    init_db()

    # Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
    bot_token = "YOUR_BOT_TOKEN"
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("referral", referral))
    dispatcher.add_handler(CommandHandler("stats", stats))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

