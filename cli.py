import requests

API = "http://127.0.0.1:5000"
TOKEN = None
USER_ID = None

# ==================================================
# ================= USER FLOW ======================
# ==================================================

def user_signup():
    print("\n👤 User Signup (Email OTP)")
    name = input("Name: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    email = input("Email: ").strip()

    r = requests.post(f"{API}/signup", json={
        "name": name,
        "username": username,
        "password": password,
        "email": email
    })

    if r.status_code != 201:
        print("❌ Signup failed:", r.json())
        return

    print(f"📨 OTP sent to {email}")

    while True:
        print("\n1. Enter OTP")
        print("2. Cancel")
        c = input("Choice: ").strip()

        if c == "1":
            otp = input("OTP: ").strip()
            vr = requests.post(f"{API}/verify-otp", json={
                "email": email,
                "otp": otp
            })

            if vr.status_code == 200:
                print("✅ Account verified")
                return
            else:
                print("❌", vr.json().get("error"))

        elif c == "2":
            return


def user_login():
    global TOKEN, USER_ID
    print("\n🔐 User Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    r = requests.post(f"{API}/login", json={
        "username": username,
        "password": password
    })

    if r.status_code == 200:
        data = r.json()
        TOKEN = data["token"]
        USER_ID = data.get("user_id")
        print("✅ Logged in successfully")
        user_dashboard()
    else:
        print("❌ Login failed:", r.json().get("error"))


def user_dashboard():
    """User Dashboard - Book appointments and manage consultations"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n=== USER DASHBOARD ===")
        print("1. View Available Doctors")
        print("2. Book Appointment")
        print("3. My Appointments")
        print("4. View Appointment Details")
        print("5. View Messages (Chat)")
        print("6. Send Message")
        print("7. Cancel Appointment")
        print("8. Logout")

        c = input("Choice: ").strip()

        if c == "1":
            view_available_doctors()
        elif c == "2":
            book_appointment_user()
        elif c == "3":
            view_user_appointments()
        elif c == "4":
            view_appointment_detail_user()
        elif c == "5":
            view_messages_user()
        elif c == "6":
            send_message_user()
        elif c == "7":
            cancel_appointment_user()
        elif c == "8":
            TOKEN = None
            USER_ID = None
            print("👋 Logged out")
            return
        else:
            print("❌ Invalid choice")


def view_available_doctors():
    """View all available approved doctors grouped by specialization"""
    r = requests.get(f"{API}/workers/available")
    
    if r.status_code == 200:
        data = r.json()
        workers = data.get("workers", [])
        
        if not workers:
            print("\n👨‍⚕️ No doctors available at the moment")
            return
        
        # Group doctors by specialization
        doctors_by_specialization = {}
        for doc in workers:
            specialization = doc.get('specialization', 'Other')
            if specialization not in doctors_by_specialization:
                doctors_by_specialization[specialization] = []
            doctors_by_specialization[specialization].append(doc)
        
        print("\n👨‍⚕️ Available Doctors by Specialization:")
        print("=" * 80)
        
        # Display each specialization section
        for specialization, docs in sorted(doctors_by_specialization.items()):
            print(f"\n🏥 {specialization.upper()} SECTION")
            print("-" * 80)
            for doc in docs:
                print(f"  ID: {doc['id']} | Dr. {doc['full_name']}")
                print(f"    Experience: {doc['experience']} years")
                print("-" * 80)
        
        print("\n" + "=" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch doctors"))


def book_appointment_user():
    """Book an appointment with a doctor"""
    global USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    if not USER_ID:
        # Try to get user_id from API
        r = requests.get(f"{API}/user/info", headers={"Authorization": f"Bearer {TOKEN}"})
        if r.status_code == 200:
            USER_ID = r.json().get("user_id")
        else:
            print("❌ Could not get user information. Please login again.")
            return
    
    print("\n📅 Book Appointment")
    worker_id = input("Doctor ID: ").strip()
    user_name = input("Your Name: ").strip()
    symptoms = input("Symptoms/Reason: ").strip()
    date = input("Preferred Date (YYYY-MM-DD): ").strip()
    
    if not all([worker_id, user_name, symptoms, date]):
        print("❌ All fields are required")
        return
    
    r = requests.post(f"{API}/book-appointment", json={
        "user_id": int(USER_ID),
        "worker_id": int(worker_id),
        "user_name": user_name,
        "symptoms": symptoms,
        "date": date
    })
    
    if r.status_code == 201:
        data = r.json()
        print(f"✅ Appointment requested successfully!")
        print(f"📋 Appointment ID: {data['id']}")
        print("⏳ Waiting for doctor's approval...")
    else:
        print("❌ Error:", r.json().get("error", "Failed to book appointment"))


def view_user_appointments():
    """View all appointments for the logged-in user"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
    
    if r.status_code == 200:
        data = r.json()
        appointments = data.get("appointments", [])
        
        if not appointments:
            print("\n📭 No appointments found")
            return
        
        print("\n📋 Your Appointments:")
        print("-" * 80)
        for apt in appointments:
            status_icon = {
                "pending": "⏳",
                "accepted": "✅",
                "rejected": "❌",
                "in_consultation": "💬",
                "completed": "✓",
                "cancelled": "🚫"
            }.get(apt["status"], "❓")
            
            print(f"ID: {apt['id']} | {status_icon} {apt['status'].upper()}")
            print(f"  Doctor ID: {apt['worker_id']}")
            print(f"  Symptoms: {apt['patient_symptoms']}")
            print(f"  Date: {apt['booking_date']}")
            print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointments"))


def view_appointment_detail_user():
    """View detailed information about a specific appointment"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/appointment/{apt_id}?sender_role=user", 
                     headers={"Authorization": f"Bearer {TOKEN}"})
    
    if r.status_code == 200:
        apt = r.json()
        print("\n📄 Appointment Details:")
        print("-" * 80)
        print(f"ID: {apt['id']}")
        print(f"Status: {apt['status']}")
        print(f"Doctor ID: {apt['worker_id']}")
        print(f"Patient: {apt['user_name']}")
        print(f"Symptoms: {apt['patient_symptoms']}")
        print(f"Booking Date: {apt['booking_date']}")
        print(f"Created: {apt['created_at']}")
        print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointment"))


def view_messages_user():
    """View messages in an appointment chat"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/messages/{apt_id}?sender_role=user",
                     headers={"Authorization": f"Bearer {TOKEN}"})
    
    if r.status_code == 200:
        data = r.json()
        messages = data.get("messages", [])
        
        if not messages:
            print("\n📭 No messages yet")
            return
        
        print(f"\n💬 Messages for Appointment #{apt_id}:")
        print("-" * 80)
        for msg in messages:
            sender_label = "👤 You" if msg["sender_role"] == "user" else "👨‍⚕️ Doctor"
            print(f"{sender_label} ({msg['timestamp'][:19]}):")
            print(f"  {msg['message']}")
            print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch messages"))


def send_message_user():
    """Send a message in an appointment chat"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    apt_id = input("Appointment ID: ").strip()
    message = input("Message: ").strip()
    
    if not message:
        print("❌ Message cannot be empty")
        return
    
    r = requests.post(f"{API}/messages/send", json={
        "appointment_id": int(apt_id),
        "sender_role": "user",
        "message": message
    }, headers={"Authorization": f"Bearer {TOKEN}"})
    
    if r.status_code == 201:
        print("✅ Message sent successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to send message"))


def cancel_appointment_user():
    """Cancel an appointment"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    apt_id = input("Appointment ID: ").strip()
    
    confirm = input("Are you sure you want to cancel? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Cancelled")
        return
    
    r = requests.post(f"{API}/appointment/cancel", json={
        "appointment_id": int(apt_id)
    })
    
    if r.status_code == 200:
        print("✅ Appointment cancelled successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to cancel appointment"))


def user_menu():
    while True:
        print("\n--- USER MENU ---")
        print("1. Signup")
        print("2. Login")
        print("3. Back")

        c = input("Choice: ").strip()

        if c == "1":
            user_signup()
        elif c == "2":
            user_login()
        elif c == "3":
            return


# ==================================================
# ================= WORKER FLOW ====================
# ==================================================

def healthcare_worker_signup():
    print("\n🩺 Healthcare Worker Signup")

    full_name = input("Full Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    specialization = input("Specialization (Dentist, Eye, etc): ").strip()

    while True:
        exp = input("Experience (years - number only): ").strip()
        if exp.isdigit():
            experience = int(exp)
            break
        print("❌ Enter numbers only")

    r = requests.post(f"{API}/worker/healthcare/signup", json={
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "specialization": specialization,
        "experience": experience
    })

    if r.status_code == 201:
        data = r.json()
        print("\n✅ Worker registered successfully")
        print("🆔 Worker ID:", data["worker_id"])
        print("⏳ Status: Pending approval (2–3 hours)")
        print("📤 Documents will be uploaded via App/UI later")
    else:
        print("❌", r.json().get("error"))


def worker_login():
    print("\n🔐 Worker Login (After Approval)")
    email = input("Email: ").strip()

    r = requests.post(f"{API}/worker/login", json={"email": email})

    if r.status_code == 200:
        data = r.json()
        print("\n✅ Login Successful")
        print("Service:", data["service"])
        print("Specialization:", data["specialization"])
        worker_id = data["worker_id"]
        worker_dashboard(worker_id)
    else:
        print("❌", r.json().get("error"))


def worker_menu():
    print("\n👷 Welcome Worker")

    while True:
        print("\n--- WORKER MENU ---")
        print("1. Healthcare Signup")
        print("2. Worker Login")
        print("3. Back")

        c = input("Choice: ").strip()

        if c == "1":
            healthcare_worker_signup()
        elif c == "2":
            worker_login()
        elif c == "3":
            return


def worker_dashboard(worker_id):
    """Worker Dashboard - Manage appointments and consultations"""
    while True:
        print("\n=== WORKER DASHBOARD ===")
        print("1. View All Appointments")
        print("2. View Appointment Details")
        print("3. Accept/Reject Appointment")
        print("4. Start Consultation")
        print("5. Complete Appointment")
        print("6. Cancel Appointment")
        print("7. View Messages (Chat)")
        print("8. Send Message")
        print("9. Logout")

        c = input("Choice: ").strip()

        if c == "1":
            view_worker_appointments(worker_id)
        elif c == "2":
            view_appointment_detail_worker(worker_id)
        elif c == "3":
            respond_to_appointment(worker_id)
        elif c == "4":
            start_consultation_worker(worker_id)
        elif c == "5":
            complete_appointment_worker(worker_id)
        elif c == "6":
            cancel_appointment_worker(worker_id)
        elif c == "7":
            view_messages_worker(worker_id)
        elif c == "8":
            send_message_worker(worker_id)
        elif c == "9":
            print("👋 Logged out")
            return
        else:
            print("❌ Invalid choice")


def view_worker_appointments(worker_id):
    """View all appointments for the worker"""
    r = requests.get(f"{API}/worker/appointments/{worker_id}")
    
    if r.status_code == 200:
        appointments = r.json()
        if not appointments:
            print("\n📭 No appointments found")
            return
        
        print("\n📋 Your Appointments:")
        print("-" * 80)
        for apt in appointments:
            status_icon = {
                "pending": "⏳",
                "accepted": "✅",
                "rejected": "❌",
                "in_consultation": "💬",
                "completed": "✓",
                "cancelled": "🚫"
            }.get(apt["status"], "❓")
            
            print(f"ID: {apt['id']} | {status_icon} {apt['status'].upper()}")
            print(f"  Patient: {apt['user_name']}")
            print(f"  Symptoms: {apt['patient_symptoms']}")
            print(f"  Date: {apt['booking_date']}")
            print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointments"))


def view_appointment_detail_worker(worker_id):
    """View detailed information about a specific appointment"""
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/appointment/{apt_id}?sender_role=worker&worker_id={worker_id}")
    
    if r.status_code == 200:
        apt = r.json()
        print("\n📄 Appointment Details:")
        print("-" * 80)
        print(f"ID: {apt['id']}")
        print(f"Status: {apt['status']}")
        print(f"Patient: {apt['user_name']}")
        print(f"Symptoms: {apt['patient_symptoms']}")
        print(f"Booking Date: {apt['booking_date']}")
        print(f"Created: {apt['created_at']}")
        print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointment"))


def respond_to_appointment(worker_id):
    """Accept or reject an appointment"""
    apt_id = input("Appointment ID: ").strip()
    
    print("\n1. Accept")
    print("2. Reject")
    choice = input("Choice: ").strip()
    
    if choice == "1":
        status = "accepted"
    elif choice == "2":
        status = "rejected"
    else:
        print("❌ Invalid choice")
        return
    
    r = requests.post(f"{API}/worker/respond-appointment", json={
        "appointment_id": int(apt_id),
        "status": status
    })
    
    if r.status_code == 200:
        print(f"✅ Appointment {status} successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to update appointment"))


def start_consultation_worker(worker_id):
    """Start consultation for an accepted appointment"""
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.post(f"{API}/appointment/start-consultation", json={
        "appointment_id": int(apt_id)
    })
    
    if r.status_code == 200:
        print("✅ Consultation started successfully")
        print("💬 Chat is now available for this appointment")
    else:
        print("❌ Error:", r.json().get("error", "Failed to start consultation"))


def complete_appointment_worker(worker_id):
    """Mark an appointment as completed"""
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.post(f"{API}/appointment/complete", json={
        "appointment_id": int(apt_id)
    })
    
    if r.status_code == 200:
        print("✅ Appointment marked as completed")
    else:
        print("❌ Error:", r.json().get("error", "Failed to complete appointment"))


def cancel_appointment_worker(worker_id):
    """Cancel an appointment"""
    apt_id = input("Appointment ID: ").strip()
    
    confirm = input("Are you sure you want to cancel? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Cancelled")
        return
    
    r = requests.post(f"{API}/appointment/cancel", json={
        "appointment_id": int(apt_id)
    })
    
    if r.status_code == 200:
        print("✅ Appointment cancelled successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to cancel appointment"))


def view_messages_worker(worker_id):
    """View messages in an appointment chat"""
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/messages/{apt_id}?sender_role=worker&worker_id={worker_id}")
    
    if r.status_code == 200:
        data = r.json()
        messages = data.get("messages", [])
        
        if not messages:
            print("\n📭 No messages yet")
            return
        
        print(f"\n💬 Messages for Appointment #{apt_id}:")
        print("-" * 80)
        for msg in messages:
            sender_label = "👤 You" if msg["sender_role"] == "worker" else "👨‍⚕️ Patient"
            print(f"{sender_label} ({msg['timestamp'][:19]}):")
            print(f"  {msg['message']}")
            print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch messages"))


def send_message_worker(worker_id):
    """Send a message in an appointment chat"""
    apt_id = input("Appointment ID: ").strip()
    message = input("Message: ").strip()
    
    if not message:
        print("❌ Message cannot be empty")
        return
    
    r = requests.post(f"{API}/messages/send", json={
        "appointment_id": int(apt_id),
        "sender_role": "worker",
        "worker_id": worker_id,
        "message": message
    })
    
    if r.status_code == 201:
        print("✅ Message sent successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to send message"))


# ==================================================
# ================= ADMIN DASHBOARD ================
# ==================================================

def admin_login():
    print("\n🔐 Admin Login")

    u = input("Username: ").strip()
    p = input("Password: ").strip()

    if u == "admin" and p == "admin123":
        print("✅ Admin logged in")
        admin_menu()
    else:
        print("❌ Invalid credentials")


def admin_menu():
    while True:
        print("\n=== ADMIN DASHBOARD ===")
        print("1. View Pending Workers")
        print("2. Approve Worker")
        print("3. Reject Worker")
        print("4. Logout")

        c = input("Choice: ").strip()

        if c == "1":
            r = requests.get(f"{API}/admin/workers/pending")
            print("\nPending Workers:")
            for w in r.json():
                print(f"ID:{w[0]} | {w[1]} | {w[2]} | {w[3]}")

        elif c == "2":
            wid = input("Worker ID: ").strip()
            requests.post(f"{API}/admin/worker/approve/{wid}")
            print("✅ Worker approved")

        elif c == "3":
            wid = input("Worker ID: ").strip()
            requests.post(f"{API}/admin/worker/reject/{wid}")
            print("❌ Worker rejected")

        elif c == "4":
            return


# ==================================================
# ================= MAIN ===========================
# ==================================================

def main():
    while True:
        print("\n=== ExpertEase ===")
        print("1. User")
        print("2. Worker")
        print("3. Admin")
        print("4. Exit")

        c = input("Choice: ").strip()

        if c == "1":
            user_menu()
        elif c == "2":
            worker_menu()
        elif c == "3":
            admin_login()
        elif c == "4":
            print("👋 Goodbye")
            break


if __name__ == "__main__":
    main()
