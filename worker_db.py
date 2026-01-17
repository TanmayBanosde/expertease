import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "data/workers.db"

class WorkerDB:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            service TEXT,
            specialization TEXT,
            experience INTEGER,
            documents_json TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
        """)
        self.conn.commit()

    # ---------- CHECK EXISTING ----------
    def worker_exists(self, email):
        self.cursor.execute(
            "SELECT id FROM workers WHERE email=?",
            (email,)
        )
        return self.cursor.fetchone()

    # ---------- REGISTER ----------
    def register_worker(self, full_name, email, phone, service, specialization, experience):
        self.cursor.execute("""
        INSERT INTO workers
        (full_name, email, phone, service, specialization, experience, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name,
            email,
            phone,
            service,
            specialization,
            experience,
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    # ---------- DOCUMENTS ----------
    def save_documents(self, worker_id, documents_dict):
        self.cursor.execute("""
        UPDATE workers
        SET documents_json=?
        WHERE id=?
        """, (
            json.dumps(documents_dict),
            worker_id
        ))
        self.conn.commit()

    # ---------- ADMIN ----------
    def get_pending_workers(self):
        self.cursor.execute("""
        SELECT id, full_name, service, specialization
        FROM workers
        WHERE status='pending'
        """)
        return self.cursor.fetchall()

    def get_worker_documents(self, worker_id):
        self.cursor.execute(
            "SELECT documents_json FROM workers WHERE id=?",
            (worker_id,)
        )
        row = self.cursor.fetchone()
        return json.loads(row[0]) if row and row[0] else {}

    def approve_worker(self, worker_id):
        self.cursor.execute(
            "UPDATE workers SET status='approved' WHERE id=?",
            (worker_id,)
        )
        self.conn.commit()

    def reject_worker(self, worker_id):
        self.cursor.execute(
            "UPDATE workers SET status='rejected' WHERE id=?",
            (worker_id,)
        )
        self.conn.commit()

    # ---------- WORKER LOGIN ----------
    def verify_worker_login(self, email):
        self.cursor.execute("""
        SELECT id, status, service, specialization
        FROM workers
        WHERE email=?
        """, (email,))
        return self.cursor.fetchone()

    def get_worker_by_email(self, email):
        self.cursor.execute("""
        SELECT id, status FROM workers WHERE email=?
        """, (email,))
        return self.cursor.fetchone()

    def get_approved_workers(self):
        """Get all approved workers for users to book appointments"""
        self.cursor.execute("""
        SELECT id, full_name, specialization, experience
        FROM workers
        WHERE status='approved' AND service='healthcare'
        ORDER BY full_name
        """)
        rows = self.cursor.fetchall()
        return [
            {
                "id": row[0],
                "full_name": row[1],
                "specialization": row[2],
                "experience": row[3]
            }
            for row in rows
        ]