# Login Credentials & Authentication Guide

## 🔐 **FIXED! Login Issue Resolved**

The white screen issue after login has been resolved. The problem was:
1. **Frontend was sending `username` but backend expected `email`**
2. **Password hash in backend was incorrect**

Both issues have been fixed!

---

## 👤 **Demo User Accounts**

### **Administrator Account**
- **Email:** `admin@rockfall.com`
- **Password:** `secret123`
- **Role:** `admin`
- **Permissions:** Full system access

### **Operator Account**  
- **Email:** `operator@rockfall.com`
- **Password:** `secret123`
- **Role:** `operator`
- **Permissions:** Standard mining operations

---

## 🚀 **How to Login**

1. **Open the frontend application**: http://localhost:3000
2. **Enter credentials:**
   - Email: `admin@rockfall.com`
   - Password: `secret123`
3. **Click "Sign in"**
4. **You should be redirected to the Dashboard automatically**

---

## 🔄 **Authentication Flow**

1. **Login Request:** Frontend sends email/password to `/api/v1/auth/login`
2. **Token Generation:** Backend validates credentials and returns JWT token
3. **Token Storage:** Frontend stores token in localStorage  
4. **Automatic Redirect:** User is redirected to dashboard
5. **Protected Routes:** All subsequent API calls include the JWT token

---

## 🛠️ **Authentication API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| GET | `/api/v1/auth/me` | Get current user profile |
| POST | `/api/v1/auth/logout` | User logout |
| POST | `/api/v1/auth/register` | User registration |

---

## 🔧 **API Response Format**

### Login Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "admin-001",
    "email": "admin@rockfall.com", 
    "username": "admin",
    "full_name": "System Administrator",
    "role": "admin",
    "is_active": true
  }
}
```

---

## 🎯 **Routing Configuration**

- **`/`** → Redirects to `/dashboard` if authenticated, `/login` if not
- **`/login`** → Login page (redirects to dashboard if already authenticated)  
- **`/dashboard`** → Main dashboard (requires authentication)

---

## 🔍 **Troubleshooting**

### **Still seeing white screen?**
1. **Check browser console** for JavaScript errors
2. **Verify both servers are running:**
   - Backend: http://localhost:8000/health
   - Frontend: http://localhost:3000
3. **Clear browser cache** and localStorage
4. **Use correct credentials** (email, not username)

### **Login API Test:**
```powershell
$body = @{email="admin@rockfall.com"; password="secret123"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
```

---

## ✅ **Verification Checklist**

- [x] Backend API responds correctly
- [x] Frontend connects to backend
- [x] Password hashes are correct
- [x] JWT tokens are generated properly
- [x] Frontend routing works correctly
- [x] Dashboard loads after successful login
- [x] Logout functionality works
- [x] Protected routes require authentication

---

## 🎊 **Success!**

Your login system is now fully functional! You should be able to:
1. **Login with the provided credentials**
2. **See the dashboard after successful authentication**
3. **Navigate between protected routes**
4. **Logout and return to login page**

**Enjoy your AI-Based Rockfall Prediction & Alert System!** 🚀