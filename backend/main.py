"""
FastAPI Main Application
Comprehensive Rockfall Prediction System API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.routers import auth, sites, devices, predictions, predictions_enhanced, dashboard, training

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    try:
        # Initialize database connection
        logger.info("Starting Rockfall Prediction System...")
        await connect_to_mongo()
        logger.info("Database connection initialized")
        yield
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down...")
        await close_mongo_connection()

# Create FastAPI application
app = FastAPI(
    title="Rockfall Prediction System API",
    description="Advanced Mining Safety and Rockfall Prediction System with Real-time Monitoring",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Rockfall Prediction System API",
        "version": "2.0.0"
    }

# Simple test endpoint for frontend connection
@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Backend is working!", "timestamp": "2025-09-21"}

# Test endpoints for debugging dashboard (no auth required)
@app.get("/test/dashboard/stats")
async def test_dashboard_stats():
    """Test dashboard stats endpoint without auth"""
    return {
        "total_sites": 12,
        "active_alerts": 3,
        "devices_online": 45,
        "total_devices": 48,
        "high_risk_sites": 2,
        "predictions_today": 156,
        "system_uptime": "99.8%"
    }

@app.get("/test/dashboard/predictions")
async def test_dashboard_predictions():
    """Test dashboard predictions endpoint without auth"""
    return [
        {
            "id": "pred_001",
            "site_id": "site_001",
            "site_name": "Alpha Mining Site",
            "risk_level": "medium",
            "probability": 0.65,
            "confidence": 0.82,
            "timestamp": "2025-09-21T10:30:00Z",
            "recommendations": ["Increase monitoring frequency", "Review sensor calibration"]
        },
        {
            "id": "pred_002", 
            "site_id": "site_002",
            "site_name": "Beta Quarry",
            "risk_level": "low",
            "probability": 0.25,
            "confidence": 0.91,
            "timestamp": "2025-09-21T10:25:00Z",
            "recommendations": ["Continue normal operations"]
        }
    ]

@app.get("/test/dashboard/alerts")
async def test_dashboard_alerts():
    """Test dashboard alerts endpoint without auth"""
    return [
        {
            "id": "alert_001",
            "type": "geological_instability",
            "severity": "high",
            "message": "Unusual seismic activity detected at Site Alpha-7",
            "site_id": "site_001",
            "site_name": "Alpha Mining Site",
            "timestamp": "2025-09-21T09:45:00Z",
            "status": "active"
        },
        {
            "id": "alert_002",
            "type": "device_offline",
            "severity": "medium", 
            "message": "Sensor array offline for maintenance",
            "site_id": "site_002",
            "site_name": "Beta Quarry",
            "timestamp": "2025-09-21T08:30:00Z",
            "status": "acknowledged"
        }
    ]

# API Router includes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(sites.router, prefix="/api/sites", tags=["Mining Sites"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(predictions_enhanced.router, prefix="/api/predictions/enhanced", tags=["Enhanced Predictions"])
app.include_router(training.router, prefix="/api/training", tags=["Model Training"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Rockfall Prediction System API",
        "version": "2.0.0",
        "documentation": "/api/docs",
        "health": "/health",
        "endpoints": {
            "authentication": "/api/auth",
            "dashboard": "/api/dashboard", 
            "sites": "/api/sites",
            "devices": "/api/devices",
            "predictions": "/api/predictions",
            "enhanced_predictions": "/api/predictions/enhanced"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )