"""
User Model
Pydantic models for user authentication and management
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class User(BaseModel):
    """User model for authentication and authorization"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password_hash: str
    role: str = Field(..., pattern=r'^(safety_officer|engineer|manager|researcher|admin)$')
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern=r'^(safety_officer|engineer|manager|researcher|admin)$')
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None

class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """User response model (without sensitive data)"""
    id: str
    username: str
    email: str
    role: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    """Password change request model"""
    current_password: str
    new_password: str = Field(..., min_length=8)