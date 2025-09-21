"""
Demo data generation for the rockfall prediction system
"""
import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import csv

class DemoDataGenerator:
    """
    Generate realistic demo data for the rockfall prediction system
    """
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Site coordinates (example mining sites)
        self.sites = [
            {
                "id": "site-001",
                "name": "Rocky Mountain Quarry",
                "location": {"lat": 39.7392, "lng": -104.9903, "elevation": 1620},
                "area_hectares": 45.2,
                "description": "Open-pit limestone quarry with steep walls and high rockfall risk",
                "safety_protocols": [
                    "Daily visual inspections",
                    "Restricted access zones", 
                    "Emergency evacuation procedures",
                    "Weather monitoring"
                ],
                "emergency_contacts": [
                    {"name": "John Smith", "role": "Site Manager", "phone": "+1234567890", "email": "john.smith@mining.com"},
                    {"name": "Sarah Johnson", "role": "Safety Officer", "phone": "+1234567891", "email": "sarah.johnson@mining.com"}
                ],
                "status": "active"
            },
            {
                "id": "site-002", 
                "name": "Sierra Nevada Mine",
                "location": {"lat": 39.1612, "lng": -119.7674, "elevation": 1380},
                "area_hectares": 78.6,
                "description": "Large-scale copper mine with multiple extraction zones",
                "safety_protocols": [
                    "Continuous seismic monitoring",
                    "Real-time weather alerts",
                    "Automated evacuation systems",
                    "Regular geotechnical assessments"
                ],
                "emergency_contacts": [
                    {"name": "Mike Wilson", "role": "Operations Director", "phone": "+1234567892", "email": "mike.wilson@mining.com"},
                    {"name": "Lisa Brown", "role": "Emergency Coordinator", "phone": "+1234567893", "email": "lisa.brown@mining.com"}
                ],
                "status": "active"
            },
            {
                "id": "site-003",
                "name": "Desert Valley Pit",
                "location": {"lat": 36.1699, "lng": -115.1398, "elevation": 610},
                "area_hectares": 32.1,
                "description": "Sand and gravel extraction site with moderate risk profile",
                "safety_protocols": [
                    "Weekly safety briefings",
                    "Equipment maintenance checks",
                    "Weather condition monitoring"
                ],
                "emergency_contacts": [
                    {"name": "Robert Davis", "role": "Site Supervisor", "phone": "+1234567894", "email": "robert.davis@mining.com"}
                ],
                "status": "active"
            }
        ]
        
        # Sensor types and their typical reading ranges
        self.sensor_types = {
            "accelerometer": {
                "parameters": ["vibration_x", "vibration_y", "vibration_z"],
                "normal_range": [0.001, 0.02],
                "alert_threshold": 0.05,
                "critical_threshold": 0.1,
                "unit": "g"
            },
            "inclinometer": {
                "parameters": ["tilt_x", "tilt_y"],
                "normal_range": [-1.0, 1.0],
                "alert_threshold": 3.0,
                "critical_threshold": 5.0,
                "unit": "degrees"
            },
            "temperature": {
                "parameters": ["temperature"],
                "normal_range": [5, 30],
                "alert_threshold": None,
                "critical_threshold": None,
                "unit": "°C"
            },
            "weather_station": {
                "parameters": ["wind_speed", "wind_direction", "precipitation"],
                "normal_range": [0, 25],
                "alert_threshold": 30,
                "critical_threshold": 50,
                "unit": "m/s, degrees, mm"
            },
            "pressure": {
                "parameters": ["atmospheric_pressure"],
                "normal_range": [990, 1030],
                "alert_threshold": None,
                "critical_threshold": None,
                "unit": "hPa"
            },
            "humidity": {
                "parameters": ["humidity"],
                "normal_range": [20, 90],
                "alert_threshold": None,
                "critical_threshold": None,
                "unit": "%"
            },
            "seismometer": {
                "parameters": ["seismic_activity"],
                "normal_range": [0, 0.01],
                "alert_threshold": 0.05,
                "critical_threshold": 0.1,
                "unit": "g"
            },
            "gps": {
                "parameters": ["displacement_x", "displacement_y", "displacement_z"],
                "normal_range": [-0.002, 0.002],
                "alert_threshold": 0.005,
                "critical_threshold": 0.01,
                "unit": "m"
            }
        }
    
    def generate_sensor_data(self, 
                           sensor_id: str, 
                           site_id: str,
                           sensor_types: List[str],
                           days: int = 30,
                           interval_minutes: int = 15) -> List[Dict]:
        """
        Generate realistic sensor data for specified period
        """
        readings = []
        start_time = datetime.utcnow() - timedelta(days=days)
        
        # Create base patterns for different scenarios
        risk_events = self._generate_risk_events(days)
        
        for i in range(days * 24 * (60 // interval_minutes)):
            timestamp = start_time + timedelta(minutes=i * interval_minutes)
            
            # Determine current risk level based on events
            current_risk = self._get_current_risk_level(timestamp, risk_events)
            
            reading = {
                "timestamp": timestamp.isoformat(),
                "sensor_id": sensor_id,
                "site_id": site_id,
                "readings": {}
            }
            
            # Generate readings for each sensor type
            for sensor_type in sensor_types:
                if sensor_type in self.sensor_types:
                    sensor_config = self.sensor_types[sensor_type]
                    
                    for param in sensor_config["parameters"]:
                        value = self._generate_sensor_value(param, sensor_config, current_risk, timestamp)
                        reading["readings"][param] = round(value, 6)
            
            readings.append(reading)
        
        return readings
    
    def _generate_risk_events(self, days: int) -> List[Dict]:
        """
        Generate risk events throughout the time period
        """
        events = []
        
        # Generate 2-5 risk events over the period
        num_events = random.randint(2, 5)
        
        for _ in range(num_events):
            start_day = random.randint(0, days - 2)
            duration_hours = random.randint(2, 24)
            risk_level = random.choice(["low", "medium", "high", "critical"])
            
            event = {
                "start_day": start_day,
                "duration_hours": duration_hours,
                "risk_level": risk_level,
                "intensity": random.uniform(0.3, 1.0)
            }
            events.append(event)
        
        return events
    
    def _get_current_risk_level(self, timestamp: datetime, risk_events: List[Dict]) -> str:
        """
        Determine current risk level based on events
        """
        base_time = timestamp - timedelta(days=30)  # Assuming 30-day period
        current_day = (timestamp - base_time).days
        current_hour = timestamp.hour
        
        for event in risk_events:
            event_start_hour = event["start_day"] * 24
            event_end_hour = event_start_hour + event["duration_hours"]
            current_total_hour = current_day * 24 + current_hour
            
            if event_start_hour <= current_total_hour <= event_end_hour:
                return event["risk_level"]
        
        return "normal"
    
    def _generate_sensor_value(self, parameter: str, sensor_config: Dict, risk_level: str, timestamp: datetime) -> float:
        """
        Generate realistic sensor value based on risk level and time
        """
        normal_range = sensor_config["normal_range"]
        base_value = random.uniform(normal_range[0], normal_range[1])
        
        # Add time-based variations (daily cycles, weather patterns)
        time_factor = self._get_time_factor(parameter, timestamp)
        base_value *= time_factor
        
        # Adjust based on risk level
        if risk_level == "high":
            multiplier = random.uniform(1.5, 3.0)
            base_value *= multiplier
        elif risk_level == "critical":
            multiplier = random.uniform(3.0, 5.0)
            base_value *= multiplier
        elif risk_level == "medium":
            multiplier = random.uniform(1.2, 1.8)
            base_value *= multiplier
        
        # Add noise
        noise = random.gauss(0, abs(base_value) * 0.05)
        base_value += noise
        
        # Parameter-specific adjustments
        if parameter in ["vibration_x", "vibration_y", "vibration_z", "seismic_activity"]:
            base_value = abs(base_value)  # These should be positive
        elif parameter in ["wind_speed", "precipitation"]:
            base_value = max(0, base_value)  # These should be non-negative
        elif parameter == "wind_direction":
            base_value = random.uniform(0, 360)
        elif parameter == "humidity":
            base_value = max(0, min(100, base_value))
        elif parameter == "atmospheric_pressure":
            base_value = max(950, min(1050, base_value))
        
        return base_value
    
    def _get_time_factor(self, parameter: str, timestamp: datetime) -> float:
        """
        Generate time-based factors for realistic patterns
        """
        hour = timestamp.hour
        day_of_year = timestamp.timetuple().tm_yday
        
        # Daily patterns
        if parameter == "temperature":
            # Temperature varies with time of day
            return 0.8 + 0.4 * np.sin(2 * np.pi * hour / 24)
        elif parameter == "wind_speed":
            # Wind typically increases during day
            return 0.7 + 0.6 * np.sin(2 * np.pi * (hour - 6) / 24)
        elif parameter in ["vibration_x", "vibration_y", "vibration_z"]:
            # Mining activity during work hours (6 AM - 6 PM)
            if 6 <= hour <= 18:
                return 1.0 + 0.5 * random.random()
            else:
                return 0.3 + 0.2 * random.random()
        else:
            # Small random variation for other parameters
            return 0.95 + 0.1 * random.random()
    
    def generate_dem_metadata(self) -> List[Dict]:
        """
        Generate Digital Elevation Model metadata
        """
        dem_files = []
        
        for site in self.sites:
            dem_file = {
                "id": f"dem_{site['id']}",
                "site_id": site["id"],
                "filename": f"{site['id']}_elevation_model.tif",
                "file_path": f"/data/dem/{site['id']}_elevation_model.tif",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
                "file_size_mb": round(random.uniform(50, 200), 2),
                "resolution_meters": random.choice([0.5, 1.0, 2.0]),
                "coordinate_system": "WGS84 / UTM Zone 12N",
                "bbox": {
                    "min_lat": site["location"]["lat"] - 0.005,
                    "max_lat": site["location"]["lat"] + 0.005,
                    "min_lng": site["location"]["lng"] - 0.005,
                    "max_lng": site["location"]["lng"] + 0.005
                },
                "elevation_stats": {
                    "min_elevation": site["location"]["elevation"] - random.randint(50, 100),
                    "max_elevation": site["location"]["elevation"] + random.randint(100, 200),
                    "mean_elevation": site["location"]["elevation"],
                    "std_elevation": round(random.uniform(20, 50), 2)
                },
                "slope_analysis": {
                    "mean_slope": round(random.uniform(15, 45), 2),
                    "max_slope": round(random.uniform(60, 85), 2),
                    "high_risk_areas_percent": round(random.uniform(5, 25), 2)
                },
                "processing_parameters": {
                    "source": "LiDAR survey",
                    "accuracy_cm": random.choice([10, 15, 20]),
                    "collection_date": "2024-01-10",
                    "processing_software": "ArcGIS Pro 3.0"
                }
            }
            dem_files.append(dem_file)
        
        return dem_files
    
    def generate_drone_imagery_metadata(self) -> List[Dict]:
        """
        Generate drone imagery metadata
        """
        imagery_files = []
        
        # Generate multiple flights per site
        for site in self.sites:
            num_flights = random.randint(5, 15)
            
            for flight_num in range(1, num_flights + 1):
                flight_date = datetime.utcnow() - timedelta(days=random.randint(1, 90))
                
                imagery = {
                    "id": f"drone_{site['id']}_flight_{flight_num:03d}",
                    "site_id": site["id"],
                    "flight_number": flight_num,
                    "flight_date": flight_date.isoformat(),
                    "pilot": random.choice(["John Doe", "Jane Smith", "Mike Johnson"]),
                    "drone_model": random.choice(["DJI Mavic 3", "DJI Phantom 4 RTK", "Autel EVO II Pro"]),
                    "camera_specs": {
                        "resolution": random.choice(["20MP", "24MP", "48MP"]),
                        "sensor_size": random.choice(["1 inch", "Four Thirds", "APS-C"]),
                        "lens": "24-70mm equivalent"
                    },
                    "flight_parameters": {
                        "altitude_agl_m": random.randint(50, 150),
                        "ground_resolution_cm": round(random.uniform(2, 8), 2),
                        "overlap_percent": random.randint(70, 85),
                        "flight_speed_ms": round(random.uniform(3, 8), 1),
                        "flight_duration_min": random.randint(15, 45)
                    },
                    "weather_conditions": {
                        "wind_speed_ms": round(random.uniform(0, 12), 1),
                        "visibility_km": round(random.uniform(8, 20), 1),
                        "cloud_cover_percent": random.randint(0, 30),
                        "temperature_c": round(random.uniform(5, 25), 1)
                    },
                    "captured_images": {
                        "total_images": random.randint(150, 500),
                        "rgb_images": random.randint(150, 500),
                        "thermal_images": random.randint(0, 100),
                        "multispectral_images": random.randint(0, 50)
                    },
                    "analysis_results": {
                        "cracks_detected": random.randint(0, 25),
                        "loose_rocks_identified": random.randint(0, 15),
                        "vegetation_coverage_percent": round(random.uniform(0, 30), 2),
                        "erosion_areas_m2": round(random.uniform(0, 100), 2),
                        "overall_risk_score": round(random.uniform(0.1, 0.9), 3)
                    },
                    "file_info": {
                        "raw_images_gb": round(random.uniform(5, 50), 2),
                        "processed_orthomosaic_gb": round(random.uniform(1, 10), 2),
                        "point_cloud_gb": round(random.uniform(2, 20), 2),
                        "storage_location": f"/data/drone_imagery/{site['id']}/flight_{flight_num:03d}/"
                    }
                }
                imagery_files.append(imagery)
        
        return imagery_files
    
    def generate_environmental_data(self, days: int = 30) -> List[Dict]:
        """
        Generate environmental monitoring data
        """
        environmental_data = []
        start_date = datetime.utcnow() - timedelta(days=days)
        
        for day in range(days):
            date = start_date + timedelta(days=day)
            
            # Generate daily environmental summary
            env_record = {
                "date": date.date().isoformat(),
                "weather": {
                    "temperature_min_c": round(random.uniform(0, 15), 1),
                    "temperature_max_c": round(random.uniform(15, 30), 1),
                    "humidity_avg_percent": round(random.uniform(30, 80), 1),
                    "wind_speed_avg_ms": round(random.uniform(2, 15), 1),
                    "wind_gust_max_ms": round(random.uniform(8, 25), 1),
                    "precipitation_mm": round(max(0, random.gauss(2, 5)), 1),
                    "atmospheric_pressure_hpa": round(random.uniform(1000, 1030), 1),
                    "solar_radiation_wm2": round(random.uniform(100, 800), 1)
                },
                "geological": {
                    "seismic_events_count": random.randint(0, 5),
                    "max_seismic_magnitude": round(random.uniform(0, 3), 2),
                    "ground_temperature_c": round(random.uniform(8, 20), 1),
                    "soil_moisture_percent": round(random.uniform(10, 40), 1)
                },
                "air_quality": {
                    "pm10_ugm3": round(random.uniform(10, 80), 1),
                    "pm25_ugm3": round(random.uniform(5, 50), 1),
                    "dust_concentration_mgm3": round(random.uniform(0.1, 2.0), 2),
                    "visibility_km": round(random.uniform(5, 20), 1)
                },
                "risk_factors": {
                    "freeze_thaw_cycles": random.randint(0, 3),
                    "heavy_precipitation_events": random.randint(0, 2),
                    "high_wind_events": random.randint(0, 1),
                    "thermal_stress_events": random.randint(0, 2)
                }
            }
            environmental_data.append(env_record)
        
        return environmental_data
    
    def generate_historical_events(self) -> List[Dict]:
        """
        Generate historical rockfall and safety events
        """
        events = []
        
        # Generate events over the past 2 years
        start_date = datetime.utcnow() - timedelta(days=730)
        
        for _ in range(random.randint(20, 50)):
            event_date = start_date + timedelta(days=random.randint(0, 730))
            
            event_type = random.choice([
                "rockfall_minor", "rockfall_major", "equipment_failure",
                "weather_related", "geological_activity", "safety_incident"
            ])
            
            event = {
                "id": f"event_{len(events) + 1:04d}",
                "date": event_date.isoformat(),
                "site_id": random.choice([site["id"] for site in self.sites]),
                "event_type": event_type,
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "description": self._generate_event_description(event_type),
                "location": {
                    "zone": random.choice(["A", "B", "C", "D"]),
                    "coordinates": {
                        "lat": random.uniform(39.735, 39.745),
                        "lng": random.uniform(-104.995, -104.985)
                    }
                },
                "impact": {
                    "area_affected_m2": random.randint(10, 1000),
                    "volume_displaced_m3": round(random.uniform(0.1, 100), 2),
                    "personnel_evacuated": random.randint(0, 20),
                    "equipment_damaged": random.choice([True, False]),
                    "production_hours_lost": random.randint(0, 48)
                },
                "weather_conditions": {
                    "temperature_c": round(random.uniform(-10, 35), 1),
                    "wind_speed_ms": round(random.uniform(0, 20), 1),
                    "precipitation_mm": round(random.uniform(0, 50), 1),
                    "conditions": random.choice(["clear", "cloudy", "rainy", "snowy", "windy"])
                },
                "response_actions": self._generate_response_actions(event_type),
                "lessons_learned": f"Analysis of {event_type} event - improved monitoring protocols implemented"
            }
            events.append(event)
        
        return sorted(events, key=lambda x: x["date"])
    
    def _generate_event_description(self, event_type: str) -> str:
        """Generate realistic event descriptions"""
        descriptions = {
            "rockfall_minor": "Small rockfall event with loose debris falling from slope face",
            "rockfall_major": "Significant rockfall involving large boulder displacement",
            "equipment_failure": "Sensor equipment malfunction affecting monitoring capabilities", 
            "weather_related": "Weather-induced slope instability requiring safety measures",
            "geological_activity": "Seismic activity detected affecting slope stability",
            "safety_incident": "Safety protocol activation due to elevated risk conditions"
        }
        return descriptions.get(event_type, "Unspecified mining safety event")
    
    def _generate_response_actions(self, event_type: str) -> List[str]:
        """Generate appropriate response actions"""
        actions = {
            "rockfall_minor": [
                "Area inspection conducted",
                "Debris cleared from access roads",
                "Increased monitoring frequency"
            ],
            "rockfall_major": [
                "Immediate area evacuation",
                "Emergency response team deployed",
                "Geotechnical assessment initiated",
                "Production suspended in affected zone"
            ],
            "equipment_failure": [
                "Equipment inspection and repair",
                "Backup monitoring systems activated",
                "Technical support contacted"
            ],
            "weather_related": [
                "Weather monitoring increased",
                "Preventive safety measures implemented",
                "Personnel advised of conditions"
            ],
            "geological_activity": [
                "Seismic monitoring enhanced",
                "Structural stability assessment",
                "Emergency protocols reviewed"
            ],
            "safety_incident": [
                "Safety protocols activated",
                "Personnel briefing conducted",
                "Risk assessment updated"
            ]
        }
        return actions.get(event_type, ["Standard response procedures followed"])
    
    def save_all_demo_data(self):
        """
        Generate and save all demo data to files
        """
        print("Generating comprehensive demo data...")
        
        # Generate and save site data
        with open(os.path.join(self.output_dir, "sites.json"), "w") as f:
            json.dump(self.sites, f, indent=2)
        print(f"✓ Generated {len(self.sites)} mining sites")
        
        # Generate sensors for each site
        all_sensors = []
        all_sensor_data = []
        
        for site in self.sites:
            # Create 3-5 sensors per site
            num_sensors = random.randint(3, 5)
            
            for sensor_num in range(1, num_sensors + 1):
                sensor_id = f"sensor-{site['id'][-3:]}-{sensor_num:02d}"
                
                # Assign random sensor types
                assigned_types = random.sample(list(self.sensor_types.keys()), random.randint(2, 4))
                
                # Create sensor location near site
                sensor_location = {
                    "lat": site["location"]["lat"] + random.uniform(-0.002, 0.002),
                    "lng": site["location"]["lng"] + random.uniform(-0.002, 0.002),
                    "elevation": site["location"]["elevation"] + random.randint(-20, 50)
                }
                
                sensor = {
                    "id": sensor_id,
                    "site_id": site["id"],
                    "name": f"{site['name']} Sensor {sensor_num}",
                    "location": sensor_location,
                    "sensor_types": assigned_types,
                    "status": random.choice(["active", "active", "active", "maintenance"]),
                    "installation_date": (datetime.utcnow() - timedelta(days=random.randint(30, 365))).isoformat(),
                    "last_reading": (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat()
                }
                all_sensors.append(sensor)
                
                # Generate sensor data
                sensor_data = self.generate_sensor_data(sensor_id, site["id"], assigned_types)
                all_sensor_data.extend(sensor_data)
        
        # Save sensor data
        with open(os.path.join(self.output_dir, "sensors.json"), "w") as f:
            json.dump(all_sensors, f, indent=2)
        print(f"✓ Generated {len(all_sensors)} sensors")
        
        # Save sensor readings (split into chunks for better performance)
        chunk_size = 10000
        for i, chunk_start in enumerate(range(0, len(all_sensor_data), chunk_size)):
            chunk = all_sensor_data[chunk_start:chunk_start + chunk_size]
            filename = f"sensor_readings_chunk_{i+1:02d}.json"
            with open(os.path.join(self.output_dir, filename), "w") as f:
                json.dump(chunk, f, indent=2)
        print(f"✓ Generated {len(all_sensor_data)} sensor readings in {(len(all_sensor_data) // chunk_size) + 1} files")
        
        # Generate and save DEM metadata
        dem_data = self.generate_dem_metadata()
        with open(os.path.join(self.output_dir, "dem_metadata.json"), "w") as f:
            json.dump(dem_data, f, indent=2)
        print(f"✓ Generated {len(dem_data)} DEM files metadata")
        
        # Generate and save drone imagery metadata
        drone_data = self.generate_drone_imagery_metadata()
        with open(os.path.join(self.output_dir, "drone_imagery_metadata.json"), "w") as f:
            json.dump(drone_data, f, indent=2)
        print(f"✓ Generated {len(drone_data)} drone flight records")
        
        # Generate and save environmental data
        env_data = self.generate_environmental_data()
        with open(os.path.join(self.output_dir, "environmental_data.json"), "w") as f:
            json.dump(env_data, f, indent=2)
        print(f"✓ Generated {len(env_data)} days of environmental data")
        
        # Generate and save historical events
        events_data = self.generate_historical_events()
        with open(os.path.join(self.output_dir, "historical_events.json"), "w") as f:
            json.dump(events_data, f, indent=2)
        print(f"✓ Generated {len(events_data)} historical events")
        
        # Generate summary statistics
        summary = {
            "generation_date": datetime.utcnow().isoformat(),
            "total_sites": len(self.sites),
            "total_sensors": len(all_sensors),
            "total_sensor_readings": len(all_sensor_data),
            "total_dem_files": len(dem_data),
            "total_drone_flights": len(drone_data),
            "environmental_data_days": len(env_data),
            "historical_events": len(events_data),
            "data_period_days": 30,
            "sensor_reading_interval_minutes": 15
        }
        
        with open(os.path.join(self.output_dir, "data_summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
        
        print("\n📊 Demo Data Generation Complete!")
        print(f"📁 All files saved to: {os.path.abspath(self.output_dir)}")
        print("\n📈 Summary:")
        for key, value in summary.items():
            if key != "generation_date":
                print(f"   {key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    # Generate demo data
    generator = DemoDataGenerator("data")
    generator.save_all_demo_data()