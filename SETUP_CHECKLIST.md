# ✅ Setup Checklist for Friend's PC

## Before Running

### Step 1: Verify All Files Are Present
Check that these files exist in the same folder:
- [ ] app.py
- [ ] cli.py
- [ ] config.py
- [ ] requirements.txt
- [ ] user_db.py
- [ ] worker_db.py
- [ ] appointment_db.py
- [ ] message_db.py
- [ ] availability_db.py
- [ ] auth_utils.py
- [ ] otp_service.py
- [ ] email_service.py
- [ ] README.md (this file)

### Step 2: Install Python
- [ ] Python 3.7+ installed
- [ ] Check: `python --version` in command prompt

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install Flask bcrypt PyJWT Werkzeug
```

### Step 4: Run Backend
```bash
python app.py
```
- [ ] Server starts on http://127.0.0.1:5000
- [ ] No import errors

### Step 5: Test CLI (New Terminal)
```bash
python cli.py
```
- [ ] CLI menu appears
- [ ] Can navigate menus

## ✅ Will It Run? YES, If:

1. ✅ All files are in same folder
2. ✅ Python 3.7+ installed
3. ✅ Dependencies installed
4. ✅ Port 5000 not blocked
5. ✅ No firewall blocking localhost

## 🚨 Common Issues

### Issue: "ModuleNotFoundError"
**Solution:** Install missing package: `pip install <package_name>`

### Issue: "Port already in use"
**Solution:** Change port in app.py: `app.run(debug=True, port=5001)`

### Issue: "ImportError: cannot import name"
**Solution:** Check config.py has all variables (USER_DB, OTP_DB, etc.)

### Issue: Email/OTP not working
**Solution:** 
- Check email credentials in config.py
- For testing, can skip OTP (modify code temporarily)

## 📱 Android App Ready?

### ✅ YES - Perfect Structure!

**Why it's perfect:**
1. ✅ RESTful API (JSON responses)
2. ✅ JWT authentication (secure)
3. ✅ All endpoints documented
4. ✅ Clear request/response format
5. ✅ No platform-specific code
6. ✅ Database is portable (SQLite)

**For Android:**
- Use Retrofit/OkHttp for API calls
- Store JWT token in SharedPreferences
- Parse JSON responses
- Handle authentication headers

**Base URL:** `http://YOUR_SERVER_IP:5000`
