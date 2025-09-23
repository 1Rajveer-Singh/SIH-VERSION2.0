"""
Model Training Models for MongoDB
Defines data structures for model training operations
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class TrainingConfigRequest(BaseModel):
    """Training configuration from frontend"""
    temporal_model: Dict[str, Any] = Field(
        default={
            "type": "LSTM",
            "enabled": True
        }
    )
    spatial_model: Dict[str, Any] = Field(
        default={
            "type": "CNN", 
            "enabled": True
        }
    )
    fusion_model: Dict[str, Any] = Field(
        default={
            "type": "MLP",
            "enabled": True
        }
    )
    advanced_options: Dict[str, bool] = Field(
        default={
            "ensemble_methods": False,
            "bayesian_uncertainty": False,
            "gradient_boosting": False
        }
    )
    output_types: Dict[str, bool] = Field(
        default={
            "risk_probability": True,
            "lead_time": True,
            "confidence_score": True,
            "uncertainty_estimation": False
        }
    )
    temporal_features: Dict[str, bool] = Field(
        default={
            "displacement": True,
            "velocity": True,
            "pore_pressure": True,
            "rainfall": True,
            "blast_vibrations": False,
            "seismic_activity": True,
            "groundwater_level": False
        }
    )
    spatial_features: Dict[str, bool] = Field(
        default={
            "drone_imagery": True,
            "crack_detection": True,
            "dem_changes": True,
            "lidar_point_clouds": False,
            "surface_roughness": False,
            "vegetation_coverage": False
        }
    )
    training_window: Dict[str, Any] = Field(
        default={
            "value": 7,
            "unit": "days"
        }
    )
    prediction_horizon: Dict[str, int] = Field(
        default={
            "short_term": 24,
            "long_term": 48
        }
    )
    hyperparameters: Dict[str, Any] = Field(
        default={
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100,
            "dropout_rate": 0.2,
            "sequence_length": 96,
            "hidden_dimensions": 128,
            "attention_heads": 8
        }
    )
    dataset: Literal["historical", "synthetic", "augmented", "combined"] = "historical"

    class Config:
        json_encoders = {ObjectId: str}


class TrainingMetrics(BaseModel):
    """Training metrics for a single epoch"""
    epoch: int
    train_loss: float
    val_loss: float
    accuracy: float
    pr_auc: float
    lead_time_mae: float
    confidence_calibration: float
    temporal_loss: Optional[float] = None
    spatial_loss: Optional[float] = None
    fusion_loss: Optional[float] = None


class TrainingJob(BaseModel):
    """Training job document structure"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["queued", "preparing", "training", "completed", "failed", "cancelled"] = "queued"
    progress: float = 0.0
    current_epoch: int = 0
    total_epochs: int = 100
    
    # Configuration
    config: TrainingConfigRequest
    
    # Training state
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Results and monitoring
    metrics: List[TrainingMetrics] = []
    logs: List[str] = []
    error_message: Optional[str] = None
    
    # Model artifacts
    model_paths: Dict[str, str] = {}
    performance_summary: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TrainingStatusResponse(BaseModel):
    """Training status response"""
    job_id: str
    status: str
    progress: float
    current_epoch: int
    total_epochs: int
    estimated_time_remaining: Optional[int] = None
    latest_metrics: Optional[TrainingMetrics] = None
    logs: List[str]
    error_message: Optional[str] = None


class ModelDeploymentRequest(BaseModel):
    """Model deployment request"""
    job_id: str
    deployment_name: str
    description: Optional[str] = None
    replace_current: bool = False


class ModelPerformanceReport(BaseModel):
    """Comprehensive model performance report"""
    job_id: str
    training_summary: Dict[str, Any]
    model_architecture: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    feature_importance: Dict[str, float]
    validation_results: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)