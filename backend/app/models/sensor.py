"""
Sensor Data Models
Pydantic models for sensor readings and time-series data
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SensorType(str, Enum):
    """Supported sensor types"""
    DISPLACEMENT = "displacement"
    STRAIN = "strain"
    PORE_PRESSURE = "pore_pressure"
    VIBRATION = "vibration"
    TILT = "tilt"
    CRACK_METER = "crack_meter"

class QualityFlag(str, Enum):
    """Data quality flags"""
    GOOD = "good"
    QUESTIONABLE = "questionable"
    BAD = "bad"
    MISSING = "missing"

class GeoPoint(BaseModel):
    """GeoJSON Point geometry"""
    type: str = "Point"
    coordinates: List[float] = Field(..., min_items=2, max_items=3)

class SensorReading(BaseModel):
    """Individual sensor reading"""
    time: datetime
    device_id: str
    sensor_type: SensorType
    value: float
    unit: str
    quality_flag: QualityFlag = QualityFlag.GOOD
    location: GeoPoint
    node_name: str
    site_id: str
    battery_level: Optional[float] = Field(None, ge=0, le=100)
    signal_strength: Optional[float] = Field(None, ge=0, le=100)
    calibration_date: Optional[datetime] = None

class SensorReadingBatch(BaseModel):
    """Batch of sensor readings"""
    readings: List[SensorReading]
    batch_id: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class SensorDevice(BaseModel):
    """Sensor device information"""
    device_id: str
    sensor_type: SensorType
    location: GeoPoint
    node_name: str
    site_id: str
    status: str = Field(default="active", pattern=r'^(active|inactive|maintenance|error)$')
    installation_date: datetime
    last_calibration: Optional[datetime] = None
    calibration_interval_days: int = Field(default=90)
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    battery_life_months: Optional[int] = None
    measurement_range: Dict[str, float] = Field(default={})
    accuracy: Optional[str] = None

class SensorAlert(BaseModel):
    """Sensor-specific alert conditions"""
    device_id: str
    alert_type: str = Field(..., pattern=r'^(threshold|anomaly|battery|communication|calibration)$')
    threshold_value: Optional[float] = None
    comparison: Optional[str] = Field(None, pattern=r'^(greater_than|less_than|equal|not_equal)$')
    enabled: bool = True
    notification_channels: List[str] = Field(default=["email"])

class SensorStatistics(BaseModel):
    """Statistical summary of sensor data"""
    device_id: str
    sensor_type: SensorType
    period: str  # "1h", "24h", "7d", "30d"
    count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    percentiles: Dict[str, float] = Field(default={})
    trend: Optional[str] = None  # "increasing", "decreasing", "stable"
    anomaly_count: int = 0

class SensorQuery(BaseModel):
    """Query parameters for sensor data"""
    site_id: Optional[str] = None
    device_ids: Optional[List[str]] = None
    sensor_types: Optional[List[SensorType]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quality_flags: Optional[List[QualityFlag]] = None
    limit: int = Field(1000, ge=1, le=10000)
    skip: int = Field(0, ge=0)
    aggregate: Optional[str] = None  # "hourly", "daily", "weekly"

class AnomalyDetection(BaseModel):
    """Anomaly detection results"""
    device_id: str
    timestamp: datetime
    value: float
    anomaly_score: float = Field(..., ge=0, le=1)
    anomaly_type: str = Field(..., pattern=r'^(spike|drop|trend|pattern)$')
    severity: str = Field(..., pattern=r'^(low|medium|high|critical)$')
    description: str
    context: Dict[str, Any] = Field(default={})

class SensorCalibration(BaseModel):
    """Sensor calibration record"""
    device_id: str
    calibration_date: datetime
    calibrated_by: str
    calibration_type: str = Field(..., pattern=r'^(factory|field|remote)$')
    reference_values: List[Dict[str, float]]
    measured_values: List[Dict[str, float]]
    adjustment_factors: Dict[str, float]
    accuracy_after_calibration: str
    notes: Optional[str] = None
    next_calibration_due: datetime