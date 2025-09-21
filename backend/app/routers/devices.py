"""
Device management API endpoints
CRUD operations for monitoring devices and sensors
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.models.database import (
    Device, DeviceCreate, DeviceUpdate, DeviceResponse,
    SensorReading, SensorReadingCreate, SensorReadingResponse,
    MiningSite, Alert, DeviceStatus
)
from app.routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[DeviceResponse])
async def get_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    site_id: Optional[str] = None,
    status: Optional[DeviceStatus] = None,
    device_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all devices with optional filtering"""
    try:
        query = Device.find()
        
        if site_id:
            query = query.find(Device.site_id == site_id)
        
        if status:
            query = query.find(Device.status == status)
        
        if device_type:
            query = query.find(Device.type == device_type)
        
        devices = await query.skip(skip).limit(limit).to_list()
        
        # Enhance with recent readings and alerts
        enhanced_devices = []
        for device in devices:
            # Get recent readings count
            recent_readings_count = await SensorReading.find(
                SensorReading.device_id == device.device_id
            ).count()
            
            # Get recent alerts
            recent_alerts_count = await Alert.find(
                Alert.device_id == device.device_id,
                Alert.status == "active"
            ).count()
            
            device_response = DeviceResponse(
                **device.dict(),
                recent_readings_count=recent_readings_count,
                recent_alerts_count=recent_alerts_count
            )
            enhanced_devices.append(device_response)
        
        return enhanced_devices
        
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve devices")

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific device by ID"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get recent readings count
        recent_readings_count = await SensorReading.find(
            SensorReading.device_id == device_id
        ).count()
        
        # Get recent alerts count
        recent_alerts_count = await Alert.find(
            Alert.device_id == device_id,
            Alert.status == "active"
        ).count()
        
        return DeviceResponse(
            **device.dict(),
            recent_readings_count=recent_readings_count,
            recent_alerts_count=recent_alerts_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve device")

@router.post("/", response_model=DeviceResponse)
async def create_device(
    device_data: DeviceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new device"""
    try:
        # Verify site exists
        site = await MiningSite.get(device_data.site_id)
        if not site:
            raise HTTPException(status_code=400, detail="Site not found")
        
        # Check for duplicate device ID
        existing_device = await Device.find_one(Device.device_id == device_data.device_id)
        if existing_device:
            raise HTTPException(status_code=400, detail="Device with this ID already exists")
        
        # Create new device
        device = Device(
            **device_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_reading=None,
            status=DeviceStatus.OFFLINE
        )
        
        await device.insert()
        
        return DeviceResponse(
            **device.dict(),
            recent_readings_count=0,
            recent_alerts_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating device: {e}")
        raise HTTPException(status_code=500, detail="Failed to create device")

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing device"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Verify new site exists if changing site
        if device_data.site_id and device_data.site_id != device.site_id:
            site = await MiningSite.get(device_data.site_id)
            if not site:
                raise HTTPException(status_code=400, detail="New site not found")
        
        # Update device with provided data
        update_data = device_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(device, field, value)
        
        await device.save()
        
        # Get additional data for response
        recent_readings_count = await SensorReading.find(
            SensorReading.device_id == device_id
        ).count()
        
        recent_alerts_count = await Alert.find(
            Alert.device_id == device_id,
            Alert.status == "active"
        ).count()
        
        return DeviceResponse(
            **device.dict(),
            recent_readings_count=recent_readings_count,
            recent_alerts_count=recent_alerts_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update device")

@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a device and all associated data"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Delete associated data
        await SensorReading.find(SensorReading.device_id == device_id).delete()
        await Alert.find(Alert.device_id == device_id).delete()
        
        # Delete the device
        await device.delete()
        
        return {"message": f"Device '{device_id}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete device")

@router.post("/{device_id}/test")
async def test_device_connectivity(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Test device connectivity and response"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Simulate connectivity test - replace with actual device communication
        import random
        test_success = random.choice([True, True, True, False])  # 75% success rate
        response_time = random.uniform(50, 500)  # ms
        
        if test_success:
            # Update device status to online
            device.status = DeviceStatus.ONLINE
            device.last_reading = datetime.utcnow()
            device.updated_at = datetime.utcnow()
            await device.save()
            
            return {
                "status": "success",
                "device_id": device_id,
                "response_time_ms": response_time,
                "test_time": datetime.utcnow(),
                "message": "Device responded successfully"
            }
        else:
            # Update device status to offline
            device.status = DeviceStatus.OFFLINE
            device.updated_at = datetime.utcnow()
            await device.save()
            
            return {
                "status": "failed",
                "device_id": device_id,
                "test_time": datetime.utcnow(),
                "message": "Device did not respond to connectivity test"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to test device")

@router.get("/{device_id}/status")
async def get_device_status(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get real-time device status and health metrics"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get latest reading
        latest_reading = await SensorReading.find(
            SensorReading.device_id == device_id
        ).sort(-SensorReading.timestamp).limit(1).to_list()
        
        # Calculate health score based on various factors
        health_score = 100
        
        # Factor 1: Time since last reading
        if device.last_reading:
            time_diff = datetime.utcnow() - device.last_reading
            if time_diff > timedelta(hours=1):
                health_score -= 20
            elif time_diff > timedelta(minutes=30):
                health_score -= 10
        else:
            health_score -= 30
        
        # Factor 2: Device status
        if device.status == DeviceStatus.OFFLINE:
            health_score -= 40
        elif device.status == DeviceStatus.WARNING:
            health_score -= 20
        
        # Factor 3: Recent alerts
        recent_alerts = await Alert.find(
            Alert.device_id == device_id,
            Alert.status == "active"
        ).count()
        health_score -= min(recent_alerts * 5, 30)
        
        health_score = max(0, health_score)
        
        return {
            "device_id": device_id,
            "status": device.status,
            "health_score": health_score,
            "last_reading": device.last_reading,
            "latest_reading": latest_reading[0].dict() if latest_reading else None,
            "recent_alerts_count": recent_alerts,
            "uptime_hours": (datetime.utcnow() - device.created_at).total_seconds() / 3600,
            "coordinates": device.coordinates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device status {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get device status")

@router.post("/{device_id}/calibrate")
async def calibrate_device(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Calibrate device sensors"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Simulate calibration process
        import asyncio
        await asyncio.sleep(2)  # Simulate calibration time
        
        # Update device status
        device.status = DeviceStatus.ONLINE
        device.updated_at = datetime.utcnow()
        await device.save()
        
        return {
            "device_id": device_id,
            "status": "calibrated",
            "calibration_time": datetime.utcnow(),
            "message": "Device calibration completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calibrating device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to calibrate device")

@router.get("/health/summary")
async def get_devices_health_summary(
    current_user: dict = Depends(get_current_user)
):
    """Get overall health summary of all devices"""
    try:
        total_devices = await Device.count()
        online_devices = await Device.find(Device.status == DeviceStatus.ONLINE).count()
        warning_devices = await Device.find(Device.status == DeviceStatus.WARNING).count()
        offline_devices = await Device.find(Device.status == DeviceStatus.OFFLINE).count()
        
        # Get devices with recent readings (last 1 hour)
        recent_threshold = datetime.utcnow() - timedelta(hours=1)
        active_devices = await Device.find(
            Device.last_reading >= recent_threshold
        ).count()
        
        # Calculate overall health percentage
        if total_devices > 0:
            health_percentage = (online_devices / total_devices) * 100
        else:
            health_percentage = 0
        
        return {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "warning_devices": warning_devices,
            "offline_devices": offline_devices,
            "active_devices": active_devices,
            "health_percentage": round(health_percentage, 1),
            "status": "healthy" if health_percentage >= 80 else "warning" if health_percentage >= 60 else "critical"
        }
        
    except Exception as e:
        logger.error(f"Error getting devices health summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get health summary")

@router.get("/{device_id}/readings", response_model=List[SensorReadingResponse])
async def get_device_readings(
    device_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user)
):
    """Get sensor readings for a specific device"""
    try:
        # Verify device exists
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        query = SensorReading.find(SensorReading.device_id == device_id)
        
        if start_time:
            query = query.find(SensorReading.timestamp >= start_time)
        
        if end_time:
            query = query.find(SensorReading.timestamp <= end_time)
        
        readings = await query.sort(-SensorReading.timestamp).limit(limit).to_list()
        
        # Convert to response format
        reading_responses = []
        for reading in readings:
            reading_response = SensorReadingResponse(
                **reading.dict(),
                device_name=device.name,
                site_id=device.site_id
            )
            reading_responses.append(reading_response)
        
        return reading_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting readings for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve device readings")

@router.post("/{device_id}/readings", response_model=SensorReadingResponse)
async def create_device_reading(
    device_id: str,
    reading_data: SensorReadingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new sensor reading for a device"""
    try:
        # Verify device exists
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Create sensor reading
        reading = SensorReading(
            device_id=device_id,
            **reading_data.dict()
        )
        
        await reading.insert()
        
        # Update device last reading time and status
        device.last_reading = reading.timestamp
        device.status = DeviceStatus.ONLINE
        device.updated_at = datetime.utcnow()
        await device.save()
        
        return SensorReadingResponse(
            **reading.dict(),
            device_name=device.name,
            site_id=device.site_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reading for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create device reading")

@router.post("/{device_id}/calibrate")
async def calibrate_device(
    device_id: str,
    calibration_type: str = "full",
    current_user: dict = Depends(get_current_user)
):
    """Initiate device calibration"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Update device configuration
        if not device.configuration:
            device.configuration = {}
        
        device.configuration["last_calibration"] = datetime.utcnow().isoformat()
        device.configuration["calibration_type"] = calibration_type
        device.configuration["calibration_status"] = "in_progress"
        
        device.updated_at = datetime.utcnow()
        await device.save()
        
        # Here you would send calibration command to actual device
        # For demo, we'll simulate completion after a delay
        
        return {
            "success": True,
            "message": f"Calibration initiated for device {device_id}",
            "calibration_type": calibration_type,
            "estimated_completion": datetime.utcnow() + timedelta(minutes=5)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calibrating device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate device calibration")

@router.post("/{device_id}/restart")
async def restart_device(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Restart a device remotely"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Update device status
        device.status = DeviceStatus.MAINTENANCE
        device.updated_at = datetime.utcnow()
        await device.save()
        
        # Create maintenance alert
        alert = Alert(
            type="maintenance",
            severity="info",
            message=f"Device {device.name} restart initiated",
            device_id=device_id,
            site_id=device.site_id,
            metadata={
                "action": "restart",
                "initiated_by": current_user.get("email", "unknown"),
                "estimated_downtime": "2-5 minutes"
            }
        )
        await alert.insert()
        
        # Here you would send restart command to actual device
        
        logger.info(f"Restart initiated for device {device_id}")
        
        return {
            "success": True,
            "message": f"Restart command sent to device {device_id}",
            "status": "maintenance",
            "estimated_downtime": "2-5 minutes"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to restart device")

@router.get("/{device_id}/status")
async def get_device_status(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed device status and health information"""
    try:
        device = await Device.find_one(Device.device_id == device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get latest reading
        latest_reading = await SensorReading.find(
            SensorReading.device_id == device_id
        ).sort(-SensorReading.timestamp).first()
        
        # Calculate uptime and health metrics
        now = datetime.utcnow()
        uptime_hours = 0
        if device.last_reading:
            uptime_hours = (now - device.last_reading).total_seconds() / 3600
        
        # Get site information
        site = await MiningSite.get(device.site_id)
        site_name = site.name if site else "Unknown Site"
        
        return {
            "device_id": device_id,
            "name": device.name,
            "type": device.type,
            "status": device.status,
            "site_name": site_name,
            "last_reading": device.last_reading,
            "battery_level": device.battery_level,
            "signal_strength": device.signal_strength,
            "uptime_hours": round(uptime_hours, 2),
            "latest_reading": latest_reading.dict() if latest_reading else None,
            "configuration": device.configuration or {},
            "health_score": min(100, max(0, (device.battery_level or 0) + (device.signal_strength or 0) / 2))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device status {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get device status")