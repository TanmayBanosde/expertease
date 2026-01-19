import sqlite3
import os
from datetime import datetime

DB_PATH = "data/availability.db"

class AvailabilityDB:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            created_at TEXT
        )
        """)
        self.conn.commit()

    def set_availability(self, worker_id, date, time_slot):
        """Set a time slot as available"""
        # Check if already exists
        self.cursor.execute("""
        SELECT id FROM availability 
        WHERE worker_id=? AND date=? AND time_slot=?
        """, (worker_id, date, time_slot))
        
        if self.cursor.fetchone():
            # Update existing
            self.cursor.execute("""
            UPDATE availability 
            SET is_available=1, created_at=?
            WHERE worker_id=? AND date=? AND time_slot=?
            """, (datetime.utcnow().isoformat(), worker_id, date, time_slot))
        else:
            # Insert new
            self.cursor.execute("""
            INSERT INTO availability (worker_id, date, time_slot, is_available, created_at)
            VALUES (?, ?, ?, 1, ?)
            """, (worker_id, date, time_slot, datetime.utcnow().isoformat()))
        
        self.conn.commit()

    def remove_availability(self, worker_id, date, time_slot):
        """Remove a time slot (mark as unavailable)"""
        self.cursor.execute("""
        UPDATE availability 
        SET is_available=0
        WHERE worker_id=? AND date=? AND time_slot=?
        """, (worker_id, date, time_slot))
        self.conn.commit()

    def get_availability(self, worker_id, date=None):
        """Get availability for a worker, optionally filtered by date"""
        if date:
            self.cursor.execute("""
            SELECT date, time_slot 
            FROM availability 
            WHERE worker_id=? AND date=? AND is_available=1
            ORDER BY time_slot
            """, (worker_id, date))
        else:
            self.cursor.execute("""
            SELECT date, time_slot 
            FROM availability 
            WHERE worker_id=? AND is_available=1
            ORDER BY date, time_slot
            """, (worker_id,))
        
        rows = self.cursor.fetchall()
        return [{"date": row[0], "time_slot": row[1]} for row in rows]

    def is_available(self, worker_id, date, time_slot):
        """Check if a specific time slot is available"""
        self.cursor.execute("""
        SELECT id FROM availability 
        WHERE worker_id=? AND date=? AND time_slot=? AND is_available=1
        """, (worker_id, date, time_slot))
        return self.cursor.fetchone() is not None
