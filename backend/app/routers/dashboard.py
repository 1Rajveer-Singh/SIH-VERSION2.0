"""
Dashboard API endpoints
Provides dashboard statistics, real-time data, and summary information
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.models.database import (
    MiningSite, Device, Prediction, Alert, User,
    DashboardStats, PredictionSummary, DeviceStatus as DeviceStatusModel,
    RiskLevel, AlertSeverity, DeviceStatus
)
from app.routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get overall dashboard statistics"""
    try:
        # Get total sites
        total_sites = await MiningSite.count()
        
        # Get active alerts
        active_alerts = await Alert.find(Alert.status == "active").count()
        
        # Get device counts
        total_devices = await Device.count()
        devices_online = await Device.find(Device.status == DeviceStatus.ONLINE).count()
        
        # Get high risk sites
        current_time = datetime.utcnow()
        one_hour_ago = current_time - timedelta(hours=1)
        
        high_risk_predictions = await Prediction.find(
            Prediction.timestamp >= one_hour_ago,
            Prediction.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).to_list()
        
        high_risk_sites = len(set(p.site_id for p in high_risk_predictions))
        
        # Get predictions today
        today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        predictions_today = await Prediction.find(
            Prediction.timestamp >= today_start
        ).count()
        
        # Calculate system uptime (simplified)
        system_uptime = "99.8%"  # This would be calculated from system logs
        
        return DashboardStats(
            total_sites=total_sites,
            active_alerts=active_alerts,
            devices_online=devices_online,
            total_devices=total_devices,
            high_risk_sites=high_risk_sites,
            predictions_today=predictions_today,
            system_uptime=system_uptime
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard statistics")

@router.get("/predictions/summary", response_model=List[PredictionSummary])
async def get_prediction_summary(
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get prediction summary for all sites"""
    try:
        sites = await MiningSite.find().to_list()
        summaries = []
        
        for site in sites:
            # Get latest prediction for this site
            latest_prediction = await Prediction.find(
                Prediction.site_id == str(site.id)
            ).sort(-Prediction.timestamp).first()
            
            # Get device counts for this site
            total_devices = await Device.find(Device.site_id == str(site.id)).count()
            devices_online = await Device.find(
                Device.site_id == str(site.id),
                Device.status == DeviceStatus.ONLINE
            ).count()
            
            # Get recent alerts
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            recent_alerts = await Alert.find(
                Alert.site_id == str(site.id),
                Alert.timestamp >= one_day_ago,
                Alert.status == "active"
            ).count()
            
            summary = PredictionSummary(
                site_id=str(site.id),
                site_name=site.name,
                current_risk_level=latest_prediction.risk_level if latest_prediction else RiskLevel.LOW,
                latest_probability=latest_prediction.probability if latest_prediction else 0.0,
                last_prediction_time=latest_prediction.timestamp if latest_prediction else datetime.utcnow(),
                devices_online=devices_online,
                total_devices=total_devices,
                recent_alerts=recent_alerts
            )
            summaries.append(summary)
        
        return summaries[:limit]
        
    except Exception as e:
        logger.error(f"Error getting prediction summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prediction summary")

@router.get("/alerts/recent", response_model=List[Alert])
async def get_recent_alerts(
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[AlertSeverity] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get recent alerts"""
    try:
        query = Alert.find()
        
        if severity:
            query = query.find(Alert.severity == severity)
        
        alerts = await query.sort(-Alert.timestamp).limit(limit).to_list()
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error getting recent alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent alerts")

@router.get("/alerts/filtered")
async def get_filtered_alerts(
    time_range: str = Query("24h", description="Time range: 24h, 7d, 30d, 90d"),
    severity: Optional[str] = None,
    site_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get filtered alerts based on time range and other criteria"""
    try:
        # Calculate time threshold
        now = datetime.utcnow()
        time_thresholds = {
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        threshold = now - time_thresholds.get(time_range, timedelta(hours=24))
        
        query = Alert.find(Alert.timestamp >= threshold)
        
        if severity:
            query = query.find(Alert.severity == severity)
        
        if site_id:
            query = query.find(Alert.site_id == site_id)
        
        alerts = await query.sort(-Alert.timestamp).limit(limit).to_list()
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "time_range": time_range,
            "filters_applied": {
                "severity": severity,
                "site_id": site_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting filtered alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get filtered alerts")

@router.get("/predictions/filtered")
async def get_filtered_predictions(
    time_range: str = Query("24h", description="Time range: 24h, 7d, 30d, 90d"),
    risk_level: Optional[str] = None,
    site_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get filtered predictions based on time range and risk level"""
    try:
        # Calculate time threshold
        now = datetime.utcnow()
        time_thresholds = {
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        threshold = now - time_thresholds.get(time_range, timedelta(hours=24))
        
        query = Prediction.find(Prediction.timestamp >= threshold)
        
        if risk_level and risk_level != "all":
            query = query.find(Prediction.risk_level == risk_level.upper())
        
        if site_id:
            query = query.find(Prediction.site_id == site_id)
        
        predictions = await query.sort(-Prediction.timestamp).limit(limit).to_list()
        
        # Enhance with site names
        enhanced_predictions = []
        for prediction in predictions:
            site = await MiningSite.get(prediction.site_id)
            enhanced_prediction = {
                **prediction.dict(),
                "site_name": site.name if site else "Unknown Site"
            }
            enhanced_predictions.append(enhanced_prediction)
        
        return {
            "predictions": enhanced_predictions,
            "total_count": len(enhanced_predictions),
            "time_range": time_range,
            "filters_applied": {
                "risk_level": risk_level,
                "site_id": site_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting filtered predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get filtered predictions")

@router.get("/sensor-health")
async def get_sensor_health_overview(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive sensor health monitoring data"""
    try:
        devices = await Device.find().to_list()
        
        sensor_health = []
        for device in devices:
            # Calculate health score
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
                Alert.device_id == device.device_id,
                Alert.status == "active"
            ).count()
            health_score -= min(recent_alerts * 5, 30)
            
            health_score = max(0, health_score)
            
            sensor_health.append({
                "device_id": device.device_id,
                "device_name": device.name,
                "status": device.status,
                "health": health_score,
                "last_update": device.last_reading or device.updated_at,
                "site_id": device.site_id
            })
        
        # Calculate overall health statistics
        online_count = len([s for s in sensor_health if s["status"] == "online"])
        warning_count = len([s for s in sensor_health if s["status"] == "warning"])
        offline_count = len([s for s in sensor_health if s["status"] == "offline"])
        
        return {
            "sensors": sensor_health,
            "summary": {
                "total_sensors": len(sensor_health),
                "online": online_count,
                "warning": warning_count,
                "offline": offline_count,
                "overall_health": round(sum(s["health"] for s in sensor_health) / len(sensor_health), 1) if sensor_health else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting sensor health overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sensor health overview")

@router.get("/event-timeline")
async def get_event_timeline(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get event timeline for dashboard"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent predictions
        predictions = await Prediction.find(
            Prediction.timestamp >= cutoff_time
        ).sort(-Prediction.timestamp).limit(limit // 2).to_list()
        
        # Get recent alerts
        alerts = await Alert.find(
            Alert.timestamp >= cutoff_time
        ).sort(-Alert.timestamp).limit(limit // 2).to_list()
        
        # Combine and format events
        events = []
        
        for prediction in predictions:
            site = await MiningSite.get(prediction.site_id)
            events.append({
                "time": prediction.timestamp,
                "type": "prediction",
                "message": f"{prediction.risk_level.value} risk prediction generated for {site.name if site else prediction.site_id}",
                "risk_level": prediction.risk_level.value,
                "site_id": prediction.site_id
            })
        
        for alert in alerts:
            events.append({
                "time": alert.timestamp,
                "type": "alert",
                "message": alert.message,
                "severity": alert.severity,
                "site_id": alert.site_id
            })
        
        # Sort by time (most recent first)
        events.sort(key=lambda x: x["time"], reverse=True)
        
        return {
            "events": events[:limit],
            "period_hours": hours,
            "total_events": len(events)
        }
        
    except Exception as e:
        logger.error(f"Error getting event timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to get event timeline")

@router.get("/system-overview")
async def get_system_overview(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive system overview for enhanced dashboard"""
    try:
        # Get basic stats
        total_sites = await MiningSite.count()
        total_devices = await Device.count()
        online_devices = await Device.find(Device.status == DeviceStatus.ONLINE).count()
        
        # Get recent activity
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        recent_predictions = await Prediction.find(
            Prediction.timestamp >= twenty_four_hours_ago
        ).count()
        
        recent_alerts = await Alert.find(
            Alert.timestamp >= twenty_four_hours_ago
        ).count()
        
        # Get all predictions for accuracy calculation
        all_predictions = await Prediction.find().to_list()
        avg_confidence = sum(p.confidence for p in all_predictions) / len(all_predictions) if all_predictions else 0
        
        # Get current risk assessment
        latest_predictions = await Prediction.find().sort(-Prediction.timestamp).limit(total_sites).to_list()
        high_risk_sites = len([p for p in latest_predictions if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
        
        current_risk = "LOW"
        if high_risk_sites > total_sites * 0.3:
            current_risk = "HIGH"
        elif high_risk_sites > total_sites * 0.1:
            current_risk = "MEDIUM"
        
        return {
            "sites": {
                "total": total_sites,
                "high_risk": high_risk_sites,
                "monitored": total_sites  # Assuming all sites are monitored
            },
            "devices": {
                "total": total_devices,
                "online": online_devices,
                "offline": total_devices - online_devices,
                "health_percentage": (online_devices / total_devices * 100) if total_devices > 0 else 0
            },
            "predictions": {
                "total_lifetime": len(all_predictions),
                "recent_24h": recent_predictions,
                "average_confidence": round(avg_confidence, 3),
                "accuracy": "89.2%"  # Mock value - would be calculated from validation data
            },
            "alerts": {
                "recent_24h": recent_alerts,
                "active": await Alert.find(Alert.status == "active").count()
            },
            "system": {
                "current_risk_level": current_risk,
                "uptime": "99.8%",
                "last_updated": datetime.utcnow()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system overview")

@router.get("/devices/status", response_model=List[DeviceStatusModel])
async def get_devices_status(
    site_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get status of all devices or devices for a specific site"""
    try:
        query = Device.find()
        
        if site_id:
            query = query.find(Device.site_id == site_id)
        
        devices = await query.to_list()
        
        device_statuses = []
        for device in devices:
            status = DeviceStatusModel(
                device_id=device.device_id,
                name=device.name,
                type=device.type,
                status=device.status,
                last_reading=device.last_reading,
                battery_level=device.battery_level,
                signal_strength=device.signal_strength
            )
            device_statuses.append(status)
        
        return device_statuses
        
    except Exception as e:
        logger.error(f"Error getting device status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get device status")

@router.get("/charts/risk-trends")
async def get_risk_trends(
    site_id: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
    current_user: dict = Depends(get_current_user)
):
    """Get risk level trends for charts"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = Prediction.find(Prediction.timestamp >= start_date)
        
        if site_id:
            query = query.find(Prediction.site_id == site_id)
        
        predictions = await query.sort(-Prediction.timestamp).to_list()
        
        # Group by day and calculate average risk
        daily_data = {}
        for prediction in predictions:
            day_key = prediction.timestamp.strftime("%Y-%m-%d")
            if day_key not in daily_data:
                daily_data[day_key] = {"total": 0, "count": 0, "max_risk": 0}
            
            risk_value = {
                RiskLevel.LOW: 1,
                RiskLevel.MEDIUM: 2, 
                RiskLevel.HIGH: 3,
                RiskLevel.CRITICAL: 4
            }.get(prediction.risk_level, 1)
            
            daily_data[day_key]["total"] += risk_value
            daily_data[day_key]["count"] += 1
            daily_data[day_key]["max_risk"] = max(daily_data[day_key]["max_risk"], risk_value)
        
        # Format for charts
        chart_data = []
        for day, data in sorted(daily_data.items()):
            avg_risk = data["total"] / data["count"] if data["count"] > 0 else 0
            chart_data.append({
                "date": day,
                "average_risk": round(avg_risk, 2),
                "max_risk": data["max_risk"],
                "predictions_count": data["count"]
            })
        
        return {"data": chart_data, "period_days": days}
        
    except Exception as e:
        logger.error(f"Error getting risk trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get risk trends")

@router.post("/predictions/run")
async def run_immediate_prediction(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Run immediate prediction analysis for a site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Get recent sensor data for this site
        devices = await Device.find(Device.site_id == site_id).to_list()
        
        if not devices:
            raise HTTPException(status_code=400, detail="No devices found for this site")
        
        # This would call your ML prediction model
        # For now, we'll create a demo prediction
        import random
        
        risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
        risk_level = random.choice(risk_levels)
        probability = random.uniform(0.1, 0.9)
        confidence = random.uniform(0.7, 0.95)
        
        # Create prediction
        prediction = Prediction(
            site_id=site_id,
            timestamp=datetime.utcnow(),
            risk_level=risk_level,
            probability=probability,
            confidence=confidence,
            model_version="v1.0.0",
            contributing_factors=[
                {"factor": "Seismic Activity", "weight": 0.3},
                {"factor": "Weather Conditions", "weight": 0.2},
                {"factor": "Slope Stability", "weight": 0.5}
            ],
            recommendations=[
                "Continue monitoring",
                "Review safety protocols",
                "Increase inspection frequency"
            ],
            data_points_used=len(devices) * 24  # Simulated
        )
        
        await prediction.insert()
        
        # Create alert if high risk
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alert = Alert(
                type="prediction",
                severity="error" if risk_level == RiskLevel.CRITICAL else "warning",
                message=f"High risk prediction for {site.name}: {risk_level.value} risk level",
                site_id=site_id,
                prediction_id=str(prediction.id)
            )
            await alert.insert()
        
        return {
            "success": True,
            "prediction_id": str(prediction.id),
            "risk_level": risk_level,
            "probability": probability,
            "confidence": confidence,
            "message": "Prediction completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error running prediction: {e}")
        raise HTTPException(status_code=500, detail="Failed to run prediction")

@router.get("/notifications")
async def get_notifications(
    current_user: dict = Depends(get_current_user)
):
    """Get real-time notifications for the user"""
    try:
        # Get recent alerts and system notifications
        alerts = await Alert.find(
            Alert.status == "active"
        ).sort(-Alert.timestamp).limit(10).to_list()
        
        notifications = []
        for alert in alerts:
            # Get site name if available
            site_name = "Unknown Site"
            if alert.site_id:
                site = await MiningSite.get(alert.site_id)
                if site:
                    site_name = site.name
            
            notifications.append({
                "id": str(alert.id),
                "type": alert.type,
                "severity": alert.severity,
                "message": alert.message,
                "site_name": site_name,
                "timestamp": alert.timestamp,
                "acknowledged": alert.status == "acknowledged"
            })
        
        return {
            "notifications": notifications,
            "unread_count": len([n for n in notifications if not n["acknowledged"]]),
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")