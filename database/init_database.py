"""
Database initialization script for Rockfall Prediction System
Creates MongoDB collections, indexes, and initial configuration
"""

import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, GEO2D, TEXT
from pymongo.errors import CollectionInvalid
import logging
from typing import Dict, Any

from schemas.models import COLLECTIONS, INDEXES, TIMESERIES_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Handles MongoDB database initialization"""
    
    def __init__(self, connection_string: str = None):
        """Initialize database connection"""
        self.connection_string = connection_string or os.getenv(
            "MONGODB_URL", 
            "mongodb://localhost:27017"
        )
        self.database_name = os.getenv("DATABASE_NAME", "rockfall_prediction")
        self.client = None
        self.db = None
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def create_collections(self):
        """Create all required collections"""
        logger.info("Creating collections...")
        
        for collection_name, collection_key in COLLECTIONS.items():
            try:
                # Check if it's a time-series collection
                if collection_key in TIMESERIES_CONFIG:
                    timeseries_options = TIMESERIES_CONFIG[collection_key]
                    await self.db.create_collection(
                        collection_key,
                        timeseries=timeseries_options
                    )
                    logger.info(f"Created time-series collection: {collection_key}")
                else:
                    await self.db.create_collection(collection_key)
                    logger.info(f"Created collection: {collection_key}")
                    
            except CollectionInvalid:
                logger.info(f"Collection {collection_key} already exists")
    
    async def create_indexes(self):
        """Create indexes for all collections"""
        logger.info("Creating indexes...")
        
        for collection_name, index_specs in INDEXES.items():
            if collection_name in COLLECTIONS.values():
                collection = self.db[collection_name]
                
                # Create indexes
                index_models = []
                for index_spec in index_specs:
                    if len(index_spec) == 1 and isinstance(index_spec[0], tuple):
                        # Single field index
                        field, direction = index_spec[0]
                        if direction == "2dsphere":
                            index_models.append(IndexModel([(field, "2dsphere")]))
                        elif direction == "text":
                            index_models.append(IndexModel([(field, TEXT)]))
                        else:
                            index_models.append(IndexModel([(field, direction)]))
                    else:
                        # Compound index
                        index_fields = []
                        for field, direction in index_spec:
                            if direction == "2dsphere":
                                index_fields.append((field, "2dsphere"))
                            elif direction == "text":
                                index_fields.append((field, TEXT))
                            else:
                                index_fields.append((field, direction))
                        index_models.append(IndexModel(index_fields))
                
                if index_models:
                    try:
                        await collection.create_indexes(index_models)
                        logger.info(f"Created {len(index_models)} indexes for {collection_name}")
                    except Exception as e:
                        logger.warning(f"Error creating indexes for {collection_name}: {e}")
    
    async def create_validation_rules(self):
        """Create validation rules for collections"""
        logger.info("Setting up validation rules...")
        
        # User validation
        await self.set_collection_validation("users", {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["username", "email", "password_hash", "role"],
                "properties": {
                    "username": {"bsonType": "string", "minLength": 3, "maxLength": 50},
                    "email": {"bsonType": "string", "pattern": "^[^@]+@[^@]+\\.[^@]+$"},
                    "role": {"enum": ["safety_officer", "engineer", "manager", "researcher", "admin"]},
                    "is_active": {"bsonType": "bool"}
                }
            }
        })
        
        # Site validation
        await self.set_collection_validation("sites", {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["site_id", "name", "location", "bounds"],
                "properties": {
                    "site_id": {"bsonType": "string"},
                    "name": {"bsonType": "string", "minLength": 1},
                    "location": {"bsonType": "object"},
                    "bounds": {"bsonType": "array", "minItems": 4, "maxItems": 4},
                    "status": {"enum": ["active", "inactive", "maintenance"]}
                }
            }
        })
        
        # Prediction validation
        await self.set_collection_validation("predictions", {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["site_id", "risk_score", "risk_class", "confidence"],
                "properties": {
                    "risk_score": {"bsonType": "double", "minimum": 0, "maximum": 1},
                    "confidence": {"bsonType": "double", "minimum": 0, "maximum": 1},
                    "risk_class": {"enum": ["Low", "Medium", "High", "Critical"]}
                }
            }
        })
        
        # Alert validation
        await self.set_collection_validation("alerts", {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["site_id", "alert_type", "title", "message"],
                "properties": {
                    "alert_type": {"enum": ["Critical", "Warning", "Info", "Maintenance"]},
                    "severity": {"bsonType": "int", "minimum": 1, "maximum": 5},
                    "status": {"enum": ["pending", "sent", "acknowledged", "resolved", "failed"]},
                    "channels": {"bsonType": "array", "items": {"bsonType": "string"}}
                }
            }
        })
    
    async def set_collection_validation(self, collection_name: str, validation_rules: Dict[str, Any]):
        """Set validation rules for a specific collection"""
        try:
            await self.db.command({
                "collMod": collection_name,
                "validator": validation_rules,
                "validationLevel": "moderate",
                "validationAction": "warn"
            })
            logger.info(f"Set validation rules for {collection_name}")
        except Exception as e:
            logger.warning(f"Could not set validation for {collection_name}: {e}")
    
    async def create_admin_user(self):
        """Create default admin user"""
        users_collection = self.db[COLLECTIONS["users"]]
        
        # Check if admin user exists
        admin_exists = await users_collection.find_one({"username": "admin"})
        if not admin_exists:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            admin_user = {
                "username": "admin",
                "email": "admin@minesafety.ai",
                "password_hash": pwd_context.hash("admin123!"),  # Change in production
                "role": "admin",
                "full_name": "System Administrator",
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            
            result = await users_collection.insert_one(admin_user)
            logger.info(f"Created admin user with ID: {result.inserted_id}")
        else:
            logger.info("Admin user already exists")
    
    async def create_demo_site(self):
        """Create a demo mining site"""
        sites_collection = self.db[COLLECTIONS["sites"]]
        
        # Check if demo site exists
        demo_site_exists = await sites_collection.find_one({"site_id": "DEMO_SITE_001"})
        if not demo_site_exists:
            demo_site = {
                "site_id": "DEMO_SITE_001",
                "name": "Demo Open Pit Mine",
                "description": "Demonstration mining site for rockfall prediction system",
                "location": {
                    "type": "Point",
                    "coordinates": [-114.0708, 51.0486]  # Calgary, Alberta coordinates
                },
                "bounds": [-114.1, 51.0, -114.0, 51.1],  # Approximate bounds
                "elevation_range": {"min": 1045, "max": 1400},
                "site_type": "open_pit",
                "status": "active",
                "created_at": datetime.utcnow(),
                "created_by": None  # Will be updated after admin user creation
            }
            
            result = await sites_collection.insert_one(demo_site)
            logger.info(f"Created demo site with ID: {result.inserted_id}")
        else:
            logger.info("Demo site already exists")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    async def initialize_all(self):
        """Run complete database initialization"""
        try:
            await self.connect()
            await self.create_collections()
            await self.create_indexes()
            await self.create_validation_rules()
            await self.create_admin_user()
            await self.create_demo_site()
            logger.info("Database initialization completed successfully!")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
        finally:
            await self.close()


async def main():
    """Main initialization function"""
    logger.info("Starting database initialization...")
    
    # Get connection string from environment or use default
    connection_string = os.getenv(
        "MONGODB_URL", 
        "mongodb://localhost:27017"
    )
    
    initializer = DatabaseInitializer(connection_string)
    await initializer.initialize_all()


if __name__ == "__main__":
    asyncio.run(main())