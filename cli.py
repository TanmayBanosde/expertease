import requests

API = "http://127.0.0.1:5000"
TOKEN = None

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
    global TOKEN
    print("\n🔐 User Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    r = requests.post(f"{API}/login", json={
        "username": username,
        "password": password
    })

    if r.status_code == 200:
        TOKEN = r.json()["token"]
        print("✅ Logged in successfully")
    else:
        print("❌ Login failed:", r.json().get("error"))


def ask_expert():
    if not TOKEN:
        print("⚠️ Please login first")
        return

    q = input("Ask ExpertEase: ").strip()
    r = requests.post(
        f"{API}/expert-query",
        json={"query": q},
        headers={"Authorization": TOKEN}
    )
    print(r.json())


def user_menu():
    while True:
        print("\n--- USER MENU ---")
        print("1. Signup")
        print("2. Login")
        print("3. Ask Expert")
        print("4. Back")

        c = input("Choice: ").strip()

        if c == "1":
            user_signup()
        elif c == "2":
            user_login()
        elif c == "3":
            ask_expert()
        elif c == "4":
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
        print("👷 Worker Dashboard coming next")
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
