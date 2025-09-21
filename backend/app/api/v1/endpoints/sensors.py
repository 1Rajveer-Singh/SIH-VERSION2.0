"""
Sensor Data Endpoints
Real-time sensor monitoring and time-series data management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging
from datetime import datetime, timedelta
from bson import ObjectId

from app.models.sensor import (
    SensorReading, SensorReadingBatch, SensorDevice, SensorQuery,
    SensorStatistics, AnomalyDetection, SensorType, QualityFlag
)
from app.models.user import User
from app.core.auth import get_current_active_user, require_engineer
from app.core.database import get_database
from app.services.sensor_service import SensorService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/readings", response_model=dict)
async def upload_sensor_readings(
    batch: SensorReadingBatch,
    current_user: User = Depends(require_engineer)
):
    """
    Upload batch of sensor readings
    
    - **readings**: List of sensor readings
    - **batch_id**: Optional batch identifier for tracking
    
    Requires engineer-level access or higher
    """
    try:
        db = get_database()
        sensor_collection = db["sensor_timeseries"]
        
        # Convert readings to dict format for MongoDB
        readings_data = []
        for reading in batch.readings:
            reading_dict = {
                "time": reading.time,
                "device_id": reading.device_id,
                "sensor_type": reading.sensor_type.value,
                "value": reading.value,
                "unit": reading.unit,
                "quality_flag": reading.quality_flag.value,
                "location": reading.location.dict(),
                "node_name": reading.node_name,
                "site_id": reading.site_id,
                "battery_level": reading.battery_level,
                "signal_strength": reading.signal_strength,
                "calibration_date": reading.calibration_date,
                "uploaded_by": str(current_user.id),
                "uploaded_at": batch.uploaded_at
            }
            readings_data.append(reading_dict)
        
        # Insert batch
        result = await sensor_collection.insert_many(readings_data)
        
        logger.info(
            f"Uploaded {len(readings_data)} sensor readings in batch {batch.batch_id} "
            f"by user {current_user.username}"
        )
        
        return {
            "message": f"Successfully uploaded {len(readings_data)} readings",
            "batch_id": batch.batch_id,
            "inserted_count": len(result.inserted_ids),
            "inserted_ids": [str(id) for id in result.inserted_ids[:10]]  # Limit for response size
        }
        
    except Exception as e:
        logger.error(f"Failed to upload sensor readings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload sensor readings: {str(e)}"
        )

@router.get("/readings", response_model=List[dict])
async def get_sensor_readings(
    site_id: Optional[str] = None,
    device_ids: Optional[str] = None,  # Comma-separated
    sensor_types: Optional[str] = None,  # Comma-separated
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    quality_flags: Optional[str] = None,  # Comma-separated
    limit: int = 1000,
    skip: int = 0,
    aggregate: Optional[str] = None,  # "hourly", "daily", "weekly"
    current_user: User = Depends(get_current_active_user)
):
    """
    Get sensor readings with filtering options
    
    - **site_id**: Filter by site ID
    - **device_ids**: Comma-separated list of device IDs
    - **sensor_types**: Comma-separated list of sensor types
    - **start_time**: Start time for range filter
    - **end_time**: End time for range filter
    - **quality_flags**: Comma-separated quality flags to include
    - **limit**: Maximum number of results (1-10000)
    - **skip**: Number of results to skip for pagination
    - **aggregate**: Aggregation level (hourly, daily, weekly)
    """
    try:
        db = get_database()
        sensor_collection = db["sensor_timeseries"]
        
        # Build query filter
        query_filter = {}
        
        if site_id:
            query_filter["site_id"] = site_id
        
        if device_ids:
            device_list = [id.strip() for id in device_ids.split(",")]
            query_filter["device_id"] = {"$in": device_list}
        
        if sensor_types:
            type_list = [t.strip() for t in sensor_types.split(",")]
            query_filter["sensor_type"] = {"$in": type_list}
        
        if start_time or end_time:
            time_filter = {}
            if start_time:
                time_filter["$gte"] = start_time
            if end_time:
                time_filter["$lte"] = end_time
            query_filter["time"] = time_filter
        
        if quality_flags:
            flag_list = [f.strip() for f in quality_flags.split(",")]
            query_filter["quality_flag"] = {"$in": flag_list}
        
        # Set reasonable default time range if not specified
        if not start_time and not end_time:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            query_filter["time"] = {"$gte": start_time, "$lte": end_time}
        
        # Apply aggregation if requested
        if aggregate:
            readings = await _get_aggregated_readings(
                sensor_collection, query_filter, aggregate, limit
            )
        else:
            # Standard query
            cursor = sensor_collection.find(query_filter).sort("time", -1).skip(skip).limit(limit)
            readings = await cursor.to_list(length=limit)
            
            # Convert ObjectIds to strings
            for reading in readings:
                if "_id" in reading:
                    reading["_id"] = str(reading["_id"])
        
        logger.info(
            f"Retrieved {len(readings)} sensor readings for user {current_user.username}"
        )
        
        return readings
        
    except Exception as e:
        logger.error(f"Failed to retrieve sensor readings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sensor readings"
        )

@router.get("/devices", response_model=List[SensorDevice])
async def get_sensor_devices(
    site_id: Optional[str] = None,
    sensor_type: Optional[SensorType] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get sensor device information
    
    - **site_id**: Filter by site ID
    - **sensor_type**: Filter by sensor type
    - **status**: Filter by device status
    """
    try:
        # For now, return mock data since device management would be separate
        # In production, this would query a devices collection
        mock_devices = []
        
        device_configs = [
            {"device_id": "SENSOR-001-DISP", "sensor_type": "displacement", "node_name": "Node-001"},
            {"device_id": "SENSOR-002-STRAIN", "sensor_type": "strain", "node_name": "Node-002"},
            {"device_id": "SENSOR-003-VIBR", "sensor_type": "vibration", "node_name": "Node-003"},
            {"device_id": "SENSOR-004-TILT", "sensor_type": "tilt", "node_name": "Node-004"},
        ]
        
        for config in device_configs:
            if site_id and site_id != "DEMO_SITE_001":
                continue
            if sensor_type and sensor_type.value != config["sensor_type"]:
                continue
            if status and status != "active":
                continue
                
            device = SensorDevice(
                device_id=config["device_id"],
                sensor_type=config["sensor_type"],
                location={
                    "type": "Point",
                    "coordinates": [-114.05 + len(mock_devices) * 0.01, 51.05 + len(mock_devices) * 0.01]
                },
                node_name=config["node_name"],
                site_id=site_id or "DEMO_SITE_001",
                status="active",
                installation_date=datetime.utcnow() - timedelta(days=30),
                last_calibration=datetime.utcnow() - timedelta(days=15),
                manufacturer="SensorTech Inc.",
                model="ST-2000",
                firmware_version="2.1.0"
            )
            mock_devices.append(device)
        
        return mock_devices
        
    except Exception as e:
        logger.error(f"Failed to retrieve sensor devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sensor devices"
        )

@router.get("/statistics", response_model=List[SensorStatistics])
async def get_sensor_statistics(
    site_id: Optional[str] = None,
    device_ids: Optional[str] = None,
    period: str = "24h",
    current_user: User = Depends(get_current_active_user)
):
    """
    Get statistical summary of sensor data
    
    - **site_id**: Filter by site ID
    - **device_ids**: Comma-separated list of device IDs
    - **period**: Time period for statistics ("1h", "24h", "7d", "30d")
    """
    try:
        sensor_service = SensorService()
        
        # Parse period
        period_hours = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}.get(period, 24)
        
        device_list = []
        if device_ids:
            device_list = [id.strip() for id in device_ids.split(",")]
        
        statistics = await sensor_service.calculate_statistics(
            site_id=site_id,
            device_ids=device_list,
            hours=period_hours
        )
        
        return statistics
        
    except Exception as e:
        logger.error(f"Failed to calculate sensor statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate sensor statistics"
        )

@router.get("/anomalies", response_model=List[AnomalyDetection])
async def detect_sensor_anomalies(
    site_id: Optional[str] = None,
    device_ids: Optional[str] = None,
    hours: int = 24,
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Detect sensor data anomalies
    
    - **site_id**: Filter by site ID
    - **device_ids**: Comma-separated list of device IDs
    - **hours**: Hours of history to analyze
    - **severity**: Filter by severity level
    """
    try:
        sensor_service = SensorService()
        
        device_list = []
        if device_ids:
            device_list = [id.strip() for id in device_ids.split(",")]
        
        anomalies = await sensor_service.detect_anomalies(
            site_id=site_id,
            device_ids=device_list,
            hours=hours,
            severity_filter=severity
        )
        
        return anomalies
        
    except Exception as e:
        logger.error(f"Failed to detect anomalies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect anomalies"
        )

@router.get("/health", response_model=dict)
async def get_sensor_health_summary(
    site_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get overall sensor health summary
    
    - **site_id**: Filter by site ID
    """
    try:
        db = get_database()
        sensor_collection = db["sensor_timeseries"]
        
        # Get recent data (last 2 hours)
        recent_time = datetime.utcnow() - timedelta(hours=2)
        
        query = {"time": {"$gte": recent_time}}
        if site_id:
            query["site_id"] = site_id
        
        # Aggregate health statistics
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$device_id",
                    "last_reading": {"$max": "$time"},
                    "reading_count": {"$sum": 1},
                    "avg_battery": {"$avg": "$battery_level"},
                    "avg_signal": {"$avg": "$signal_strength"},
                    "quality_flags": {"$push": "$quality_flag"}
                }
            }
        ]
        
        results = await sensor_collection.aggregate(pipeline).to_list(length=None)
        
        # Calculate summary statistics
        total_devices = len(results)
        online_devices = 0
        low_battery_devices = 0
        poor_quality_devices = 0
        
        for device in results:
            # Device is online if it has readings in last 2 hours
            time_since_last = datetime.utcnow() - device["last_reading"]
            if time_since_last.total_seconds() < 7200:  # 2 hours
                online_devices += 1
            
            # Low battery check
            if device.get("avg_battery", 100) < 20:
                low_battery_devices += 1
            
            # Quality check
            bad_quality_count = sum(1 for flag in device["quality_flags"] if flag in ["bad", "questionable"])
            if bad_quality_count > device["reading_count"] * 0.1:  # More than 10% bad quality
                poor_quality_devices += 1
        
        return {
            "site_id": site_id,
            "total_devices": total_devices,
            "online_devices": online_devices,
            "offline_devices": total_devices - online_devices,
            "low_battery_devices": low_battery_devices,
            "poor_quality_devices": poor_quality_devices,
            "health_percentage": round((online_devices / total_devices * 100) if total_devices > 0 else 0, 1),
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sensor health summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sensor health summary"
        )

async def _get_aggregated_readings(collection, query_filter: dict, aggregate: str, limit: int):
    """Get aggregated sensor readings"""
    # Define aggregation intervals
    intervals = {
        "hourly": {"$dateToString": {"format": "%Y-%m-%d %H:00:00", "date": "$time"}},
        "daily": {"$dateToString": {"format": "%Y-%m-%d", "date": "$time"}},
        "weekly": {"$dateToString": {"format": "%Y-W%V", "date": "$time"}}
    }
    
    if aggregate not in intervals:
        raise ValueError(f"Invalid aggregation: {aggregate}")
    
    pipeline = [
        {"$match": query_filter},
        {
            "$group": {
                "_id": {
                    "device_id": "$device_id",
                    "sensor_type": "$sensor_type",
                    "interval": intervals[aggregate]
                },
                "avg_value": {"$avg": "$value"},
                "min_value": {"$min": "$value"},
                "max_value": {"$max": "$value"},
                "count": {"$sum": 1},
                "last_time": {"$max": "$time"}
            }
        },
        {"$sort": {"_id.interval": -1, "_id.device_id": 1}},
        {"$limit": limit}
    ]
    
    results = await collection.aggregate(pipeline).to_list(length=limit)
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_results.append({
            "device_id": result["_id"]["device_id"],
            "sensor_type": result["_id"]["sensor_type"],
            "interval": result["_id"]["interval"],
            "avg_value": round(result["avg_value"], 3),
            "min_value": result["min_value"],
            "max_value": result["max_value"],
            "reading_count": result["count"],
            "last_time": result["last_time"]
        })
    
    return formatted_results