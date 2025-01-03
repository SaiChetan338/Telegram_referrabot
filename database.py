import sqlite3
import uuid

# Initialize the database
def initialize_database():
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            referral_code TEXT UNIQUE,
            referrals INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# Add a new user or get an existing user's referral code
def get_referral_code(user_id, username):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT referral_code FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        referral_code = result[0]
    else:
        referral_code = str(uuid.uuid4())[:8]  # Generate a unique referral code
        cursor.execute("INSERT INTO users (id, username, referral_code) VALUES (?, ?, ?)",
                       (user_id, username, referral_code))
    conn.commit()
    conn.close()
    return referral_code

# Increment referral count
def increment_referral_count(referral_code):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE referral_code = ?", (referral_code,))
    conn.commit()
    conn.close()

# Get referral stats
def get_leaderboard(user_id):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT referrals FROM users WHERE id = ?", (user_id,))
    referrals = cursor.fetchone()
    conn.close()
    return referrals[0] if referrals else 0
