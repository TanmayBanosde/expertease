import sqlite3
import os
from datetime import datetime

DB_PATH = "data/appointments.db"

class AppointmentDB:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            worker_id INTEGER,
            user_name TEXT,
            patient_symptoms TEXT,
            booking_date TEXT,
            status TEXT DEFAULT 'pending', 
            created_at TEXT
        )
        """)
        # status lifecycle: pending → accepted → in_consultation → completed
        #                   pending → rejected (dead-end)
        #                   accepted → cancelled (cancelled before consultation)
        #                   in_consultation → cancelled (cancelled during consultation)
        self.conn.commit()

    def create_appointment(self, user_id, worker_id, user_name, symptoms, date):
        self.cursor.execute("""
        INSERT INTO appointments 
        (user_id, worker_id, user_name, patient_symptoms, booking_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, worker_id, user_name, symptoms, date, datetime.utcnow().isoformat()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_worker_appointments(self, worker_id):
        # This is what the Doctor sees on their dashboard
        self.cursor.execute("""
        SELECT id, user_name, patient_symptoms, booking_date, status 
        FROM appointments 
        WHERE worker_id=? ORDER BY created_at DESC
        """, (worker_id,))
        rows = self.cursor.fetchall()
        return [
            {
                "id": row[0],
                "user_name": row[1],
                "patient_symptoms": row[2],
                "booking_date": row[3],
                "status": row[4]
            }
            for row in rows
        ]

    def get_user_appointments(self, user_id):
        """Get all appointments for a user"""
        self.cursor.execute("""
        SELECT id, worker_id, user_name, patient_symptoms, booking_date, status, created_at
        FROM appointments 
        WHERE user_id=? ORDER BY created_at DESC
        """, (user_id,))
        rows = self.cursor.fetchall()
        return [
            {
                "id": row[0],
                "worker_id": row[1],
                "user_name": row[2],
                "patient_symptoms": row[3],
                "booking_date": row[4],
                "status": row[5],
                "created_at": row[6]
            }
            for row in rows
        ]

    def get_appointment_details(self, appointment_id):
        """Get full appointment details by ID"""
        self.cursor.execute("""
        SELECT id, user_id, worker_id, user_name, patient_symptoms, booking_date, status, created_at
        FROM appointments WHERE id=?
        """, (appointment_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "user_id": row[1],
            "worker_id": row[2],
            "user_name": row[3],
            "patient_symptoms": row[4],
            "booking_date": row[5],
            "status": row[6],
            "created_at": row[7]
        }

    def get_appointment(self, appointment_id):
        """Get appointment by ID for validation (lightweight)"""
        self.cursor.execute("""
        SELECT id, user_id, worker_id, status FROM appointments WHERE id=?
        """, (appointment_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "user_id": row[1],
            "worker_id": row[2],
            "status": row[3]
        }

    def _is_valid_transition(self, current_status, new_status):
        """Validate status transitions according to lifecycle rules"""
        valid_transitions = {
            "pending": ["accepted", "rejected"],
            "accepted": ["in_consultation", "cancelled"],
            "in_consultation": ["completed", "cancelled"],
            "rejected": [],  # Dead-end state
            "completed": [],  # Dead-end state
            "cancelled": []  # Dead-end state
        }
        allowed = valid_transitions.get(current_status, [])
        return new_status in allowed

    def update_status(self, appointment_id, new_status):
        """Update appointment status with validation"""
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return False, "Appointment not found"
        
        current_status = appointment["status"]
        
        if not self._is_valid_transition(current_status, new_status):
            return False, f"Invalid transition from '{current_status}' to '{new_status}'"
        
        self.cursor.execute("""
        UPDATE appointments SET status=? WHERE id=?
        """, (new_status, appointment_id))
        self.conn.commit()
        return True, "Status updated successfully"

    def start_consultation(self, appointment_id):
        """Transition from accepted to in_consultation"""
        return self.update_status(appointment_id, "in_consultation")

    def complete_appointment(self, appointment_id):
        """Transition from in_consultation to completed"""
        return self.update_status(appointment_id, "completed")

    def cancel_appointment(self, appointment_id):
        """Cancel appointment (from accepted or in_consultation)"""
        return self.update_status(appointment_id, "cancelled")