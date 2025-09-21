"""
Main API Router
Combines all API endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, sites, predictions, sensors, alerts, upload, dashboard

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(sites.router, prefix="/sites", tags=["Site Management"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["AI Predictions"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensor Data"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts & Notifications"])
api_router.include_router(upload.router, prefix="/upload", tags=["File Upload"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard & Analytics"])