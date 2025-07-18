import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create users table with email verification fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT,
            role TEXT,
            email TEXT UNIQUE,
            password TEXT,
            company_name TEXT,
            full_name TEXT,
            mobile_number TEXT,
            email_verified BOOLEAN DEFAULT FALSE,
            verification_token TEXT,
            verification_token_expires DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create email_verification_logs table to track verification attempts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_verification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            email TEXT,
            verification_token TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            verified_at DATETIME,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# Check if we need to add new columns to existing table
def update_db_schema():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add new columns if they don't exist
    if 'email_verified' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE')
    if 'verification_token' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN verification_token TEXT')
    if 'verification_token_expires' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN verification_token_expires DATETIME')
    if 'created_at' not in columns:
        # SQLite doesn't support CURRENT_TIMESTAMP as default in ALTER TABLE
        # So we add the column without default, then update existing records
        cursor.execute('ALTER TABLE users ADD COLUMN created_at DATETIME')
        # Update existing records with current timestamp
        cursor.execute("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL")

    conn.commit()
    conn.close()

init_db()
update_db_schema()
