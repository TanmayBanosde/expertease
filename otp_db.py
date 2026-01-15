import sqlite3
import os
from config import OTP_DB

class OTPDB:
    def __init__(self):
        os.makedirs(os.path.dirname(OTP_DB), exist_ok=True)
        self.conn = sqlite3.connect(OTP_DB, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS otps (
            email TEXT PRIMARY KEY,
            otp TEXT,
            expires_at TEXT,
            attempts_left INTEGER
        )
        """)
        self.conn.commit()

    def store_otp(self, email, otp, expires_at):
        self.cursor.execute("""
        INSERT OR REPLACE INTO otps (email, otp, expires_at, attempts_left)
        VALUES (?, ?, ?, 3)
        """, (email, otp, expires_at))
        self.conn.commit()

    def get_otp(self, email):
        self.cursor.execute(
            "SELECT otp, expires_at, attempts_left FROM otps WHERE email = ?",
            (email,)
        )
        return self.cursor.fetchone()

    def decrease_attempt(self, email):
        self.cursor.execute("""
        UPDATE otps
        SET attempts_left = attempts_left - 1
        WHERE email = ?
        """, (email,))
        self.conn.commit()

    def delete_otp(self, email):
        self.cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
        self.conn.commit()
