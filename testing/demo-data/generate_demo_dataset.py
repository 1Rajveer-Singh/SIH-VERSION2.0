"""
Comprehensive Demo Dataset Generator for Rockfall Prediction System
Generates realistic mining data, predictions, sensor readings, and alerts for testing
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import math

def generate_demo_sites() -> List[Dict[str, Any]]:
    """Generate demo mining sites"""
    sites = []
    
    site_templates = [
        {
            "name": "Rocky Mountain Quarry",
            "description": "Large limestone quarry in Colorado mountains",
            "location": {
                "latitude": 39.7392,
                "longitude": -104.9903,
                "elevation": 1620,
                "address": "Denver, Colorado, USA"
            },
            "area_hectares": 45.2,
            "rock_type": "Limestone"
        },
        {
            "name": "Alpine Granite Mine",
            "description": "Open-pit granite extraction facility",
            "location": {
                "latitude": 46.8772,
                "longitude": -110.4382,
                "elevation": 2100,
                "address": "Montana, USA"
            },
            "area_hectares": 78.5,
            "rock_type": "Granite"
        },
        {
            "name": "Cascade Copper Mine",
            "description": "Copper ore extraction with steep walls",
            "location": {
                "latitude": 47.0379,
                "longitude": -122.9007,
                "elevation": 890,
                "address": "Washington, USA"
            },
            "area_hectares": 124.7,
            "rock_type": "Sedimentary"
        }
    ]
    
    for i, template in enumerate(site_templates):
        site = {
            "_id": f"site-{i+1:03d}",
            **template,
            "zones": [
                {
                    "zone_id": f"zone-{chr(65+j)}",
                    "name": f"{['North', 'South', 'East', 'West', 'Central', 'Upper'][j]} Wall",
                    "risk_level": random.choice(["low", "medium", "high"])
                }
                for j in range(random.randint(3, 6))
            ],
            "emergency_contacts": [
                {
                    "name": f"{random.choice(['John', 'Sarah', 'Mike', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}",
                    "role": "Site Manager",
                    "phone": f"+1{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}",
                    "email": f"manager{i+1}@mining.com"
                }
            ],
            "safety_protocols": [
                "Daily visual inspections",
                "Continuous sensor monitoring",
                "Emergency evacuation procedures",
                "Weather condition monitoring"
            ],
            "status": "active",
            "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
        }
        sites.append(site)
    
    return sites

def generate_demo_devices(sites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate demo monitoring devices"""
    devices = []
    device_types = ["vibration", "temperature", "humidity", "strain", "tilt", "weather"]
    
    device_id = 1
    for site in sites:
        # Generate 15-25 devices per site
        num_devices = random.randint(15, 25)
        
        for _ in range(num_devices):
            device_type = random.choice(device_types)
            
            device = {
                "_id": f"device-{device_id:04d}",
                "device_id": f"DEV-{device_id:04d}",
                "site_id": site["_id"],
                "name": f"{device_type.title()} Sensor {device_id}",
                "type": device_type,
                "model": f"{device_type.upper()}-{random.randint(100, 999)}",
                "location": {
                    "zone": random.choice(site["zones"])["zone_id"],
                    "coordinates": {
                        "x": round(random.uniform(-100, 100), 2),
                        "y": round(random.uniform(-100, 100), 2),
                        "z": round(random.uniform(0, 50), 2)
                    }
                },
                "status": random.choice(["active", "active", "active", "maintenance", "offline"]),
                "battery_level": random.randint(20, 100),
                "signal_strength": random.randint(60, 100),
                "last_reading": (datetime.now() - timedelta(minutes=random.randint(1, 30))).isoformat(),
                "calibration_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "installation_date": (datetime.now() - timedelta(days=random.randint(91, 365))).isoformat(),
                "specs": {
                    "measurement_range": f"0-{random.randint(50, 500)} {get_unit(device_type)}",
                    "accuracy": f"±{random.uniform(0.1, 2.0):.1f}%",
                    "resolution": f"{random.uniform(0.01, 0.1):.2f} {get_unit(device_type)}"
                }
            }
            devices.append(device)
            device_id += 1
    
    return devices

def get_unit(device_type: str) -> str:
    """Get measurement unit for device type"""
    units = {
        "vibration": "mm/s",
        "temperature": "°C",
        "humidity": "%RH",
        "strain": "με",
        "tilt": "°",
        "weather": "various"
    }
    return units.get(device_type, "units")

def generate_sensor_readings(devices: List[Dict[str, Any]], days: int = 30) -> List[Dict[str, Any]]:
    """Generate realistic sensor readings for the past N days"""
    readings = []
    
    for device in devices:
        if device["status"] == "offline":
            continue
            
        # Generate readings for each day
        for day in range(days):
            # Skip some readings randomly to simulate real-world gaps
            if random.random() < 0.05:  # 5% chance to skip a day
                continue
                
            base_date = datetime.now() - timedelta(days=day)
            
            # Generate 24-96 readings per day (every 15-60 minutes)
            readings_per_day = random.randint(24, 96)
            
            for reading_num in range(readings_per_day):
                timestamp = base_date + timedelta(
                    hours=reading_num * 24 / readings_per_day,
                    minutes=random.randint(-15, 15)
                )
                
                reading = {
                    "_id": str(uuid.uuid4()),
                    "device_id": device["device_id"],
                    "site_id": device["site_id"],
                    "timestamp": timestamp.isoformat(),
                    "processed": True
                }
                
                # Generate realistic values based on device type
                if device["type"] == "vibration":
                    # Add some periodic patterns and occasional spikes
                    base_value = 0.5 + 0.3 * math.sin(timestamp.hour * math.pi / 12)
                    noise = random.gauss(0, 0.1)
                    spike = 2.0 if random.random() < 0.02 else 0  # 2% chance of spike
                    reading["vibration"] = max(0, round(base_value + noise + spike, 3))
                    
                elif device["type"] == "temperature":
                    # Temperature with daily cycle
                    base_temp = 15 + 10 * math.sin((timestamp.hour - 6) * math.pi / 12)
                    seasonal_variation = 5 * math.sin(timestamp.timetuple().tm_yday * 2 * math.pi / 365)
                    noise = random.gauss(0, 1)
                    reading["temperature"] = round(base_temp + seasonal_variation + noise, 2)
                    
                elif device["type"] == "humidity":
                    # Humidity inversely related to temperature
                    base_humidity = 60 - 20 * math.sin((timestamp.hour - 6) * math.pi / 12)
                    noise = random.gauss(0, 5)
                    reading["humidity"] = max(10, min(90, round(base_humidity + noise, 1)))
                    
                elif device["type"] == "strain":
                    # Strain with gradual changes and stress events
                    base_strain = 100 + random.gauss(0, 10)
                    stress_event = 50 if random.random() < 0.01 else 0
                    reading["strain"] = round(base_strain + stress_event, 2)
                    
                elif device["type"] == "tilt":
                    # Tilt with very gradual changes
                    base_tilt = random.gauss(0, 0.1)
                    drift = (timestamp - datetime.now()).days * 0.001
                    reading["tilt"] = round(base_tilt + drift, 4)
                
                readings.append(reading)
    
    return readings

def generate_predictions(sites: List[Dict[str, Any]], devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate realistic predictions"""
    predictions = []
    
    for i in range(50):  # Generate 50 predictions
        site = random.choice(sites)
        site_devices = [d for d in devices if d["site_id"] == site["_id"]]
        
        # Create prediction with realistic data
        created_at = datetime.now() - timedelta(days=random.randint(1, 30))
        risk_score = random.uniform(0.1, 0.95)
        
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        prediction = {
            "_id": f"pred-{i+1:04d}",
            "site_id": site["_id"],
            "device_ids": [d["device_id"] for d in random.sample(site_devices, min(5, len(site_devices)))],
            "risk_level": risk_level,
            "risk_score": round(risk_score, 3),
            "confidence": round(random.uniform(0.7, 0.95), 3),
            "created_at": created_at.isoformat(),
            "processed_data": {
                "rock_exposure_analysis": {
                    "percentage": round(random.uniform(60, 90), 1),
                    "confidence": round(random.uniform(0.8, 0.95), 2)
                },
                "crack_analysis": {
                    "total_cracks": random.randint(15, 45),
                    "critical_cracks": random.randint(2, 8),
                    "max_width": round(random.uniform(0.5, 3.0), 1)
                },
                "structural_analysis": {
                    "weakness_score": round(random.uniform(3.0, 9.0), 1),
                    "stability_index": round(random.uniform(0.3, 0.8), 2)
                },
                "vegetation_analysis": {
                    "coverage_percentage": round(random.uniform(5, 25), 1),
                    "health_index": round(random.uniform(0.4, 0.9), 2)
                },
                "risk_factors": [
                    {
                        "factor": random.choice([
                            "Vertical crack patterns",
                            "Weathered rock surface",
                            "Minimal vegetation support",
                            "High vibration levels",
                            "Temperature fluctuations",
                            "Rainfall saturation"
                        ]),
                        "severity": random.choice(["Low", "Medium", "High"]),
                        "confidence": round(random.uniform(0.6, 0.95), 2)
                    }
                    for _ in range(random.randint(2, 5))
                ]
            },
            "metadata": {
                "drone_mission_id": f"mission-{random.randint(1000, 9999)}",
                "total_images": random.randint(50, 200),
                "analysis_duration": round(random.uniform(120, 600), 1),
                "weather_conditions": random.choice([
                    "Clear", "Partly Cloudy", "Overcast", "Light Rain", "Heavy Rain"
                ])
            }
        }
        
        predictions.append(prediction)
    
    return predictions

def generate_alerts(predictions: List[Dict[str, Any]], devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate realistic alerts"""
    alerts = []
    
    # Generate alerts for high-risk predictions
    high_risk_predictions = [p for p in predictions if p["risk_level"] == "high"]
    
    for pred in high_risk_predictions:
        alert = {
            "_id": str(uuid.uuid4()),
            "prediction_id": pred["_id"],
            "site_id": pred["site_id"],
            "alert_type": "high_risk_prediction",
            "severity": "high",
            "message": f"High rockfall risk detected at site {pred['site_id']} with {pred['confidence']*100:.1f}% confidence",
            "created_at": pred["created_at"],
            "status": random.choice(["active", "acknowledged", "resolved"]),
            "acknowledged_by": "operator" if random.random() > 0.3 else None,
            "acknowledged_at": (datetime.fromisoformat(pred["created_at"]) + timedelta(hours=random.randint(1, 24))).isoformat() if random.random() > 0.3 else None
        }
        alerts.append(alert)
    
    # Generate device alerts
    offline_devices = [d for d in devices if d["status"] == "offline"]
    for device in offline_devices:
        alert = {
            "_id": str(uuid.uuid4()),
            "device_id": device["device_id"],
            "site_id": device["site_id"],
            "alert_type": "device_offline",
            "severity": "medium",
            "message": f"Device {device['name']} has gone offline",
            "created_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "status": random.choice(["active", "acknowledged"]),
            "acknowledged_by": "technician" if random.random() > 0.5 else None
        }
        alerts.append(alert)
    
    # Generate maintenance alerts
    for _ in range(15):
        device = random.choice(devices)
        alert = {
            "_id": str(uuid.uuid4()),
            "device_id": device["device_id"],
            "site_id": device["site_id"],
            "alert_type": random.choice(["maintenance_required", "calibration_due", "battery_low"]),
            "severity": random.choice(["low", "medium"]),
            "message": f"Maintenance required for {device['name']}",
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat(),
            "status": random.choice(["active", "acknowledged", "resolved"])
        }
        alerts.append(alert)
    
    return alerts

def main():
    """Generate complete demo dataset"""
    print("Generating comprehensive demo dataset...")
    
    # Generate all data
    sites = generate_demo_sites()
    print(f"Generated {len(sites)} mining sites")
    
    devices = generate_demo_devices(sites)
    print(f"Generated {len(devices)} monitoring devices")
    
    sensor_readings = generate_sensor_readings(devices, days=30)
    print(f"Generated {len(sensor_readings)} sensor readings")
    
    predictions = generate_predictions(sites, devices)
    print(f"Generated {len(predictions)} predictions")
    
    alerts = generate_alerts(predictions, devices)
    print(f"Generated {len(alerts)} alerts")
    
    # Save to files
    import os
    base_path = os.path.dirname(__file__)
    
    with open(os.path.join(base_path, "sites.json"), "w") as f:
        json.dump(sites, f, indent=2, default=str)
    
    with open(os.path.join(base_path, "devices.json"), "w") as f:
        json.dump(devices, f, indent=2, default=str)
    
    with open(os.path.join(base_path, "sensor_readings.json"), "w") as f:
        json.dump(sensor_readings, f, indent=2, default=str)
    
    with open(os.path.join(base_path, "predictions.json"), "w") as f:
        json.dump(predictions, f, indent=2, default=str)
    
    with open(os.path.join(base_path, "alerts.json"), "w") as f:
        json.dump(alerts, f, indent=2, default=str)
    
    # Generate summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_sites": len(sites),
        "total_devices": len(devices),
        "total_sensor_readings": len(sensor_readings),
        "total_predictions": len(predictions),
        "total_alerts": len(alerts),
        "data_timespan_days": 30,
        "high_risk_predictions": len([p for p in predictions if p["risk_level"] == "high"]),
        "active_alerts": len([a for a in alerts if a["status"] == "active"])
    }
    
    with open(os.path.join(base_path, "dataset_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("\nDataset generation completed!")
    print(f"Files saved to: {base_path}")
    print("\nSummary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()