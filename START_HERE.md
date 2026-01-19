# 🚀 START HERE - Quick Setup

## ⚠️ IMPORTANT: You Need TWO Terminals!

### Step 1: Start the Server (Terminal 1)

```bash
python app.py
```

**Wait for this message:**
```
 * Running on http://127.0.0.1:5000
```

**✅ Keep this terminal open!** The server must keep running.

---

### Step 2: Run the CLI (Terminal 2)

**Open a NEW terminal** (don't close Terminal 1!) and run:

```bash
python cli.py
```

The CLI will check if the server is running automatically.

---

## ❌ If You See This Error:

```
ConnectionRefusedError: No connection could be made
```

**Solution:** 
1. Make sure `python app.py` is running in another terminal
2. Check that you see "Running on http://127.0.0.1:5000"
3. Then try `python cli.py` again

---

## 📋 Complete Setup (First Time Only)

1. Install Python 3.7+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Follow Step 1 and Step 2 above

---

## ✅ Success Looks Like:

**Terminal 1:**
```
 * Running on http://127.0.0.1:5000
```

**Terminal 2:**
```
🔍 Checking server connection...
✅ Server connection successful!

=== ExpertEase ===
1. User
2. Worker
3. Admin
4. Exit
```

---

## 💡 Pro Tip

- **Terminal 1** = Backend Server (always running)
- **Terminal 2** = CLI Interface (for testing)

You can close Terminal 2 anytime, but **NEVER close Terminal 1** while using the app!
