"""
FastAPI Main Application
Comprehensive Rockfall Prediction System API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.routers import auth, sites, devices, predictions, dashboard
from app.routers import predictions_enhanced

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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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

# API Router includes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(sites.router, prefix="/api/sites", tags=["Mining Sites"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(predictions_enhanced.router, prefix="/api/predictions/enhanced", tags=["Enhanced Predictions"])

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