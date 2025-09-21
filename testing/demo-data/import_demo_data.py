"""
Demo Data Importer for Rockfall Prediction System
Imports the generated demo dataset into MongoDB database
"""

import json
import asyncio
import os
import sys
from datetime import datetime

# Add the backend path to import database models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Import all models
from app.models.database import (
    User, MiningSite, Device, SensorReading, 
    Prediction, Alert, SystemSetting, SystemLog
)

async def connect_to_database():
    """Connect to MongoDB database"""
    # MongoDB connection URL
    mongo_url = os.getenv("DATABASE_URL", "mongodb://admin:rockfall123@localhost:27017/rockfall_prediction?authSource=admin")
    
    print(f"Connecting to MongoDB...")
    
    # Create Motor client
    client = AsyncIOMotorClient(mongo_url)
    
    # Get database
    database = client.rockfall_prediction
    
    # Test connection
    await client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # Initialize Beanie with document models
    await init_beanie(
        database=database,
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
    print("Beanie ODM initialized successfully!")
    
    return client, database

async def clear_existing_data():
    """Clear existing demo data (optional)"""
    print("Clearing existing demo data...")
    
    # Clear collections (be careful with this in production!)
    await MiningSite.delete_all()
    await Device.delete_all()
    await SensorReading.delete_all()
    await Prediction.delete_all()
    await Alert.delete_all()
    
    print("Existing demo data cleared!")

async def import_sites(sites_data):
    """Import mining sites"""
    print(f"Importing {len(sites_data)} mining sites...")
    
    for site_data in sites_data:
        # Convert to MiningSite model format
        site = MiningSite(
            _id=site_data["_id"],
            name=site_data["name"],
            description=site_data["description"],
            location={
                "latitude": site_data["location"]["latitude"],
                "longitude": site_data["location"]["longitude"],
                "elevation": site_data["location"]["elevation"],
                "address": site_data["location"]["address"]
            },
            zones=[
                {
                    "zone_id": zone["zone_id"],
                    "name": zone["name"],
                    "risk_level": zone["risk_level"]
                }
                for zone in site_data["zones"]
            ],
            emergency_contacts=[
                {
                    "name": contact["name"],
                    "role": contact["role"],
                    "phone": contact["phone"],
                    "email": contact["email"]
                }
                for contact in site_data["emergency_contacts"]
            ],
            area_hectares=site_data["area_hectares"],
            safety_protocols=site_data["safety_protocols"],
            status=site_data["status"],
            created_at=datetime.fromisoformat(site_data["created_at"])
        )
        
        await site.insert()
    
    print(f"Successfully imported {len(sites_data)} mining sites!")

async def import_devices(devices_data):
    """Import monitoring devices"""
    print(f"Importing {len(devices_data)} monitoring devices...")
    
    batch_size = 100
    for i in range(0, len(devices_data), batch_size):
        batch = devices_data[i:i + batch_size]
        devices = []
        
        for device_data in batch:
            device = Device(
                _id=device_data["_id"],
                device_id=device_data["device_id"],
                site_id=device_data["site_id"],
                name=device_data["name"],
                type=device_data["type"],
                model=device_data["model"],
                location={
                    "zone": device_data["location"]["zone"],
                    "coordinates": device_data["location"]["coordinates"]
                },
                status=device_data["status"],
                battery_level=device_data["battery_level"],
                signal_strength=device_data["signal_strength"],
                last_reading=datetime.fromisoformat(device_data["last_reading"]),
                calibration_date=datetime.fromisoformat(device_data["calibration_date"]),
                installation_date=datetime.fromisoformat(device_data["installation_date"]),
                specs=device_data["specs"]
            )
            devices.append(device)
        
        await Device.insert_many(devices)
        print(f"Imported batch {i//batch_size + 1}/{(len(devices_data) + batch_size - 1)//batch_size}")
    
    print(f"Successfully imported {len(devices_data)} monitoring devices!")

async def import_sensor_readings(readings_data):
    """Import sensor readings in batches"""
    print(f"Importing {len(readings_data)} sensor readings...")
    
    batch_size = 1000
    for i in range(0, len(readings_data), batch_size):
        batch = readings_data[i:i + batch_size]
        readings = []
        
        for reading_data in batch:
            reading = SensorReading(
                _id=reading_data["_id"],
                device_id=reading_data["device_id"],
                site_id=reading_data["site_id"],
                timestamp=datetime.fromisoformat(reading_data["timestamp"]),
                processed=reading_data["processed"]
            )
            
            # Add type-specific measurements
            if "vibration" in reading_data:
                reading.vibration = reading_data["vibration"]
            if "temperature" in reading_data:
                reading.temperature = reading_data["temperature"]
            if "humidity" in reading_data:
                reading.humidity = reading_data["humidity"]
            if "strain" in reading_data:
                reading.strain = reading_data["strain"]
            if "tilt" in reading_data:
                reading.tilt = reading_data["tilt"]
            
            readings.append(reading)
        
        await SensorReading.insert_many(readings)
        print(f"Imported batch {i//batch_size + 1}/{(len(readings_data) + batch_size - 1)//batch_size}")
    
    print(f"Successfully imported {len(readings_data)} sensor readings!")

async def import_predictions(predictions_data):
    """Import predictions"""
    print(f"Importing {len(predictions_data)} predictions...")
    
    for pred_data in predictions_data:
        prediction = Prediction(
            _id=pred_data["_id"],
            site_id=pred_data["site_id"],
            device_ids=pred_data["device_ids"],
            risk_level=pred_data["risk_level"],
            risk_score=pred_data["risk_score"],
            confidence=pred_data["confidence"],
            created_at=datetime.fromisoformat(pred_data["created_at"]),
            processed_data=pred_data["processed_data"],
            metadata=pred_data["metadata"]
        )
        
        await prediction.insert()
    
    print(f"Successfully imported {len(predictions_data)} predictions!")

async def import_alerts(alerts_data):
    """Import alerts"""
    print(f"Importing {len(alerts_data)} alerts...")
    
    for alert_data in alerts_data:
        alert = Alert(
            _id=alert_data["_id"],
            alert_type=alert_data["alert_type"],
            severity=alert_data["severity"],
            message=alert_data["message"],
            created_at=datetime.fromisoformat(alert_data["created_at"]),
            status=alert_data["status"]
        )
        
        # Add optional fields
        if "prediction_id" in alert_data:
            alert.prediction_id = alert_data["prediction_id"]
        if "device_id" in alert_data:
            alert.device_id = alert_data["device_id"]
        if "site_id" in alert_data:
            alert.site_id = alert_data["site_id"]
        if "acknowledged_by" in alert_data and alert_data["acknowledged_by"]:
            alert.acknowledged_by = alert_data["acknowledged_by"]
        if "acknowledged_at" in alert_data and alert_data["acknowledged_at"]:
            alert.acknowledged_at = datetime.fromisoformat(alert_data["acknowledged_at"])
        
        await alert.insert()
    
    print(f"Successfully imported {len(alerts_data)} alerts!")

async def main():
    """Main import function"""
    print("Starting demo data import...")
    
    # Connect to database
    client, database = await connect_to_database()
    
    try:
        # Ask user if they want to clear existing data
        clear_data = input("Clear existing demo data? (y/N): ").lower().strip()
        if clear_data == 'y':
            await clear_existing_data()
        
        # Load data files
        base_path = os.path.dirname(__file__)
        
        print("Loading data files...")
        with open(os.path.join(base_path, "sites.json"), "r") as f:
            sites_data = json.load(f)
        
        with open(os.path.join(base_path, "devices.json"), "r") as f:
            devices_data = json.load(f)
        
        with open(os.path.join(base_path, "sensor_readings.json"), "r") as f:
            readings_data = json.load(f)
        
        with open(os.path.join(base_path, "predictions.json"), "r") as f:
            predictions_data = json.load(f)
        
        with open(os.path.join(base_path, "alerts.json"), "r") as f:
            alerts_data = json.load(f)
        
        print("Data files loaded successfully!")
        
        # Import data in order (dependencies matter)
        await import_sites(sites_data)
        await import_devices(devices_data)
        await import_sensor_readings(readings_data)
        await import_predictions(predictions_data)
        await import_alerts(alerts_data)
        
        print("\n🎉 Demo data import completed successfully!")
        print(f"Imported:")
        print(f"  - {len(sites_data)} mining sites")
        print(f"  - {len(devices_data)} monitoring devices")
        print(f"  - {len(readings_data)} sensor readings")
        print(f"  - {len(predictions_data)} predictions")
        print(f"  - {len(alerts_data)} alerts")
        
    except Exception as e:
        print(f"Error during import: {e}")
        raise
    finally:
        # Close database connection
        client.close()
        print("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())