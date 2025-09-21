"""User management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_active_user, require_admin
from app.core.database import get_database

router = APIRouter()

@router.get("/")
async def get_users(current_user = Depends(require_admin)):
    """Get all users (admin only)"""
    db = get_database()
    users = await db["users"].find({}, {"password_hash": 0}).to_list(length=None)
    return [{"id": str(u["_id"]), **{k: v for k, v in u.items() if k != "_id"}} for u in users]

@router.get("/profile")
async def get_profile(current_user = Depends(get_current_active_user)):
    """Get current user profile"""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "full_name": current_user.full_name
    }