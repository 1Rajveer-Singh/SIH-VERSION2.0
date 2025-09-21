"""
Comprehensive database models for Rockfall Prediction System
Using MongoDB with Beanie ODM for async operations
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums for better type safety
class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class DeviceType(str, Enum):
    ACCELEROMETER = "accelerometer"
    INCLINOMETER = "inclinometer"
    SEISMOMETER = "seismometer"
    WEATHER_STATION = "weather_station"
    GPS = "gps"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"

class SiteStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class AlertType(str, Enum):
    PREDICTION = "prediction"
    DEVICE = "device"
    SYSTEM = "system"
    MAINTENANCE = "maintenance"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Embedded models
class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation: Optional[float] = None
    address: Optional[str] = None

class Zone(BaseModel):
    zone_id: str
    name: str
    risk_level: RiskLevel = RiskLevel.LOW
    description: Optional[str] = None

class EmergencyContact(BaseModel):
    name: str
    role: str
    phone: str
    email: EmailStr

class DeviceConfiguration(BaseModel):
    sampling_rate: int = 60  # seconds
    thresholds: Dict[str, float] = {}
    calibration_date: Optional[datetime] = None
    firmware_version: Optional[str] = None

class ContributingFactor(BaseModel):
    factor: str
    weight: float = Field(..., ge=0, le=1)
    description: Optional[str] = None

# Database document models (export all needed classes)
class User(Document):
    email: str = Field(..., unique=True)
    username: str = Field(..., unique=True)
    full_name: Optional[str] = None
    password_hash: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    profile_picture: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            "email",
            "username", 
            "role",
            "is_active"
        ]

class MiningSite(Document):
    name: str
    description: Optional[str] = None
    location: Location
    zones: List[Zone] = []
    status: SiteStatus = SiteStatus.ACTIVE
    emergency_contacts: List[EmergencyContact] = []
    area_hectares: Optional[float] = None
    safety_protocols: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "mining_sites"
        indexes = [
            "name",
            "status",
            [("location.latitude", 1), ("location.longitude", 1)]
        ]

class Device(Document):
    device_id: str = Field(..., unique=True)
    name: str
    type: DeviceType
    site_id: str  # Reference to MiningSite
    zone_id: Optional[str] = None
    location: Optional[Location] = None
    status: DeviceStatus = DeviceStatus.OFFLINE
    configuration: DeviceConfiguration = Field(default_factory=DeviceConfiguration)
    last_reading: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    battery_level: Optional[float] = None  # 0-100%
    signal_strength: Optional[float] = None  # 0-100%
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "devices"
        indexes = [
            "device_id",
            "site_id",
            "type",
            "status",
            "last_reading"
        ]

class SensorReading(Document):
    device_id: str  # Reference to Device
    timestamp: datetime
    readings: Dict[str, Any]  # Flexible readings data
    quality_score: Optional[float] = Field(None, ge=0, le=1)
    anomaly_detected: bool = False
    processed: bool = False

    class Settings:
        name = "sensor_readings"
        indexes = [
            [("device_id", 1), ("timestamp", -1)],
            [("timestamp", -1)],
            "processed"
        ]

class Prediction(Document):
    site_id: str  # Reference to MiningSite
    zone_id: Optional[str] = None
    timestamp: datetime
    risk_level: RiskLevel
    probability: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    prediction_model_version: str
    contributing_factors: List[ContributingFactor] = []
    recommendations: List[str] = []
    data_points_used: int = 0
    processing_time_ms: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "predictions"
        indexes = [
            [("site_id", 1), ("timestamp", -1)],
            "risk_level",
            [("timestamp", -1)]
        ]

class Alert(Document):
    type: AlertType
    severity: AlertSeverity
    message: str
    site_id: Optional[str] = None  # Reference to MiningSite
    device_id: Optional[str] = None  # Reference to Device
    prediction_id: Optional[str] = None  # Reference to Prediction
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_by: Optional[str] = None  # Reference to User
    acknowledged_at: Optional[datetime] = None
    status: AlertStatus = AlertStatus.ACTIVE
    details: Optional[Dict[str, Any]] = None
    auto_resolve: bool = False
    resolve_after_minutes: Optional[int] = None

    class Settings:
        name = "alerts"
        indexes = [
            [("timestamp", -1)],
            "status",
            "severity",
            "site_id"
        ]

class SystemSetting(Document):
    key: str = Field(..., unique=True)
    value: Any
    description: Optional[str] = None
    data_type: str = "string"  # string, int, float, bool, json
    updated_by: Optional[str] = None  # Reference to User
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "system_settings"
        indexes = ["key"]

class SystemLog(Document):
    level: LogLevel
    message: str
    source: Optional[str] = None
    user_id: Optional[str] = None  # Reference to User
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Settings:
        name = "system_logs"
        indexes = [
            [("timestamp", -1)],
            "level",
            "source"
        ]

# Create and Update models for API
class MiningSiteCreate(BaseModel):
    """Model for creating a new mining site"""
    name: str
    description: Optional[str] = None
    location: Location
    zones: List[Zone] = []
    status: SiteStatus = SiteStatus.ACTIVE
    emergency_contacts: List[EmergencyContact] = []
    area_hectares: Optional[float] = None
    safety_protocols: List[str] = []

class MiningSiteUpdate(BaseModel):
    """Model for updating a mining site"""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[Location] = None
    zones: Optional[List[Zone]] = None
    status: Optional[SiteStatus] = None
    emergency_contacts: Optional[List[EmergencyContact]] = None
    area_hectares: Optional[float] = None
    safety_protocols: Optional[List[str]] = None

class DeviceCreate(BaseModel):
    """Model for creating a new device"""
    device_id: str
    name: str
    type: DeviceType
    site_id: str
    zone_id: Optional[str] = None
    location: Optional[Location] = None
    configuration: Optional[DeviceConfiguration] = None

class DeviceUpdate(BaseModel):
    """Model for updating a device"""
    name: Optional[str] = None
    type: Optional[DeviceType] = None
    site_id: Optional[str] = None
    zone_id: Optional[str] = None
    location: Optional[Location] = None
    status: Optional[DeviceStatus] = None
    configuration: Optional[DeviceConfiguration] = None
    battery_level: Optional[float] = None
    signal_strength: Optional[float] = None

class SensorReadingCreate(BaseModel):
    """Model for creating a sensor reading"""
    timestamp: datetime
    readings: Dict[str, Any]
    quality_score: Optional[float] = None
    anomaly_detected: bool = False

class AlertCreate(BaseModel):
    """Model for creating an alert"""
    type: AlertType
    severity: AlertSeverity
    message: str
    site_id: Optional[str] = None
    device_id: Optional[str] = None
    prediction_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    auto_resolve: bool = False
    resolve_after_minutes: Optional[int] = None

class AlertUpdate(BaseModel):
    """Model for updating an alert"""
    severity: Optional[AlertSeverity] = None
    message: Optional[str] = None
    status: Optional[AlertStatus] = None
    details: Optional[Dict[str, Any]] = None

# Additional models for API responses
class PredictionSummary(BaseModel):
    site_id: str
    site_name: str
    current_risk_level: RiskLevel
    latest_probability: float
    last_prediction_time: datetime
    devices_online: int
    total_devices: int
    recent_alerts: int

class DeviceStatus(BaseModel):
    device_id: str
    name: str
    type: DeviceType
    status: DeviceStatus
    last_reading: Optional[datetime]
    battery_level: Optional[float]
    signal_strength: Optional[float]

class DashboardStats(BaseModel):
    total_sites: int
    active_alerts: int
    devices_online: int
    total_devices: int
    high_risk_sites: int
    predictions_today: int
    system_uptime: str

# Response models for API
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    profile_picture: Optional[str]
    last_login: Optional[datetime]
    created_at: datetime

class SiteResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    location: Location
    zones: List[Zone]
    status: SiteStatus
    emergency_contacts: List[EmergencyContact]
    current_risk_level: Optional[RiskLevel]
    devices_count: int
    active_alerts: int

class MiningSiteResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    location: Location
    zones: List[Zone]
    status: SiteStatus
    emergency_contacts: List[EmergencyContact]
    area_hectares: Optional[float]
    safety_protocols: List[str]
    created_at: datetime
    updated_at: Optional[datetime]
    current_risk_level: Optional[RiskLevel]
    devices_count: int
    active_alerts: int

class DeviceResponse(BaseModel):
    id: str
    device_id: str
    name: str
    type: DeviceType
    site_id: str
    zone_id: Optional[str]
    location: Optional[Location]
    status: DeviceStatus
    last_reading: Optional[datetime]
    battery_level: Optional[float]
    signal_strength: Optional[float]
    configuration: DeviceConfiguration

class PredictionResponse(BaseModel):
    id: str
    site_id: str
    zone_id: Optional[str]
    timestamp: datetime
    risk_level: RiskLevel
    probability: float
    confidence: float
    prediction_model_version: str
    contributing_factors: List[ContributingFactor]
    recommendations: List[str]

class AlertResponse(BaseModel):
    id: str
    type: AlertType
    severity: AlertSeverity
    message: str
    site_id: Optional[str]
    device_id: Optional[str]
    prediction_id: Optional[str]
    timestamp: datetime
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    status: AlertStatus
    details: Optional[Dict[str, Any]]

class SensorReadingResponse(BaseModel):
    id: str
    device_id: str
    timestamp: datetime
    readings: Dict[str, Any]
    quality_score: Optional[float]
    anomaly_detected: bool

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]