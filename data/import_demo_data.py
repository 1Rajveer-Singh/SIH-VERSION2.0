"""
Import demo data into MongoDB database
"""
import json
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_database
from backend.models.site import Site
from backend.models.sensor import Sensor, SensorReading
from backend.models.prediction import Prediction
from backend.models.user import User
from bson import ObjectId

class DataImporter:
    """
    Import demo data into MongoDB
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.db = None
    
    async def connect_database(self):
        """Connect to MongoDB"""
        self.db = await get_database()
        print("✓ Connected to MongoDB")
    
    async def import_sites(self):
        """Import mining sites"""
        with open(os.path.join(self.data_dir, "sites.json"), "r") as f:
            sites_data = json.load(f)
        
        sites_collection = self.db.sites
        await sites_collection.delete_many({})  # Clear existing data
        
        for site_data in sites_data:
            site_data["_id"] = site_data["id"]
            site_data["created_at"] = datetime.utcnow()
            site_data["updated_at"] = datetime.utcnow()
            
        result = await sites_collection.insert_many(sites_data)
        print(f"✓ Imported {len(result.inserted_ids)} sites")
        return [site["id"] for site in sites_data]
    
    async def import_sensors(self):
        """Import sensors"""
        with open(os.path.join(self.data_dir, "sensors.json"), "r") as f:
            sensors_data = json.load(f)
        
        sensors_collection = self.db.sensors
        await sensors_collection.delete_many({})  # Clear existing data
        
        for sensor_data in sensors_data:
            sensor_data["_id"] = sensor_data["id"]
            sensor_data["created_at"] = datetime.utcnow()
            sensor_data["updated_at"] = datetime.utcnow()
            
            # Convert installation_date and last_reading to datetime
            if "installation_date" in sensor_data:
                sensor_data["installation_date"] = datetime.fromisoformat(
                    sensor_data["installation_date"].replace("Z", "+00:00")
                )
            if "last_reading" in sensor_data:
                sensor_data["last_reading"] = datetime.fromisoformat(
                    sensor_data["last_reading"].replace("Z", "+00:00")
                )
        
        result = await sensors_collection.insert_many(sensors_data)
        print(f"✓ Imported {len(result.inserted_ids)} sensors")
        return [sensor["id"] for sensor in sensors_data]
    
    async def import_sensor_readings(self):
        """Import sensor readings from chunked files"""
        readings_collection = self.db.sensor_readings
        await readings_collection.delete_many({})  # Clear existing data
        
        total_imported = 0
        chunk_files = [f for f in os.listdir(self.data_dir) if f.startswith("sensor_readings_chunk_")]
        
        for chunk_file in sorted(chunk_files):
            with open(os.path.join(self.data_dir, chunk_file), "r") as f:
                readings_data = json.load(f)
            
            # Process readings
            for reading in readings_data:
                reading["_id"] = f"{reading['sensor_id']}_{reading['timestamp']}"
                reading["timestamp"] = datetime.fromisoformat(
                    reading["timestamp"].replace("Z", "+00:00")
                )
                reading["created_at"] = datetime.utcnow()
            
            if readings_data:
                result = await readings_collection.insert_many(readings_data)
                total_imported += len(result.inserted_ids)
                print(f"✓ Imported {len(result.inserted_ids)} readings from {chunk_file}")
        
        print(f"✓ Total sensor readings imported: {total_imported}")
        
        # Create indexes for better query performance
        await readings_collection.create_index([("sensor_id", 1), ("timestamp", -1)])
        await readings_collection.create_index([("site_id", 1), ("timestamp", -1)])
        print("✓ Created database indexes for sensor readings")
    
    async def import_dem_metadata(self):
        """Import DEM metadata"""
        with open(os.path.join(self.data_dir, "dem_metadata.json"), "r") as f:
            dem_data = json.load(f)
        
        dem_collection = self.db.dem_files
        await dem_collection.delete_many({})  # Clear existing data
        
        for dem in dem_data:
            dem["_id"] = dem["id"]
            dem["created_at"] = datetime.fromisoformat(dem["created_at"].replace("Z", "+00:00"))
            dem["updated_at"] = datetime.fromisoformat(dem["updated_at"].replace("Z", "+00:00"))
        
        result = await dem_collection.insert_many(dem_data)
        print(f"✓ Imported {len(result.inserted_ids)} DEM files metadata")
    
    async def import_drone_imagery(self):
        """Import drone imagery metadata"""
        with open(os.path.join(self.data_dir, "drone_imagery_metadata.json"), "r") as f:
            drone_data = json.load(f)
        
        drone_collection = self.db.drone_imagery
        await drone_collection.delete_many({})  # Clear existing data
        
        for imagery in drone_data:
            imagery["_id"] = imagery["id"]
            imagery["flight_date"] = datetime.fromisoformat(
                imagery["flight_date"].replace("Z", "+00:00")
            )
            imagery["created_at"] = datetime.utcnow()
        
        result = await drone_collection.insert_many(drone_data)
        print(f"✓ Imported {len(result.inserted_ids)} drone imagery records")
        
        # Create indexes
        await drone_collection.create_index([("site_id", 1), ("flight_date", -1)])
        print("✓ Created database indexes for drone imagery")
    
    async def import_environmental_data(self):
        """Import environmental data"""
        with open(os.path.join(self.data_dir, "environmental_data.json"), "r") as f:
            env_data = json.load(f)
        
        env_collection = self.db.environmental_data
        await env_collection.delete_many({})  # Clear existing data
        
        for env_record in env_data:
            env_record["_id"] = env_record["date"]
            env_record["date"] = datetime.fromisoformat(env_record["date"])
            env_record["created_at"] = datetime.utcnow()
        
        result = await env_collection.insert_many(env_data)
        print(f"✓ Imported {len(result.inserted_ids)} environmental data records")
        
        # Create index
        await env_collection.create_index([("date", -1)])
        print("✓ Created database indexes for environmental data")
    
    async def import_historical_events(self):
        """Import historical events"""
        with open(os.path.join(self.data_dir, "historical_events.json"), "r") as f:
            events_data = json.load(f)
        
        events_collection = self.db.historical_events
        await events_collection.delete_many({})  # Clear existing data
        
        for event in events_data:
            event["_id"] = event["id"]
            event["date"] = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
            event["created_at"] = datetime.utcnow()
        
        result = await events_collection.insert_many(events_data)
        print(f"✓ Imported {len(result.inserted_ids)} historical events")
        
        # Create indexes
        await events_collection.create_index([("site_id", 1), ("date", -1)])
        await events_collection.create_index([("event_type", 1), ("severity", 1)])
        print("✓ Created database indexes for historical events")
    
    async def create_demo_users(self):
        """Create demo users"""
        users_collection = self.db.users
        await users_collection.delete_many({})  # Clear existing data
        
        demo_users = [
            {
                "_id": "user_admin",
                "username": "admin",
                "email": "admin@mining.com",
                "full_name": "System Administrator",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                "permissions": ["read", "write", "admin"]
            },
            {
                "_id": "user_operator",
                "username": "operator",
                "email": "operator@mining.com", 
                "full_name": "Site Operator",
                "role": "operator",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                "permissions": ["read", "write"]
            },
            {
                "_id": "user_viewer",
                "username": "viewer",
                "email": "viewer@mining.com",
                "full_name": "Safety Inspector", 
                "role": "viewer",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                "permissions": ["read"]
            }
        ]
        
        result = await users_collection.insert_many(demo_users)
        print(f"✓ Created {len(result.inserted_ids)} demo users")
        print("  Default password for all demo users: 'secret'")
    
    async def generate_sample_predictions(self, site_ids: List[str]):
        """Generate sample predictions"""
        predictions_collection = self.db.predictions
        await predictions_collection.delete_many({})  # Clear existing data
        
        predictions = []
        
        # Generate predictions for each site over the last 7 days
        for site_id in site_ids:
            for day_offset in range(7):
                prediction_date = datetime.utcnow() - timedelta(days=day_offset)
                
                prediction = {
                    "_id": f"pred_{site_id}_{prediction_date.strftime('%Y%m%d')}",
                    "site_id": site_id,
                    "timestamp": prediction_date,
                    "model_version": "v2.1.0",
                    "risk_score": round(random.uniform(0.1, 0.9), 3),
                    "risk_level": random.choice(["low", "medium", "high"]),
                    "confidence": round(random.uniform(0.7, 0.95), 3),
                    "contributing_factors": random.sample([
                        "seismic_activity", "weather_conditions", "slope_angle",
                        "rock_composition", "vibration_levels", "recent_blasting"
                    ], random.randint(2, 4)),
                    "recommended_actions": [
                        "Continue monitoring",
                        "Increase inspection frequency",
                        "Review safety protocols"
                    ][:random.randint(1, 3)],
                    "created_at": prediction_date,
                    "model_inputs": {
                        "sensor_count": random.randint(3, 8),
                        "data_points": random.randint(1000, 5000),
                        "weather_factor": round(random.uniform(0.1, 1.0), 3),
                        "geological_factor": round(random.uniform(0.1, 1.0), 3)
                    }
                }
                predictions.append(prediction)
        
        if predictions:
            result = await predictions_collection.insert_many(predictions)
            print(f"✓ Generated {len(result.inserted_ids)} sample predictions")
            
            # Create indexes
            await predictions_collection.create_index([("site_id", 1), ("timestamp", -1)])
            await predictions_collection.create_index([("risk_level", 1), ("timestamp", -1)])
            print("✓ Created database indexes for predictions")
    
    async def create_database_summary(self):
        """Create a summary of imported data"""
        collections_info = {}
        
        collection_names = [
            "sites", "sensors", "sensor_readings", "dem_files", 
            "drone_imagery", "environmental_data", "historical_events",
            "users", "predictions"
        ]
        
        for collection_name in collection_names:
            collection = self.db[collection_name]
            count = await collection.count_documents({})
            collections_info[collection_name] = count
        
        summary = {
            "import_date": datetime.utcnow().isoformat(),
            "database_name": self.db.name,
            "collections": collections_info,
            "total_documents": sum(collections_info.values())
        }
        
        # Save summary to file
        with open(os.path.join(self.data_dir, "import_summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
        
        print("\n📊 Database Import Summary:")
        print(f"📁 Database: {self.db.name}")
        print(f"📈 Total Documents: {summary['total_documents']}")
        print("\n📋 Collections:")
        for collection, count in collections_info.items():
            print(f"   {collection}: {count:,} documents")
    
    async def import_all_data(self):
        """Import all demo data"""
        print("🚀 Starting demo data import...")
        
        try:
            await self.connect_database()
            
            # Import core data
            site_ids = await self.import_sites()
            sensor_ids = await self.import_sensors()
            await self.import_sensor_readings()
            await self.import_dem_metadata()
            await self.import_drone_imagery()
            await self.import_environmental_data()
            await self.import_historical_events()
            
            # Create demo users and predictions
            await self.create_demo_users()
            await self.generate_sample_predictions(site_ids)
            
            # Create summary
            await self.create_database_summary()
            
            print("\n✅ Demo data import completed successfully!")
            print("\n🔐 Demo User Accounts:")
            print("   Username: admin     | Password: secret | Role: Administrator")
            print("   Username: operator  | Password: secret | Role: Site Operator")
            print("   Username: viewer    | Password: secret | Role: Safety Inspector")
            
        except Exception as e:
            print(f"❌ Error during import: {str(e)}")
            raise

# Additional imports for predictions
import random
from datetime import timedelta

async def main():
    """Main import function"""
    importer = DataImporter("data")
    await importer.import_all_data()

if __name__ == "__main__":
    asyncio.run(main())