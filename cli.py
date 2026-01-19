import requests
import sys

API = "http://127.0.0.1:5000"
TOKEN = None
USER_ID = None

def check_server_connection():
    """Check if Flask server is running"""
    try:
        _ = requests.get(f"{API}/workers/available", timeout=2)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False

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
        service_selection()
    else:
        print("❌ Login failed:", r.json().get("error"))


def service_selection():
    """Service Selection Screen - User selects from 5 services"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*50)
        print("🏠 EXPERTEASE - SELECT A SERVICE")
        print("="*50)
        print("1. 🏥 Healthcare")
        print("2. 🏠 Housekeeping")
        print("3. 📦 Resource Management")
        print("4. 🚗 Car Services")
        print("5. 💰 Money Management")
        print("6. 👋 Logout")
        
        choice = input("\nSelect service: ").strip()
        
        if choice == "1":
            healthcare_navigation()
        elif choice == "2":
            print("🚧 Housekeeping service coming soon!")
        elif choice == "3":
            print("🚧 Resource Management service coming soon!")
        elif choice == "4":
            print("🚧 Car Services coming soon!")
        elif choice == "5":
            print("🚧 Money Management coming soon!")
        elif choice == "6":
            TOKEN = None
            USER_ID = None
            print("👋 Logged out")
            return
        else:
            print("❌ Invalid choice")


def healthcare_navigation():
    """Healthcare Navigation - 5 tabs like Instagram bottom nav"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*50)
        print("🏥 HEALTHCARE")
        print("="*50)
        print("1. 🏠 Home")
        print("2. 🤖 AI Care")
        print("3. 🔍 Explore")
        print("4. 📅 Appointments")
        print("5. 👤 Profile")
        print("6. ⬅️  Back to Services")
        
        choice = input("\nSelect tab: ").strip()
        
        if choice == "1":
            healthcare_home_tab()
        elif choice == "2":
            healthcare_ai_care_tab()
        elif choice == "3":
            healthcare_explore_tab()
        elif choice == "4":
            healthcare_appointments_tab()
        elif choice == "5":
            healthcare_profile_tab()
        elif choice == "6":
            return
        else:
            print("❌ Invalid choice")


def healthcare_home_tab():
    """Healthcare Home Tab - Show specializations, then doctor cards"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    # Get all specializations
    r = requests.get(f"{API}/healthcare/specializations")
    if r.status_code != 200:
        print("❌ Error fetching specializations")
        return
    
    specializations = r.json().get("specializations", [])
    
    # Default specializations if none in DB
    default_specs = [
        "Dentist", "Cardiologist", "Eye Specialist", "ENT", "Orthopedic",
        "Dermatologist", "Neurologist", "Psychiatrist", "Gynecologist",
        "Pediatrician", "General Physician", "Urologist", "Gastroenterologist",
        "Endocrinologist", "Pulmonologist", "Oncologist", "Rheumatologist",
        "Nephrologist", "Hepatologist", "Allergist"
    ]
    
    if not specializations:
        specializations = default_specs
    
    while True:
        print("\n" + "="*60)
        print("🏠 HEALTHCARE HOME")
        print("="*60)
        print("\n📋 Medical Specializations:")
        print("-" * 60)
        
        for idx, spec in enumerate(specializations[:20], 1):  # Show max 20
            print(f"{idx:2}. {spec}")
        
        print(f"\n{len(specializations) + 1}. 🔍 Search within specialization")
        print(f"{len(specializations) + 2}. ⬅️  Back")
        
        choice = input("\nSelect specialization: ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(specializations):
                selected_spec = specializations[choice_num - 1]
                show_doctors_by_specialization(selected_spec)
            elif choice_num == len(specializations) + 1:
                search_within_specialization()
            elif choice_num == len(specializations) + 2:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def show_doctors_by_specialization(specialization):
    """Show doctor cards for a selected specialization"""
    global TOKEN, USER_ID
    
    r = requests.get(f"{API}/healthcare/doctors/{specialization}")
    if r.status_code != 200:
        print("❌ Error fetching doctors")
        return
    
    doctors = r.json().get("doctors", [])
    
    if not doctors:
        print(f"\n👨‍⚕️ No {specialization} doctors available at the moment")
        input("\nPress Enter to continue...")
        return
    
    while True:
        print("\n" + "="*70)
        print(f"🏥 {specialization.upper()} - Available Doctors")
        print("="*70)
        
        for idx, doc in enumerate(doctors, 1):
            print(f"\n[{idx}] DOCTOR CARD")
            print("-" * 70)
            print(f"👤 Name: Dr. {doc['full_name']}")
            print(f"⭐ Rating: {doc.get('rating', 0.0):.1f}/5.0")
            print(f"📅 Experience: {doc['experience']} years")
            print(f"📍 Location: {doc.get('clinic_location', 'Location not specified')}")
            print(f"🆔 Doctor ID: {doc['id']}")
            print("-" * 70)
        
        print(f"\n{len(doctors) + 1}. 🔍 Search by doctor name")
        print(f"{len(doctors) + 2}. ⬅️  Back to Specializations")
        
        choice = input("\nSelect doctor (or search/back): ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(doctors):
                selected_doc = doctors[choice_num - 1]
                show_doctor_actions(selected_doc)
            elif choice_num == len(doctors) + 1:
                search_doctor_by_name(doctors)
            elif choice_num == len(doctors) + 2:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def show_doctor_actions(doctor):
    """Show actions for selected doctor: Book Appointment, Audio/Video Call"""
    global TOKEN, USER_ID
    
    while True:
        print("\n" + "="*60)
        print(f"👨‍⚕️ Dr. {doctor['full_name']}")
        print("="*60)
        print(f"Specialization: {doctor['specialization']}")
        print(f"Experience: {doctor['experience']} years")
        print(f"Location: {doctor.get('clinic_location', 'N/A')}")
        print(f"Rating: {doctor.get('rating', 0.0):.1f}/5.0")
        print("="*60)
        print("\n1. 📅 Book Appointment")
        print("2. 📞 Audio / Video Call")
        print("3. ⬅️  Back")
        
        choice = input("\nSelect action: ").strip()
        
        if choice == "1":
            book_appointment_user(doctor['id'])
        elif choice == "2":
            print("🚧 Audio/Video Call feature coming soon!")
            print("💡 This will be available after appointment is accepted")
            input("\nPress Enter to continue...")
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")


def search_within_specialization():
    """Search doctors within a specialization"""
    spec = input("Enter specialization name: ").strip()
    if spec:
        show_doctors_by_specialization(spec)
    else:
        print("❌ Please enter a specialization name")


def search_doctor_by_name(doctors):
    """Search doctor by name within current list"""
    query = input("Enter doctor name to search: ").strip().lower()
    if not query:
        return
    
    matched = [doc for doc in doctors if query in doc['full_name'].lower()]
    
    if not matched:
        print(f"\n❌ No doctors found matching '{query}'")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n✅ Found {len(matched)} doctor(s):")
    for idx, doc in enumerate(matched, 1):
        print(f"{idx}. Dr. {doc['full_name']} - {doc['specialization']}")
    
    if len(matched) == 1:
        show_doctor_actions(matched[0])
    else:
        choice = input("\nSelect doctor number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(matched):
            show_doctor_actions(matched[int(choice) - 1])


def healthcare_ai_care_tab():
    """AI Care Tab - Symptom checker that suggests doctors"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    print("\n" + "="*60)
    print("🤖 AI CARE - Symptom Checker")
    print("="*60)
    print("Describe your health issue and AI will suggest the right doctor")
    print("-" * 60)
    
    symptoms = input("\n💬 What health issue are you experiencing? ").strip()
    
    if not symptoms:
        print("❌ Please describe your symptoms")
        return
    
    print("\n🤖 AI is analyzing your symptoms...")
    
    r = requests.post(f"{API}/healthcare/ai-care", json={"symptoms": symptoms})
    
    if r.status_code != 200:
        print("❌ Error:", r.json().get("error", "AI Care service unavailable"))
        return
    
    data = r.json()
    suggested_specs = data.get("suggested_specializations", [])
    suggested_doctors = data.get("suggested_doctors", [])
    
    print("\n" + "="*60)
    print("🤖 AI ANALYSIS RESULTS")
    print("="*60)
    
    if suggested_specs:
        print("\n📋 Suggested Specializations:")
        for idx, spec in enumerate(suggested_specs, 1):
            print(f"  {idx}. {spec}")
    else:
        print("\n⚠️ Could not identify specific specialization")
        print("💡 Consider consulting a General Physician")
    
    if suggested_doctors:
        print("\n👨‍⚕️ Recommended Doctors:")
        print("-" * 60)
        for idx, doc in enumerate(suggested_doctors, 1):
            print(f"\n[{idx}] Dr. {doc['full_name']}")
            print(f"   Specialization: {doc['specialization']}")
            print(f"   Experience: {doc['experience']} years")
            print(f"   Rating: {doc.get('rating', 0.0):.1f}/5.0")
            print(f"   Location: {doc.get('clinic_location', 'N/A')}")
        
        print("\n" + "-" * 60)
        choice = input("\nSelect doctor to book appointment (or 0 to go back): ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(suggested_doctors):
                book_appointment_user(suggested_doctors[choice_num - 1]['id'])
            elif choice_num == 0:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")
    else:
        print("\n💡 No specific doctors found. Please try the Explore tab.")
    
    input("\nPress Enter to continue...")


def healthcare_explore_tab():
    """Explore Tab - Global doctor search"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*60)
        print("🔍 EXPLORE - Search Doctors")
        print("="*60)
        print("Search by: Doctor name, Specialization, or Location")
        print("-" * 60)
        
        query = input("\n🔍 Enter search query: ").strip()
        
        if not query:
            print("❌ Please enter a search query")
            continue
        
        if query.lower() == "back":
            return
        
        print("\n🔍 Searching...")
        
        r = requests.get(f"{API}/healthcare/search?q={query}")
        
        if r.status_code != 200:
            print("❌ Error:", r.json().get("error", "Search failed"))
            continue
        
        doctors = r.json().get("doctors", [])
        
        if not doctors:
            print(f"\n❌ No doctors found matching '{query}'")
            input("\nPress Enter to continue...")
            continue
        
        print(f"\n✅ Found {len(doctors)} doctor(s):")
        print("="*60)
        
        for idx, doc in enumerate(doctors, 1):
            print(f"\n[{idx}] Dr. {doc['full_name']}")
            print(f"   Specialization: {doc['specialization']}")
            print(f"   Experience: {doc['experience']} years")
            print(f"   Rating: {doc.get('rating', 0.0):.1f}/5.0")
            print(f"   Location: {doc.get('clinic_location', 'N/A')}")
            print(f"   ID: {doc['id']}")
        
        print("\n" + "="*60)
        print(f"{len(doctors) + 1}. 🔍 New Search")
        print(f"{len(doctors) + 2}. ⬅️  Back")
        
        choice = input("\nSelect doctor (or search/back): ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(doctors):
                show_doctor_actions(doctors[choice_num - 1])
            elif choice_num == len(doctors) + 1:
                continue  # New search
            elif choice_num == len(doctors) + 2:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def book_appointment_user(doctor_id=None):
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
    
    print("\n" + "="*60)
    print("📅 BOOK APPOINTMENT")
    print("="*60)
    
    if doctor_id:
        worker_id = str(doctor_id)
        print(f"Doctor ID: {worker_id}")
    else:
        worker_id = input("Doctor ID: ").strip()
    
    user_name = input("Your Name: ").strip()
    symptoms = input("Symptoms/Reason: ").strip()
    date = input("Preferred Date (YYYY-MM-DD): ").strip()

    print("\nAppointment Type:")
    print("1. Clinic Visit")
    print("2. Video / Audio Consultation")
    apt_type_choice = input("Choose type (1/2): ").strip()
    if apt_type_choice == "2":
        appointment_type = "video"
    else:
        appointment_type = "clinic"
    
    if not all([worker_id, user_name, symptoms, date]):
        print("❌ All fields are required")
        input("\nPress Enter to continue...")
        return
    
    r = requests.post(f"{API}/book-appointment", json={
        "user_id": int(USER_ID),
        "worker_id": int(worker_id),
        "user_name": user_name,
        "symptoms": symptoms,
        "date": date,
        "appointment_type": appointment_type
    })
    
    if r.status_code == 201:
        data = r.json()
        print("\n✅ Appointment requested successfully!")
        print(f"📋 Appointment ID: {data['id']}")
        if appointment_type == "video":
            print("📹 Type: Video / Audio Consultation")
        else:
            print("🏥 Type: Clinic Visit")
        print("⏳ Waiting for doctor's approval...")
    else:
        print("❌ Error:", r.json().get("error", "Failed to book appointment"))
    
    input("\nPress Enter to continue...")


def healthcare_appointments_tab():
    """Healthcare Appointments Tab - View and manage appointments"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*60)
        print("📅 APPOINTMENTS")
        print("="*60)
        
        r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
        
        if r.status_code != 200:
            print("❌ Error:", r.json().get("error", "Failed to fetch appointments"))
            input("\nPress Enter to continue...")
            return
        
        appointments = r.json().get("appointments", [])
        
        if not appointments:
            print("\n📭 No appointments found")
            print("\n1. ⬅️  Back")
            choice = input("\nChoice: ").strip()
            if choice == "1":
                return
            continue
        
        print("\n📋 Your Appointments:")
        print("-" * 60)
        
        for idx, apt in enumerate(appointments, 1):
            status_icon = {
                "pending": "⏳",
                "accepted": "✅",
                "rejected": "❌",
                "in_consultation": "💬",
                "completed": "✓",
                "cancelled": "🚫"
            }.get(apt["status"], "❓")
            apt_type = apt.get("appointment_type", "clinic")
            type_label = "VIDEO" if apt_type == "video" else "CLINIC"
            
            print(f"\n[{idx}] {status_icon} {apt['status'].upper()} ({type_label})")
            print(f"    Appointment ID: {apt['id']}")
            print(f"    Doctor ID: {apt['worker_id']}")
            print(f"    Symptoms: {apt['patient_symptoms']}")
            print(f"    Date: {apt['booking_date']}")
            print("-" * 60)
        
        print(f"\n{len(appointments) + 1}. View Appointment Details")
        print(f"{len(appointments) + 2}. Cancel Appointment")
        print(f"{len(appointments) + 3}. Join Video Call (if accepted)")
        print(f"{len(appointments) + 4}. View Messages")
        print(f"{len(appointments) + 5}. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(appointments):
                apt = appointments[choice_num - 1]
                view_appointment_detail_user(apt['id'])
            elif choice_num == len(appointments) + 1:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    view_appointment_detail_user(apt_id)
            elif choice_num == len(appointments) + 2:
                apt_id = input("Enter Appointment ID to cancel: ").strip()
                if apt_id:
                    cancel_appointment_user(apt_id)
            elif choice_num == len(appointments) + 3:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    join_video_call(appointments, apt_id)
            elif choice_num == len(appointments) + 4:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    view_messages_user(apt_id)
            elif choice_num == len(appointments) + 5:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def join_video_call(appointments, appointment_id):
    """Join video/audio call for a video appointment (simulated)"""
    # Find appointment in list
    apt = None
    for a in appointments:
        if str(a["id"]) == str(appointment_id):
            apt = a
            break

    if not apt:
        print("❌ Appointment not found in your list")
        input("\nPress Enter to continue...")
        return

    apt_type = apt.get("appointment_type", "clinic")
    status = apt.get("status", "")

    if apt_type != "video":
        print("\n❌ This is a clinic appointment. Video/Audio call is not available.")
        input("\nPress Enter to continue...")
        return

    if status not in ["accepted", "in_consultation"]:
        print("\n❌ Video/Audio call available only after doctor accepts the appointment.")
        print(f"Current status: {status}")
        input("\nPress Enter to continue...")
        return

    print("\n" + "="*60)
    print("📹 JOINING VIDEO / AUDIO CONSULTATION (SIMULATED)")
    print("="*60)
    print(f"Appointment ID: {apt['id']}")
    print(f"Doctor ID: {apt['worker_id']}")
    print(f"Status: {status}")

    if status == "accepted":
        print("\n⏳ Waiting for doctor to start the consultation...")
    elif status == "in_consultation":
        print("\n✅ Video/Audio consultation started (simulated).")

    print("\n💬 This is a simulation. In the real app, a video SDK (e.g., Jitsi/Zoom/Agora) would open here.")
    input("\nPress Enter to leave the call...")


def healthcare_profile_tab():
    """Healthcare Profile Tab - User details and appointment history"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*60)
        print("👤 PROFILE")
        print("="*60)
        
        # Get user info
        r = requests.get(f"{API}/user/info", headers={"Authorization": f"Bearer {TOKEN}"})
        if r.status_code == 200:
            user_info = r.json()
            print(f"\n🆔 User ID: {user_info.get('user_id', 'N/A')}")
        
        # Get appointment history
        r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
        if r.status_code == 200:
            appointments = r.json().get("appointments", [])
            
            print(f"\n📊 Appointment Statistics:")
            print("-" * 60)
            status_counts = {}
            for apt in appointments:
                status = apt['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"  {status.upper()}: {count}")
            
            print(f"\n📋 Total Appointments: {len(appointments)}")
        
        print("\n" + "="*60)
        print("1. View Full Appointment History")
        print("2. 👋 Logout")
        print("3. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_full_appointment_history()
        elif choice == "2":
            TOKEN = None
            USER_ID = None
            print("👋 Logged out")
            return
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")


def view_full_appointment_history():
    """View complete appointment history"""
    global TOKEN
    
    r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
    if r.status_code != 200:
        print("❌ Error fetching appointments")
        input("\nPress Enter to continue...")
        return
    
    appointments = r.json().get("appointments", [])
    
    if not appointments:
        print("\n📭 No appointment history")
        input("\nPress Enter to continue...")
        return
    
    print("\n" + "="*70)
    print("📋 COMPLETE APPOINTMENT HISTORY")
    print("="*70)
    
    for apt in appointments:
        status_icon = {
            "pending": "⏳",
            "accepted": "✅",
            "rejected": "❌",
            "in_consultation": "💬",
            "completed": "✓",
            "cancelled": "🚫"
        }.get(apt["status"], "❓")
        
        print(f"\n{status_icon} Appointment #{apt['id']} - {apt['status'].upper()}")
        print(f"   Doctor ID: {apt['worker_id']}")
        print(f"   Symptoms: {apt['patient_symptoms']}")
        print(f"   Booking Date: {apt['booking_date']}")
        print(f"   Created: {apt.get('created_at', 'N/A')}")
        print("-" * 70)
    
    input("\nPress Enter to continue...")


def view_user_appointments():
    """Legacy function - redirects to healthcare appointments tab"""
    healthcare_appointments_tab()


def view_appointment_detail_user(appointment_id=None):
    """View detailed information about a specific appointment"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/appointment/{appointment_id}?sender_role=user", 
                     headers={"Authorization": f"Bearer {TOKEN}"})
    
    if r.status_code == 200:
        apt = r.json()
        print("\n" + "="*60)
        print("📄 APPOINTMENT DETAILS")
        print("="*60)
        print(f"ID: {apt['id']}")
        print(f"Status: {apt['status']}")
        print(f"Doctor ID: {apt['worker_id']}")
        print(f"Patient: {apt['user_name']}")
        print(f"Symptoms: {apt['patient_symptoms']}")
        print(f"Booking Date: {apt['booking_date']}")
        print(f"Created: {apt['created_at']}")
        print("="*60)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointment"))
    
    input("\nPress Enter to continue...")


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
    specialization = input("Specialization (Dentist, Eye Specialist, etc): ").strip()
    clinic_location = input("Clinic Location: ").strip()

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
        "experience": experience,
        "clinic_location": clinic_location
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
    """Doctor Dashboard - 5 tabs: Dashboard, Availability, Requests, Appointments, Profile"""
    while True:
        print("\n" + "="*60)
        print("👨‍⚕️ DOCTOR DASHBOARD")
        print("="*60)
        print("1. 📊 Dashboard")
        print("2. 📅 Availability")
        print("3. 📥 Requests")
        print("4. 📋 Appointments")
        print("5. 👤 Profile")
        print("6. 👋 Logout")

        c = input("\nSelect tab: ").strip()

        if c == "1":
            doctor_dashboard_tab(worker_id)
        elif c == "2":
            doctor_availability_tab(worker_id)
        elif c == "3":
            doctor_requests_tab(worker_id)
        elif c == "4":
            doctor_appointments_tab(worker_id)
        elif c == "5":
            should_logout = doctor_profile_tab(worker_id)
            if should_logout:
                return
        elif c == "6":
            print("👋 Logged out")
            return
        else:
            print("❌ Invalid choice")


def doctor_dashboard_tab(worker_id):
    """Dashboard Tab - Shows today's appointments, pending requests, and status"""
    while True:
        print("\n" + "="*60)
        print("📊 DASHBOARD")
        print("="*60)
        
        # Get dashboard stats
        r = requests.get(f"{API}/worker/{worker_id}/dashboard/stats")
        if r.status_code == 200:
            stats = r.json()
            print(f"\n📥 Pending Requests: {stats.get('pending_requests', 0)}")
            print(f"📅 Today's Appointments: {stats.get('today_appointments', 0)}")
            print(f"✅ Accepted Appointments: {stats.get('accepted_appointments', 0)}")
            print(f"📊 Total Appointments: {stats.get('total_appointments', 0)}")
        else:
            print("❌ Error fetching dashboard stats")
        
        # Get worker status
        r = requests.get(f"{API}/worker/{worker_id}/status")
        if r.status_code == 200:
            status_data = r.json()
            status = status_data.get('status', 'online')
            status_icon = "🟢" if status == "online" else "🔴"
            print(f"\n{status_icon} Status: {status.upper()}")
        
        # Show today's appointments
        r = requests.get(f"{API}/worker/{worker_id}/dashboard/stats")
        if r.status_code == 200:
            stats = r.json()
            today_list = stats.get('today_appointments_list', [])
            if today_list:
                print("\n📅 Today's Appointments:")
                print("-" * 60)
                for apt in today_list:
                    status_icon = {
                        "pending": "⏳",
                        "accepted": "✅",
                        "in_consultation": "💬",
                        "completed": "✓"
                    }.get(apt['status'], "❓")
                    print(f"{status_icon} Appointment #{apt['id']} - {apt['user_name']}")
                    print(f"   Time: {apt['booking_date']}")
                    print(f"   Symptoms: {apt['patient_symptoms'][:50]}...")
                    print("-" * 60)
        
        print("\n" + "="*60)
        print("1. 🔄 Refresh")
        print("2. ⚙️  Change Status")
        print("3. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            continue  # Refresh
        elif choice == "2":
            change_worker_status(worker_id)
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")


def change_worker_status(worker_id):
    """Change worker online/offline status"""
    print("\n" + "="*60)
    print("⚙️ CHANGE STATUS")
    print("="*60)
    print("1. 🟢 Online")
    print("2. 🔴 Offline")
    print("3. ⬅️  Back")
    
    choice = input("\nSelect status: ").strip()
    
    if choice == "1":
        status = "online"
    elif choice == "2":
        status = "offline"
    elif choice == "3":
        return
    else:
        print("❌ Invalid choice")
        return
    
    r = requests.post(f"{API}/worker/{worker_id}/status", json={"status": status})
    if r.status_code == 200:
        print(f"\n✅ Status changed to {status.upper()}")
    else:
        print("❌ Error changing status")
    
    input("\nPress Enter to continue...")


def doctor_availability_tab(worker_id):
    """Availability Tab - Manage available dates and time slots"""
    while True:
        print("\n" + "="*60)
        print("📅 AVAILABILITY")
        print("="*60)
        print("1. View Availability")
        print("2. Add Time Slot")
        print("3. Remove Time Slot")
        print("4. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_worker_availability(worker_id)
        elif choice == "2":
            add_availability_slot(worker_id)
        elif choice == "3":
            remove_availability_slot(worker_id)
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice")


def view_worker_availability(worker_id):
    """View worker's availability"""
    print("\n" + "="*60)
    print("📅 YOUR AVAILABILITY")
    print("="*60)
    
    date_filter = input("Enter date to filter (YYYY-MM-DD) or press Enter for all: ").strip()
    
    url = f"{API}/worker/{worker_id}/availability"
    if date_filter:
        url += f"?date={date_filter}"
    
    r = requests.get(url)
    
    if r.status_code == 200:
        availability = r.json().get("availability", [])
        
        if not availability:
            print("\n📭 No availability set")
        else:
            # Group by date
            by_date = {}
            for slot in availability:
                date = slot['date']
                if date not in by_date:
                    by_date[date] = []
                by_date[date].append(slot['time_slot'])
            
            for date in sorted(by_date.keys()):
                print(f"\n📅 {date}")
                print("-" * 60)
                for time_slot in sorted(by_date[date]):
                    print(f"  ⏰ {time_slot}")
    else:
        print("❌ Error fetching availability")
    
    input("\nPress Enter to continue...")


def add_availability_slot(worker_id):
    """Add a new availability time slot"""
    print("\n" + "="*60)
    print("➕ ADD AVAILABILITY")
    print("="*60)
    
    date = input("Date (YYYY-MM-DD): ").strip()
    time_slot = input("Time Slot (e.g., 09:00-10:00): ").strip()
    
    if not date or not time_slot:
        print("❌ Date and time slot are required")
        input("\nPress Enter to continue...")
        return
    
    r = requests.post(f"{API}/worker/{worker_id}/availability", json={
        "date": date,
        "time_slot": time_slot
    })
    
    if r.status_code == 200:
        print("\n✅ Availability added successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to add availability"))
    
    input("\nPress Enter to continue...")


def remove_availability_slot(worker_id):
    """Remove an availability time slot"""
    print("\n" + "="*60)
    print("➖ REMOVE AVAILABILITY")
    print("="*60)
    
    date = input("Date (YYYY-MM-DD): ").strip()
    time_slot = input("Time Slot (e.g., 09:00-10:00): ").strip()
    
    if not date or not time_slot:
        print("❌ Date and time slot are required")
        input("\nPress Enter to continue...")
        return
    
    r = requests.delete(f"{API}/worker/{worker_id}/availability", json={
        "date": date,
        "time_slot": time_slot
    })
    
    if r.status_code == 200:
        print("\n✅ Availability removed successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to remove availability"))
    
    input("\nPress Enter to continue...")


def doctor_requests_tab(worker_id):
    """Requests Tab - View and respond to appointment requests"""
    while True:
        print("\n" + "="*60)
        print("📥 REQUESTS")
        print("="*60)
        
        r = requests.get(f"{API}/worker/{worker_id}/requests")
        
        if r.status_code != 200:
            print("❌ Error fetching requests")
            input("\nPress Enter to continue...")
            return
        
        requests_list = r.json().get("requests", [])
        
        if not requests_list:
            print("\n📭 No pending requests")
            print("\n1. 🔄 Refresh")
            print("2. ⬅️  Back")
            
            choice = input("\nSelect option: ").strip()
            if choice == "1":
                continue
            elif choice == "2":
                return
            continue
        
        print(f"\n📥 Pending Requests: {len(requests_list)}")
        print("-" * 60)
        
        for idx, req in enumerate(requests_list, 1):
            print(f"\n[{idx}] Appointment #{req['id']}")
            print(f"    Patient: {req['user_name']}")
            print(f"    Date: {req['booking_date']}")
            print(f"    Symptoms: {req['patient_symptoms']}")
            print("-" * 60)
        
        print(f"\n{len(requests_list) + 1}. 🔄 Refresh")
        print(f"{len(requests_list) + 2}. ⬅️  Back")
        
        choice = input("\nSelect request to respond (or refresh/back): ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(requests_list):
                respond_to_appointment(worker_id, requests_list[choice_num - 1]['id'])
            elif choice_num == len(requests_list) + 1:
                continue  # Refresh
            elif choice_num == len(requests_list) + 2:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def doctor_appointments_tab(worker_id):
    """Appointments Tab - Manage accepted appointments"""
    while True:
        print("\n" + "="*60)
        print("📋 APPOINTMENTS")
        print("="*60)
        
        r = requests.get(f"{API}/worker/{worker_id}/accepted-appointments")
        
        if r.status_code != 200:
            print("❌ Error fetching appointments")
            input("\nPress Enter to continue...")
            return
        
        appointments = r.json().get("appointments", [])
        
        if not appointments:
            print("\n📭 No accepted appointments")
            print("\n1. 🔄 Refresh")
            print("2. ⬅️  Back")
            
            choice = input("\nSelect option: ").strip()
            if choice == "1":
                continue
            elif choice == "2":
                return
            continue
        
        print(f"\n📋 Accepted Appointments: {len(appointments)}")
        print("-" * 60)
        
        for idx, apt in enumerate(appointments, 1):
            status_icon = {
                "accepted": "✅",
                "in_consultation": "💬",
                "completed": "✓"
            }.get(apt['status'], "❓")
            apt_type = apt.get("appointment_type", "clinic")
            type_label = "VIDEO" if apt_type == "video" else "CLINIC"
            
            print(f"\n[{idx}] {status_icon} Appointment #{apt['id']} - {apt['status'].upper()} ({type_label})")
            print(f"    Patient: {apt['user_name']}")
            print(f"    Date: {apt['booking_date']}")
            print(f"    Symptoms: {apt['patient_symptoms']}")
            print("-" * 60)
        
        print(f"\n{len(appointments) + 1}. View Details")
        print(f"{len(appointments) + 2}. Start Consultation")
        print(f"{len(appointments) + 3}. Complete Appointment")
        print(f"{len(appointments) + 4}. View Messages")
        print(f"{len(appointments) + 5}. 🔄 Refresh")
        print(f"{len(appointments) + 6}. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(appointments):
                apt_id = appointments[choice_num - 1]['id']
                view_appointment_detail_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 1:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    view_appointment_detail_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 2:
                apt_id = input("Enter Appointment ID to start consultation: ").strip()
                if apt_id:
                    start_consultation_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 3:
                apt_id = input("Enter Appointment ID to complete: ").strip()
                if apt_id:
                    complete_appointment_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 4:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    view_messages_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 5:
                continue  # Refresh
            elif choice_num == len(appointments) + 6:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def doctor_profile_tab(worker_id):
    """Profile Tab - Doctor personal details and settings"""
    while True:
        print("\n" + "="*60)
        print("👤 PROFILE")
        print("="*60)
        
        # Get worker info - we'll need to fetch from appointments or create an endpoint
        # For now, show basic info
        print(f"\n🆔 Worker ID: {worker_id}")
        print("📋 Verification Status: Approved")
        print("💡 Full profile details coming soon")
        print("\nThis will show:")
        print("  - Name")
        print("  - Email")
        print("  - Specialization")
        print("  - Experience")
        print("  - Clinic Location")
        print("  - Rating")
        
        print("\n" + "="*60)
        print("1. View Full Details")
        print("2. 👋 Logout")
        print("3. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_worker_full_profile(worker_id)
        elif choice == "2":
            print("👋 Logged out")
            return True  # Signal logout
        elif choice == "3":
            return False
        else:
            print("❌ Invalid choice")


def view_worker_full_profile(worker_id):
    """View complete worker profile"""
    print("\n" + "="*60)
    print("👤 DOCTOR PROFILE")
    print("="*60)
    print("💡 Full profile view coming soon")
    print("This will show: Name, Email, Specialization, Experience, Location, Rating")
    input("\nPress Enter to continue...")


def respond_to_appointment(worker_id, appointment_id=None):
    """Accept or reject an appointment request"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    print("\n" + "="*60)
    print("📥 RESPOND TO REQUEST")
    print("="*60)
    print("1. ✅ Accept")
    print("2. ❌ Reject")
    print("3. ⬅️  Cancel")
    
    choice = input("\nSelect action: ").strip()
    
    if choice == "1":
        status = "accepted"
    elif choice == "2":
        status = "rejected"
    elif choice == "3":
        return
    else:
        print("❌ Invalid choice")
        return
    
    r = requests.post(f"{API}/worker/respond-appointment", json={
        "appointment_id": int(appointment_id),
        "status": status
    })
    
    if r.status_code == 200:
        print(f"\n✅ Appointment {status} successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to update appointment"))
    
    input("\nPress Enter to continue...")


def view_appointment_detail_worker(worker_id, appointment_id=None):
    """View detailed information about a specific appointment"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/appointment/{appointment_id}?sender_role=worker&worker_id={worker_id}")
    
    if r.status_code == 200:
        apt = r.json()
        print("\n" + "="*60)
        print("📄 APPOINTMENT DETAILS")
        print("="*60)
        print(f"ID: {apt['id']}")
        print(f"Status: {apt['status']}")
        print(f"Patient: {apt['user_name']}")
        print(f"Symptoms: {apt['patient_symptoms']}")
        print(f"Booking Date: {apt['booking_date']}")
        print(f"Created: {apt['created_at']}")
        print("="*60)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointment"))
    
    input("\nPress Enter to continue...")


def start_consultation_worker(worker_id, appointment_id=None):
    """Start consultation for an accepted appointment"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.post(f"{API}/appointment/start-consultation", json={
        "appointment_id": int(appointment_id)
    })
    
    if r.status_code == 200:
        print("\n✅ Consultation started successfully")
        print("💬 Chat is now available for this appointment")
        print("📹 If this is a video appointment, the video/audio session is now considered ACTIVE (simulated).")
    else:
        print("❌ Error:", r.json().get("error", "Failed to start consultation"))
    
    input("\nPress Enter to continue...")


def complete_appointment_worker(worker_id, appointment_id=None):
    """Mark an appointment as completed"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.post(f"{API}/appointment/complete", json={
        "appointment_id": int(appointment_id)
    })
    
    if r.status_code == 200:
        print("\n✅ Appointment marked as completed")
        print("📹 Any associated video/audio consultation is now considered ENDED (simulated).")
    else:
        print("❌ Error:", r.json().get("error", "Failed to complete appointment"))
    
    input("\nPress Enter to continue...")


def view_messages_worker(worker_id, appointment_id=None):
    """View messages in an appointment chat"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/messages/{appointment_id}?sender_role=worker&worker_id={worker_id}")
    
    if r.status_code == 200:
        data = r.json()
        messages = data.get("messages", [])
        
        if not messages:
            print("\n📭 No messages yet")
        else:
            print(f"\n💬 Messages for Appointment #{appointment_id}:")
            print("-" * 60)
            for msg in messages:
                sender_label = "👤 You" if msg["sender_role"] == "worker" else "👨‍⚕️ Patient"
                print(f"{sender_label} ({msg['timestamp'][:19]}):")
                print(f"  {msg['message']}")
                print("-" * 60)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch messages"))
    
    input("\nPress Enter to continue...")


def send_message_worker(worker_id, appointment_id=None):
    """Send a message in an appointment chat"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    message = input("Message: ").strip()
    
    if not message:
        print("❌ Message cannot be empty")
        return
    
    r = requests.post(f"{API}/messages/send", json={
        "appointment_id": int(appointment_id),
        "sender_role": "worker",
        "worker_id": worker_id,
        "message": message
    })
    
    if r.status_code == 201:
        print("✅ Message sent successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to send message"))
    
    input("\nPress Enter to continue...")


def view_worker_appointments(worker_id):
    """Legacy function - redirects to appointments tab"""
    doctor_appointments_tab(worker_id)


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
    # Check if server is running
    print("\n🔍 Checking server connection...")
    if not check_server_connection():
        print("\n" + "="*60)
        print("❌ ERROR: Flask server is not running!")
        print("="*60)
        print("\n📋 To fix this:")
        print("1. Open a NEW terminal/command prompt")
        print("2. Navigate to the project folder")
        print("3. Run: python app.py")
        print("4. Wait for: 'Running on http://127.0.0.1:5000'")
        print("5. Then come back here and run: python cli.py")
        print("\n💡 Keep the server running in the background!")
        print("="*60)
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("✅ Server connection successful!")
    
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
