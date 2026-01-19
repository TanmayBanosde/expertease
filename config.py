# ---------- DATABASE ----------
USER_DB = "data/users.db"
USERS_DB = "data/users.db"  # Alias for compatibility
OTP_DB = "data/otp.db"
WORKER_DB = "data/workers.db"  # For healthcare_db.py

# ---------- EMAIL (MATCH email_service.py) ----------
EMAIL_ADDRESS = "co2023.vedant.gate@ves.ac.in"
EMAIL_PASSWORD = "cius tckr tpva tewf"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ---------- JWT ----------
JWT_SECRET = "super-secret-key"
JWT_EXP_MINUTES = 60

# ---------- OTP ----------
OTP_EXPIRY_MINUTES = 2

# ---------- HEALTHCARE UPLOAD (for worker_healthcare.py) ----------
HEALTHCARE_UPLOAD_DIR = "uploads/healthcare"
HEALTHCARE_REQUIRED_DOCS = ["license", "certificate", "id_proof"]
