"""
Application Configuration
Environment-based settings using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    PROJECT_NAME: str = "Rockfall Prediction System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "rockfall_prediction"
    
    # AWS/S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-west-2"
    S3_BUCKET_NAME: str = "rockfall-data"
    S3_ENDPOINT_URL: Optional[str] = None  # For MinIO compatibility
    
    # Notification Services
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "alerts@minesafety.ai"
    
    # Redis Configuration (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://minesafety.ai"
    ]
    
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "api.minesafety.ai"
    ]
    
    # AI/ML Configuration
    MODEL_STORAGE_PATH: str = "./models"
    MODEL_VERSION: str = "1.2.0"
    PREDICTION_BATCH_SIZE: int = 32
    MAX_PREDICTION_HISTORY_DAYS: int = 365
    
    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".tiff", ".tif"]
    ALLOWED_DEM_EXTENSIONS: List[str] = [".tif", ".tiff", ".asc", ".dem"]
    
    # Monitoring
    ENABLE_PROMETHEUS: bool = True
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Alert Configuration
    CRITICAL_RISK_THRESHOLD: float = 0.8
    HIGH_RISK_THRESHOLD: float = 0.6
    MEDIUM_RISK_THRESHOLD: float = 0.4
    
    MAX_ALERT_RETRIES: int = 3
    ALERT_RETRY_DELAY_SECONDS: int = 300  # 5 minutes
    
    # Sensor Configuration
    SENSOR_DATA_RETENTION_DAYS: int = 1095  # 3 years
    SENSOR_ANOMALY_THRESHOLD: float = 3.0  # Standard deviations
    
    # Geospatial Configuration
    DEFAULT_COORDINATE_SYSTEM: str = "EPSG:4326"
    DEFAULT_DEM_RESOLUTION: float = 1.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()