"""
Authentication Endpoints
JWT-based authentication with role-based access control
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import timedelta, datetime
import logging

from app.models.user import LoginRequest, TokenResponse, RefreshTokenRequest, UserResponse, PasswordChangeRequest
from app.core.auth import authenticate_user, create_access_token, create_refresh_token, refresh_access_token, get_current_active_user, get_password_hash, verify_password
from app.core.config import settings
from app.core.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return JWT tokens
    
    - **username**: User's username
    - **password**: User's password
    
    Returns access token, refresh token, and user information
    """
    user = await authenticate_user(login_data.username, login_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Convert user to response model
    user_response = UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role,
        full_name=user.full_name,
        phone=user.phone,
        department=user.department,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at
    )
    
    logger.info(f"Successful login for user: {user.username}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token
    """
    try:
        new_access_token = await refresh_access_token(refresh_data.refresh_token)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.post("/logout")
async def logout(current_user = Depends(get_current_active_user)):
    """
    Logout user (client should discard tokens)
    
    Note: In a production system, you might want to implement token blacklisting
    """
    logger.info(f"User logged out: {current_user.username}")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """
    Get current user information
    
    Returns the current authenticated user's profile
    """
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        full_name=current_user.full_name,
        phone=current_user.phone,
        department=current_user.department,
        is_active=current_user.is_active,
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Change user password
    
    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password in database
    db = get_database()
    users_collection = db["users"]
    
    new_password_hash = get_password_hash(password_data.new_password)
    
    await users_collection.update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "password_hash": new_password_hash,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"Password changed for user: {current_user.username}")
    
    return {"message": "Password changed successfully"}

@router.post("/validate-token")
async def validate_token(current_user = Depends(get_current_active_user)):
    """
    Validate if the current token is valid
    
    Returns user information if token is valid
    """
    return {
        "valid": True,
        "user": UserResponse(
            id=str(current_user.id),
            username=current_user.username,
            email=current_user.email,
            role=current_user.role,
            full_name=current_user.full_name,
            phone=current_user.phone,
            department=current_user.department,
            is_active=current_user.is_active,
            last_login=current_user.last_login,
            created_at=current_user.created_at
        )
    }