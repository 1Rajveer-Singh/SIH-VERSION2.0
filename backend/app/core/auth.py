"""
Authentication and Authorization
JWT token handling and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging

from app.core.config import settings
from app.core.database import get_database
from app.models.user import User

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise AuthenticationError()
            
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise AuthenticationError()
    
    # Get user from database
    db = get_database()
    users_collection = db["users"]
    
    user_data = await users_collection.find_one({"username": username})
    if user_data is None:
        raise AuthenticationError("User not found")
    
    if not user_data.get("is_active", True):
        raise AuthenticationError("User account is disabled")
    
    # Update last login
    await users_collection.update_one(
        {"_id": user_data["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    return User(**user_data)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user

def require_roles(*allowed_roles: str):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationError(
                f"Operation requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

# Convenience functions for common role requirements
require_admin = require_roles("admin")
require_safety_officer = require_roles("admin", "safety_officer")
require_engineer = require_roles("admin", "safety_officer", "engineer")
require_manager = require_roles("admin", "safety_officer", "engineer", "manager")

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    db = get_database()
    users_collection = db["users"]
    
    user_data = await users_collection.find_one({"username": username})
    if not user_data:
        return None
    
    if not verify_password(password, user_data["password_hash"]):
        return None
    
    if not user_data.get("is_active", True):
        return None
    
    return User(**user_data)

async def refresh_access_token(refresh_token: str) -> str:
    """Refresh access token using refresh token"""
    try:
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise AuthenticationError("Invalid refresh token")
            
    except JWTError:
        raise AuthenticationError("Invalid refresh token")
    
    # Verify user still exists and is active
    db = get_database()
    users_collection = db["users"]
    
    user_data = await users_collection.find_one({"username": username})
    if not user_data or not user_data.get("is_active", True):
        raise AuthenticationError("User not found or inactive")
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, 
        expires_delta=access_token_expires
    )
    
    return access_token