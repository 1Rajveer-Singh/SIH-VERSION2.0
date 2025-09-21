"""Dashboard and analytics endpoints"""
from fastapi import APIRouter, Depends
from app.core.auth import get_current_active_user
from app.core.database import get_database
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(
    site_id: str = None,
    current_user = Depends(get_current_active_user)
):
    """Get dashboard overview data"""
    db = get_database()
    
    # Mock dashboard data
    return {
        "site_id": site_id or "DEMO_SITE_001",
        "current_risk_level": "Medium",
        "active_alerts": 3,
        "sensor_status": {
            "online": 8,
            "offline": 0,
            "maintenance": 0
        },
        "recent_predictions": [
            {"timestamp": datetime.utcnow() - timedelta(hours=1), "risk_score": 0.45, "risk_class": "Medium"},
            {"timestamp": datetime.utcnow() - timedelta(hours=6), "risk_score": 0.38, "risk_class": "Medium"},
            {"timestamp": datetime.utcnow() - timedelta(hours=12), "risk_score": 0.32, "risk_class": "Low"}
        ]
    }

@router.get("/analytics")
async def get_analytics(
    site_id: str = None,
    period: str = "7d",
    current_user = Depends(get_current_active_user)
):
    """Get analytics data"""
    return {
        "site_id": site_id,
        "period": period,
        "risk_trend": "stable",
        "prediction_accuracy": 0.92,
        "alert_response_time_avg": 4.2,
        "sensor_uptime": 0.98
    }