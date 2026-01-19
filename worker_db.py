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
            clinic_location TEXT,
            rating REAL DEFAULT 0.0,
            documents_json TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
        """)
        # Add new columns if they don't exist (for existing databases)
        try:
            self.cursor.execute("ALTER TABLE workers ADD COLUMN clinic_location TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            self.cursor.execute("ALTER TABLE workers ADD COLUMN rating REAL DEFAULT 0.0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        self.conn.commit()

    # ---------- CHECK EXISTING ----------
    def worker_exists(self, email):
        self.cursor.execute(
            "SELECT id FROM workers WHERE email=?",
            (email,)
        )
        return self.cursor.fetchone()

    # ---------- REGISTER ----------
    def register_worker(self, full_name, email, phone, service, specialization, experience, clinic_location=None, rating=0.0):
        self.cursor.execute("""
        INSERT INTO workers
        (full_name, email, phone, service, specialization, experience, clinic_location, rating, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name,
            email,
            phone,
            service,
            specialization,
            experience,
            clinic_location or "",
            rating,
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
        SELECT id, full_name, specialization, experience, clinic_location, rating
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
                "experience": row[3],
                "clinic_location": row[4] or "Location not specified",
                "rating": row[5] or 0.0
            }
            for row in rows
        ]
    
    def get_workers_by_specialization(self, specialization):
        """Get approved workers filtered by specialization"""
        self.cursor.execute("""
        SELECT id, full_name, specialization, experience, clinic_location, rating
        FROM workers
        WHERE status='approved' AND service='healthcare' AND specialization=?
        ORDER BY rating DESC, full_name
        """, (specialization,))
        rows = self.cursor.fetchall()
        return [
            {
                "id": row[0],
                "full_name": row[1],
                "specialization": row[2],
                "experience": row[3],
                "clinic_location": row[4] or "Location not specified",
                "rating": row[5] or 0.0
            }
            for row in rows
        ]
    
    def get_all_specializations(self):
        """Get list of all unique specializations from approved healthcare workers"""
        self.cursor.execute("""
        SELECT DISTINCT specialization
        FROM workers
        WHERE status='approved' AND service='healthcare' AND specialization IS NOT NULL
        ORDER BY specialization
        """)
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]
    
    def search_workers(self, query):
        """Search workers by name, specialization, or location"""
        search_term = f"%{query}%"
        self.cursor.execute("""
        SELECT id, full_name, specialization, experience, clinic_location, rating
        FROM workers
        WHERE status='approved' AND service='healthcare'
        AND (full_name LIKE ? OR specialization LIKE ? OR clinic_location LIKE ?)
        ORDER BY rating DESC, full_name
        """, (search_term, search_term, search_term))
        rows = self.cursor.fetchall()
        return [
            {
                "id": row[0],
                "full_name": row[1],
                "specialization": row[2],
                "experience": row[3],
                "clinic_location": row[4] or "Location not specified",
                "rating": row[5] or 0.0
            }
            for row in rows
        ]