"""
Tests for authentication system
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException

from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from conftest import TestUtils

class TestPasswordHashing:
    """Test password hashing functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) > 0
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
        
        # Should fail with wrong password
        assert verify_password("wrong_password", hashed) is False
    
    def test_same_password_different_hashes(self):
        """Test that same password generates different hashes."""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # Both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

class TestTokenGeneration:
    """Test JWT token generation and verification."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should be a valid JWT
        from main import SECRET_KEY, ALGORITHM
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "admin"
        assert "exp" in decoded
    
    def test_create_token_with_expiry(self):
        """Test token creation with custom expiry."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        from main import SECRET_KEY, ALGORITHM
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check expiry is roughly 15 minutes from now
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        time_diff = exp_time - now
        
        # Should be close to 15 minutes (within 1 minute tolerance)
        assert 14 * 60 < time_diff.total_seconds() < 16 * 60
    
    def test_verify_valid_token(self):
        """Test verification of valid token."""
        data = {"sub": "testuser", "role": "operator"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "operator"
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_verify_expired_token(self):
        """Test verification of expired token."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401

@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication endpoints."""
    
    async def test_login_success(self, client, admin_user):
        """Test successful login."""
        response = await client.post(
            "/auth/login",
            data={
                "username": admin_user["username"],
                "password": "testpassword"
            }
        )
        
        data = TestUtils.assert_valid_response(response)
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    async def test_login_wrong_username(self, client):
        """Test login with wrong username."""
        response = await client.post(
            "/auth/login",
            data={
                "username": "nonexistent",
                "password": "testpassword"
            }
        )
        
        TestUtils.assert_error_response(response, 401, "Incorrect username or password")
    
    async def test_login_wrong_password(self, client, admin_user):
        """Test login with wrong password."""
        response = await client.post(
            "/auth/login",
            data={
                "username": admin_user["username"],
                "password": "wrongpassword"
            }
        )
        
        TestUtils.assert_error_response(response, 401, "Incorrect username or password")
    
    async def test_login_inactive_user(self, client, test_db):
        """Test login with inactive user."""
        from auth import get_password_hash
        
        inactive_user = {
            "_id": "inactive_user",
            "username": "inactive",
            "email": "inactive@test.com",
            "full_name": "Inactive User",
            "role": "viewer",
            "is_active": False,  # Inactive user
            "hashed_password": get_password_hash("testpassword"),
            "permissions": ["read"]
        }
        
        await test_db.users.insert_one(inactive_user)
        
        response = await client.post(
            "/auth/login",
            data={
                "username": "inactive",
                "password": "testpassword"
            }
        )
        
        TestUtils.assert_error_response(response, 401, "Inactive user")
    
    async def test_get_current_user_profile(self, client, auth_headers_admin):
        """Test getting current user profile."""
        response = await client.get(
            "/auth/me",
            headers=auth_headers_admin
        )
        
        data = TestUtils.assert_valid_response(response)
        
        assert "username" in data
        assert "email" in data
        assert "full_name" in data
        assert "role" in data
        assert "is_active" in data
        assert "permissions" in data
        assert data["username"] == "testadmin"
        assert data["role"] == "admin"
    
    async def test_get_current_user_without_token(self, client):
        """Test getting current user without authentication."""
        response = await client.get("/auth/me")
        TestUtils.assert_error_response(response, 401, "Not authenticated")
    
    async def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        TestUtils.assert_error_response(response, 401, "Could not validate credentials")

@pytest.mark.asyncio 
class TestAuthorization:
    """Test authorization and permissions."""
    
    async def test_admin_access_admin_endpoint(self, client, auth_headers_admin):
        """Test admin user can access admin endpoints."""
        response = await client.get(
            "/users/",
            headers=auth_headers_admin
        )
        
        # Should succeed for admin
        assert response.status_code in [200, 404]  # 404 if no users yet
    
    async def test_operator_cannot_access_admin_endpoint(self, client, auth_headers_operator):
        """Test operator user cannot access admin endpoints."""
        response = await client.get(
            "/users/",
            headers=auth_headers_operator
        )
        
        # Should be forbidden for operator
        TestUtils.assert_error_response(response, 403, "Not enough permissions")
    
    async def test_viewer_cannot_access_admin_endpoint(self, client, auth_headers_viewer):
        """Test viewer user cannot access admin endpoints."""
        response = await client.get(
            "/users/",
            headers=auth_headers_viewer
        )
        
        # Should be forbidden for viewer
        TestUtils.assert_error_response(response, 403, "Not enough permissions")
    
    async def test_viewer_can_read_sites(self, client, auth_headers_viewer, test_site):
        """Test viewer can read sites."""
        response = await client.get(
            "/sites/",
            headers=auth_headers_viewer
        )
        
        # Should succeed for viewer (read permission)
        data = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(data)
    
    async def test_viewer_cannot_create_sites(self, client, auth_headers_viewer):
        """Test viewer cannot create sites."""
        site_data = {
            "name": "New Test Site",
            "location": {"lat": 40.0, "lng": -105.0, "elevation": 1500},
            "area_hectares": 25.0,
            "description": "Test site creation"
        }
        
        response = await client.post(
            "/sites/",
            headers=auth_headers_viewer,
            json=site_data
        )
        
        # Should be forbidden for viewer
        TestUtils.assert_error_response(response, 403, "Not enough permissions")

@pytest.mark.asyncio
class TestUserManagement:
    """Test user management functionality."""
    
    async def test_create_user(self, client, auth_headers_admin):
        """Test creating a new user."""
        user_data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "full_name": "New Test User",
            "password": "newpassword123",
            "role": "operator"
        }
        
        response = await client.post(
            "/users/",
            headers=auth_headers_admin,
            json=user_data
        )
        
        data = TestUtils.assert_valid_response(response, 201)
        
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "operator"
        assert data["is_active"] is True
        assert "hashed_password" not in data  # Should not return password
    
    async def test_create_duplicate_username(self, client, auth_headers_admin, admin_user):
        """Test creating user with duplicate username."""
        user_data = {
            "username": admin_user["username"],  # Duplicate username
            "email": "different@test.com",
            "full_name": "Different User",
            "password": "password123",
            "role": "viewer"
        }
        
        response = await client.post(
            "/users/",
            headers=auth_headers_admin,
            json=user_data
        )
        
        TestUtils.assert_error_response(response, 400, "already exists")
    
    async def test_update_user(self, client, auth_headers_admin, operator_user):
        """Test updating user information."""
        update_data = {
            "full_name": "Updated Full Name",
            "email": "updated@test.com"
        }
        
        response = await client.put(
            f"/users/{operator_user['_id']}",
            headers=auth_headers_admin,
            json=update_data
        )
        
        data = TestUtils.assert_valid_response(response)
        
        assert data["full_name"] == "Updated Full Name"
        assert data["email"] == "updated@test.com"
        assert data["username"] == operator_user["username"]  # Should remain unchanged
    
    async def test_delete_user(self, client, auth_headers_admin, viewer_user):
        """Test deleting a user."""
        response = await client.delete(
            f"/users/{viewer_user['_id']}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 204
        
        # Verify user is deleted
        response = await client.get(
            f"/users/{viewer_user['_id']}",
            headers=auth_headers_admin
        )
        
        TestUtils.assert_error_response(response, 404, "User not found")