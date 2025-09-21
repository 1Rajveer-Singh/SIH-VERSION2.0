"""
Alerts and notifications management router
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import random
import sys
import os
from enum import Enum
from .auth import get_current_user

# Add path for notification system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from notification_system.notifications import send_alert_notification, test_notification_system
    from notification_system.escalation import initiate_alert_escalation, acknowledge_alert_escalation
    NOTIFICATION_SYSTEM_AVAILABLE = True
    print("Notification system imported successfully")
except ImportError as e:
    print(f"Notification system not available: {e}")
    NOTIFICATION_SYSTEM_AVAILABLE = False

router = APIRouter()

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class AlertType(str, Enum):
    PREDICTION = "prediction"
    SENSOR_MALFUNCTION = "sensor_malfunction"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    SYSTEM_ERROR = "system_error"
    MAINTENANCE_DUE = "maintenance_due"

class AlertCreate(BaseModel):
    site_id: str
    title: str
    message: str
    severity: AlertSeverity
    alert_type: AlertType
    sensor_ids: Optional[List[str]] = []
    prediction_id: Optional[str] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = None
    resolution_notes: Optional[str] = None

class AlertResponse(BaseModel):
    id: str
    site_id: str
    title: str
    message: str
    severity: AlertSeverity
    alert_type: AlertType
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    sensor_ids: List[str] = []
    prediction_id: Optional[str] = None

class NotificationChannel(BaseModel):
    type: str  # "email", "sms", "webhook", "push"
    enabled: bool
    config: Dict

class NotificationPreferences(BaseModel):
    user_id: str
    channels: List[NotificationChannel]
    severity_filter: List[AlertSeverity]
    site_filters: List[str] = []

# Mock alerts database
ALERTS_DB = {}

# Mock notification preferences
NOTIFICATION_PREFERENCES = {}

# Sample alerts for demo
SAMPLE_ALERTS = [
    {
        "id": "alert-001",
        "site_id": "site-001",
        "title": "High Rockfall Risk Detected",
        "message": "ML model predicts 85% probability of rockfall in Zone A within next 6 hours",
        "severity": "high",
        "alert_type": "prediction",
        "status": "active",
        "created_at": datetime.utcnow() - timedelta(minutes=30),
        "updated_at": datetime.utcnow() - timedelta(minutes=30),
        "sensor_ids": ["sensor-001", "sensor-002"],
        "prediction_id": "pred-000123"
    },
    {
        "id": "alert-002",
        "site_id": "site-001",
        "title": "Sensor Communication Lost",
        "message": "Accelerometer Station A1 has not reported data for 2 hours",
        "severity": "medium",
        "alert_type": "sensor_malfunction",
        "status": "acknowledged",
        "created_at": datetime.utcnow() - timedelta(hours=2),
        "updated_at": datetime.utcnow() - timedelta(minutes=45),
        "acknowledged_by": "john.doe@mining.com",
        "acknowledged_at": datetime.utcnow() - timedelta(minutes=45),
        "sensor_ids": ["sensor-001"]
    },
    {
        "id": "alert-003",
        "site_id": "site-002",
        "title": "Vibration Threshold Exceeded",
        "message": "Seismometer readings exceeded safe threshold (0.5g) at 14:30",
        "severity": "critical",
        "alert_type": "threshold_exceeded",
        "status": "resolved",
        "created_at": datetime.utcnow() - timedelta(hours=4),
        "updated_at": datetime.utcnow() - timedelta(hours=1),
        "acknowledged_by": "admin@mining.com",
        "acknowledged_at": datetime.utcnow() - timedelta(hours=3),
        "resolved_at": datetime.utcnow() - timedelta(hours=1),
        "resolution_notes": "False alarm - equipment calibration issue resolved",
        "sensor_ids": ["sensor-003"]
    }
]

# Initialize with sample data
for alert in SAMPLE_ALERTS:
    ALERTS_DB[alert["id"]] = alert

async def send_notification(alert: Dict, user_preferences: NotificationPreferences):
    """
    Send notification based on user preferences
    """
    if NOTIFICATION_SYSTEM_AVAILABLE:
        try:
            # Convert user preferences to notification system format
            user_prefs = [{
                'user_id': user_preferences.user_id,
                'channels': [
                    {
                        'type': channel.type,
                        'enabled': channel.enabled,
                        'config': channel.config
                    } for channel in user_preferences.channels
                ],
                'severity_filter': user_preferences.severity_filter
            }]
            
            # Send notification using the notification system
            result = send_alert_notification(alert, user_prefs)
            print(f"Notification sent for alert {alert['id']}: {result}")
            
        except Exception as e:
            print(f"Error sending notification: {e}")
    else:
        # Fallback simulation
        print(f"Sending notification for alert {alert['id']} to user {user_preferences.user_id}")
        
        for channel in user_preferences.channels:
            if channel.enabled and alert["severity"] in user_preferences.severity_filter:
                if channel.type == "email":
                    print(f"Email sent to {channel.config.get('address', 'unknown')}")
                elif channel.type == "sms":
                    print(f"SMS sent to {channel.config.get('phone', 'unknown')}")
                elif channel.type == "push":
                    print(f"Push notification sent")
                elif channel.type == "webhook":
                    print(f"Webhook triggered: {channel.config.get('url', 'unknown')}")

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    alert_type: Optional[AlertType] = Query(None, description="Filter by alert type"),
    hours: int = Query(24, description="Hours of alerts to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    """Get alerts with optional filtering"""
    
    # Filter by time
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    alerts = [
        alert for alert in ALERTS_DB.values()
        if alert["created_at"] >= cutoff_time
    ]
    
    # Apply filters
    if site_id:
        alerts = [a for a in alerts if a["site_id"] == site_id]
    
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    
    if alert_type:
        alerts = [a for a in alerts if a["alert_type"] == alert_type]
    
    # Sort by creation time (newest first)
    alerts.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [AlertResponse(**alert) for alert in alerts]

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific alert by ID"""
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse(**alert)

@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create new alert"""
    
    alert_id = f"alert-{len(ALERTS_DB) + 1:03d}"
    
    new_alert = {
        "id": alert_id,
        **alert_data.dict(),
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    ALERTS_DB[alert_id] = new_alert
    
    # Initiate escalation process for high severity alerts
    if NOTIFICATION_SYSTEM_AVAILABLE and alert_data.severity in ['high', 'critical']:
        try:
            escalation_result = initiate_alert_escalation(new_alert)
            print(f"Escalation initiated: {escalation_result}")
        except Exception as e:
            print(f"Error initiating escalation: {e}")
    
    # Send notifications in background
    for user_prefs in NOTIFICATION_PREFERENCES.values():
        if (not user_prefs.site_filters or alert_data.site_id in user_prefs.site_filters):
            background_tasks.add_task(send_notification, new_alert, user_prefs)
    
    return AlertResponse(**new_alert)

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update alert status"""
    
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Update alert data
    for field, value in alert_update.dict(exclude_unset=True).items():
        alert[field] = value
    
    alert["updated_at"] = datetime.utcnow()
    
    # Set timestamps based on status changes
    if alert_update.status == "acknowledged" and not alert.get("acknowledged_at"):
        alert["acknowledged_at"] = datetime.utcnow()
        alert["acknowledged_by"] = current_user["email"]
        
        # Record acknowledgment in escalation system
        if NOTIFICATION_SYSTEM_AVAILABLE:
            try:
                acknowledge_alert_escalation(alert_id, current_user["email"])
            except Exception as e:
                print(f"Error acknowledging escalation: {e}")
                
    elif alert_update.status == "resolved" and not alert.get("resolved_at"):
        alert["resolved_at"] = datetime.utcnow()
    
    return AlertResponse(**alert)

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, current_user: dict = Depends(get_current_user)):
    """Delete alert (admin only)"""
    
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if alert_id not in ALERTS_DB:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    del ALERTS_DB[alert_id]
    return {"message": "Alert deleted successfully"}

@router.get("/analytics/summary")
async def get_alerts_summary(
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    days: int = Query(7, description="Days for summary analysis"),
    current_user: dict = Depends(get_current_user)
):
    """Get alerts summary and analytics"""
    
    cutoff_time = datetime.utcnow() - timedelta(days=days)
    alerts = [
        alert for alert in ALERTS_DB.values()
        if alert["created_at"] >= cutoff_time
    ]
    
    if site_id:
        alerts = [a for a in alerts if a["site_id"] == site_id]
    
    # Calculate statistics
    total_alerts = len(alerts)
    severity_counts = {
        "low": len([a for a in alerts if a["severity"] == "low"]),
        "medium": len([a for a in alerts if a["severity"] == "medium"]),
        "high": len([a for a in alerts if a["severity"] == "high"]),
        "critical": len([a for a in alerts if a["severity"] == "critical"])
    }
    
    status_counts = {
        "active": len([a for a in alerts if a["status"] == "active"]),
        "acknowledged": len([a for a in alerts if a["status"] == "acknowledged"]),
        "resolved": len([a for a in alerts if a["status"] == "resolved"]),
        "dismissed": len([a for a in alerts if a["status"] == "dismissed"])
    }
    
    type_counts = {}
    for alert_type in AlertType:
        type_counts[alert_type.value] = len([a for a in alerts if a["alert_type"] == alert_type.value])
    
    # Calculate response times
    acknowledged_alerts = [a for a in alerts if a.get("acknowledged_at")]
    avg_response_time = None
    if acknowledged_alerts:
        response_times = [
            (a["acknowledged_at"] - a["created_at"]).total_seconds() / 60
            for a in acknowledged_alerts
        ]
        avg_response_time = sum(response_times) / len(response_times)
    
    return {
        "period_days": days,
        "site_id": site_id,
        "total_alerts": total_alerts,
        "severity_distribution": severity_counts,
        "status_distribution": status_counts,
        "type_distribution": type_counts,
        "average_response_time_minutes": round(avg_response_time, 2) if avg_response_time else None,
        "critical_alerts_last_24h": len([
            a for a in alerts 
            if a["severity"] == "critical" and a["created_at"] >= datetime.utcnow() - timedelta(hours=24)
        ])
    }

@router.post("/notifications/preferences", response_model=NotificationPreferences)
async def set_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user)
):
    """Set user notification preferences"""
    
    # Ensure user can only set their own preferences
    if preferences.user_id != current_user["email"]:
        raise HTTPException(status_code=403, detail="Can only set own preferences")
    
    NOTIFICATION_PREFERENCES[preferences.user_id] = preferences
    return preferences

@router.get("/notifications/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(current_user: dict = Depends(get_current_user)):
    """Get user notification preferences"""
    
    user_id = current_user["email"]
    preferences = NOTIFICATION_PREFERENCES.get(user_id)
    
    if not preferences:
        # Return default preferences
        preferences = NotificationPreferences(
            user_id=user_id,
            channels=[
                NotificationChannel(
                    type="email",
                    enabled=True,
                    config={"address": user_id}
                )
            ],
            severity_filter=["high", "critical"]
        )
    
    return preferences

@router.post("/test-notification")
async def test_notification(
    severity: AlertSeverity,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Send test notification"""
    
    if NOTIFICATION_SYSTEM_AVAILABLE:
        try:
            # Use the notification system test function
            test_config = {
                'email': current_user.get('email', 'test@example.com'),
                'phone': '+1234567890',  # Demo phone number
                'webhook_url': 'https://httpbin.org/post'  # Test webhook
            }
            
            result = test_notification_system(test_config)
            return {
                "message": "Test notification sent using notification system",
                "results": result,
                "severity": severity
            }
            
        except Exception as e:
            return {
                "message": f"Test notification failed: {str(e)}",
                "severity": severity
            }
    else:
        # Fallback test
        test_alert = {
            "id": "test-alert",
            "site_id": "test-site",
            "title": "Test Notification",
            "message": "This is a test notification to verify your alert settings",
            "severity": severity,
            "alert_type": "system_error",
            "status": "active",
            "created_at": datetime.utcnow()
        }
        
        user_prefs = NOTIFICATION_PREFERENCES.get(current_user["email"])
        if user_prefs:
            background_tasks.add_task(send_notification, test_alert, user_prefs)
            return {"message": "Test notification sent (fallback mode)"}
        else:
            return {"message": "No notification preferences found. Please set preferences first."}

@router.post("/bulk-acknowledge")
async def bulk_acknowledge_alerts(
    alert_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Acknowledge multiple alerts at once"""
    
    updated_alerts = []
    for alert_id in alert_ids:
        alert = ALERTS_DB.get(alert_id)
        if alert and alert["status"] == "active":
            alert["status"] = "acknowledged"
            alert["acknowledged_by"] = current_user["email"]
            alert["acknowledged_at"] = datetime.utcnow()
            alert["updated_at"] = datetime.utcnow()
            updated_alerts.append(alert_id)
    
    return {
        "acknowledged_count": len(updated_alerts),
        "alert_ids": updated_alerts
    }