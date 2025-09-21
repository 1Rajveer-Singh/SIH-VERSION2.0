"""
Sensors management router
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import random
from .auth import get_current_user

router = APIRouter()

class SensorLocationModel(BaseModel):
    lat: float
    lng: float
    elevation: float

class SensorCreate(BaseModel):
    site_id: str
    name: str
    location: SensorLocationModel
    sensor_types: List[str]

class SensorUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[SensorLocationModel] = None
    status: Optional[str] = None

class SensorResponse(BaseModel):
    id: str
    site_id: str
    name: str
    location: SensorLocationModel
    sensor_types: List[str]
    status: str
    last_reading: Optional[datetime]
    installation_date: datetime

class SensorReading(BaseModel):
    timestamp: datetime
    sensor_id: str
    readings: Dict[str, float]

# Mock sensors database
SENSORS_DB = {
    "sensor-001": {
        "id": "sensor-001",
        "site_id": "site-001",
        "name": "Accelerometer Station A1",
        "location": {"lat": 39.7400, "lng": -104.9900, "elevation": 1620},
        "sensor_types": ["accelerometer", "inclinometer", "temperature"],
        "status": "active",
        "last_reading": datetime.utcnow() - timedelta(minutes=5),
        "installation_date": datetime(2023, 1, 15)
    },
    "sensor-002": {
        "id": "sensor-002",
        "site_id": "site-001", 
        "name": "Weather Station A2",
        "location": {"lat": 39.7380, "lng": -104.9920, "elevation": 1615},
        "sensor_types": ["weather_station", "pressure", "humidity"],
        "status": "active",
        "last_reading": datetime.utcnow() - timedelta(minutes=2),
        "installation_date": datetime(2023, 2, 10)
    },
    "sensor-003": {
        "id": "sensor-003",
        "site_id": "site-002",
        "name": "Seismometer B1", 
        "location": {"lat": 39.1620, "lng": -119.7680, "elevation": 1380},
        "sensor_types": ["seismometer", "gps", "accelerometer"],
        "status": "maintenance",
        "last_reading": datetime.utcnow() - timedelta(hours=2),
        "installation_date": datetime(2023, 3, 5)
    }
}

@router.get("/", response_model=List[SensorResponse])
async def get_sensors(
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user)
):
    """Get all sensors with optional filtering"""
    sensors = list(SENSORS_DB.values())
    
    if site_id:
        sensors = [s for s in sensors if s["site_id"] == site_id]
    
    if status:
        sensors = [s for s in sensors if s["status"] == status]
    
    return [SensorResponse(**sensor) for sensor in sensors]

@router.get("/{sensor_id}", response_model=SensorResponse)
async def get_sensor(sensor_id: str, current_user: dict = Depends(get_current_user)):
    """Get sensor by ID"""
    sensor = SENSORS_DB.get(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    return SensorResponse(**sensor)

@router.post("/", response_model=SensorResponse)
async def create_sensor(sensor_data: SensorCreate, current_user: dict = Depends(get_current_user)):
    """Create new sensor"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    sensor_id = f"sensor-{len(SENSORS_DB) + 1:03d}"
    new_sensor = {
        "id": sensor_id,
        **sensor_data.dict(),
        "status": "active",
        "last_reading": None,
        "installation_date": datetime.utcnow()
    }
    
    SENSORS_DB[sensor_id] = new_sensor
    return SensorResponse(**new_sensor)

@router.put("/{sensor_id}", response_model=SensorResponse)
async def update_sensor(sensor_id: str, sensor_update: SensorUpdate, current_user: dict = Depends(get_current_user)):
    """Update sensor"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    sensor = SENSORS_DB.get(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Update sensor data
    for field, value in sensor_update.dict(exclude_unset=True).items():
        if field == "location" and value:
            sensor[field] = value.dict()
        else:
            sensor[field] = value
    
    return SensorResponse(**sensor)

@router.delete("/{sensor_id}")
async def delete_sensor(sensor_id: str, current_user: dict = Depends(get_current_user)):
    """Delete sensor"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if sensor_id not in SENSORS_DB:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    del SENSORS_DB[sensor_id]
    return {"message": "Sensor deleted successfully"}

@router.get("/{sensor_id}/readings")
async def get_sensor_readings(
    sensor_id: str,
    hours: int = Query(24, description="Hours of data to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    """Get sensor readings for specified time period"""
    sensor = SENSORS_DB.get(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Generate mock readings
    readings = []
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    for i in range(hours * 4):  # 4 readings per hour
        timestamp = start_time + timedelta(minutes=i * 15)
        
        # Generate realistic readings based on sensor types
        mock_readings = {}
        for sensor_type in sensor["sensor_types"]:
            if sensor_type == "accelerometer":
                mock_readings.update({
                    "vibration_x": round(random.uniform(0.001, 0.05), 4),
                    "vibration_y": round(random.uniform(0.001, 0.05), 4),
                    "vibration_z": round(random.uniform(0.001, 0.05), 4)
                })
            elif sensor_type == "inclinometer":
                mock_readings.update({
                    "tilt_x": round(random.uniform(-2, 2), 2),
                    "tilt_y": round(random.uniform(-2, 2), 2)
                })
            elif sensor_type == "temperature":
                mock_readings["temperature"] = round(random.uniform(10, 25), 1)
            elif sensor_type == "weather_station":
                mock_readings.update({
                    "wind_speed": round(random.uniform(0, 20), 1),
                    "wind_direction": round(random.uniform(0, 360), 0),
                    "precipitation": round(max(0, random.gauss(0, 2)), 1)
                })
            elif sensor_type == "pressure":
                mock_readings["atmospheric_pressure"] = round(random.uniform(1000, 1030), 1)
            elif sensor_type == "humidity":
                mock_readings["humidity"] = round(random.uniform(30, 80), 1)
            elif sensor_type == "seismometer":
                mock_readings["seismic_activity"] = round(abs(random.gauss(0, 0.1)), 4)
            elif sensor_type == "gps":
                mock_readings.update({
                    "displacement_x": round(random.gauss(0, 0.001), 6),
                    "displacement_y": round(random.gauss(0, 0.001), 6),
                    "displacement_z": round(random.gauss(0, 0.0005), 6)
                })
        
        readings.append(SensorReading(
            timestamp=timestamp,
            sensor_id=sensor_id,
            readings=mock_readings
        ))
    
    return {
        "sensor_id": sensor_id,
        "period_hours": hours,
        "total_readings": len(readings),
        "readings": readings[-50:]  # Return last 50 readings to avoid too much data
    }

@router.get("/{sensor_id}/status")
async def get_sensor_status(sensor_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed sensor status"""
    sensor = SENSORS_DB.get(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Mock status data
    return {
        "sensor_id": sensor_id,
        "status": sensor["status"],
        "last_reading": sensor["last_reading"],
        "battery_level": random.randint(70, 100) if sensor["status"] == "active" else 0,
        "signal_strength": random.randint(80, 100) if sensor["status"] == "active" else 0,
        "data_quality": "good" if sensor["status"] == "active" else "poor",
        "uptime_hours": random.randint(100, 8760),
        "total_readings_today": random.randint(80, 96)
    }