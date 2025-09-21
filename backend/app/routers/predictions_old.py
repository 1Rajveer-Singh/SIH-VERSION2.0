"""
Predictions API endpoints
ML-based rockfall prediction analysis and management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.models.database import (
    Prediction, PredictionCreate, PredictionResponse,
    MiningSite, Device, SensorReading, Alert,
    RiskLevel, AlertSeverity
)
from app.routers.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Simulate ML analysis for demo purposes
async def _simulate_ml_analysis(sensor_data: List[SensorReading], site: MiningSite) -> dict:
    """Simulate ML prediction analysis (replace with actual ML model calls)"""
    import random
    
    # Analyze sensor data patterns
    vibration_readings = [r for r in sensor_data if r.sensor_type == "vibration"]
    pressure_readings = [r for r in sensor_data if r.sensor_type == "pressure"]
    tilt_readings = [r for r in sensor_data if r.sensor_type == "tilt"]
    
    # Calculate risk factors based on sensor data
    vibration_factor = 0.0
    if vibration_readings:
        avg_vibration = sum(r.value for r in vibration_readings) / len(vibration_readings)
        vibration_factor = min(1.0, avg_vibration / 10.0)  # Normalize to 0-1
    
    pressure_factor = 0.0
    if pressure_readings:
        avg_pressure = sum(r.value for r in pressure_readings) / len(pressure_readings)
        pressure_factor = min(1.0, avg_pressure / 1000.0)  # Normalize to 0-1
    
    tilt_factor = 0.0
    if tilt_readings:
        avg_tilt = sum(r.value for r in tilt_readings) / len(tilt_readings)
        tilt_factor = min(1.0, avg_tilt / 5.0)  # Normalize to 0-1
    
    # Calculate overall risk
    overall_risk = (vibration_factor * 0.4 + pressure_factor * 0.3 + tilt_factor * 0.3)
    
    # Add some randomization for demonstration
    overall_risk += random.uniform(-0.1, 0.1)
    overall_risk = max(0.0, min(1.0, overall_risk))
    
    # Determine risk level
    if overall_risk < 0.25:
        risk_level = RiskLevel.LOW
    elif overall_risk < 0.5:
        risk_level = RiskLevel.MEDIUM
    elif overall_risk < 0.75:
        risk_level = RiskLevel.HIGH
    else:
        risk_level = RiskLevel.CRITICAL
    
    # Generate realistic contributing factors
    contributing_factors = []
    if vibration_factor > 0.3:
        contributing_factors.append({"factor": "Seismic Activity", "weight": vibration_factor})
    if pressure_factor > 0.3:
        contributing_factors.append({"factor": "Ground Pressure", "weight": pressure_factor})
    if tilt_factor > 0.3:
        contributing_factors.append({"factor": "Slope Instability", "weight": tilt_factor})
    
    # Add weather factor (simulated)
    weather_factor = random.uniform(0.1, 0.4)
    contributing_factors.append({"factor": "Weather Conditions", "weight": weather_factor})
    
    # Generate recommendations based on risk level
    recommendations = []
    if risk_level == RiskLevel.LOW:
        recommendations = ["Continue normal monitoring", "Regular equipment maintenance"]
    elif risk_level == RiskLevel.MEDIUM:
        recommendations = ["Increase monitoring frequency", "Review safety protocols", "Check equipment calibration"]
    elif risk_level == RiskLevel.HIGH:
        recommendations = ["Implement enhanced safety measures", "Consider evacuation planning", "Increase inspection frequency", "Alert emergency services"]
    else:  # CRITICAL
        recommendations = ["IMMEDIATE EVACUATION", "Stop all operations", "Emergency response activation", "Notify authorities"]
    
    return {
        "risk_level": risk_level,
        "probability": overall_risk,
        "confidence": random.uniform(0.75, 0.95),
        "model_version": "v2.1.0",
        "contributing_factors": contributing_factors,
        "recommendations": recommendations,
        "weather_conditions": {
            "temperature": random.uniform(-5, 35),
            "humidity": random.uniform(30, 90),
            "wind_speed": random.uniform(0, 25),
            "precipitation": random.uniform(0, 10)
        },
        "geological_factors": {
            "rock_stability": random.uniform(0.5, 1.0),
            "soil_moisture": random.uniform(0.1, 0.8),
            "slope_angle": random.uniform(15, 45)
        }
    }

@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    site_id: Optional[str] = None,
    risk_level: Optional[RiskLevel] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get predictions with optional filtering"""
    try:
        query = Prediction.find()
        
        if site_id:
            query = query.find(Prediction.site_id == site_id)
        
        if risk_level:
            query = query.find(Prediction.risk_level == risk_level)
        
        if start_date:
            query = query.find(Prediction.timestamp >= start_date)
        
        if end_date:
            query = query.find(Prediction.timestamp <= end_date)
        
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
        
        # Check for recent prediction (within last hour) unless forced
        if not force_analysis:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_prediction = await Prediction.find(
                Prediction.site_id == site_id,
                Prediction.timestamp >= one_hour_ago
            ).first()
            
            if recent_prediction:
                raise HTTPException(
                    status_code=429,
                    detail=f"Recent prediction exists. Use force_analysis=true to override."
                )
        
        # Get devices for this site
        devices = await Device.find(Device.site_id == site_id).to_list()
        if not devices:
            raise HTTPException(status_code=400, detail="No devices found for this site")
        
        # Get recent sensor data (last 24 hours)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        sensor_data = []
        
        for device in devices:
            readings = await SensorReading.find(
                SensorReading.device_id == device.device_id,
                SensorReading.timestamp >= twenty_four_hours_ago
            ).to_list()
            sensor_data.extend(readings)
        
        if not sensor_data:
            raise HTTPException(status_code=400, detail="Insufficient sensor data for analysis")
        
        # Simulate ML analysis (in production, this would call your ML models)
        risk_analysis = await _simulate_ml_analysis(sensor_data, site)
        
        # Create prediction record
        prediction = Prediction(
            site_id=site_id,
            timestamp=datetime.utcnow(),
            risk_level=risk_analysis["risk_level"],
            probability=risk_analysis["probability"],
            confidence=risk_analysis["confidence"],
            model_version=risk_analysis["model_version"],
            contributing_factors=risk_analysis["contributing_factors"],
            recommendations=risk_analysis["recommendations"],
            data_points_used=len(sensor_data),
            weather_conditions=risk_analysis.get("weather_conditions"),
            geological_factors=risk_analysis.get("geological_factors")
        )
        
        await prediction.insert()
        
        # Create alert if high risk
        if prediction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            severity = AlertSeverity.CRITICAL if prediction.risk_level == RiskLevel.CRITICAL else AlertSeverity.WARNING
            
            alert = Alert(
                type="prediction",
                severity=severity,
                message=f"High risk prediction for {site.name}: {prediction.risk_level.value} ({prediction.probability:.1%} probability)",
                site_id=site_id,
                prediction_id=str(prediction.id),
                metadata={
                    "risk_level": prediction.risk_level.value,
                    "probability": prediction.probability,
                    "confidence": prediction.confidence,
                    "model_version": prediction.model_version
                }
            )
            await alert.insert()
        
        logger.info(f"Prediction analysis completed for site {site_id}: {prediction.risk_level.value}")
        
        return PredictionResponse(
            **prediction.dict(),
            site_name=site.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running prediction analysis for site {site_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to run prediction analysis")
except ImportError as e:
    print(f"ML models not available: {e}")
    ML_MODELS_AVAILABLE = False

from .auth import get_current_user

router = APIRouter()

class PredictionRequest(BaseModel):
    site_id: str
    sensor_ids: List[str]
    prediction_type: str  # "rockfall", "landslide", "general"
    time_horizon: int  # hours to predict ahead

class RiskLevel(BaseModel):
    level: str  # "low", "medium", "high", "critical"
    probability: float
    confidence: float

class PredictionResponse(BaseModel):
    id: str
    site_id: str
    sensor_ids: List[str]
    prediction_type: str
    timestamp: datetime
    risk_level: RiskLevel
    factors: Dict[str, float]
    recommendations: List[str]
    validity_period: int  # hours

class ModelPerformance(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    last_trained: datetime

# Mock predictions database
PREDICTIONS_DB = {}

# ML Model performance metrics
MODEL_PERFORMANCE = {
    "rockfall": ModelPerformance(
        accuracy=0.94,
        precision=0.91,
        recall=0.89,
        f1_score=0.90,
        last_trained=datetime(2024, 1, 1)
    ),
    "landslide": ModelPerformance(
        accuracy=0.88,
        precision=0.85,
        recall=0.87,
        f1_score=0.86,
        last_trained=datetime(2024, 1, 1)
    ),
    "general": ModelPerformance(
        accuracy=0.92,
        precision=0.90,
        recall=0.91,
        f1_score=0.905,
        last_trained=datetime(2024, 1, 1)
    )
}

def simulate_ml_prediction(sensor_data: List[str], prediction_type: str, site_id: str) -> Dict:
    """
    Use actual ML model prediction or fall back to simulation
    """
    
    if ML_MODELS_AVAILABLE:
        try:
            # Create mock sensor data for ML model
            mock_sensor_data = [{
                'vibration_x': random.uniform(0.001, 0.05),
                'vibration_y': random.uniform(0.001, 0.05),
                'vibration_z': random.uniform(0.001, 0.05),
                'tilt_x': random.uniform(-2, 2),
                'tilt_y': random.uniform(-2, 2),
                'temperature': random.uniform(10, 25),
                'wind_speed': random.uniform(0, 20),
                'wind_direction': random.uniform(0, 360),
                'precipitation': max(0, random.gauss(0, 2)),
                'atmospheric_pressure': random.uniform(1000, 1030),
                'humidity': random.uniform(30, 80),
                'seismic_activity': abs(random.gauss(0, 0.1)),
                'displacement_x': random.gauss(0, 0.001),
                'displacement_y': random.gauss(0, 0.001),
                'displacement_z': random.gauss(0, 0.0005)
            }]
            
            # Get ML prediction
            ml_result = predict_rockfall_risk(mock_sensor_data)
            
            # Get explanation
            explanation = explain_prediction(mock_sensor_data[0], ml_result)
            
            # Combine results
            result = {
                'risk_level': ml_result['risk_level'],
                'factors': ml_result['factors'],
                'recommendations': ml_result['recommendations'],
                'explanation': explanation
            }
            
            return result
            
        except Exception as e:
            print(f"ML prediction failed, falling back to simulation: {e}")
            # Fall back to simulation if ML fails
            pass
    
    # Simulate complex risk calculation (fallback)
    base_risk = random.uniform(0.1, 0.9)
    
    # Adjust risk based on prediction type
    if prediction_type == "rockfall":
        # Higher base risk for rockfall
        base_risk = min(0.95, base_risk + random.uniform(0.1, 0.3))
    elif prediction_type == "landslide":
        # Moderate adjustment
        base_risk = min(0.95, base_risk + random.uniform(0.05, 0.2))
    
    # Determine risk level
    if base_risk < 0.3:
        risk_level = "low"
    elif base_risk < 0.6:
        risk_level = "medium"
    elif base_risk < 0.8:
        risk_level = "high"
    else:
        risk_level = "critical"
    
    # Generate contributing factors
    factors = {
        "vibration_intensity": round(random.uniform(0.1, 1.0), 3),
        "slope_stability": round(random.uniform(0.2, 0.9), 3),
        "weather_conditions": round(random.uniform(0.1, 0.8), 3),
        "geological_stress": round(random.uniform(0.15, 0.85), 3),
        "historical_patterns": round(random.uniform(0.2, 0.7), 3)
    }
    
    # Generate recommendations based on risk level
    recommendations = []
    if risk_level in ["high", "critical"]:
        recommendations.extend([
            "Evacuate personnel from high-risk zones immediately",
            "Increase monitoring frequency to real-time",
            "Deploy additional sensors in affected areas"
        ])
    elif risk_level == "medium":
        recommendations.extend([
            "Restrict access to potentially affected areas",
            "Increase monitoring frequency",
            "Prepare evacuation procedures"
        ])
    else:
        recommendations.extend([
            "Continue normal monitoring procedures",
            "Review sensor data for anomalies"
        ])
    
    if prediction_type == "rockfall":
        recommendations.append("Install protective barriers if not present")
    elif prediction_type == "landslide":
        recommendations.append("Monitor drainage systems and water accumulation")
    
    return {
        "risk_level": {
            "level": risk_level,
            "probability": round(base_risk, 3),
            "confidence": round(random.uniform(0.7, 0.95), 3)
        },
        "factors": factors,
        "recommendations": recommendations[:4]  # Limit recommendations
    }

@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    prediction_request: PredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate new prediction using ML models"""
    
    # Simulate ML model processing
    ml_result = simulate_ml_prediction(
        prediction_request.sensor_ids,
        prediction_request.prediction_type,
        prediction_request.site_id
    )
    
    prediction_id = f"pred-{len(PREDICTIONS_DB) + 1:06d}"
    
    prediction = {
        "id": prediction_id,
        "site_id": prediction_request.site_id,
        "sensor_ids": prediction_request.sensor_ids,
        "prediction_type": prediction_request.prediction_type,
        "timestamp": datetime.utcnow(),
        "risk_level": ml_result["risk_level"],
        "factors": ml_result["factors"],
        "recommendations": ml_result["recommendations"],
        "validity_period": prediction_request.time_horizon
    }
    
    PREDICTIONS_DB[prediction_id] = prediction
    
    # If high risk, this would trigger alerts in real system
    if ml_result["risk_level"]["level"] in ["high", "critical"]:
        # Log for alert system
        print(f"High risk prediction generated: {prediction_id}")
    
    return PredictionResponse(**prediction)

@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    hours: int = Query(24, description="Hours of predictions to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    """Get predictions with optional filtering"""
    
    # Filter by time
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    predictions = [
        p for p in PREDICTIONS_DB.values() 
        if p["timestamp"] >= cutoff_time
    ]
    
    # Apply filters
    if site_id:
        predictions = [p for p in predictions if p["site_id"] == site_id]
    
    if risk_level:
        predictions = [p for p in predictions if p["risk_level"]["level"] == risk_level]
    
    # Sort by timestamp (newest first)
    predictions.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return [PredictionResponse(**pred) for pred in predictions[:50]]  # Limit results

@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(prediction_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific prediction by ID"""
    prediction = PREDICTIONS_DB.get(prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return PredictionResponse(**prediction)

@router.get("/model/performance")
async def get_model_performance(
    model_type: Optional[str] = Query(None, description="Model type"),
    current_user: dict = Depends(get_current_user)
):
    """Get ML model performance metrics"""
    
    if model_type and model_type in MODEL_PERFORMANCE:
        return {
            "model_type": model_type,
            "performance": MODEL_PERFORMANCE[model_type]
        }
    
    return {
        "all_models": MODEL_PERFORMANCE
    }

@router.post("/batch")
async def create_batch_predictions(
    requests: List[PredictionRequest],
    current_user: dict = Depends(get_current_user)
):
    """Create multiple predictions in batch"""
    
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="Batch size limited to 10 predictions")
    
    results = []
    for request in requests:
        # Simulate ML processing for each request
        ml_result = simulate_ml_prediction(
            request.sensor_ids,
            request.prediction_type,
            request.site_id
        )
        
        prediction_id = f"pred-{len(PREDICTIONS_DB) + len(results) + 1:06d}"
        
        prediction = {
            "id": prediction_id,
            "site_id": request.site_id,
            "sensor_ids": request.sensor_ids,
            "prediction_type": request.prediction_type,
            "timestamp": datetime.utcnow(),
            "risk_level": ml_result["risk_level"],
            "factors": ml_result["factors"],
            "recommendations": ml_result["recommendations"],
            "validity_period": request.time_horizon
        }
        
        PREDICTIONS_DB[prediction_id] = prediction
        results.append(PredictionResponse(**prediction))
    
    return {
        "batch_size": len(results),
        "predictions": results
    }

@router.get("/analytics/trends")
async def get_prediction_trends(
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    days: int = Query(7, description="Days of data for trend analysis"),
    current_user: dict = Depends(get_current_user)
):
    """Get prediction trends and analytics"""
    
    # In real system, this would analyze historical prediction data
    # For demo, generate mock trend data
    
    trend_data = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days-i-1)
        
        # Generate mock daily statistics
        daily_stats = {
            "date": date.date(),
            "total_predictions": random.randint(10, 50),
            "risk_distribution": {
                "low": random.randint(5, 20),
                "medium": random.randint(3, 15),
                "high": random.randint(1, 8),
                "critical": random.randint(0, 3)
            },
            "accuracy_score": round(random.uniform(0.85, 0.95), 3),
            "average_confidence": round(random.uniform(0.75, 0.90), 3)
        }
        trend_data.append(daily_stats)
    
    return {
        "site_id": site_id,
        "period_days": days,
        "trends": trend_data,
        "summary": {
            "total_predictions": sum(day["total_predictions"] for day in trend_data),
            "average_accuracy": round(sum(day["accuracy_score"] for day in trend_data) / len(trend_data), 3),
            "high_risk_incidents": sum(day["risk_distribution"]["high"] + day["risk_distribution"]["critical"] for day in trend_data)
        }
    }

@router.post("/retrain")
async def trigger_model_retraining(
    model_type: str = Query(..., description="Model type to retrain"),
    current_user: dict = Depends(get_current_user)
):
    """Trigger ML model retraining (admin only)"""
    
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if model_type not in MODEL_PERFORMANCE:
        raise HTTPException(status_code=400, detail="Invalid model type")
    
    # In real system, this would trigger actual model retraining
    # For demo, just update the last_trained timestamp
    MODEL_PERFORMANCE[model_type].last_trained = datetime.utcnow()
    
    return {
        "message": f"Model retraining initiated for {model_type}",
        "model_type": model_type,
        "estimated_completion": datetime.utcnow() + timedelta(hours=2),
        "status": "training_started"
    }