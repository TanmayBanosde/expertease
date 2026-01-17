from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from appointment_db import AppointmentDB

from user_db import UserDB
from worker_db import WorkerDB
from message_db import MessageDB
from auth_utils import generate_token, verify_token
from otp_service import send_otp, verify_otp

app = Flask(__name__)

UPLOAD_ROOT = "uploads/workers"
os.makedirs(UPLOAD_ROOT, exist_ok=True)

user_db = UserDB()
worker_db = WorkerDB()
appt_db = AppointmentDB()
message_db = MessageDB()


# ================= USER AUTH =================

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    if not all(k in data for k in ["name","username","password","email"]):
        return jsonify({"error":"Missing fields"}),400

    if user_db.user_exists(data["username"], data["email"]):
        return jsonify({"error":"User already exists"}),400

    user_db.create_user(
        data["name"],
        data["username"],
        data["password"],
        data["email"]
    )

    send_otp(data["email"])
    return jsonify({"msg":"OTP sent"}),201


@app.route("/verify-otp", methods=["POST"])
def verify_user_otp():
    success, msg = verify_otp(
        request.json["email"],
        request.json["otp"]
    )
    if not success:
        return jsonify({"error":msg}),400

    user_db.mark_verified(request.json["email"])
    return jsonify({"msg":msg})


@app.route("/login", methods=["POST"])
def login():
    success, msg = user_db.verify_user(
        request.json["username"],
        request.json["password"]
    )
    if not success:
        return jsonify({"error":msg}),401

    user_id = user_db.get_user_by_username(request.json["username"])
    return jsonify({
        "token": generate_token(request.json["username"]),
        "user_id": user_id
    })

@app.route("/user/info", methods=["GET"])
def get_user_info():
    """Get user info from JWT token"""
    user_id, error, status_code = require_auth()
    if error:
        return jsonify({"error": error}), status_code
    
    return jsonify({"user_id": user_id}), 200

# ================= WORKER SIGNUP =================

@app.route("/worker/healthcare/signup", methods=["POST"])
def healthcare_worker_signup():
    data = request.json
    required = ["full_name","email","phone","specialization","experience"]

    if not all(k in data for k in required):
        return jsonify({"error":"Missing fields"}),400

    if worker_db.worker_exists(data["email"]):
        return jsonify({"error":"Worker already registered with this email"}),400

    worker_id = worker_db.register_worker(
        data["full_name"],
        data["email"],
        data["phone"],
        "healthcare",
        data["specialization"],
        data["experience"]
    )

    return jsonify({
        "msg":"Worker registered successfully",
        "worker_id":worker_id,
        "status":"pending"
    }),201

# ================= DOCUMENT UPLOAD =================

@app.route("/worker/upload-documents/<int:worker_id>", methods=["POST"])
def upload_documents(worker_id):
    if not request.files:
        return jsonify({"error":"No files uploaded"}),400

    folder = os.path.join(UPLOAD_ROOT, f"worker_{worker_id}")
    os.makedirs(folder, exist_ok=True)

    docs = {}
    for key in request.files:
        file = request.files[key]
        if file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(folder, filename))
            docs[key] = filename

    worker_db.save_documents(worker_id, docs)
    return jsonify({"msg":"Documents uploaded","status":"pending"})

# ================= WORKER LOGIN =================

@app.route("/worker/login", methods=["POST"])
def worker_login():
    email = request.json.get("email")
    worker = worker_db.verify_worker_login(email)

    if not worker:
        return jsonify({"error":"Worker not registered"}),404

    wid, status, service, specialization = worker

    if status == "pending":
        return jsonify({"error":"Verification pending"}),403
    if status == "rejected":
        return jsonify({"error":"Application rejected"}),403

    return jsonify({
        "msg":"Login successful",
        "worker_id":wid,
        "service":service,
        "specialization":specialization
    })

# ================= ADMIN =================

@app.route("/admin/workers/pending")
def admin_pending():
    return jsonify(worker_db.get_pending_workers())

@app.route("/workers/available", methods=["GET"])
def get_available_workers():
    """Get all approved healthcare workers for booking"""
    workers = worker_db.get_approved_workers()
    return jsonify({"workers": workers}), 200

@app.route("/admin/worker/approve/<int:worker_id>", methods=["POST"])
def approve(worker_id):
    worker_db.approve_worker(worker_id)
    return jsonify({"msg":"Worker approved"})

@app.route("/admin/worker/reject/<int:worker_id>", methods=["POST"])
def reject(worker_id):
    worker_db.reject_worker(worker_id)
    return jsonify({"msg":"Worker rejected"})

@app.route("/admin/view-file/<int:worker_id>/<filename>")
def view_file(worker_id, filename):
    return send_from_directory(
        os.path.join(UPLOAD_ROOT,f"worker_{worker_id}"),
        filename
    )

# ================= APPOINTMENTS (THE BRIDGE) =================

@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    # Vedant's User App calls this
    data = request.json
    appt_id = appt_db.create_appointment(
        data["user_id"],
        data["worker_id"],
        data["user_name"],
        data["symptoms"],
        data["date"]
    )
    return jsonify({"msg": "Appointment requested", "id": appt_id}), 201

@app.route("/user/appointments", methods=["GET"])
def get_user_appointments():
    """
    Get all appointments for the authenticated user.
    Requires JWT authentication.
    """
    # Authenticate user via JWT
    user_id, error, status_code = require_auth()
    if error:
        return jsonify({"error": error}), status_code
    
    appointments = appt_db.get_user_appointments(user_id)
    return jsonify({"appointments": appointments}), 200

@app.route("/appointment/<int:appointment_id>", methods=["GET"])
def get_appointment_details(appointment_id):
    """
    Get detailed information about a specific appointment.
    Requires JWT for users or worker_id for workers.
    Validates that requester belongs to the appointment.
    """
    appointment = appt_db.get_appointment_details(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    
    # Get requester role and validate access
    sender_role = request.args.get("sender_role")  # "user" or "worker"
    
    if sender_role == "user":
        # User authentication via JWT
        user_id, error, status_code = require_auth()
        if error:
            return jsonify({"error": error}), status_code
        
        # Validate user belongs to this appointment
        if appointment["user_id"] != user_id:
            return jsonify({"error": "You are not authorized to view this appointment"}), 403
            
    elif sender_role == "worker":
        # Worker authentication via worker_id in query params
        worker_id = request.args.get("worker_id")
        if not worker_id:
            return jsonify({"error": "worker_id required for worker access"}), 400
        
        try:
            worker_id = int(worker_id)
        except ValueError:
            return jsonify({"error": "Invalid worker_id"}), 400
        
        # Validate worker belongs to this appointment
        if appointment["worker_id"] != worker_id:
            return jsonify({"error": "You are not authorized to view this appointment"}), 403
    else:
        return jsonify({"error": "sender_role query parameter required: 'user' or 'worker'"}), 400
    
    return jsonify(appointment), 200

@app.route("/worker/appointments/<int:worker_id>")
def get_worker_requests(worker_id):
    # YOUR Worker App calls this to see jobs
    jobs = appt_db.get_worker_appointments(worker_id)
    return jsonify(jobs)

@app.route("/worker/respond-appointment", methods=["POST"])
def respond_appointment():
    # YOUR Worker App calls this to Accept/Reject
    data = request.json
    # Status should be 'accepted' or 'rejected'
    success, msg = appt_db.update_status(data["appointment_id"], data["status"])
    if not success:
        return jsonify({"error": msg}), 400
    return jsonify({"msg": msg})

@app.route("/appointment/start-consultation", methods=["POST"])
def start_consultation():
    """Start consultation: accepted → in_consultation"""
    data = request.json
    success, msg = appt_db.start_consultation(data["appointment_id"])
    if not success:
        return jsonify({"error": msg}), 400
    return jsonify({"msg": msg})

@app.route("/appointment/complete", methods=["POST"])
def complete_appointment():
    """Complete appointment: in_consultation → completed"""
    data = request.json
    success, msg = appt_db.complete_appointment(data["appointment_id"])
    if not success:
        return jsonify({"error": msg}), 400
    return jsonify({"msg": msg})

@app.route("/appointment/cancel", methods=["POST"])
def cancel_appointment():
    """Cancel appointment: accepted or in_consultation → cancelled"""
    data = request.json
    success, msg = appt_db.cancel_appointment(data["appointment_id"])
    if not success:
        return jsonify({"error": msg}), 400
    return jsonify({"msg": msg})

# ================= MESSAGES / CHAT SYSTEM =================

def require_auth():
    """Helper to verify JWT token and return user_id"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None, "Missing authorization header", 401
    
    try:
        token = auth_header.split(" ")[1]  # "Bearer <token>"
    except IndexError:
        return None, "Invalid authorization format", 401
    
    username = verify_token(token)
    if not username:
        return None, "Invalid or expired token", 401
    
    user_id = user_db.get_user_by_username(username)
    if not user_id:
        return None, "User not found", 404
    
    return user_id, None, None

@app.route("/messages/send", methods=["POST"])
def send_message():
    """
    Send a message in an appointment chat.
    Requires JWT for users. Workers send worker_id in request body.
    Chat only allowed for accepted or in_consultation appointments.
    """
    data = request.json
    
    # Validate required fields
    required_fields = ["appointment_id", "message"]
    if not all(k in data for k in required_fields):
        return jsonify({"error": "Missing required fields: appointment_id, message"}), 400
    
    appointment_id = data["appointment_id"]
    message_text = data["message"]
    
    # Get appointment and validate it exists
    appointment = appt_db.get_appointment(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    
    # Validate appointment status - chat only allowed for accepted or in_consultation
    status = appointment["status"]
    if status not in ["accepted", "in_consultation"]:
        return jsonify({
            "error": f"Chat not available for appointment status '{status}'. Chat is only available for accepted or in_consultation appointments."
        }), 403
    
    # Determine sender role and ID
    sender_role = data.get("sender_role")  # "user" or "worker"
    sender_id = None
    
    if sender_role == "user":
        # User authentication via JWT
        user_id, error, status_code = require_auth()
        if error:
            return jsonify({"error": error}), status_code
        sender_id = user_id
        
        # Validate user belongs to this appointment
        if appointment["user_id"] != sender_id:
            return jsonify({"error": "You are not authorized to send messages for this appointment"}), 403
            
    elif sender_role == "worker":
        # Worker authentication via worker_id in request
        worker_id = data.get("worker_id")
        if not worker_id:
            return jsonify({"error": "worker_id required for worker messages"}), 400
        
        sender_id = worker_id
        
        # Validate worker belongs to this appointment
        if appointment["worker_id"] != worker_id:
            return jsonify({"error": "You are not authorized to send messages for this appointment"}), 403
    else:
        return jsonify({"error": "sender_role must be 'user' or 'worker'"}), 400
    
    # Store the message
    message_id = message_db.send_message(appointment_id, sender_role, sender_id, message_text)
    
    return jsonify({
        "msg": "Message sent successfully",
        "message_id": message_id
    }), 201

@app.route("/messages/<int:appointment_id>", methods=["GET"])
def get_messages(appointment_id):
    """
    Get all messages for an appointment.
    Requires JWT for users. Workers can access with worker_id.
    Chat only accessible for accepted or in_consultation appointments.
    """
    # Get appointment and validate it exists
    appointment = appt_db.get_appointment(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    
    # Validate appointment status - chat only allowed for accepted or in_consultation
    status = appointment["status"]
    if status not in ["accepted", "in_consultation"]:
        return jsonify({
            "error": f"Chat not available for appointment status '{status}'. Chat is only available for accepted or in_consultation appointments."
        }), 403
    
    # Determine requester role and validate access
    sender_role = request.args.get("sender_role")  # "user" or "worker" as query param
    
    if sender_role == "user":
        # User authentication via JWT
        user_id, error, status_code = require_auth()
        if error:
            return jsonify({"error": error}), status_code
        
        # Validate user belongs to this appointment
        if appointment["user_id"] != user_id:
            return jsonify({"error": "You are not authorized to view messages for this appointment"}), 403
            
    elif sender_role == "worker":
        # Worker authentication via worker_id in query params
        worker_id = request.args.get("worker_id")
        if not worker_id:
            return jsonify({"error": "worker_id required for worker access"}), 400
        
        try:
            worker_id = int(worker_id)
        except ValueError:
            return jsonify({"error": "Invalid worker_id"}), 400
        
        # Validate worker belongs to this appointment
        if appointment["worker_id"] != worker_id:
            return jsonify({"error": "You are not authorized to view messages for this appointment"}), 403
    else:
        return jsonify({"error": "sender_role query parameter required: 'user' or 'worker'"}), 400
    
    # Get all messages
    messages = message_db.get_messages(appointment_id)
    
    return jsonify({
        "appointment_id": appointment_id,
        "messages": messages
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
