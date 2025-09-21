"""
MongoDB Schema Definitions for Rockfall Prediction System
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# User Management Schema
class User(BaseModel):
    """User authentication and authorization schema"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password_hash: str
    role: str = Field(..., regex=r'^(safety_officer|engineer|manager|researcher|admin)$')
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Site Management Schema
class Site(BaseModel):
    """Mining site information schema"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    site_id: str = Field(..., unique=True)
    name: str
    description: Optional[str] = None
    location: Dict[str, Any] = Field(..., description="GeoJSON Point")
    bounds: List[float] = Field(..., description="[minx, miny, maxx, maxy]")
    elevation_range: Dict[str, float] = Field(default={"min": 0, "max": 1000})
    site_type: str = Field(default="open_pit")
    status: str = Field(default="active", regex=r'^(active|inactive|maintenance)$')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: PyObjectId

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# DEM Collection Schema
class DEMCollection(BaseModel):
    """Digital Elevation Model data schema"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    site_id: str
    filename: str
    s3_url: str
    s3_bucket: str
    file_size_bytes: int
    bounds: List[float] = Field(..., description="[minx, miny, maxx, maxy]")
    resolution_m: float = Field(default=1.0, description="Resolution in meters")
    coordinate_system: str = Field(default="EPSG:4326")
    elevation_range: Dict[str, float]
    metadata: Optional[Dict[str, Any]] = None
    processing_status: str = Field(default="pending", regex=r'^(pending|processing|completed|failed)$')
    uploaded_by: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Drone Images Schema
class DroneImage(BaseModel):
    """Drone imagery metadata schema"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    site_id: str
    filename: str
    s3_url: str
    s3_bucket: str
    file_size_bytes: int
    geotag: Dict[str, Any] = Field(..., description="GeoJSON Point")
    altitude_m: Optional[float] = None
    camera: Dict[str, Any] = Field(
        default={
            "focal_length_mm": 24,
            "sensor_size_mm": [36, 24],
            "iso": 100,
            "aperture": "f/8",
            "shutter_speed": "1/500"
        }
    )
    flight_mission_id: Optional[str] = None
    weather_conditions: Optional[Dict[str, Any]] = None
    image_quality_score: Optional[float] = Field(default=None, ge=0, le=1)
    processing_status: str = Field(default="pending", regex=r'^(pending|processing|completed|failed)$')
    uploaded_by: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Sensor Time-Series Schema (MongoDB Time-Series Collection)
class SensorTimeSeries(BaseModel):
    """Sensor time-series data schema"""
    time: datetime = Field(..., description="Measurement timestamp")
    device_id: str
    sensor_type: str = Field(..., regex=r'^(displacement|strain|pore_pressure|vibration|tilt|crack_meter)$')
    value: float
    unit: str
    quality_flag: str = Field(default="good", regex=r'^(good|questionable|bad|missing)$')
    location: Dict[str, Any] = Field(..., description="GeoJSON Point")
    node_name: str
    site_id: str
    battery_level: Optional[float] = Field(default=None, ge=0, le=100)
    signal_strength: Optional[float] = Field(default=None, ge=0, le=100)
    calibration_date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True


# Environmental Data Schema
class EnvironmentalData(BaseModel):
    """Environmental monitoring data schema"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    site_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    rainfall_mm: Optional[float] = Field(default=None, ge=0)
    rainfall_24h: Optional[float] = Field(default=None, ge=0)
    temperature_c: Optional[float] = None
    humidity: Optional[float] = Field(default=None, ge=0, le=100)
    wind_speed_kmh: Optional[float] = Field(default=None, ge=0)
    wind_direction_deg: Optional[float] = Field(default=None, ge=0, le=360)
    atmospheric_pressure_hpa: Optional[float] = None
    vibration_level: Optional[float] = Field(default=None, ge=0)
    seismic_activity: Optional[float] = Field(default=None, ge=0)
    soil_moisture: Optional[float] = Field(default=None, ge=0, le=100)
    data_source: str = Field(default="weather_station")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Predictions Schema
class Prediction(BaseModel):
    """AI model prediction results schema"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    site_id: str
    risk_score: float = Field(..., ge=0, le=1, description="Risk probability score")
    risk_class: str = Field(..., regex=r'^(Low|Medium|High|Critical)$')
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")
    explanation: Dict[str, Any] = Field(
        default={
            "top_features": [],
            "feature_importance": {},
            "image_gradcam_url": None,
            "shap_values": {}
        }
    )
    geojson_zone: Optional[Dict[str, Any]] = Field(None, description="Risk zone GeoJSON")
    model_metadata: Dict[str, Any] = Field(
        default={
            "model_version": "1.0.0",
            "model_type": "ensemble",
            "training_date": None,
            "feature_count": 0
        }
    )
    input_data_sources: List[str] = Field(default=[])
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processed_by: str = Field(default="rockfall_prediction_model_v1")
    is_archived: bool = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Alerts Schema
class Alert(BaseModel):
    """System alerts and notifications schema"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    site_id: str
    prediction_id: Optional[PyObjectId] = None
    alert_type: str = Field(..., regex=r'^(Critical|Warning|Info|Maintenance)$')
    severity: int = Field(..., ge=1, le=5, description="1=Info, 5=Critical")
    title: str
    message: str
    channels: List[str] = Field(default=["Email"], description="SMS, Email, Webhook, Push")
    status: str = Field(default="pending", regex=r'^(pending|sent|acknowledged|resolved|failed)$')
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


# Model Registry Schema
class MLModel(BaseModel):
    """Machine learning model metadata schema"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    version: str
    model_type: str = Field(..., regex=r'^(regression|classification|ensemble|neural_network)$')
    framework: str = Field(default="pytorch")
    s3_model_path: str
    performance_metrics: Dict[str, float] = Field(
        default={
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "auc_roc": 0.0
        }
    )
    feature_schema: Dict[str, Any]
    training_data_period: Dict[str, datetime]
    hyperparameters: Dict[str, Any]
    is_active: bool = Field(default=False)
    deployment_status: str = Field(default="development", regex=r'^(development|staging|production|deprecated)$')
    created_by: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_retrained: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Collection Names
COLLECTIONS = {
    "users": "users",
    "sites": "sites", 
    "dem_collection": "dem_collection",
    "drone_images": "drone_images",
    "sensor_timeseries": "sensor_timeseries",  # Time-series collection
    "environmental_data": "environmental_data",
    "predictions": "predictions",
    "alerts": "alerts",
    "ml_models": "ml_models"
}

# Indexes Configuration
INDEXES = {
    "users": [
        [("username", 1)],
        [("email", 1)],
        [("role", 1)],
        [("created_at", -1)]
    ],
    "sites": [
        [("site_id", 1)],
        [("location", "2dsphere")],
        [("status", 1)],
        [("created_at", -1)]
    ],
    "dem_collection": [
        [("site_id", 1)],
        [("created_at", -1)],
        [("processing_status", 1)],
        [("site_id", 1), ("created_at", -1)]
    ],
    "drone_images": [
        [("site_id", 1)],
        [("geotag", "2dsphere")],
        [("created_at", -1)],
        [("processing_status", 1)],
        [("site_id", 1), ("created_at", -1)]
    ],
    "environmental_data": [
        [("site_id", 1)],
        [("timestamp", -1)],
        [("site_id", 1), ("timestamp", -1)]
    ],
    "predictions": [
        [("site_id", 1)],
        [("timestamp", -1)],
        [("risk_class", 1)],
        [("site_id", 1), ("timestamp", -1)],
        [("geojson_zone", "2dsphere")]
    ],
    "alerts": [
        [("site_id", 1)],
        [("status", 1)],
        [("alert_type", 1)],
        [("created_at", -1)],
        [("site_id", 1), ("created_at", -1)],
        [("status", 1), ("created_at", -1)]
    ],
    "ml_models": [
        [("name", 1), ("version", 1)],
        [("is_active", 1)],
        [("deployment_status", 1)],
        [("created_at", -1)]
    ]
}

# Time-series collection configuration
TIMESERIES_CONFIG = {
    "sensor_timeseries": {
        "timeField": "time",
        "metaField": "device_id",
        "granularity": "minutes"
    }
}