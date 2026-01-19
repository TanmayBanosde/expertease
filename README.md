# ExpertEase - Healthcare Appointment System

A Flask-based backend API for a multi-service healthcare application with user and doctor dashboards.

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation Steps

1. **Copy all files** to your friend's PC in a folder (e.g., `C:\Users\Friend\expertease`)

2. **Open Command Prompt or PowerShell** in that folder

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or manually:
   ```bash
   pip install Flask==3.0.0 bcrypt==4.1.2 PyJWT==2.8.0 Werkzeug==3.0.1
   ```

4. **IMPORTANT: Start the backend server FIRST:**
   
   Open **Terminal 1** and run:
   ```bash
   python app.py
   ```
   
   You should see:
   ```
   * Running on http://127.0.0.1:5000
   * Debug mode: on
   ```
   
   **⚠️ KEEP THIS TERMINAL OPEN!** The server must keep running.

5. **In a NEW terminal (Terminal 2), run the CLI:**
   ```bash
   python cli.py
   ```
   
   The CLI will automatically check if the server is running and show an error if it's not.

## 📁 Required Files

Make sure these files are present:
- ✅ `app.py` - Main Flask server
- ✅ `cli.py` - Command-line interface
- ✅ `config.py` - Configuration
- ✅ `requirements.txt` - Dependencies
- ✅ `user_db.py` - User database
- ✅ `worker_db.py` - Doctor database
- ✅ `appointment_db.py` - Appointments database
- ✅ `message_db.py` - Messages database
- ✅ `availability_db.py` - Availability database
- ✅ `auth_utils.py` - JWT authentication
- ✅ `otp_service.py` - OTP service
- ✅ `email_service.py` - Email service

## 🔧 Configuration

The `config.py` file contains:
- Database paths
- Email settings (for OTP)
- JWT secret key
- OTP expiry time

**Note:** Email credentials are in `config.py`. Make sure SMTP settings are correct for OTP to work.

## 📱 Android App Development

### ✅ Perfect for Android Development

This backend is **100% ready** for Android app development:

1. **RESTful API Design**
   - All endpoints return JSON
   - Standard HTTP methods (GET, POST, DELETE)
   - Clear request/response formats

2. **Complete API Coverage**
   - User authentication (signup, login, OTP)
   - Service selection
   - Healthcare navigation (5 tabs)
   - Doctor dashboard (5 tabs)
   - Appointment management
   - Chat/messaging
   - Availability management

3. **JWT Authentication**
   - Token-based auth for secure API calls
   - Works perfectly with Android HTTP clients

4. **Database Structure**
   - SQLite databases (portable, no server needed)
   - All data stored locally
   - Easy to backup/restore

### Android Integration Points

**Base URL:** `http://127.0.0.1:5000` (change to your server IP for production)

**Key Endpoints:**
- `POST /signup` - User registration
- `POST /login` - User login
- `GET /healthcare/specializations` - Get specializations
- `GET /healthcare/doctors/{specialization}` - Get doctors
- `POST /book-appointment` - Book appointment
- `GET /worker/{id}/dashboard/stats` - Doctor dashboard stats
- `POST /worker/{id}/availability` - Set availability

## 🐛 Troubleshooting

### Import Errors
- Make sure all `.py` files are in the same folder
- Check that `config.py` exists and has all required variables

### Port Already in Use
- Change port in `app.py` last line: `app.run(debug=True, port=5001)`

### Database Errors
- The `data/` folder will be created automatically
- Make sure Python has write permissions

### Email/OTP Not Working
- Check email credentials in `config.py`
- Verify SMTP settings are correct
- For testing, you can skip OTP verification temporarily

## 📝 Testing

Use `cli.py` to test all functionality:
1. User signup/login
2. Service selection
3. Healthcare navigation
4. Doctor dashboard
5. Appointment booking
6. Chat functionality

## 🔒 Security Notes

- Change `JWT_SECRET` in `config.py` for production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Add rate limiting for production

## 📞 Support

If something doesn't work:
1. Check Python version: `python --version` (should be 3.7+)
2. Verify all files are present
3. Check error messages in terminal
4. Ensure port 5000 is not blocked by firewall
