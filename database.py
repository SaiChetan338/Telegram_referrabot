import sqlite3

# Initialize the database
def init_db():
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

# Add a new user
def add_user(user_id, username, referral_code):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, referral_code)
        VALUES (?, ?, ?)
    """, (user_id, username, referral_code))
    conn.commit()
    conn.close()

# Check if a referral code exists
def check_referral_code(referral_code):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE referral_code = ?", (referral_code,))
    user = cursor.fetchone()
    conn.close()
    return user

# Increment referral count for a user
def increment_referrals(user_id):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Get referral stats
def get_referrals(user_id):
    conn = sqlite3.connect("referral_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT referrals FROM users WHERE id = ?", (user_id,))
    referrals = cursor.fetchone()
    conn.close()
    return referrals[0] if referrals else 0
