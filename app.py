from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename

from user_db import UserDB
from worker_db import WorkerDB
from auth_utils import generate_token
from otp_service import send_otp, verify_otp

app = Flask(__name__)

UPLOAD_ROOT = "uploads/workers"
os.makedirs(UPLOAD_ROOT, exist_ok=True)

user_db = UserDB()
worker_db = WorkerDB()

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

    return jsonify({"token": generate_token(request.json["username"])})

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

if __name__ == "__main__":
    app.run(debug=True)
