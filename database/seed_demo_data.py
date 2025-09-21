"""
Database seeding script for demo data
Populates MongoDB with realistic mining and sensor data
"""

import asyncio
import random
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging
import json
import numpy as np
from typing import List, Dict, Any

from schemas.models import COLLECTIONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoDataSeeder:
    """Generates and seeds realistic demo data"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv(
            "MONGODB_URL", 
            "mongodb://localhost:27017"
        )
        self.database_name = os.getenv("DATABASE_NAME", "rockfall_prediction")
        self.client = None
        self.db = None
        
        # Demo site configuration
        self.demo_site_id = "DEMO_SITE_001"
        self.demo_site_bounds = [-114.1, 51.0, -114.0, 51.1]
        
        # Sensor configurations
        self.sensor_types = [
            {"type": "displacement", "unit": "mm", "range": (-5, 5), "base": 0},
            {"type": "strain", "unit": "microstrain", "range": (-100, 100), "base": 0},
            {"type": "pore_pressure", "unit": "kPa", "range": (50, 200), "base": 100},
            {"type": "vibration", "unit": "mm/s", "range": (0, 10), "base": 1},
            {"type": "tilt", "unit": "degrees", "range": (-2, 2), "base": 0},
            {"type": "crack_meter", "unit": "mm", "range": (0, 20), "base": 5}
        ]
        
        self.device_locations = [
            {"name": "Sensor-001", "coordinates": [-114.05, 51.05]},
            {"name": "Sensor-002", "coordinates": [-114.06, 51.06]},
            {"name": "Sensor-003", "coordinates": [-114.07, 51.07]},
            {"name": "Sensor-004", "coordinates": [-114.08, 51.08]},
            {"name": "Sensor-005", "coordinates": [-114.09, 51.09]},
            {"name": "Sensor-006", "coordinates": [-114.04, 51.04]},
            {"name": "Sensor-007", "coordinates": [-114.03, 51.03]},
            {"name": "Sensor-008", "coordinates": [-114.02, 51.02]}
        ]
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB for seeding")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def seed_dem_data(self):
        """Seed DEM collection with sample data"""
        logger.info("Seeding DEM data...")
        collection = self.db[COLLECTIONS["dem_collection"]]
        
        dem_files = [
            {
                "site_id": self.demo_site_id,
                "filename": "dem_202401_1m.tif",
                "s3_url": "s3://rockfall-data/dem/dem_202401_1m.tif",
                "s3_bucket": "rockfall-data",
                "file_size_bytes": 45678901,
                "bounds": self.demo_site_bounds,
                "resolution_m": 1.0,
                "coordinate_system": "EPSG:4326",
                "elevation_range": {"min": 1045.2, "max": 1398.7},
                "metadata": {
                    "source": "drone_photogrammetry",
                    "flight_date": "2024-01-15",
                    "processing_software": "Pix4D",
                    "accuracy_m": 0.15
                },
                "processing_status": "completed",
                "uploaded_by": ObjectId(),
                "created_at": datetime.utcnow() - timedelta(days=30),
                "processed_at": datetime.utcnow() - timedelta(days=29)
            },
            {
                "site_id": self.demo_site_id,
                "filename": "dem_202402_1m.tif",
                "s3_url": "s3://rockfall-data/dem/dem_202402_1m.tif",
                "s3_bucket": "rockfall-data",
                "file_size_bytes": 46234567,
                "bounds": self.demo_site_bounds,
                "resolution_m": 1.0,
                "coordinate_system": "EPSG:4326",
                "elevation_range": {"min": 1045.0, "max": 1398.9},
                "metadata": {
                    "source": "drone_photogrammetry",
                    "flight_date": "2024-02-15",
                    "processing_software": "Pix4D",
                    "accuracy_m": 0.12
                },
                "processing_status": "completed",
                "uploaded_by": ObjectId(),
                "created_at": datetime.utcnow() - timedelta(days=15),
                "processed_at": datetime.utcnow() - timedelta(days=14)
            }
        ]
        
        await collection.insert_many(dem_files)
        logger.info(f"Inserted {len(dem_files)} DEM records")
    
    async def seed_drone_images(self):
        """Seed drone images collection"""
        logger.info("Seeding drone images...")
        collection = self.db[COLLECTIONS["drone_images"]]
        
        drone_images = []
        base_time = datetime.utcnow() - timedelta(days=7)
        
        for i in range(20):
            image_time = base_time + timedelta(hours=i*6)
            # Random location within site bounds
            lon = random.uniform(self.demo_site_bounds[0], self.demo_site_bounds[2])
            lat = random.uniform(self.demo_site_bounds[1], self.demo_site_bounds[3])
            
            drone_image = {
                "site_id": self.demo_site_id,
                "filename": f"drone_img_{i+1:03d}.jpg",
                "s3_url": f"s3://rockfall-data/drone/drone_img_{i+1:03d}.jpg",
                "s3_bucket": "rockfall-data",
                "file_size_bytes": random.randint(5000000, 15000000),
                "geotag": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "altitude_m": random.uniform(50, 150),
                "camera": {
                    "focal_length_mm": random.choice([24, 35, 50]),
                    "sensor_size_mm": [36, 24],
                    "iso": random.choice([100, 200, 400]),
                    "aperture": random.choice(["f/5.6", "f/8", "f/11"]),
                    "shutter_speed": random.choice(["1/250", "1/500", "1/1000"])
                },
                "flight_mission_id": f"MISSION_{(i//5)+1:02d}",
                "weather_conditions": {
                    "visibility_km": random.uniform(8, 15),
                    "wind_speed_kmh": random.uniform(5, 25),
                    "cloud_cover": random.choice(["clear", "partly_cloudy", "overcast"])
                },
                "image_quality_score": random.uniform(0.7, 0.98),
                "processing_status": "completed",
                "uploaded_by": ObjectId(),
                "created_at": image_time,
                "processed_at": image_time + timedelta(minutes=30)
            }
            drone_images.append(drone_image)
        
        await collection.insert_many(drone_images)
        logger.info(f"Inserted {len(drone_images)} drone images")
    
    async def seed_sensor_data(self):
        """Seed sensor time-series data"""
        logger.info("Seeding sensor time-series data...")
        collection = self.db[COLLECTIONS["sensor_timeseries"]]
        
        sensor_data = []
        start_time = datetime.utcnow() - timedelta(days=30)
        
        # Generate data for each sensor and sensor type
        for device in self.device_locations:
            for sensor_config in self.sensor_types:
                # Generate 30 days of hourly data
                for hour in range(30 * 24):
                    timestamp = start_time + timedelta(hours=hour)
                    
                    # Simulate realistic sensor patterns
                    base_value = sensor_config["base"]
                    noise = random.gauss(0, abs(sensor_config["range"][1] - sensor_config["range"][0]) * 0.1)
                    
                    # Add some trending and anomalies
                    if sensor_config["type"] == "displacement" and hour > 20*24:
                        # Simulate increasing displacement over time
                        base_value += (hour - 20*24) * 0.01
                    
                    if sensor_config["type"] == "vibration" and random.random() < 0.05:
                        # Occasional vibration spikes
                        noise += random.uniform(5, 15)
                    
                    value = max(sensor_config["range"][0], 
                              min(sensor_config["range"][1], base_value + noise))
                    
                    sensor_reading = {
                        "time": timestamp,
                        "device_id": f"{device['name']}_{sensor_config['type'].upper()}",
                        "sensor_type": sensor_config["type"],
                        "value": round(value, 3),
                        "unit": sensor_config["unit"],
                        "quality_flag": random.choice(["good"] * 90 + ["questionable"] * 8 + ["bad"] * 2),
                        "location": {
                            "type": "Point",
                            "coordinates": device["coordinates"]
                        },
                        "node_name": device["name"],
                        "site_id": self.demo_site_id,
                        "battery_level": random.uniform(20, 100),
                        "signal_strength": random.uniform(60, 100)
                    }
                    sensor_data.append(sensor_reading)
                    
                    # Insert in batches to avoid memory issues
                    if len(sensor_data) >= 1000:
                        await collection.insert_many(sensor_data)
                        sensor_data = []
        
        # Insert remaining data
        if sensor_data:
            await collection.insert_many(sensor_data)
        
        logger.info("Finished seeding sensor time-series data")
    
    async def seed_environmental_data(self):
        """Seed environmental monitoring data"""
        logger.info("Seeding environmental data...")
        collection = self.db[COLLECTIONS["environmental_data"]]
        
        environmental_data = []
        start_time = datetime.utcnow() - timedelta(days=30)
        
        # Generate daily environmental readings
        for day in range(30):
            timestamp = start_time + timedelta(days=day)
            
            # Simulate realistic weather patterns
            base_temp = 15 + 5 * np.sin(2 * np.pi * day / 365)  # Seasonal variation
            temp_variation = random.gauss(0, 3)
            
            env_data = {
                "site_id": self.demo_site_id,
                "timestamp": timestamp,
                "rainfall_mm": max(0, random.gauss(2, 5)),
                "rainfall_24h": max(0, random.gauss(5, 10)),
                "temperature_c": round(base_temp + temp_variation, 1),
                "humidity": round(random.uniform(40, 85), 1),
                "wind_speed_kmh": round(random.uniform(5, 35), 1),
                "wind_direction_deg": round(random.uniform(0, 360), 0),
                "atmospheric_pressure_hpa": round(random.uniform(980, 1020), 1),
                "vibration_level": round(random.uniform(0.1, 2.0), 2),
                "seismic_activity": round(random.uniform(0, 0.5), 3),
                "soil_moisture": round(random.uniform(15, 45), 1),
                "data_source": "weather_station_001"
            }
            environmental_data.append(env_data)
        
        await collection.insert_many(environmental_data)
        logger.info(f"Inserted {len(environmental_data)} environmental records")
    
    async def seed_predictions(self):
        """Seed AI predictions data"""
        logger.info("Seeding prediction data...")
        collection = self.db[COLLECTIONS["predictions"]]
        
        predictions = []
        start_time = datetime.utcnow() - timedelta(days=7)
        
        # Generate predictions every 6 hours for the last week
        for i in range(7 * 4):
            timestamp = start_time + timedelta(hours=i*6)
            
            # Simulate risk escalation over time
            base_risk = 0.2 + (i / (7 * 4)) * 0.4  # Risk increases over time
            risk_noise = random.gauss(0, 0.1)
            risk_score = max(0, min(1, base_risk + risk_noise))
            
            # Determine risk class
            if risk_score < 0.25:
                risk_class = "Low"
            elif risk_score < 0.5:
                risk_class = "Medium"
            elif risk_score < 0.75:
                risk_class = "High"
            else:
                risk_class = "Critical"
            
            prediction = {
                "site_id": self.demo_site_id,
                "risk_score": round(risk_score, 3),
                "risk_class": risk_class,
                "confidence": round(random.uniform(0.75, 0.95), 3),
                "explanation": {
                    "top_features": [
                        ["displacement_trend", round(random.uniform(0.2, 0.4), 3)],
                        ["rainfall_24h", round(random.uniform(0.1, 0.3), 3)],
                        ["vibration_anomaly", round(random.uniform(0.05, 0.2), 3)],
                        ["historical_pattern", round(random.uniform(0.1, 0.25), 3)]
                    ],
                    "feature_importance": {
                        "displacement": 0.35,
                        "environmental": 0.25,
                        "vibration": 0.20,
                        "historical": 0.20
                    },
                    "image_gradcam_url": f"s3://rockfall-analysis/gradcam/prediction_{i+1}.png"
                },
                "geojson_zone": {
                    "type": "FeatureCollection",
                    "features": [{
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [-114.07, 51.06],
                                [-114.06, 51.06],
                                [-114.06, 51.07],
                                [-114.07, 51.07],
                                [-114.07, 51.06]
                            ]]
                        },
                        "properties": {
                            "risk_level": risk_class,
                            "confidence": round(random.uniform(0.75, 0.95), 3)
                        }
                    }]
                },
                "model_metadata": {
                    "model_version": "1.2.0",
                    "model_type": "ensemble",
                    "training_date": "2024-01-15",
                    "feature_count": 47
                },
                "input_data_sources": ["sensors", "environmental", "dem", "historical"],
                "processing_time_ms": random.uniform(150, 500),
                "timestamp": timestamp,
                "processed_by": "rockfall_prediction_model_v1.2.0",
                "is_archived": False
            }
            predictions.append(prediction)
        
        await collection.insert_many(predictions)
        logger.info(f"Inserted {len(predictions)} predictions")
        
        return predictions  # Return for use in alerts
    
    async def seed_alerts(self, predictions: List[Dict]):
        """Seed alerts based on predictions"""
        logger.info("Seeding alerts...")
        collection = self.db[COLLECTIONS["alerts"]]
        
        alerts = []
        
        # Create alerts for high and critical risk predictions
        for prediction in predictions:
            if prediction["risk_class"] in ["High", "Critical"]:
                severity = 4 if prediction["risk_class"] == "High" else 5
                
                alert = {
                    "site_id": self.demo_site_id,
                    "prediction_id": prediction.get("_id"),
                    "alert_type": "Critical" if prediction["risk_class"] == "Critical" else "Warning",
                    "severity": severity,
                    "title": f"{prediction['risk_class']} Risk Detected",
                    "message": f"Rockfall risk assessment shows {prediction['risk_class'].lower()} risk "
                              f"(score: {prediction['risk_score']:.3f}) in monitoring zone. "
                              f"Immediate attention required.",
                    "channels": ["SMS", "Email"] if severity == 5 else ["Email"],
                    "status": random.choice(["sent", "acknowledged"] * 3 + ["pending"]),
                    "recipients": ["safety@minesite.com", "engineer@minesite.com"],
                    "metadata": {
                        "risk_zone_coordinates": prediction["geojson_zone"]["features"][0]["geometry"]["coordinates"][0][0],
                        "confidence": prediction["confidence"]
                    },
                    "retry_count": 0,
                    "max_retries": 3,
                    "escalation_level": 1 if severity <= 4 else 2,
                    "created_at": prediction["timestamp"],
                    "sent_at": prediction["timestamp"] + timedelta(minutes=2)
                }
                
                # Some alerts are acknowledged
                if alert["status"] == "acknowledged":
                    alert["acknowledged_by"] = ObjectId()
                    alert["acknowledged_at"] = alert["sent_at"] + timedelta(minutes=random.randint(10, 120))
                
                alerts.append(alert)
        
        if alerts:
            await collection.insert_many(alerts)
            logger.info(f"Inserted {len(alerts)} alerts")
    
    async def seed_ml_models(self):
        """Seed ML model registry"""
        logger.info("Seeding ML models...")
        collection = self.db[COLLECTIONS["ml_models"]]
        
        models = [
            {
                "name": "Rockfall Risk Ensemble",
                "version": "1.2.0",
                "model_type": "ensemble",
                "framework": "pytorch",
                "s3_model_path": "s3://rockfall-models/ensemble_v1.2.0/model.pkl",
                "performance_metrics": {
                    "accuracy": 0.92,
                    "precision": 0.89,
                    "recall": 0.94,
                    "f1_score": 0.91,
                    "auc_roc": 0.96
                },
                "feature_schema": {
                    "displacement_features": 12,
                    "environmental_features": 8,
                    "vibration_features": 10,
                    "dem_features": 15,
                    "temporal_features": 2
                },
                "training_data_period": {
                    "start": datetime(2023, 1, 1),
                    "end": datetime(2024, 1, 15)
                },
                "hyperparameters": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "learning_rate": 0.1,
                    "ensemble_weights": [0.4, 0.3, 0.3]
                },
                "is_active": True,
                "deployment_status": "production",
                "created_by": ObjectId(),
                "created_at": datetime(2024, 1, 20),
                "last_retrained": datetime(2024, 1, 15)
            },
            {
                "name": "Deep Learning Risk Predictor",
                "version": "2.0.0-beta",
                "model_type": "neural_network",
                "framework": "pytorch",
                "s3_model_path": "s3://rockfall-models/dl_v2.0.0/model.pth",
                "performance_metrics": {
                    "accuracy": 0.94,
                    "precision": 0.91,
                    "recall": 0.96,
                    "f1_score": 0.93,
                    "auc_roc": 0.97
                },
                "feature_schema": {
                    "sensor_sequence_length": 168,  # 1 week hourly
                    "image_features": 512,
                    "environmental_features": 8,
                    "spatial_features": 20
                },
                "training_data_period": {
                    "start": datetime(2023, 6, 1),
                    "end": datetime(2024, 2, 1)
                },
                "hyperparameters": {
                    "hidden_layers": [256, 128, 64],
                    "dropout_rate": 0.2,
                    "learning_rate": 0.001,
                    "batch_size": 32
                },
                "is_active": False,
                "deployment_status": "staging",
                "created_by": ObjectId(),
                "created_at": datetime(2024, 2, 10),
                "last_retrained": datetime(2024, 2, 5)
            }
        ]
        
        await collection.insert_many(models)
        logger.info(f"Inserted {len(models)} ML models")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    async def seed_all(self):
        """Run complete data seeding"""
        try:
            await self.connect()
            await self.seed_dem_data()
            await self.seed_drone_images()
            await self.seed_sensor_data()
            await self.seed_environmental_data()
            predictions = await self.seed_predictions()
            await self.seed_alerts(predictions)
            await self.seed_ml_models()
            logger.info("Demo data seeding completed successfully!")
        except Exception as e:
            logger.error(f"Demo data seeding failed: {e}")
            raise
        finally:
            await self.close()


async def main():
    """Main seeding function"""
    logger.info("Starting demo data seeding...")
    
    connection_string = os.getenv(
        "MONGODB_URL", 
        "mongodb://localhost:27017"
    )
    
    seeder = DemoDataSeeder(connection_string)
    await seeder.seed_all()


if __name__ == "__main__":
    asyncio.run(main())