"""
Authentication router
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import jwt
import hashlib
import secrets

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock user database
USERS_DB = {
    "admin@rockfall.com": {
        "id": "admin-001",
        "email": "admin@rockfall.com",
        "username": "admin",
        "full_name": "System Administrator",
        "hashed_password": "fcf730b6d95236ecd3c9fc2d92d7b6b2bb061514961aec041d6c7a7192f592e4",  # secret123
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow()
    },
    "operator@rockfall.com": {
        "id": "op-001", 
        "email": "operator@rockfall.com",
        "username": "operator",
        "full_name": "Mine Operator",
        "hashed_password": "fcf730b6d95236ecd3c9fc2d92d7b6b2bb061514961aec041d6c7a7192f592e4",  # secret123
        "role": "operator",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
}

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = USERS_DB.get(email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """User login endpoint"""
    user = USERS_DB.get(login_data.email)
    
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user)
    )

@router.post("/register", response_model=UserResponse)
async def register(register_data: RegisterRequest):
    """User registration endpoint"""
    if register_data.email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = f"user-{secrets.token_hex(8)}"
    hashed_password = hash_password(register_data.password)
    
    new_user = {
        "id": user_id,
        "email": register_data.email,
        "username": register_data.username,
        "full_name": register_data.full_name,
        "hashed_password": hashed_password,
        "role": "operator",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    USERS_DB[register_data.email] = new_user
    
    return UserResponse(**new_user)

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(**current_user)

@router.post("/logout")
async def logout():
    """User logout endpoint"""
    return {"message": "Successfully logged out"}

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    full_name: Optional[str] = None,
    username: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    user_email = current_user["email"]
    user = USERS_DB.get(user_email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if full_name:
        user["full_name"] = full_name
    if username:
        user["username"] = username
    
    user["updated_at"] = datetime.utcnow()
    USERS_DB[user_email] = user
    
    return UserResponse(**user)

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    user_email = current_user["email"]
    user = USERS_DB.get(user_email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    user["hashed_password"] = hash_password(new_password)
    user["updated_at"] = datetime.utcnow()
    USERS_DB[user_email] = user
    
    return {"message": "Password changed successfully"}

@router.get("/notifications")
async def get_user_notifications(
    unread_only: bool = False,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    # Mock notifications for demonstration
    notifications = [
        {
            "id": "notif-001",
            "type": "alert",
            "title": "High Risk Detected",
            "message": "Critical risk level detected at North Mine Site",
            "timestamp": datetime.utcnow() - timedelta(minutes=15),
            "read": False,
            "severity": "high"
        },
        {
            "id": "notif-002",
            "type": "system",
            "title": "Device Offline",
            "message": "Sensor SM-001 has gone offline",
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "read": False,
            "severity": "medium"
        },
        {
            "id": "notif-003",
            "type": "maintenance",
            "title": "Scheduled Maintenance",
            "message": "Weekly sensor calibration completed",
            "timestamp": datetime.utcnow() - timedelta(hours=3),
            "read": True,
            "severity": "low"
        },
        {
            "id": "notif-004",
            "type": "prediction",
            "title": "New Prediction Available",
            "message": "Updated risk assessment for South Mine Site",
            "timestamp": datetime.utcnow() - timedelta(hours=6),
            "read": True,
            "severity": "low"
        }
    ]
    
    if unread_only:
        notifications = [n for n in notifications if not n["read"]]
    
    return {
        "notifications": notifications[:limit],
        "total_count": len(notifications),
        "unread_count": len([n for n in notifications if not n["read"]])
    }

@router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    # In a real implementation, this would update the database
    return {"message": f"Notification {notification_id} marked as read"}

@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user)
):
    """Mark all notifications as read"""
    return {"message": "All notifications marked as read"}

@router.get("/preferences")
async def get_user_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get user preferences and settings"""
    # Mock preferences
    preferences = {
        "notifications": {
            "email_alerts": True,
            "sms_alerts": False,
            "push_notifications": True,
            "alert_threshold": "medium"
        },
        "dashboard": {
            "theme": "light",
            "refresh_interval": 30,
            "default_time_range": "24h",
            "show_advanced_metrics": True
        },
        "reports": {
            "auto_generate": True,
            "frequency": "weekly",
            "include_predictions": True,
            "include_device_status": True
        }
    }
    
    return preferences

@router.put("/preferences")
async def update_user_preferences(
    preferences: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences and settings"""
    # In a real implementation, this would save to database
    return {
        "message": "Preferences updated successfully",
        "preferences": preferences
    }

@router.get("/activity")
async def get_user_activity(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user activity log"""
    # Mock activity data
    activities = [
        {
            "id": "act-001",
            "action": "login",
            "description": "User logged in",
            "timestamp": datetime.utcnow() - timedelta(minutes=5),
            "ip_address": "192.168.1.100"
        },
        {
            "id": "act-002",
            "action": "view_dashboard",
            "description": "Viewed main dashboard",
            "timestamp": datetime.utcnow() - timedelta(minutes=10),
            "ip_address": "192.168.1.100"
        },
        {
            "id": "act-003",
            "action": "export_report",
            "description": "Exported site analytics report",
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "ip_address": "192.168.1.100"
        }
    ]
    
    return {
        "activities": activities[:limit],
        "total_count": len(activities)
    }