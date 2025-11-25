# 🔍 Account Creation Troubleshooting Guide

## 🚀 Quick Fix Steps

### Step 1: Run Diagnostic
1. Double-click: **`run_diagnostic.bat`**
2. Wait for it to complete
3. Note any ❌ failures

### Step 2: Check Browser Console
1. Open your app at: `http://127.0.0.1:8000/accounts/register/`
2. Press: `F12` (Open Developer Tools)
3. Click: **"Console"** tab
4. Try registering
5. Look for error messages

### Step 3: Identify the Problem
Follow the console logs:

```
🔍 Form submitted with: {...}
🔐 CSRF Token: [token]
📤 Sending payload: {...}
📥 Response status: 200
📥 Response data: {...}
✅ Registration successful!
```

---

## Common Issues & Fixes

### ❌ Issue 1: "Missing required fields"
**What it means**: Email or password fields are empty

**Fix**:
- Make sure you're entering a valid email
- Make sure passwords are long enough
- Check that passwords match

---

### ❌ Issue 2: "Email already registered"
**What it means**: This email account already exists

**Fix**:
- Use a different email address
- Or login if you already have an account

---

### ❌ Issue 3: "Password does not meet requirements"
**What it means**: Password is too simple

**Fix**: Password must have:
- ✅ At least 8 characters
- ✅ One uppercase letter (A-Z)
- ✅ One lowercase letter (a-z)
- ✅ One number (0-9)
- ✅ One special character (!@#$%^&*)

**Example good password**: `SecurePass123!`

---

### ❌ Issue 4: "Connection error"
**What it means**: Can't reach the server

**Fix**:
1. Make sure server is running
2. Visit: `http://127.0.0.1:8000` first (check if it loads)
3. Check browser console for network errors
4. Restart the server

---

### ❌ Issue 5: No response or loading forever
**What it means**: Server stopped or is hanging

**Fix**:
1. Press `Ctrl + C` in the Command Prompt (stop server)
2. Wait 5 seconds
3. Run: **`run_server_debug.bat`** again
4. Wait for: "Starting development server"
5. Try registration again

---

## 🔧 Advanced Troubleshooting

### Check Database
```bash
"C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" manage.py shell
>>> from accounts.models import PendingRegistration
>>> PendingRegistration.objects.all().count()
```

If this fails, migrations aren't applied.

### Reapply Migrations
```bash
"C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" manage.py migrate
```

### Reset Everything
```bash
del db.sqlite3
"C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" manage.py migrate
```

---

## 📊 Step-by-Step Debug Session

### 1. Start Server
- Double-click: `run_server_debug.bat`
- Wait for: "Starting development server at http://0.0.0.0:8000/"

### 2. Open Browser Console
- Navigate to: `http://127.0.0.1:8000/accounts/register/`
- Press: `F12`
- Click: **"Console"** tab

### 3. Try Registration
- Email: `test@example.com`
- Password: `TestPass123!@#`
- Confirm Password: `TestPass123!@#`
- Click: **"Create Account"**

### 4. Watch Console Output
Look for:
```
🔍 Form submitted with: {...}  ← Form validation
🔐 CSRF Token: abc123...        ← Security token
📤 Sending payload: {...}       ← API request
📥 Response status: 200          ← Server response
📥 Response data: {...}          ← Response body
✅ Registration successful!      ← Success!
```

### 5. If Error Occurs
Find the red error:
```
❌ Server error: [error message]
```

Copy this message and Google it or check troubleshooting above.

---

## 🆘 If Still Not Working

### Option A: Use Production
Your app is fully working at:
```
https://futureme-uwf5.onrender.com
```

No local setup needed!

### Option B: Full Reset
1. Stop server (press `Ctrl + C`)
2. Run: 
   ```bash
   del b:\DJANGO\futureme\db.sqlite3
   "C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" manage.py migrate
   "C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" manage.py runserver
   ```
3. Try registration again

### Option C: Check .env
Make sure `b:\DJANGO\futureme\.env` has:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 📋 Checklist

Before troubleshooting, verify:

- ✅ Server running? (`http://127.0.0.1:8000` loads)
- ✅ Email format valid? (has `@` and domain)
- ✅ Password strong enough? (8 chars, upper, lower, number, special)
- ✅ Passwords match? (same in both fields)
- ✅ Browser console checked? (`F12` → Console tab)
- ✅ .env file has `DEBUG=True`?

---

## 🎯 Expected Flow

```
User fills form
         ↓
Click "Create Account"
         ↓
Form validates locally
         ↓
CSRF token sent
         ↓
API request sent to server
         ↓
Server creates OTP
         ↓
OTP shown (development) OR emailed (production)
         ↓
Redirect to verify OTP page
         ↓
User enters OTP
         ↓
Account created ✅
```

---

## 💡 Pro Tips

1. **Check console first** - Most errors are shown there
2. **Password requirements** - Follow the checklist on the form
3. **Different email each time** - Can't register same email twice
4. **Server must be running** - Page loads but no registration = server down
5. **Use production if frustrated** - https://futureme-uwf5.onrender.com works 100%

---

## Questions?

Create a GitHub issue with:
1. Browser console errors (screenshot or copy/paste)
2. Server console errors (from Command Prompt)
3. .env file contents (hide sensitive keys)
4. Steps to reproduce

Good luck! 🚀
