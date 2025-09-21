#!/usr/bin/env python3
"""
Simple test server to verify backend connectivity
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create a simple FastAPI app for testing
app = FastAPI(title="Test Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Test server is running",
        "port": 8000
    }

# Handle the /api prefix that somehow gets added
@app.get("/api/health")
async def api_health_check():
    """API Health check endpoint with /api prefix"""
    return {
        "status": "healthy",
        "message": "API Test server is running",
        "port": 8000
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Backend connection test successful!", "timestamp": "2025-09-21"}

@app.post("/api/auth/login")
async def mock_login(body: dict):
    """Mock login endpoint with /api prefix"""
    email = body.get("email", "")
    password = body.get("password", "")
    
    if email == "admin@rockfall.com" and password == "secret123":
        return {
            "access_token": "mock-jwt-token-12345",
            "token_type": "bearer",
            "user": {
                "id": "admin-001",
                "email": email,
                "username": "admin",
                "full_name": "Admin User",
                "role": "admin"
            }
        }
    else:
        return {"detail": "Invalid credentials"}, 401

# Handle the double /api prefix issue
@app.post("/api/api/auth/login")
async def mock_login_double_api(body: dict):
    """Mock login endpoint with double /api prefix (fallback)"""
    return await mock_login(body)

if __name__ == "__main__":
    print("Starting test server on http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000, log_level="info")