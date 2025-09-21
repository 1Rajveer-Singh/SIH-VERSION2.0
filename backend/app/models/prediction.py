"""
Prediction Models
Pydantic models for AI predictions and risk assessments
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

from app.models.user import PyObjectId

class PredictionFeature(BaseModel):
    """Individual feature in prediction explanation"""
    name: str
    importance: float = Field(..., ge=0, le=1)
    value: float
    description: Optional[str] = None

class PredictionExplanation(BaseModel):
    """Explanation of prediction results"""
    top_features: List[List[Any]] = Field(default=[], description="Top contributing features")
    feature_importance: Dict[str, float] = Field(default={})
    shap_values: Dict[str, Any] = Field(default={})
    image_gradcam_url: Optional[str] = None
    confidence_factors: Dict[str, float] = Field(default={})
    risk_factors: List[str] = Field(default=[])

class ModelMetadata(BaseModel):
    """Metadata about the ML model used"""
    model_version: str
    model_type: str
    training_date: Optional[datetime] = None
    feature_count: int
    performance_metrics: Dict[str, float] = Field(default={})

class GeoJSONGeometry(BaseModel):
    """GeoJSON geometry"""
    type: str
    coordinates: List[Any]

class GeoJSONFeature(BaseModel):
    """GeoJSON feature"""
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: Dict[str, Any] = Field(default={})

class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON feature collection"""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

class Prediction(BaseModel):
    """AI prediction result model"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    site_id: str
    risk_score: float = Field(..., ge=0, le=1, description="Risk probability score")
    risk_class: str = Field(..., pattern=r'^(Low|Medium|High|Critical)$')
    confidence: float = Field(..., ge=0, le=1, description="Model confidence")
    explanation: PredictionExplanation = Field(default_factory=PredictionExplanation)
    geojson_zone: Optional[GeoJSONFeatureCollection] = None
    model_metadata: ModelMetadata
    input_data_sources: List[str] = Field(default=[])
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processed_by: str
    is_archived: bool = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PredictionRequest(BaseModel):
    """Request for generating a prediction"""
    site_id: str
    include_explanation: bool = True
    include_risk_zone: bool = True
    model_version: Optional[str] = None

class PredictionResponse(BaseModel):
    """Response containing prediction results"""
    id: str
    site_id: str
    risk_score: float
    risk_class: str
    confidence: float
    explanation: Optional[PredictionExplanation] = None
    geojson_zone: Optional[GeoJSONFeatureCollection] = None
    timestamp: datetime
    processing_time_ms: float

class PredictionFilter(BaseModel):
    """Filter for querying predictions"""
    site_id: Optional[str] = None
    risk_class: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)
    limit: int = Field(50, ge=1, le=1000)
    skip: int = Field(0, ge=0)

class RiskSummary(BaseModel):
    """Summary of risk assessments"""
    site_id: str
    total_predictions: int
    risk_distribution: Dict[str, int]
    average_risk_score: float
    confidence_average: float
    last_prediction: Optional[datetime] = None
    trend: str  # "increasing", "decreasing", "stable"

class PredictionTrend(BaseModel):
    """Trend analysis of predictions over time"""
    site_id: str
    period: str  # "24h", "7d", "30d"
    data_points: List[Dict[str, Any]]
    trend_direction: str
    trend_strength: float
    anomalies: List[Dict[str, Any]] = Field(default=[])