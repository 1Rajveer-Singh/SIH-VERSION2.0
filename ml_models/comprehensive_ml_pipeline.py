"""
Enhanced Rockfall Prediction ML Pipeline
Comprehensive AI/ML system combining computer vision and sensor data analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from dataclasses import dataclass
import json

# Simulate ML libraries (in production, use actual libraries)
try:
    # import cv2
    # import tensorflow as tf
    # import torch
    # import xgboost as xgb
    # import lightgbm as lgb
    # import shap
    pass
except ImportError:
    # Fallback for demo environment
    pass

logger = logging.getLogger(__name__)

@dataclass
class DroneImageData:
    """Drone image data structure"""
    image_id: str
    image_type: str  # 'DEM', 'orthophoto', 'pointcloud', 'aerial_photo'
    file_path: str
    coordinates: Optional[Dict[str, float]] = None
    elevation: Optional[float] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SensorDataPoint:
    """Individual sensor reading"""
    timestamp: datetime
    sensor_id: str
    sensor_type: str
    location: Optional[Dict[str, float]] = None
    measurements: Dict[str, float] = None

@dataclass
class ExtractedFeatures:
    """Features extracted from various data sources"""
    # Geometric features (from drone imagery)
    slope_angle: Optional[float] = None
    bench_face_height: Optional[float] = None
    bench_width: Optional[float] = None
    surface_roughness: Optional[float] = None
    
    # Structural features (computer vision)
    crack_density: Optional[float] = None
    crack_length_total: Optional[float] = None
    crack_width_max: Optional[float] = None
    surface_displacement: Optional[float] = None
    vegetation_coverage: Optional[float] = None
    
    # Geotechnical features (sensors)
    pore_pressure_avg: Optional[float] = None
    pore_pressure_max: Optional[float] = None
    subsurface_displacement: Optional[float] = None
    acceleration_max: Optional[float] = None
    rock_mass_rating: Optional[int] = None
    unconfined_compressive_strength: Optional[float] = None
    
    # Environmental features
    rainfall_24h: Optional[float] = None
    rainfall_7d: Optional[float] = None
    temperature_avg: Optional[float] = None
    temperature_range: Optional[float] = None
    seismic_activity_count: Optional[int] = None
    seismic_magnitude_max: Optional[float] = None
    
    # Temporal features
    time_since_last_event: Optional[float] = None
    seasonal_factor: Optional[float] = None
    weather_pattern_index: Optional[float] = None

@dataclass
class PredictionResult:
    """ML prediction result with explainability"""
    probability: float
    risk_level: str
    confidence: float
    alert_level: str
    contributing_factors: List[Dict[str, Any]]
    model_version: str
    prediction_timestamp: datetime
    shap_values: Optional[Dict[str, float]] = None
    recommendations: List[str] = None

class ComputerVisionProcessor:
    """Computer vision processing for drone imagery analysis"""
    
    def __init__(self):
        """Initialize computer vision models"""
        self.crack_detection_model = None
        self.dem_analysis_model = None
        self.surface_analysis_model = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained computer vision models"""
        # In production, load actual models:
        # self.crack_detection_model = tf.keras.models.load_model('crack_detection_cnn.h5')
        # self.dem_analysis_model = torch.load('dem_analysis_resnet.pth')
        logger.info("Computer vision models loaded (simulated)")
    
    async def process_aerial_photos(self, images: List[DroneImageData]) -> Dict[str, Any]:
        """Process aerial photographs for structural analysis"""
        logger.info(f"Processing {len(images)} aerial photographs")
        
        # Simulate computer vision processing
        await asyncio.sleep(1)  # Simulate processing time
        
        # Mock crack detection results
        crack_features = {
            "crack_density": len(images) * 0.8 + np.random.normal(0, 0.2),
            "crack_length_total": len(images) * 15.5 + np.random.normal(0, 5),
            "crack_width_max": 0.5 + len(images) * 0.1 + np.random.normal(0, 0.1),
            "surface_displacement": 0.02 + len(images) * 0.005,
            "vegetation_coverage": max(0, min(1, 0.3 - len(images) * 0.02))
        }
        
        return crack_features
    
    async def process_dem_data(self, dem_images: List[DroneImageData]) -> Dict[str, Any]:
        """Process Digital Elevation Model data"""
        logger.info(f"Processing {len(dem_images)} DEM images")
        
        await asyncio.sleep(1.5)  # Simulate DEM processing
        
        # Mock DEM analysis results
        geometric_features = {
            "slope_angle": 65 + len(dem_images) * 2 + np.random.normal(0, 3),
            "bench_face_height": 12 + len(dem_images) * 0.8 + np.random.normal(0, 1),
            "bench_width": 8 + len(dem_images) * 0.5 + np.random.normal(0, 0.5),
            "surface_roughness": 0.6 + len(dem_images) * 0.05 + np.random.normal(0, 0.1)
        }
        
        return geometric_features
    
    async def process_orthophotos(self, ortho_images: List[DroneImageData]) -> Dict[str, Any]:
        """Process orthophoto data for detailed surface analysis"""
        logger.info(f"Processing {len(ortho_images)} orthophotos")
        
        await asyncio.sleep(0.8)
        
        # Mock orthophoto analysis
        surface_features = {
            "surface_texture_variance": 0.4 + len(ortho_images) * 0.02,
            "moisture_content_estimate": 0.15 + len(ortho_images) * 0.01,
            "weathering_index": 0.5 + len(ortho_images) * 0.03
        }
        
        return surface_features

class SensorDataProcessor:
    """Advanced sensor data processing and analysis"""
    
    def __init__(self):
        """Initialize sensor data processing"""
        self.calibration_factors = {
            "pore_pressure": 1.0,
            "acceleration": 1.0,
            "displacement": 1.0,
            "temperature": 1.0,
            "rainfall": 1.0
        }
    
    async def process_geotechnical_sensors(self, sensor_data: List[SensorDataPoint]) -> Dict[str, Any]:
        """Process geotechnical sensor readings"""
        logger.info(f"Processing {len(sensor_data)} geotechnical sensor readings")
        
        if not sensor_data:
            return {}
        
        # Extract and analyze pore pressure data
        pore_pressures = [
            point.measurements.get("porePressure", 0) 
            for point in sensor_data 
            if point.measurements and "porePressure" in point.measurements
        ]
        
        # Extract displacement data
        displacements = [
            point.measurements.get("subsurfaceDisplacement", 0)
            for point in sensor_data
            if point.measurements and "subsurfaceDisplacement" in point.measurements
        ]
        
        # Extract acceleration data
        accelerations = [
            point.measurements.get("acceleration", 0)
            for point in sensor_data
            if point.measurements and "acceleration" in point.measurements
        ]
        
        geotechnical_features = {
            "pore_pressure_avg": np.mean(pore_pressures) if pore_pressures else 0,
            "pore_pressure_max": np.max(pore_pressures) if pore_pressures else 0,
            "pore_pressure_trend": self._calculate_trend(pore_pressures) if len(pore_pressures) > 3 else 0,
            "subsurface_displacement": np.max(displacements) if displacements else 0,
            "displacement_rate": self._calculate_rate(displacements, sensor_data) if len(displacements) > 2 else 0,
            "acceleration_max": np.max(accelerations) if accelerations else 0,
            "vibration_frequency": self._analyze_vibration_frequency(accelerations) if accelerations else 0
        }
        
        return geotechnical_features
    
    async def process_environmental_sensors(self, sensor_data: List[SensorDataPoint]) -> Dict[str, Any]:
        """Process environmental sensor readings"""
        logger.info(f"Processing environmental sensor data")
        
        if not sensor_data:
            return {}
        
        # Extract environmental measurements
        rainfalls = [
            point.measurements.get("rainfall", 0)
            for point in sensor_data
            if point.measurements and "rainfall" in point.measurements
        ]
        
        temperatures = [
            point.measurements.get("temperature", 20)
            for point in sensor_data
            if point.measurements and "temperature" in point.measurements
        ]
        
        seismic_activities = [
            point.measurements.get("seismicActivity", 0)
            for point in sensor_data
            if point.measurements and "seismicActivity" in point.measurements
        ]
        
        # Calculate time-based features
        now = datetime.utcnow()
        recent_data = [p for p in sensor_data if (now - p.timestamp).days <= 7]
        
        environmental_features = {
            "rainfall_24h": self._sum_last_n_hours(rainfalls, sensor_data, 24),
            "rainfall_7d": sum(rainfalls) if rainfalls else 0,
            "temperature_avg": np.mean(temperatures) if temperatures else 20,
            "temperature_range": (np.max(temperatures) - np.min(temperatures)) if len(temperatures) > 1 else 0,
            "seismic_activity_count": len([s for s in seismic_activities if s > 2.0]),
            "seismic_magnitude_max": np.max(seismic_activities) if seismic_activities else 0
        }
        
        return environmental_features
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in time series data"""
        if len(values) < 2:
            return 0
        
        # Simple linear trend calculation
        x = np.arange(len(values))
        return np.polyfit(x, values, 1)[0] if len(values) > 1 else 0
    
    def _calculate_rate(self, values: List[float], sensor_data: List[SensorDataPoint]) -> float:
        """Calculate rate of change"""
        if len(values) < 2:
            return 0
        
        # Calculate rate based on time differences
        time_diff = (sensor_data[-1].timestamp - sensor_data[0].timestamp).total_seconds() / 3600  # hours
        value_diff = values[-1] - values[0]
        
        return value_diff / time_diff if time_diff > 0 else 0
    
    def _analyze_vibration_frequency(self, accelerations: List[float]) -> float:
        """Analyze vibration frequency patterns"""
        if len(accelerations) < 10:
            return 0
        
        # Simple frequency analysis (in production, use FFT)
        return np.std(accelerations) if accelerations else 0
    
    def _sum_last_n_hours(self, values: List[float], sensor_data: List[SensorDataPoint], hours: int) -> float:
        """Sum values from last N hours"""
        if not values or not sensor_data:
            return 0
        
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=hours)
        
        recent_values = [
            values[i] for i, point in enumerate(sensor_data)
            if i < len(values) and point.timestamp >= cutoff_time
        ]
        
        return sum(recent_values)

class HybridMLModel:
    """Hybrid ML model combining computer vision and sensor data"""
    
    def __init__(self):
        """Initialize hybrid ML model"""
        self.cnn_model = None  # For image features
        self.xgboost_model = None  # For tabular sensor data
        self.fusion_model = None  # For combining predictions
        self.feature_importance = {}
        self.model_version = "v2.1.3"
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained ML models"""
        # In production:
        # self.cnn_model = tf.keras.models.load_model('rockfall_cnn_v2.h5')
        # self.xgboost_model = xgb.Booster()
        # self.xgboost_model.load_model('rockfall_xgb_v2.json')
        # self.fusion_model = tf.keras.models.load_model('fusion_ensemble_v2.h5')
        
        logger.info("Hybrid ML models loaded (simulated)")
    
    async def predict_rockfall_risk(self, features: ExtractedFeatures) -> PredictionResult:
        """Make comprehensive rockfall risk prediction"""
        logger.info("Running hybrid ML prediction pipeline")
        
        # Simulate ML inference time
        await asyncio.sleep(0.5)
        
        # Convert features to prediction inputs
        feature_vector = self._features_to_vector(features)
        
        # Computer vision prediction (for image-based features)
        vision_prediction = await self._cnn_prediction(feature_vector)
        
        # Sensor data prediction (for tabular features)
        sensor_prediction = await self._xgboost_prediction(feature_vector)
        
        # Fusion prediction
        final_prediction = await self._fusion_prediction(vision_prediction, sensor_prediction)
        
        # Generate SHAP explanations
        shap_values = self._generate_shap_values(feature_vector)
        
        # Create contributing factors with importance scores
        contributing_factors = self._create_contributing_factors(features, shap_values)
        
        # Determine risk and alert levels
        risk_level, alert_level = self._determine_risk_levels(final_prediction["probability"])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(features, final_prediction, contributing_factors)
        
        return PredictionResult(
            probability=final_prediction["probability"],
            risk_level=risk_level,
            confidence=final_prediction["confidence"],
            alert_level=alert_level,
            contributing_factors=contributing_factors,
            model_version=self.model_version,
            prediction_timestamp=datetime.utcnow(),
            shap_values=shap_values,
            recommendations=recommendations
        )
    
    def _features_to_vector(self, features: ExtractedFeatures) -> Dict[str, float]:
        """Convert ExtractedFeatures to model input vector"""
        feature_dict = {
            # Geometric features
            "slope_angle": features.slope_angle or 45.0,
            "bench_face_height": features.bench_face_height or 10.0,
            "bench_width": features.bench_width or 8.0,
            "surface_roughness": features.surface_roughness or 0.5,
            
            # Structural features
            "crack_density": features.crack_density or 0.0,
            "crack_length_total": features.crack_length_total or 0.0,
            "crack_width_max": features.crack_width_max or 0.0,
            "surface_displacement": features.surface_displacement or 0.0,
            
            # Geotechnical features
            "pore_pressure_avg": features.pore_pressure_avg or 30.0,
            "pore_pressure_max": features.pore_pressure_max or 40.0,
            "subsurface_displacement": features.subsurface_displacement or 0.0,
            "acceleration_max": features.acceleration_max or 0.0,
            "rock_mass_rating": features.rock_mass_rating or 60.0,
            "unconfined_compressive_strength": features.unconfined_compressive_strength or 50.0,
            
            # Environmental features
            "rainfall_24h": features.rainfall_24h or 0.0,
            "rainfall_7d": features.rainfall_7d or 0.0,
            "temperature_avg": features.temperature_avg or 20.0,
            "seismic_activity_count": features.seismic_activity_count or 0.0,
            "seismic_magnitude_max": features.seismic_magnitude_max or 0.0,
            
            # Temporal features
            "time_since_last_event": features.time_since_last_event or 365.0,
            "seasonal_factor": features.seasonal_factor or 0.5
        }
        
        return feature_dict
    
    async def _cnn_prediction(self, features: Dict[str, float]) -> Dict[str, float]:
        """Computer vision model prediction"""
        # Simulate CNN inference for image-based features
        geometric_risk = (
            (features["slope_angle"] - 45) / 45 * 0.4 +
            (features["crack_density"]) / 5.0 * 0.3 +
            (features["surface_displacement"]) / 0.1 * 0.3
        )
        
        return {
            "probability": max(0.0, min(1.0, geometric_risk)),
            "confidence": 0.85
        }
    
    async def _xgboost_prediction(self, features: Dict[str, float]) -> Dict[str, float]:
        """XGBoost model prediction for sensor data"""
        # Simulate XGBoost inference for tabular sensor features
        sensor_risk = (
            (features["pore_pressure_avg"] - 30) / 50 * 0.3 +
            (features["rainfall_7d"]) / 100 * 0.25 +
            (features["seismic_activity_count"]) / 10 * 0.2 +
            (features["acceleration_max"]) / 1.0 * 0.25
        )
        
        return {
            "probability": max(0.0, min(1.0, sensor_risk)),
            "confidence": 0.88
        }
    
    async def _fusion_prediction(self, vision_pred: Dict[str, float], sensor_pred: Dict[str, float]) -> Dict[str, float]:
        """Fusion model combining vision and sensor predictions"""
        # Weighted ensemble of predictions
        vision_weight = 0.6
        sensor_weight = 0.4
        
        fused_probability = (
            vision_pred["probability"] * vision_weight +
            sensor_pred["probability"] * sensor_weight
        )
        
        fused_confidence = (
            vision_pred["confidence"] * vision_weight +
            sensor_pred["confidence"] * sensor_weight
        )
        
        return {
            "probability": fused_probability,
            "confidence": fused_confidence
        }
    
    def _generate_shap_values(self, features: Dict[str, float]) -> Dict[str, float]:
        """Generate SHAP values for explainable AI"""
        # Simulate SHAP value calculation
        # In production: shap_values = explainer.shap_values(features)
        
        total_impact = sum(abs(v) for v in features.values())
        normalized_impact = {k: abs(v) / total_impact if total_impact > 0 else 0 for k, v in features.items()}
        
        # Select top contributing features
        sorted_features = sorted(normalized_impact.items(), key=lambda x: x[1], reverse=True)
        top_features = dict(sorted_features[:8])  # Top 8 contributing features
        
        return top_features
    
    def _create_contributing_factors(self, features: ExtractedFeatures, shap_values: Dict[str, float]) -> List[Dict[str, Any]]:
        """Create contributing factors with importance and categories"""
        factor_mapping = {
            "slope_angle": ("Slope Angle", "geometric", f"{features.slope_angle:.1f}°"),
            "crack_density": ("Crack Density", "geometric", f"{features.crack_density:.1f}/m²"),
            "pore_pressure_avg": ("Pore Pressure", "geotechnical", f"{features.pore_pressure_avg:.1f} kPa"),
            "rainfall_7d": ("7-Day Rainfall", "environmental", f"{features.rainfall_7d:.1f}mm"),
            "seismic_activity_count": ("Seismic Events", "environmental", f"{features.seismic_activity_count} events"),
            "surface_displacement": ("Surface Displacement", "geometric", f"{features.surface_displacement:.3f}m"),
            "acceleration_max": ("Max Acceleration", "geotechnical", f"{features.acceleration_max:.3f}g"),
            "rock_mass_rating": ("Rock Mass Rating", "geotechnical", f"{features.rock_mass_rating}")
        }
        
        contributing_factors = []
        for feature_name, importance in shap_values.items():
            if feature_name in factor_mapping and importance > 0.05:  # Only significant factors
                name, category, value = factor_mapping[feature_name]
                contributing_factors.append({
                    "factor": name,
                    "importance": importance,
                    "value": value,
                    "category": category
                })
        
        return contributing_factors
    
    def _determine_risk_levels(self, probability: float) -> Tuple[str, str]:
        """Determine risk and alert levels based on probability"""
        if probability >= 0.8:
            return "critical", "evacuation"
        elif probability >= 0.6:
            return "high", "urgent"
        elif probability >= 0.4:
            return "medium", "caution"
        else:
            return "low", "monitoring"
    
    def _generate_recommendations(self, features: ExtractedFeatures, prediction: Dict[str, float], 
                                 contributing_factors: List[Dict[str, Any]]) -> List[str]:
        """Generate specific recommendations based on analysis"""
        recommendations = []
        prob = prediction["probability"]
        
        # High-level risk recommendations
        if prob >= 0.8:
            recommendations.extend([
                "IMMEDIATE EVACUATION of personnel from high-risk zones",
                "Deploy emergency response teams",
                "Implement continuous real-time monitoring"
            ])
        elif prob >= 0.6:
            recommendations.extend([
                "Increase monitoring frequency to every 15 minutes",
                "Restrict access to identified risk areas",
                "Prepare evacuation procedures"
            ])
        elif prob >= 0.4:
            recommendations.extend([
                "Enhance monitoring to hourly intervals",
                "Review and update safety protocols",
                "Conduct detailed geological assessment"
            ])
        
        # Feature-specific recommendations
        for factor in contributing_factors:
            factor_name = factor["factor"]
            
            if factor_name == "Slope Angle" and features.slope_angle and features.slope_angle > 65:
                recommendations.append("Consider slope angle reduction through controlled blasting")
            
            if factor_name == "Crack Density" and features.crack_density and features.crack_density > 2.0:
                recommendations.append("Install precision crack monitoring with automated alerts")
            
            if factor_name == "Pore Pressure" and features.pore_pressure_avg and features.pore_pressure_avg > 45:
                recommendations.append("Implement drainage improvements to reduce pore pressure")
            
            if factor_name == "7-Day Rainfall" and features.rainfall_7d and features.rainfall_7d > 50:
                recommendations.append("Enhance surface drainage and water management systems")
            
            if factor_name == "Seismic Events" and features.seismic_activity_count and features.seismic_activity_count > 3:
                recommendations.append("Correlate seismic data with slope stability measurements")
        
        # Default recommendations if none specific
        if not recommendations:
            recommendations = [
                "Continue routine monitoring protocols",
                "Maintain current safety measures",
                "Schedule next detailed inspection within standard timeframe"
            ]
        
        return recommendations[:6]  # Limit to 6 recommendations

class RockfallPredictionPipeline:
    """Complete rockfall prediction pipeline orchestrator"""
    
    def __init__(self):
        """Initialize the comprehensive prediction pipeline"""
        self.cv_processor = ComputerVisionProcessor()
        self.sensor_processor = SensorDataProcessor()
        self.ml_model = HybridMLModel()
        logger.info("Rockfall prediction pipeline initialized")
    
    async def run_comprehensive_analysis(self, drone_images: List[DroneImageData], 
                                       sensor_data: List[SensorDataPoint]) -> PredictionResult:
        """Run complete analysis pipeline"""
        logger.info("Starting comprehensive rockfall prediction analysis")
        
        # Stage 1: Process drone imagery
        image_features = await self._process_all_drone_images(drone_images)
        
        # Stage 2: Process sensor data
        sensor_features = await self._process_all_sensor_data(sensor_data)
        
        # Stage 3: Combine features
        combined_features = self._combine_features(image_features, sensor_features)
        
        # Stage 4: ML prediction
        prediction_result = await self.ml_model.predict_rockfall_risk(combined_features)
        
        logger.info(f"Analysis completed. Risk level: {prediction_result.risk_level}, "
                   f"Probability: {prediction_result.probability:.3f}")
        
        return prediction_result
    
    async def _process_all_drone_images(self, drone_images: List[DroneImageData]) -> Dict[str, Any]:
        """Process all drone images and extract features"""
        if not drone_images:
            return {}
        
        # Categorize images by type
        aerial_photos = [img for img in drone_images if img.image_type == 'aerial_photo']
        dem_images = [img for img in drone_images if img.image_type == 'DEM']
        orthophotos = [img for img in drone_images if img.image_type == 'orthophoto']
        
        # Process each category
        tasks = []
        if aerial_photos:
            tasks.append(self.cv_processor.process_aerial_photos(aerial_photos))
        if dem_images:
            tasks.append(self.cv_processor.process_dem_data(dem_images))
        if orthophotos:
            tasks.append(self.cv_processor.process_orthophotos(orthophotos))
        
        # Combine results
        image_features = {}
        if tasks:
            results = await asyncio.gather(*tasks)
            for result in results:
                image_features.update(result)
        
        return image_features
    
    async def _process_all_sensor_data(self, sensor_data: List[SensorDataPoint]) -> Dict[str, Any]:
        """Process all sensor data and extract features"""
        if not sensor_data:
            return {}
        
        # Process geotechnical and environmental sensors
        geotechnical_task = self.sensor_processor.process_geotechnical_sensors(sensor_data)
        environmental_task = self.sensor_processor.process_environmental_sensors(sensor_data)
        
        geotechnical_features, environmental_features = await asyncio.gather(
            geotechnical_task, environmental_task
        )
        
        # Combine sensor features
        sensor_features = {}
        sensor_features.update(geotechnical_features)
        sensor_features.update(environmental_features)
        
        return sensor_features
    
    def _combine_features(self, image_features: Dict[str, Any], sensor_features: Dict[str, Any]) -> ExtractedFeatures:
        """Combine image and sensor features into unified feature set"""
        # Create comprehensive feature object
        features = ExtractedFeatures(
            # Geometric features (from images)
            slope_angle=image_features.get("slope_angle"),
            bench_face_height=image_features.get("bench_face_height"),
            bench_width=image_features.get("bench_width"),
            surface_roughness=image_features.get("surface_roughness"),
            
            # Structural features (from computer vision)
            crack_density=image_features.get("crack_density"),
            crack_length_total=image_features.get("crack_length_total"),
            crack_width_max=image_features.get("crack_width_max"),
            surface_displacement=image_features.get("surface_displacement"),
            vegetation_coverage=image_features.get("vegetation_coverage"),
            
            # Geotechnical features (from sensors)
            pore_pressure_avg=sensor_features.get("pore_pressure_avg"),
            pore_pressure_max=sensor_features.get("pore_pressure_max"),
            subsurface_displacement=sensor_features.get("subsurface_displacement"),
            acceleration_max=sensor_features.get("acceleration_max"),
            
            # Environmental features (from sensors)
            rainfall_24h=sensor_features.get("rainfall_24h"),
            rainfall_7d=sensor_features.get("rainfall_7d"),
            temperature_avg=sensor_features.get("temperature_avg"),
            temperature_range=sensor_features.get("temperature_range"),
            seismic_activity_count=sensor_features.get("seismic_activity_count"),
            seismic_magnitude_max=sensor_features.get("seismic_magnitude_max"),
            
            # Temporal features (calculated)
            seasonal_factor=self._calculate_seasonal_factor(),
            time_since_last_event=365.0  # Default: 1 year since last event
        )
        
        return features
    
    def _calculate_seasonal_factor(self) -> float:
        """Calculate seasonal factor based on current date"""
        current_month = datetime.utcnow().month
        
        # Higher risk in wet seasons (assuming southern hemisphere mining)
        if current_month in [5, 6, 7, 8]:  # Winter months (wet season)
            return 0.8
        elif current_month in [11, 12, 1, 2]:  # Summer months (dry season)
            return 0.3
        else:  # Transition months
            return 0.5

# Export main pipeline class
__all__ = ['RockfallPredictionPipeline', 'DroneImageData', 'SensorDataPoint', 'PredictionResult']