"""
Database Connection and Configuration
MongoDB async client with connection pooling
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    """MongoDB database manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    database = None

# Global database instance
database = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        # Create MongoDB client with connection pooling
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=2,
            maxIdleTimeMS=30000,
            waitQueueMultiple=10,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
        )
        
        # Test the connection
        await database.client.admin.command('ping')
        
        # Get database instance
        database.database = database.client[settings.DATABASE_NAME]
        
        logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return database.database

async def init_database():
    """Initialize database connection"""
    await connect_to_mongo()
    
    # Ensure collections exist with proper indexes
    await ensure_collections_and_indexes()

async def ensure_collections_and_indexes():
    """Ensure all collections exist with proper indexes"""
    db = get_database()
    
    # Collection configurations
    collections_config = {
        "users": {
            "indexes": [
                [("username", 1)],
                [("email", 1)],
                [("role", 1)],
                [("created_at", -1)]
            ]
        },
        "sites": {
            "indexes": [
                [("site_id", 1)],
                [("location", "2dsphere")],
                [("status", 1)]
            ]
        },
        "dem_collection": {
            "indexes": [
                [("site_id", 1)],
                [("created_at", -1)],
                [("processing_status", 1)]
            ]
        },
        "drone_images": {
            "indexes": [
                [("site_id", 1)],
                [("geotag", "2dsphere")],
                [("created_at", -1)]
            ]
        },
        "environmental_data": {
            "indexes": [
                [("site_id", 1)],
                [("timestamp", -1)],
                [("site_id", 1), ("timestamp", -1)]
            ]
        },
        "predictions": {
            "indexes": [
                [("site_id", 1)],
                [("timestamp", -1)],
                [("risk_class", 1)],
                [("site_id", 1), ("timestamp", -1)]
            ]
        },
        "alerts": {
            "indexes": [
                [("site_id", 1)],
                [("status", 1)],
                [("alert_type", 1)],
                [("created_at", -1)]
            ]
        },
        "ml_models": {
            "indexes": [
                [("name", 1), ("version", 1)],
                [("is_active", 1)],
                [("deployment_status", 1)]
            ]
        }
    }
    
    # Create time-series collection for sensor data
    try:
        await db.create_collection(
            "sensor_timeseries",
            timeseries={
                "timeField": "time",
                "metaField": "device_id",
                "granularity": "minutes"
            }
        )
        logger.info("Created time-series collection: sensor_timeseries")
    except Exception as e:
        logger.info(f"Time-series collection may already exist: {e}")
    
    # Create regular collections and indexes
    for collection_name, config in collections_config.items():
        collection = db[collection_name]
        
        # Create indexes
        for index_spec in config["indexes"]:
            try:
                if len(index_spec) == 1 and isinstance(index_spec[0], tuple):
                    field, direction = index_spec[0]
                    if direction == "2dsphere":
                        await collection.create_index([(field, "2dsphere")])
                    else:
                        await collection.create_index([(field, direction)])
                else:
                    # Compound index
                    index_fields = []
                    for field, direction in index_spec:
                        if direction == "2dsphere":
                            index_fields.append((field, "2dsphere"))
                        else:
                            index_fields.append((field, direction))
                    await collection.create_index(index_fields)
                    
            except Exception as e:
                logger.warning(f"Could not create index for {collection_name}: {e}")
    
    logger.info("Database collections and indexes ensured")