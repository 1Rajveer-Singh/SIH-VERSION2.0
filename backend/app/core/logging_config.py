"""
Logging Configuration
Structured logging with JSON format for production
"""

import logging
import logging.config
import sys
from typing import Dict, Any
import json
from datetime import datetime

from app.core.config import settings

class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'site_id'):
            log_entry["site_id"] = record.site_id
        
        return json.dumps(log_entry)

def setup_logging():
    """Configure application logging"""
    
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure logging
    if settings.ENVIRONMENT == "production":
        # Production: JSON structured logging
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": JSONFormatter,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": sys.stdout,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "json",
                    "filename": "logs/app.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                },
            },
            "loggers": {
                "": {  # Root logger
                    "handlers": ["console", "file"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "fastapi": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    else:
        # Development: Human-readable logging
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "simple": {
                    "format": "%(levelname)s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "detailed",
                    "stream": sys.stdout,
                },
            },
            "loggers": {
                "": {  # Root logger
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    
    logging.config.dictConfig(logging_config)
    
    # Configure third-party loggers
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.ENVIRONMENT} environment")

def get_logger(name: str) -> logging.Logger:
    """Get logger instance with name"""
    return logging.getLogger(name)

# Context manager for adding request context to logs
class LogContext:
    """Context manager for adding request context to logs"""
    
    def __init__(self, **kwargs):
        self.context = kwargs
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)