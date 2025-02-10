import sqlite3

def create_tables():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        referral_code TEXT,
                        referred_by INTEGER,
                        vip_status INTEGER DEFAULT 0,
                        download_count INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def add_user(user_id, referral_code, referred_by=None):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute('''INSERT INTO users (user_id, referral_code, referred_by)
                          VALUES (?, ?, ?)''', (user_id, referral_code, referred_by))
        conn.commit()

    conn.close()

def get_vip_status(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT vip_status FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def set_vip_status(user_id, vip_status):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET vip_status = ? WHERE user_id = ?', (vip_status, user_id))
    conn.commit()
    conn.close()

def increment_download_count(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET download_count = download_count + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT vip_status, download_count FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        return None  

    vip_status = "✅ VIP" if user[0] else "❌ Обычный"
    download_count = user[1]

    cursor.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (user_id,))
    referrals = cursor.fetchone()[0]

    conn.close()
    return {
        "vip_status": vip_status,
        "referrals": referrals,
        "download_count": download_count
    }
