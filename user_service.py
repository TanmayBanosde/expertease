import sqlite3
from config import USERS_DB


def init_user_db():
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()


init_user_db()


def user_exists(username, email):
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    exists = c.fetchone() is not None
    conn.close()
    return exists


def create_user(name, username, password, email):
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (name, username, password, email) VALUES (?, ?, ?, ?)",
        (name, username, password, email)
    )
    conn.commit()
    conn.close()
