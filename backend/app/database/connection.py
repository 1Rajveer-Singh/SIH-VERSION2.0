"""
MongoDB database connection using Beanie ODM
"""
import asyncio
import logging
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

from app.models.database import (
    User, MiningSite, Device, SensorReading, 
    Prediction, Alert, SystemSetting, SystemLog
)

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    # MongoDB connection URL
    mongo_url = os.getenv("DATABASE_URL", "mongodb://admin:rockfall123@localhost:27017/rockfall_prediction?authSource=admin")
    
    logger.info(f"Connecting to MongoDB: {mongo_url.split('@')[1] if '@' in mongo_url else mongo_url}")
    
    try:
        # Create Motor client
        db.client = AsyncIOMotorClient(mongo_url)
        
        # Get database
        db.database = db.client.rockfall_prediction
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=db.database,
            document_models=[
                User,
                MiningSite, 
                Device,
                SensorReading,
                Prediction,
                Alert,
                SystemSetting,
                SystemLog
            ]
        )
        logger.info("Beanie ODM initialized successfully!")
        
        # Create initial data if needed
        await create_initial_data()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Database connection closed")

async def create_initial_data():
    """Create initial system data if not exists"""
    try:
        # Check if admin user exists
        admin_user = await User.find_one(User.email == "admin@rockfall.com")
        if not admin_user:
            # Create admin user
            import hashlib
            password_hash = hashlib.sha256("secret123".encode()).hexdigest()
            
            admin_user = User(
                email="admin@rockfall.com",
                username="admin",
                full_name="System Administrator",
                password_hash=password_hash,
                role="admin",
                is_active=True
            )
            await admin_user.insert()
            logger.info("✅ Admin user created")
        
        # Check if operator user exists
        operator_user = await User.find_one(User.email == "operator@rockfall.com")
        if not operator_user:
            import hashlib
            password_hash = hashlib.sha256("secret123".encode()).hexdigest()
            
            operator_user = User(
                email="operator@rockfall.com",
                username="operator",
                full_name="Mine Operator",
                password_hash=password_hash,
                role="operator",
                is_active=True
            )
            await operator_user.insert()
            logger.info("✅ Operator user created")
            
        # Create default system settings
        default_settings = [
            {"key": "prediction_threshold_low", "value": 0.3, "description": "Low risk threshold", "data_type": "float"},
            {"key": "prediction_threshold_medium", "value": 0.6, "description": "Medium risk threshold", "data_type": "float"},
            {"key": "prediction_threshold_high", "value": 0.8, "description": "High risk threshold", "data_type": "float"},
            {"key": "alert_email_enabled", "value": True, "description": "Enable email alerts", "data_type": "bool"},
            {"key": "alert_sms_enabled", "value": False, "description": "Enable SMS alerts", "data_type": "bool"},
            {"key": "data_retention_days", "value": 365, "description": "Data retention period in days", "data_type": "int"},
            {"key": "api_rate_limit", "value": 1000, "description": "API rate limit per hour", "data_type": "int"},
            {"key": "system_name", "value": "Rockfall Prediction System", "description": "System display name", "data_type": "string"},
        ]
        
        for setting in default_settings:
            existing = await SystemSetting.find_one(SystemSetting.key == setting["key"])
            if not existing:
                system_setting = SystemSetting(**setting)
                await system_setting.insert()
        
        logger.info("✅ Default system settings created")
        
        # Create demo mining site if none exist
        site_count = await MiningSite.count()
        if site_count == 0:
            from app.models.database import Location, Zone, EmergencyContact
            
            demo_site = MiningSite(
                name="Rocky Mountain Quarry",
                description="Demo open-pit limestone quarry for system testing",
                location=Location(
                    latitude=39.7392,
                    longitude=-104.9903,
                    elevation=1620,
                    address="Denver, Colorado, USA"
                ),
                zones=[
                    Zone(zone_id="zone-a", name="North Wall", risk_level="medium"),
                    Zone(zone_id="zone-b", name="South Wall", risk_level="low"),
                    Zone(zone_id="zone-c", name="East Slope", risk_level="high")
                ],
                emergency_contacts=[
                    EmergencyContact(
                        name="John Smith",
                        role="Site Manager", 
                        phone="+1234567890",
                        email="john.smith@mining.com"
                    )
                ],
                area_hectares=45.2,
                safety_protocols=[
                    "Daily visual inspections",
                    "Continuous sensor monitoring",
                    "Emergency evacuation procedures"
                ]
            )
            await demo_site.insert()
            logger.info("✅ Demo mining site created")
            
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")