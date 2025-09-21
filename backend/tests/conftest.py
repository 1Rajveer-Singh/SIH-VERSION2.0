"""
Test configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add the backend and app directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from app.main import app
from app.database.connection import get_database
from app.core.auth import get_current_user
from app.models.user import User

# Test database configuration
TEST_MONGODB_URL = "mongodb://localhost:27017/rockfall_prediction_test"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create a test database connection."""
    client = AsyncIOMotorClient(TEST_MONGODB_URL)
    db = client.get_default_database()
    
    # Clean up any existing test data
    collections = await db.list_collection_names()
    for collection_name in collections:
        await db[collection_name].delete_many({})
    
    yield db
    
    # Cleanup after tests
    for collection_name in collections:
        await db[collection_name].delete_many({})
    client.close()

@pytest.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    # Override the database dependency
    app.dependency_overrides[get_database] = lambda: test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture
async def admin_user(test_db) -> dict:
    """Create an admin user for testing."""
    from auth import get_password_hash
    
    user_data = {
        "_id": "test_admin",
        "username": "testadmin",
        "email": "admin@test.com",
        "full_name": "Test Admin",
        "role": "admin",
        "is_active": True,
        "hashed_password": get_password_hash("testpassword"),
        "permissions": ["read", "write", "admin"]
    }
    
    await test_db.users.insert_one(user_data)
    return user_data

@pytest.fixture
async def operator_user(test_db) -> dict:
    """Create an operator user for testing."""
    from auth import get_password_hash
    
    user_data = {
        "_id": "test_operator",
        "username": "testoperator", 
        "email": "operator@test.com",
        "full_name": "Test Operator",
        "role": "operator",
        "is_active": True,
        "hashed_password": get_password_hash("testpassword"),
        "permissions": ["read", "write"]
    }
    
    await test_db.users.insert_one(user_data)
    return user_data

@pytest.fixture
async def viewer_user(test_db) -> dict:
    """Create a viewer user for testing."""
    from auth import get_password_hash
    
    user_data = {
        "_id": "test_viewer",
        "username": "testviewer",
        "email": "viewer@test.com", 
        "full_name": "Test Viewer",
        "role": "viewer",
        "is_active": True,
        "hashed_password": get_password_hash("testpassword"),
        "permissions": ["read"]
    }
    
    await test_db.users.insert_one(user_data)
    return user_data

@pytest.fixture
async def admin_token(client: AsyncClient, admin_user) -> str:
    """Get an admin authentication token."""
    response = await client.post(
        "/auth/login",
        data={
            "username": admin_user["username"],
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def operator_token(client: AsyncClient, operator_user) -> str:
    """Get an operator authentication token."""
    response = await client.post(
        "/auth/login",
        data={
            "username": operator_user["username"],
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def viewer_token(client: AsyncClient, viewer_user) -> str:
    """Get a viewer authentication token."""
    response = await client.post(
        "/auth/login", 
        data={
            "username": viewer_user["username"],
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_headers_admin(admin_token) -> dict:
    """Get authentication headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def auth_headers_operator(operator_token) -> dict:
    """Get authentication headers for operator user.""" 
    return {"Authorization": f"Bearer {operator_token}"}

@pytest.fixture
def auth_headers_viewer(viewer_token) -> dict:
    """Get authentication headers for viewer user."""
    return {"Authorization": f"Bearer {viewer_token}"}

@pytest.fixture
async def test_site(test_db) -> dict:
    """Create a test site."""
    site_data = {
        "_id": "test_site_001",
        "name": "Test Mining Site",
        "location": {
            "lat": 39.7392,
            "lng": -104.9903,
            "elevation": 1620
        },
        "area_hectares": 45.2,
        "description": "Test site for automated testing",
        "status": "active",
        "safety_protocols": ["Test protocol 1", "Test protocol 2"],
        "emergency_contacts": [
            {
                "name": "Test Contact",
                "role": "Test Manager",
                "phone": "+1234567890",
                "email": "test@example.com"
            }
        ]
    }
    
    await test_db.sites.insert_one(site_data)
    return site_data

@pytest.fixture
async def test_sensor(test_db, test_site) -> dict:
    """Create a test sensor."""
    sensor_data = {
        "_id": "test_sensor_001",
        "site_id": test_site["_id"],
        "name": "Test Accelerometer",
        "location": {
            "lat": 39.7393,
            "lng": -104.9904,
            "elevation": 1625
        },
        "sensor_types": ["accelerometer", "temperature"],
        "status": "active",
        "installation_date": "2024-01-01T00:00:00Z",
        "last_reading": "2024-01-15T12:00:00Z"
    }
    
    await test_db.sensors.insert_one(sensor_data)
    return sensor_data

# Test utility functions
class TestUtils:
    """Utility functions for tests."""
    
    @staticmethod
    def assert_valid_response(response, expected_status: int = 200):
        """Assert that a response has the expected status and valid JSON."""
        assert response.status_code == expected_status
        assert response.headers["content-type"] == "application/json"
        return response.json()
    
    @staticmethod
    def assert_error_response(response, expected_status: int, expected_detail: str = None):
        """Assert that a response is an error with expected status and detail."""
        assert response.status_code == expected_status
        data = response.json()
        assert "detail" in data
        if expected_detail:
            assert expected_detail in data["detail"]
        return data
    
    @staticmethod
    def assert_pagination_response(data: dict):
        """Assert that a response has proper pagination structure."""
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["size"], int)
        assert isinstance(data["pages"], int)

# Test data generators
class TestDataGenerator:
    """Generate test data."""
    
    @staticmethod
    def generate_sensor_reading(sensor_id: str, site_id: str) -> dict:
        """Generate a test sensor reading."""
        from datetime import datetime
        return {
            "sensor_id": sensor_id,
            "site_id": site_id,
            "timestamp": datetime.utcnow().isoformat(),
            "readings": {
                "vibration_x": 0.015,
                "vibration_y": 0.012,
                "vibration_z": 0.018,
                "temperature": 22.5
            }
        }
    
    @staticmethod
    def generate_prediction(site_id: str) -> dict:
        """Generate a test prediction."""
        from datetime import datetime
        return {
            "site_id": site_id,
            "timestamp": datetime.utcnow().isoformat(),
            "model_version": "v2.1.0",
            "risk_score": 0.75,
            "risk_level": "medium",
            "confidence": 0.85,
            "contributing_factors": ["seismic_activity", "weather_conditions"],
            "recommended_actions": ["Increase monitoring", "Review protocols"]
        }
    
    @staticmethod
    def generate_alert(site_id: str) -> dict:
        """Generate a test alert."""
        from datetime import datetime
        return {
            "site_id": site_id,
            "type": "rockfall_risk",
            "severity": "medium",
            "title": "Test Alert",
            "description": "This is a test alert for automated testing",
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "metadata": {
                "risk_score": 0.75,
                "affected_area": "Zone A"
            }
        }