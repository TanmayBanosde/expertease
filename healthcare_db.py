import sqlite3
import os
from config import WORKER_DB

os.makedirs("data", exist_ok=True)

class HealthcareWorkerDB:
    def __init__(self):
        self.conn = sqlite3.connect(WORKER_DB, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS healthcare_workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            gender TEXT,
            specialization TEXT,
            experience INTEGER,
            home_address TEXT,
            clinic_address TEXT,
            status TEXT DEFAULT 'PENDING'
        )
        """)
        self.conn.commit()

    def create_worker(self, data):
        self.cursor.execute("""
        INSERT INTO healthcare_workers
        (full_name, email, phone, gender, specialization,
         experience, home_address, clinic_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["full_name"],
            data["email"],
            data["phone"],
            data["gender"],
            data["specialization"],
            data["experience"],
            data["home_address"],
            data["clinic_address"]
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_worker_status(self, email):
        self.cursor.execute(
            "SELECT status FROM healthcare_workers WHERE email=?",
            (email,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None
