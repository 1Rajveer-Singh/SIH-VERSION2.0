"""
Mining sites API endpoints
CRUD operations for mining sites with geographic and operational data
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.models.database import (
    MiningSite, MiningSiteCreate, MiningSiteUpdate, MiningSiteResponse,
    Device, Prediction, Alert, RiskLevel
)
from app.routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[MiningSiteResponse])
async def get_mining_sites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    risk_level: Optional[RiskLevel] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all mining sites with optional filtering"""
    try:
        query = MiningSite.find()
        
        if status:
            query = query.find(MiningSite.status == status)
        
        sites = await query.skip(skip).limit(limit).to_list()
        
        # Enhance with latest prediction data
        enhanced_sites = []
        for site in sites:
            # Get latest prediction
            latest_prediction = await Prediction.find(
                Prediction.site_id == str(site.id)
            ).sort(-Prediction.timestamp).first()
            
            # Get device count
            device_count = await Device.find(Device.site_id == str(site.id)).count()
            
            # Get recent alerts
            recent_alerts_count = await Alert.find(
                Alert.site_id == str(site.id),
                Alert.status == "active"
            ).count()
            
            site_response = MiningSiteResponse(
                **site.dict(),
                latest_prediction=latest_prediction,
                device_count=device_count,
                recent_alerts_count=recent_alerts_count
            )
            
            # Filter by risk level if specified
            if risk_level:
                if latest_prediction and latest_prediction.risk_level == risk_level:
                    enhanced_sites.append(site_response)
                elif not latest_prediction and risk_level == RiskLevel.LOW:
                    enhanced_sites.append(site_response)
            else:
                enhanced_sites.append(site_response)
        
        return enhanced_sites
        
    except Exception as e:
        logger.error(f"Error getting mining sites: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mining sites")

@router.get("/{site_id}", response_model=MiningSiteResponse)
async def get_mining_site(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific mining site by ID"""
    try:
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        # Get latest prediction
        latest_prediction = await Prediction.find(
            Prediction.site_id == site_id
        ).sort(-Prediction.timestamp).first()
        
        # Get device count
        device_count = await Device.find(Device.site_id == site_id).count()
        
        # Get recent alerts count
        recent_alerts_count = await Alert.find(
            Alert.site_id == site_id,
            Alert.status == "active"
        ).count()
        
        return MiningSiteResponse(
            **site.dict(),
            latest_prediction=latest_prediction,
            device_count=device_count,
            recent_alerts_count=recent_alerts_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mining site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mining site")

@router.post("/", response_model=MiningSiteResponse)
async def create_mining_site(
    site_data: MiningSiteCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new mining site"""
    try:
        # Check for duplicate name
        existing_site = await MiningSite.find_one(MiningSite.name == site_data.name)
        if existing_site:
            raise HTTPException(status_code=400, detail="Site with this name already exists")
        
        # Create new site
        site = MiningSite(
            **site_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await site.insert()
        
        # Return with additional data
        return MiningSiteResponse(
            **site.dict(),
            latest_prediction=None,
            device_count=0,
            recent_alerts_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating mining site: {e}")
        raise HTTPException(status_code=500, detail="Failed to create mining site")

@router.put("/{site_id}", response_model=MiningSiteResponse)
async def update_mining_site(
    site_id: str,
    site_data: MiningSiteUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing mining site"""
    try:
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        # Check for duplicate name (excluding current site)
        if site_data.name and site_data.name != site.name:
            existing_site = await MiningSite.find_one(
                MiningSite.name == site_data.name,
                MiningSite.id != site.id
            )
            if existing_site:
                raise HTTPException(status_code=400, detail="Site with this name already exists")
        
        # Update site with provided data
        update_data = site_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(site, field, value)
        
        await site.save()
        
        # Get additional data for response
        latest_prediction = await Prediction.find(
            Prediction.site_id == site_id
        ).sort(-Prediction.timestamp).first()
        
        device_count = await Device.find(Device.site_id == site_id).count()
        recent_alerts_count = await Alert.find(
            Alert.site_id == site_id,
            Alert.status == "active"
        ).count()
        
        return MiningSiteResponse(
            **site.dict(),
            latest_prediction=latest_prediction,
            device_count=device_count,
            recent_alerts_count=recent_alerts_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating mining site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update mining site")

@router.delete("/{site_id}")
async def delete_mining_site(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a mining site and all associated data"""
    try:
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        # Check if site has devices - prevent deletion if devices exist
        device_count = await Device.find(Device.site_id == site_id).count()
        if device_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete site with {device_count} active devices. Remove devices first."
            )
        
        # Delete associated data
        await Alert.find(Alert.site_id == site_id).delete()
        await Prediction.find(Prediction.site_id == site_id).delete()
        
        # Delete the site
        await site.delete()
        
        return {"message": f"Mining site '{site.name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting mining site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete mining site")

@router.get("/{site_id}/devices", response_model=List[Device])
async def get_site_devices(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all devices for a specific mining site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        devices = await Device.find(Device.site_id == site_id).to_list()
        return devices
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting devices for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve site devices")

@router.get("/{site_id}/predictions", response_model=List[Prediction])
async def get_site_predictions(
    site_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get predictions for a specific mining site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        predictions = await Prediction.find(
            Prediction.site_id == site_id
        ).sort(-Prediction.timestamp).limit(limit).to_list()
        
        return predictions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting predictions for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve site predictions")

@router.get("/{site_id}/alerts", response_model=List[Alert])
async def get_site_alerts(
    site_id: str,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get alerts for a specific mining site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        query = Alert.find(Alert.site_id == site_id)
        
        if status:
            query = query.find(Alert.status == status)
        
        alerts = await query.sort(-Alert.timestamp).limit(limit).to_list()
        
        return alerts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alerts for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve site alerts")

@router.post("/{site_id}/emergency")
async def trigger_emergency_protocol(
    site_id: str,
    emergency_type: str,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Trigger emergency protocol for a mining site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        # Create critical alert
        alert = Alert(
            type="emergency",
            severity="critical",
            message=f"EMERGENCY: {emergency_type} at {site.name}",
            site_id=site_id,
            metadata={
                "emergency_type": emergency_type,
                "description": description or "",
                "triggered_by": current_user.get("email", "unknown"),
                "protocol_activated": True
            }
        )
        
        await alert.insert()
        
        # Update site status to emergency
        site.status = "emergency"
        site.updated_at = datetime.utcnow()
        await site.save()
        
        # Here you would trigger actual emergency protocols:
        # - Send SMS/email notifications
        # - Alert emergency services
        # - Activate evacuation procedures
        # - Notify regulatory authorities
        
        logger.warning(f"Emergency protocol activated for site {site.name}: {emergency_type}")
        
        return {
            "success": True,
            "message": "Emergency protocol activated",
            "alert_id": str(alert.id),
            "emergency_type": emergency_type,
            "site_status": "emergency"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering emergency protocol for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger emergency protocol")

@router.get("/{site_id}/overview")
async def get_site_overview(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive overview of a mining site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        # Get devices
        devices = await Device.find(Device.site_id == site_id).to_list()
        online_devices = [d for d in devices if d.status == "online"]
        
        # Get latest predictions
        latest_predictions = await Prediction.find(
            Prediction.site_id == site_id
        ).sort(-Prediction.timestamp).limit(10).to_list()
        
        # Get active alerts
        active_alerts = await Alert.find(
            Alert.site_id == site_id,
            Alert.status == "active"
        ).to_list()
        
        # Calculate risk assessment
        current_risk = "LOW"
        if latest_predictions:
            latest_risk = latest_predictions[0].risk_level
            if latest_risk in ["HIGH", "CRITICAL"]:
                current_risk = latest_risk
            elif latest_risk == "MEDIUM":
                current_risk = "MEDIUM"
        
        return {
            "site_info": {
                "id": str(site.id),
                "name": site.name,
                "location": site.location,
                "coordinates": site.coordinates,
                "status": site.status,
                "operational_since": site.created_at
            },
            "devices": {
                "total": len(devices),
                "online": len(online_devices),
                "offline": len(devices) - len(online_devices),
                "health_percentage": (len(online_devices) / len(devices) * 100) if devices else 0
            },
            "risk_assessment": {
                "current_level": current_risk,
                "recent_predictions": len(latest_predictions),
                "active_alerts": len(active_alerts),
                "last_updated": latest_predictions[0].timestamp if latest_predictions else None
            },
            "operational_status": {
                "status": site.status,
                "emergency_contacts": getattr(site, 'emergency_contacts', []),
                "last_inspection": getattr(site, 'last_inspection', None),
                "next_inspection": getattr(site, 'next_inspection', None)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting site overview for {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get site overview")

@router.get("/{site_id}/analytics")
async def get_site_analytics(
    site_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics data for a specific mining site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get predictions in time range
        predictions = await Prediction.find(
            Prediction.site_id == site_id,
            Prediction.timestamp >= cutoff_date
        ).to_list()
        
        # Get alerts in time range
        alerts = await Alert.find(
            Alert.site_id == site_id,
            Alert.timestamp >= cutoff_date
        ).to_list()
        
        # Calculate risk distribution
        risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for prediction in predictions:
            risk_distribution[prediction.risk_level] += 1
        
        # Calculate alert severity distribution
        alert_distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alert in alerts:
            alert_distribution[alert.severity] += 1
        
        # Calculate confidence metrics
        confidences = [p.confidence for p in predictions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Calculate trend data (simulate daily aggregation)
        daily_risk_trend = []
        for i in range(min(days, 30)):  # Limit to 30 days for visualization
            day_start = datetime.utcnow() - timedelta(days=i+1)
            day_end = datetime.utcnow() - timedelta(days=i)
            
            day_predictions = [p for p in predictions if day_start <= p.timestamp < day_end]
            avg_risk_score = 0
            if day_predictions:
                risk_scores = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
                avg_risk_score = sum(risk_scores[p.risk_level] for p in day_predictions) / len(day_predictions)
            
            daily_risk_trend.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "risk_score": round(avg_risk_score, 2),
                "prediction_count": len(day_predictions)
            })
        
        return {
            "period_days": days,
            "predictions": {
                "total": len(predictions),
                "risk_distribution": risk_distribution,
                "average_confidence": round(avg_confidence, 3),
                "trend": list(reversed(daily_risk_trend))  # Most recent first
            },
            "alerts": {
                "total": len(alerts),
                "severity_distribution": alert_distribution,
                "active": len([a for a in alerts if a.status == "active"])
            },
            "summary": {
                "risk_assessment": "HIGH" if risk_distribution["HIGH"] + risk_distribution["CRITICAL"] > len(predictions) * 0.3 else "MEDIUM" if risk_distribution["MEDIUM"] > len(predictions) * 0.2 else "LOW",
                "alert_frequency": len(alerts) / days if days > 0 else 0,
                "prediction_accuracy": "91.5%"  # Mock value - would be calculated from validation
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting site analytics for {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get site analytics")

@router.post("/{site_id}/maintenance")
async def schedule_maintenance(
    site_id: str,
    maintenance_type: str,
    scheduled_date: datetime,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Schedule maintenance for a mining site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        # Create maintenance alert
        alert = Alert(
            type="maintenance",
            severity="low",
            message=f"Scheduled maintenance: {maintenance_type} for {site.name}",
            site_id=site_id,
            metadata={
                "maintenance_type": maintenance_type,
                "scheduled_date": scheduled_date.isoformat(),
                "description": description or "",
                "scheduled_by": current_user.get("email", "unknown"),
                "status": "scheduled"
            }
        )
        
        await alert.insert()
        
        logger.info(f"Maintenance scheduled for site {site.name}: {maintenance_type} on {scheduled_date}")
        
        return {
            "success": True,
            "message": "Maintenance scheduled successfully",
            "alert_id": str(alert.id),
            "maintenance_type": maintenance_type,
            "scheduled_date": scheduled_date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling maintenance for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule maintenance")

@router.get("/{site_id}/exports/report")
async def export_site_report(
    site_id: str,
    report_type: str = Query("summary", description="Type of report: summary, detailed, alerts, predictions"),
    format: str = Query("json", description="Export format: json, csv"),
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Export site data and reports"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Mining site not found")
        
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        report_data = {
            "site_info": {
                "id": str(site.id),
                "name": site.name,
                "location": site.location,
                "coordinates": site.coordinates,
                "status": site.status
            },
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": current_user.get("email", "unknown"),
                "report_type": report_type,
                "period_days": days,
                "format": format
            }
        }
        
        if report_type in ["summary", "detailed", "predictions"]:
            predictions = await Prediction.find(
                Prediction.site_id == site_id,
                Prediction.timestamp >= cutoff_date
            ).to_list()
            report_data["predictions"] = [p.dict() for p in predictions]
        
        if report_type in ["summary", "detailed", "alerts"]:
            alerts = await Alert.find(
                Alert.site_id == site_id,
                Alert.timestamp >= cutoff_date
            ).to_list()
            report_data["alerts"] = [a.dict() for a in alerts]
        
        if report_type in ["detailed"]:
            devices = await Device.find(Device.site_id == site_id).to_list()
            report_data["devices"] = [d.dict() for d in devices]
        
        # For CSV format, flatten the data structure
        if format == "csv":
            # This would require additional processing to convert to CSV
            # For now, return JSON with a note
            report_data["note"] = "CSV export would require additional processing"
        
        return report_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting report for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export site report")