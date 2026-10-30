# database.py
import sqlite3
from datetime import datetime

DB_NAME = "chat_history.db"

def init_db():
    """ایجاد دیتابیس و جدول پیام‌ها با ساختار استاندارد"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # ایجاد جدول با ستون id به عنوان کلید اصلی و خودکار افزایشی
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def save_message(username, message):
    """ذخیره یک پیام جدید همراه با زمان ارسال"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO messages (username, message, timestamp)
        VALUES (?, ?, ?)
    ''', (username, message, timestamp))
    conn.commit()
    conn.close()

def get_recent_messages(limit=20):
    """دریافت ۲۰ پیام آخر بدون اضافه کردن هیچ متن اضافه‌ای"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # دریافت آخرین پیام‌ها بر اساس ترتیب زمانی
    cursor.execute('''
        SELECT username, message, timestamp FROM (
            SELECT id, username, message, timestamp FROM messages
            ORDER BY id DESC
            LIMIT ?
        ) ORDER BY id ASC
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows