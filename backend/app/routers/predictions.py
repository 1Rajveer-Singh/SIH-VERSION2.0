"""
Predictions API endpoints - Clean Version
ML-based rockfall prediction analysis and management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import random

from app.models.database import (
    Prediction, MiningSite, Device, SensorReading, Alert,
    RiskLevel, AlertSeverity, PredictionResponse
)
from app.routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    site_id: Optional[str] = None,
    risk_level: Optional[RiskLevel] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get predictions with optional filtering"""
    try:
        query = Prediction.find()
        
        if site_id:
            query = query.find(Prediction.site_id == site_id)
        
        if risk_level:
            query = query.find(Prediction.risk_level == risk_level)
        
        predictions = await query.sort(-Prediction.timestamp).skip(skip).limit(limit).to_list()
        
        # Enhance with site information
        enhanced_predictions = []
        for prediction in predictions:
            site = await MiningSite.get(prediction.site_id)
            site_name = site.name if site else "Unknown Site"
            
            prediction_response = PredictionResponse(
                **prediction.dict(),
                site_name=site_name
            )
            enhanced_predictions.append(prediction_response)
        
        return enhanced_predictions
        
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve predictions")

@router.post("/analyze", response_model=PredictionResponse)
async def run_prediction_analysis(
    site_id: str,
    force_analysis: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Run ML prediction analysis for a specific site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Simple ML simulation for demo
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
            prediction_model_version="v2.1.0",
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
            data_points_used=100
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
        
        return PredictionResponse(
            **prediction.dict(),
            site_name=site.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running prediction analysis for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to run prediction analysis")

@router.get("/sites/{site_id}/latest", response_model=Optional[PredictionResponse])
async def get_latest_site_prediction(
    site_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the latest prediction for a specific site"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Get latest prediction
        latest_prediction = await Prediction.find(
            Prediction.site_id == site_id
        ).sort(-Prediction.timestamp).first()
        
        if not latest_prediction:
            return None
        
        return PredictionResponse(
            **latest_prediction.dict(),
            site_name=site.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest prediction for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get latest prediction")

@router.post("/pipeline/analyze")
async def run_ml_pipeline_analysis(
    site_id: str,
    drone_images_count: int = 0,
    sensor_devices_count: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Run comprehensive ML pipeline analysis with step-by-step processing"""
    try:
        # Verify site exists
        site = await MiningSite.get(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Validate inputs
        if drone_images_count == 0:
            raise HTTPException(status_code=400, detail="At least one drone image is required")
        
        if sensor_devices_count == 0:
            raise HTTPException(status_code=400, detail="Sensor data is required")
        
        # Simulate ML pipeline stages
        import asyncio
        
        stages = [
            {"id": "preprocessing", "name": "Image Preprocessing", "duration": 2.0},
            {"id": "dem_generation", "name": "DEM Generation", "duration": 3.0},
            {"id": "feature_extraction", "name": "Feature Extraction", "duration": 2.5},
            {"id": "sensor_validation", "name": "Sensor Validation", "duration": 1.5},
            {"id": "data_fusion", "name": "Data Fusion", "duration": 3.0},
            {"id": "ml_analysis", "name": "ML Analysis", "duration": 4.0},
            {"id": "final_prediction", "name": "Final Prediction", "duration": 1.5},
            {"id": "storage", "name": "Result Storage", "duration": 1.0}
        ]
        
        # Simulate processing time
        total_duration = sum(stage["duration"] for stage in stages)
        await asyncio.sleep(min(total_duration / 4, 5))  # Accelerated for demo
        
        # Generate realistic results
        import random
        
        # Determine risk level based on mock analysis
        risk_probability = random.uniform(0.1, 0.9)
        if risk_probability < 0.3:
            risk_level = RiskLevel.LOW
        elif risk_probability < 0.7:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        confidence = random.uniform(0.75, 0.95)
        
        # Generate detailed analysis results
        analysis_results = {
            "geological_features": {
                "fractures_detected": random.randint(8, 20),
                "major_joints": random.randint(2, 5),
                "rock_quality_index": random.uniform(2.0, 4.5)
            },
            "environmental_factors": {
                "rainfall_impact": "Low" if random.random() > 0.3 else "Moderate",
                "temperature_stability": "Stable",
                "seismic_activity": random.uniform(0.1, 0.8)
            },
            "sensor_data_quality": random.uniform(0.85, 0.99),
            "processing_stats": {
                "images_processed": drone_images_count,
                "sensors_analyzed": sensor_devices_count,
                "data_points": random.randint(5000, 15000),
                "processing_time_seconds": total_duration
            }
        }
        
        # Create comprehensive prediction
        prediction = Prediction(
            site_id=site_id,
            timestamp=datetime.utcnow(),
            risk_level=risk_level,
            probability=risk_probability,
            confidence=confidence,
            prediction_model_version="v2.3.0",
            contributing_factors=[
                {"factor": "Rock Quality", "weight": 0.35, "value": analysis_results["geological_features"]["rock_quality_index"]},
                {"factor": "Water Pressure", "weight": 0.25, "value": random.uniform(0.3, 0.8)},
                {"factor": "Seismic Activity", "weight": 0.15, "value": analysis_results["environmental_factors"]["seismic_activity"]},
                {"factor": "Structural Integrity", "weight": 0.25, "value": random.uniform(0.4, 0.9)}
            ],
            recommendations=[
                "Increase monitoring frequency for slope stability" if risk_level != RiskLevel.LOW else "Continue standard monitoring",
                "Install additional pore pressure sensors" if risk_level == RiskLevel.HIGH else "Maintain current sensor configuration",
                "Schedule geotechnical inspection within 48 hours" if risk_level == RiskLevel.HIGH else "Schedule routine inspection"
            ],
            data_points_used=analysis_results["processing_stats"]["data_points"],
            analysis_metadata=analysis_results
        )
        
        await prediction.insert()
        
        # Create alert if needed
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alert = Alert(
                type="prediction",
                severity="error" if risk_level == RiskLevel.CRITICAL else "warning",
                message=f"ML Pipeline detected {risk_level.value} risk at {site.name}",
                site_id=site_id,
                prediction_id=str(prediction.id)
            )
            await alert.insert()
        
        return {
            "prediction": PredictionResponse(
                **prediction.dict(),
                site_name=site.name
            ),
            "pipeline_summary": {
                "stages_completed": len(stages),
                "total_processing_time": total_duration,
                "data_quality_score": analysis_results["sensor_data_quality"]
            },
            "analysis_details": analysis_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running ML pipeline analysis for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to run ML pipeline analysis")

@router.get("/pipeline/status/{job_id}")
async def get_pipeline_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get ML pipeline processing status (for real-time updates)"""
    try:
        # Mock pipeline status - in real implementation, this would track actual job progress
        import random
        
        stages = [
            "Image Preprocessing", "DEM Generation", "Feature Extraction",
            "Sensor Validation", "Data Fusion", "ML Analysis",
            "Final Prediction", "Result Storage"
        ]
        
        # Simulate random progress
        completed_stages = random.randint(0, len(stages))
        
        return {
            "job_id": job_id,
            "status": "completed" if completed_stages == len(stages) else "processing",
            "progress_percentage": (completed_stages / len(stages)) * 100,
            "current_stage": stages[completed_stages - 1] if completed_stages > 0 else "Initializing",
            "completed_stages": completed_stages,
            "total_stages": len(stages),
            "estimated_completion": datetime.utcnow() + timedelta(minutes=5) if completed_stages < len(stages) else None
        }
        
    except Exception as e:
        logger.error(f"Error getting pipeline status for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pipeline status")

@router.get("/analytics/summary")
async def get_prediction_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get prediction analytics and trends"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get predictions in date range
        predictions = await Prediction.find(
            Prediction.timestamp >= start_date,
            Prediction.timestamp <= end_date
        ).to_list()
        
        # Calculate analytics
        total_predictions = len(predictions)
        high_risk_count = len([p for p in predictions if p.risk_level == RiskLevel.HIGH])
        medium_risk_count = len([p for p in predictions if p.risk_level == RiskLevel.MEDIUM])
        low_risk_count = len([p for p in predictions if p.risk_level == RiskLevel.LOW])
        
        # Calculate average confidence
        avg_confidence = sum(p.confidence for p in predictions) / total_predictions if total_predictions > 0 else 0
        
        # Get unique sites analyzed
        unique_sites = len(set(p.site_id for p in predictions))
        
        return {
            "period_days": days,
            "total_predictions": total_predictions,
            "risk_distribution": {
                "high": high_risk_count,
                "medium": medium_risk_count,
                "low": low_risk_count
            },
            "average_confidence": round(avg_confidence, 3),
            "sites_analyzed": unique_sites,
            "prediction_frequency": round(total_predictions / days, 2) if days > 0 else 0,
            "model_version": "v2.3.0"
        }
        
    except Exception as e:
        logger.error(f"Error getting prediction analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prediction analytics")