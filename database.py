import sqlite3
from datetime import datetime, timedelta

DB_NAME = "subscribers.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            start_date TEXT,
            expiry_date TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_subscriber(user_id, full_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    start = datetime.now()
    expiry = start + timedelta(days=31)
    c.execute('''
        INSERT OR REPLACE INTO subscribers (user_id, full_name, start_date, expiry_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, full_name, start.isoformat(), expiry.isoformat()))
    conn.commit()
    conn.close()


def is_subscriber_active(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT expiry_date FROM subscribers WHERE user_id=?', (user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        expiry = datetime.fromisoformat(row[0])
        return expiry > datetime.now()
    return False


def get_expiring_soon():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    target = datetime.now() + timedelta(days=2)
    c.execute('SELECT user_id FROM subscribers WHERE expiry_date BETWEEN ? AND ?', 
              (datetime.now().isoformat(), target.isoformat()))
    users = c.fetchall()
    conn.close()
    return [u[0] for u in users]


def remove_expired_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM subscribers WHERE expiry_date < ?', (datetime.now().isoformat(),))
    conn.commit()
    conn.close()
