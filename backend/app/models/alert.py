"""
Alert Models
Pydantic models for alerts and notifications
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

from app.models.user import PyObjectId

class AlertType(str, Enum):
    """Alert types"""
    CRITICAL = "Critical"
    WARNING = "Warning"
    INFO = "Info"
    MAINTENANCE = "Maintenance"

class AlertStatus(str, Enum):
    """Alert status"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FAILED = "failed"

class NotificationChannel(str, Enum):
    """Notification channels"""
    SMS = "SMS"
    EMAIL = "Email"
    WEBHOOK = "Webhook"
    PUSH = "Push"
    DASHBOARD = "Dashboard"

class Alert(BaseModel):
    """Alert model"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    site_id: str
    prediction_id: Optional[PyObjectId] = None
    alert_type: AlertType
    severity: int = Field(..., ge=1, le=5, description="1=Info, 5=Critical")
    title: str
    message: str
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.EMAIL])
    status: AlertStatus = AlertStatus.PENDING
    recipients: List[str] = Field(default=[])
    metadata: Optional[Dict[str, Any]] = None
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    escalation_level: int = Field(default=1, ge=1, le=3)
    acknowledged_by: Optional[PyObjectId] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[PyObjectId] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AlertCreate(BaseModel):
    """Create alert request"""
    site_id: str
    prediction_id: Optional[str] = None
    alert_type: AlertType
    severity: int = Field(..., ge=1, le=5)
    title: str
    message: str
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.EMAIL])
    recipients: List[str] = Field(default=[])
    metadata: Optional[Dict[str, Any]] = None
    expires_in_minutes: Optional[int] = None

class AlertUpdate(BaseModel):
    """Update alert request"""
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    escalation_level: Optional[int] = Field(None, ge=1, le=3)

class AlertResponse(BaseModel):
    """Alert response model"""
    id: str
    site_id: str
    prediction_id: Optional[str] = None
    alert_type: AlertType
    severity: int
    title: str
    message: str
    channels: List[NotificationChannel]
    status: AlertStatus
    recipients: List[str]
    retry_count: int
    escalation_level: int
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    sent_at: Optional[datetime] = None

class AlertFilter(BaseModel):
    """Filter for querying alerts"""
    site_id: Optional[str] = None
    alert_type: Optional[AlertType] = None
    status: Optional[AlertStatus] = None
    severity_min: Optional[int] = Field(None, ge=1, le=5)
    severity_max: Optional[int] = Field(None, ge=1, le=5)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=1000)
    skip: int = Field(0, ge=0)

class NotificationTemplate(BaseModel):
    """Notification message template"""
    name: str
    alert_type: AlertType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    variables: List[str] = Field(default=[])
    is_active: bool = True

class AlertRule(BaseModel):
    """Alert rule configuration"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    site_id: Optional[str] = None  # None means applies to all sites
    conditions: Dict[str, Any]
    alert_config: AlertCreate
    is_active: bool = True
    created_by: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AlertRuleCreate(BaseModel):
    """Create alert rule request"""
    name: str
    site_id: Optional[str] = None
    conditions: Dict[str, Any]
    alert_config: AlertCreate

class EscalationPolicy(BaseModel):
    """Alert escalation policy"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    site_id: Optional[str] = None
    levels: List[Dict[str, Any]] = Field(
        default=[
            {"level": 1, "delay_minutes": 0, "channels": ["Email"], "recipients": []},
            {"level": 2, "delay_minutes": 15, "channels": ["SMS", "Email"], "recipients": []},
            {"level": 3, "delay_minutes": 30, "channels": ["SMS", "Email", "Webhook"], "recipients": []}
        ]
    )
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AlertStatistics(BaseModel):
    """Alert statistics"""
    site_id: Optional[str] = None
    period: str  # "24h", "7d", "30d"
    total_alerts: int
    by_type: Dict[AlertType, int]
    by_status: Dict[AlertStatus, int]
    by_severity: Dict[int, int]
    average_response_time_minutes: float
    escalated_alerts: int
    failed_notifications: int