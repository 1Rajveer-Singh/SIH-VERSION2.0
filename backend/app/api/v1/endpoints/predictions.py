"""
Prediction Endpoints
AI-powered rockfall prediction and risk assessment
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
import logging
from datetime import datetime, timedelta
from bson import ObjectId

from app.models.prediction import (
    Prediction, PredictionRequest, PredictionResponse, PredictionFilter,
    RiskSummary, PredictionTrend
)
from app.models.user import User
from app.core.auth import get_current_active_user, require_engineer
from app.core.database import get_database
from app.services.prediction_service import PredictionService
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def generate_prediction(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_engineer)
):
    """
    Generate AI-powered rockfall risk prediction
    
    - **site_id**: ID of the mining site
    - **include_explanation**: Include feature explanations (default: True)
    - **include_risk_zone**: Include geospatial risk zones (default: True)
    - **model_version**: Specific model version to use (optional)
    
    Requires engineer-level access or higher
    """
    try:
        prediction_service = PredictionService()
        
        # Generate prediction
        prediction = await prediction_service.generate_prediction(
            site_id=request.site_id,
            include_explanation=request.include_explanation,
            include_risk_zone=request.include_risk_zone,
            model_version=request.model_version
        )
        
        # Check if alert should be triggered (background task)
        if prediction.risk_class in ["High", "Critical"]:
            alert_service = AlertService()
            background_tasks.add_task(
                alert_service.evaluate_prediction_alerts,
                prediction,
                current_user.id
            )
        
        logger.info(
            f"Generated prediction for site {request.site_id} by user {current_user.username}: "
            f"Risk={prediction.risk_class} (score={prediction.risk_score:.3f})"
        )
        
        return PredictionResponse(
            id=str(prediction.id),
            site_id=prediction.site_id,
            risk_score=prediction.risk_score,
            risk_class=prediction.risk_class,
            confidence=prediction.confidence,
            explanation=prediction.explanation if request.include_explanation else None,
            geojson_zone=prediction.geojson_zone if request.include_risk_zone else None,
            timestamp=prediction.timestamp,
            processing_time_ms=prediction.processing_time_ms or 0
        )
        
    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction generation failed: {str(e)}"
        )

@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    site_id: Optional[str] = None,
    risk_class: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_confidence: Optional[float] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get predictions with filtering options
    
    - **site_id**: Filter by site ID
    - **risk_class**: Filter by risk class (Low, Medium, High, Critical)
    - **start_date**: Start date for time range filter
    - **end_date**: End date for time range filter
    - **min_confidence**: Minimum confidence threshold
    - **limit**: Maximum number of results (1-1000)
    - **skip**: Number of results to skip for pagination
    """
    try:
        db = get_database()
        predictions_collection = db["predictions"]
        
        # Build query filter
        query_filter = {}
        
        if site_id:
            query_filter["site_id"] = site_id
        
        if risk_class:
            query_filter["risk_class"] = risk_class
        
        if start_date or end_date:
            timestamp_filter = {}
            if start_date:
                timestamp_filter["$gte"] = start_date
            if end_date:
                timestamp_filter["$lte"] = end_date
            query_filter["timestamp"] = timestamp_filter
        
        if min_confidence:
            query_filter["confidence"] = {"$gte": min_confidence}
        
        # Query database
        cursor = predictions_collection.find(query_filter).sort("timestamp", -1).skip(skip).limit(limit)
        predictions = await cursor.to_list(length=limit)
        
        # Convert to response models
        response_predictions = []
        for pred in predictions:
            response_predictions.append(
                PredictionResponse(
                    id=str(pred["_id"]),
                    site_id=pred["site_id"],
                    risk_score=pred["risk_score"],
                    risk_class=pred["risk_class"],
                    confidence=pred["confidence"],
                    explanation=pred.get("explanation"),
                    geojson_zone=pred.get("geojson_zone"),
                    timestamp=pred["timestamp"],
                    processing_time_ms=pred.get("processing_time_ms", 0)
                )
            )
        
        logger.info(f"Retrieved {len(response_predictions)} predictions for user {current_user.username}")
        
        return response_predictions
        
    except Exception as e:
        logger.error(f"Failed to retrieve predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve predictions"
        )

@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get specific prediction by ID
    
    - **prediction_id**: Unique prediction identifier
    """
    try:
        if not ObjectId.is_valid(prediction_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid prediction ID format"
            )
        
        db = get_database()
        predictions_collection = db["predictions"]
        
        prediction = await predictions_collection.find_one({"_id": ObjectId(prediction_id)})
        
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction not found"
            )
        
        return PredictionResponse(
            id=str(prediction["_id"]),
            site_id=prediction["site_id"],
            risk_score=prediction["risk_score"],
            risk_class=prediction["risk_class"],
            confidence=prediction["confidence"],
            explanation=prediction.get("explanation"),
            geojson_zone=prediction.get("geojson_zone"),
            timestamp=prediction["timestamp"],
            processing_time_ms=prediction.get("processing_time_ms", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve prediction {prediction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction"
        )

@router.get("/sites/{site_id}/summary", response_model=RiskSummary)
async def get_site_risk_summary(
    site_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get risk summary for a specific site
    
    - **site_id**: Site identifier
    - **days**: Number of days to include in summary (default: 30)
    """
    try:
        db = get_database()
        predictions_collection = db["predictions"]
        
        # Date range for analysis
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Aggregation pipeline for summary statistics
        pipeline = [
            {
                "$match": {
                    "site_id": site_id,
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_predictions": {"$sum": 1},
                    "avg_risk_score": {"$avg": "$risk_score"},
                    "avg_confidence": {"$avg": "$confidence"},
                    "risk_distribution": {
                        "$push": "$risk_class"
                    },
                    "last_prediction": {"$max": "$timestamp"}
                }
            }
        ]
        
        result = await predictions_collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            # No predictions found
            return RiskSummary(
                site_id=site_id,
                total_predictions=0,
                risk_distribution={"Low": 0, "Medium": 0, "High": 0, "Critical": 0},
                average_risk_score=0.0,
                confidence_average=0.0,
                last_prediction=None,
                trend="stable"
            )
        
        data = result[0]
        
        # Calculate risk distribution
        risk_distribution = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for risk_class in data["risk_distribution"]:
            risk_distribution[risk_class] = risk_distribution.get(risk_class, 0) + 1
        
        # Calculate trend (simplified - based on recent vs older predictions)
        trend = await _calculate_risk_trend(predictions_collection, site_id, days)
        
        return RiskSummary(
            site_id=site_id,
            total_predictions=data["total_predictions"],
            risk_distribution=risk_distribution,
            average_risk_score=round(data["avg_risk_score"], 3),
            confidence_average=round(data["avg_confidence"], 3),
            last_prediction=data["last_prediction"],
            trend=trend
        )
        
    except Exception as e:
        logger.error(f"Failed to generate risk summary for site {site_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate risk summary"
        )

@router.get("/sites/{site_id}/trend", response_model=PredictionTrend)
async def get_prediction_trend(
    site_id: str,
    period: str = "7d",
    current_user: User = Depends(get_current_active_user)
):
    """
    Get prediction trend analysis for a site
    
    - **site_id**: Site identifier
    - **period**: Time period ("24h", "7d", "30d")
    """
    try:
        # Parse period
        period_days = {"24h": 1, "7d": 7, "30d": 30}.get(period, 7)
        
        db = get_database()
        predictions_collection = db["predictions"]
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Get predictions for trend analysis
        predictions = await predictions_collection.find({
            "site_id": site_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).sort("timestamp", 1).to_list(length=None)
        
        # Generate trend data points
        data_points = []
        for pred in predictions:
            data_points.append({
                "timestamp": pred["timestamp"],
                "risk_score": pred["risk_score"],
                "risk_class": pred["risk_class"],
                "confidence": pred["confidence"]
            })
        
        # Calculate trend direction and strength
        trend_direction, trend_strength = _analyze_trend(data_points)
        
        # Detect anomalies
        anomalies = _detect_anomalies(data_points)
        
        return PredictionTrend(
            site_id=site_id,
            period=period,
            data_points=data_points,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            anomalies=anomalies
        )
        
    except Exception as e:
        logger.error(f"Failed to generate trend analysis for site {site_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate trend analysis"
        )

async def _calculate_risk_trend(collection, site_id: str, days: int) -> str:
    """Calculate overall risk trend for a site"""
    try:
        # Split period into two halves for comparison
        end_date = datetime.utcnow()
        mid_date = end_date - timedelta(days=days//2)
        start_date = end_date - timedelta(days=days)
        
        # Get average risk for each half
        recent_avg = await collection.aggregate([
            {"$match": {"site_id": site_id, "timestamp": {"$gte": mid_date, "$lte": end_date}}},
            {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}}
        ]).to_list(length=1)
        
        older_avg = await collection.aggregate([
            {"$match": {"site_id": site_id, "timestamp": {"$gte": start_date, "$lt": mid_date}}},
            {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}}
        ]).to_list(length=1)
        
        if not recent_avg or not older_avg:
            return "stable"
        
        recent_risk = recent_avg[0]["avg_risk"]
        older_risk = older_avg[0]["avg_risk"]
        
        change = recent_risk - older_risk
        
        if abs(change) < 0.05:  # Less than 5% change
            return "stable"
        elif change > 0:
            return "increasing"
        else:
            return "decreasing"
            
    except Exception:
        return "stable"

def _analyze_trend(data_points: List[dict]) -> tuple:
    """Analyze trend direction and strength"""
    if len(data_points) < 2:
        return "stable", 0.0
    
    # Simple linear trend analysis
    risk_scores = [point["risk_score"] for point in data_points]
    
    # Calculate slope using first and last points
    if len(risk_scores) >= 2:
        slope = (risk_scores[-1] - risk_scores[0]) / len(risk_scores)
        
        if abs(slope) < 0.01:
            return "stable", abs(slope)
        elif slope > 0:
            return "increasing", abs(slope)
        else:
            return "decreasing", abs(slope)
    
    return "stable", 0.0

def _detect_anomalies(data_points: List[dict]) -> List[dict]:
    """Detect anomalies in prediction data"""
    if len(data_points) < 5:
        return []
    
    anomalies = []
    risk_scores = [point["risk_score"] for point in data_points]
    
    # Calculate mean and standard deviation
    mean_risk = sum(risk_scores) / len(risk_scores)
    variance = sum((x - mean_risk) ** 2 for x in risk_scores) / len(risk_scores)
    std_dev = variance ** 0.5
    
    # Detect outliers (> 2 standard deviations)
    for i, point in enumerate(data_points):
        if abs(point["risk_score"] - mean_risk) > 2 * std_dev:
            anomalies.append({
                "timestamp": point["timestamp"],
                "risk_score": point["risk_score"],
                "deviation": abs(point["risk_score"] - mean_risk),
                "type": "outlier"
            })
    
    return anomalies