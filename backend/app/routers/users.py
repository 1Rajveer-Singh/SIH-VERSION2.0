"""
Users management router
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .auth import get_current_user

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: str = "operator"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

# Mock users database (imported from auth)
from .auth import USERS_DB

@router.get("/", response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return [UserResponse(**user) for user in USERS_DB.values()]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user by ID"""
    user = next((u for u in USERS_DB.values() if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can view their own profile, admins can view any
    if current_user["id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return UserResponse(**user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update user"""
    user = next((u for u in USERS_DB.values() if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can update their own profile, admins can update any
    if current_user["id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update user data
    for field, value in user_update.dict(exclude_unset=True).items():
        user[field] = value
    
    return UserResponse(**user)

@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Delete user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user_email = next((email for email, user in USERS_DB.items() if user["id"] == user_id), None)
    if not user_email:
        raise HTTPException(status_code=404, detail="User not found")
    
    del USERS_DB[user_email]
    return {"message": "User deleted successfully"}