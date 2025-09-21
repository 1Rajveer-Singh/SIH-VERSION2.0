"""
Data preprocessing utilities for ML models
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SensorDataPreprocessor:
    """
    Preprocessor for sensor data to prepare it for ML models
    """
    
    def __init__(self):
        self.feature_columns = [
            'vibration_x', 'vibration_y', 'vibration_z',
            'tilt_x', 'tilt_y', 'temperature',
            'wind_speed', 'wind_direction', 'precipitation',
            'atmospheric_pressure', 'humidity',
            'seismic_activity', 'displacement_x', 'displacement_y', 'displacement_z'
        ]
        
        self.engineered_features = [
            'vibration_magnitude', 'tilt_magnitude', 'displacement_magnitude',
            'weather_severity_index', 'stability_index'
        ]
    
    def clean_sensor_data(self, data: List[Dict]) -> pd.DataFrame:
        """
        Clean and validate sensor data
        """
        try:
            df = pd.DataFrame(data)
            
            # Handle missing timestamps
            if 'timestamp' not in df.columns:
                df['timestamp'] = pd.date_range(start=datetime.utcnow(), periods=len(df), freq='15min')
            else:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Fill missing feature columns with 0
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0.0
                else:
                    # Handle missing values
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
            # Remove outliers using IQR method
            df = self._remove_outliers(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning sensor data: {e}")
            raise
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove statistical outliers using IQR method
        """
        for col in self.feature_columns:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                # Define outlier bounds
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Cap outliers instead of removing them
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create engineered features from raw sensor data
        """
        try:
            # Vibration magnitude
            df['vibration_magnitude'] = np.sqrt(
                df['vibration_x']**2 + df['vibration_y']**2 + df['vibration_z']**2
            )
            
            # Tilt magnitude
            df['tilt_magnitude'] = np.sqrt(
                df['tilt_x']**2 + df['tilt_y']**2
            )
            
            # Displacement magnitude
            df['displacement_magnitude'] = np.sqrt(
                df['displacement_x']**2 + df['displacement_y']**2 + df['displacement_z']**2
            )
            
            # Weather severity index
            df['weather_severity_index'] = (
                (df['wind_speed'] / 30.0) * 0.3 +
                (df['precipitation'] / 20.0) * 0.5 +
                (abs(df['atmospheric_pressure'] - 1013) / 50.0) * 0.2
            ).clip(0, 1)
            
            # Stability index (lower means more unstable)
            df['stability_index'] = 1.0 - (
                (df['vibration_magnitude'] / 0.1) * 0.4 +
                (df['tilt_magnitude'] / 5.0) * 0.3 +
                (df['seismic_activity'] / 0.1) * 0.3
            ).clip(0, 1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error engineering features: {e}")
            raise
    
    def create_time_windows(self, df: pd.DataFrame, window_size: int = 96) -> List[np.ndarray]:
        """
        Create sliding time windows for sequence-based models
        window_size: number of readings to include (e.g., 96 = 24 hours with 15-min intervals)
        """
        try:
            all_features = self.feature_columns + self.engineered_features
            
            # Ensure all features exist
            for feature in all_features:
                if feature not in df.columns:
                    df[feature] = 0.0
            
            windows = []
            feature_data = df[all_features].values
            
            for i in range(len(feature_data) - window_size + 1):
                window = feature_data[i:i + window_size]
                windows.append(window)
            
            return windows
            
        except Exception as e:
            logger.error(f"Error creating time windows: {e}")
            raise
    
    def calculate_risk_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate various risk indicators from sensor data
        """
        try:
            indicators = {}
            
            # Recent trend analysis (last 24 readings)
            recent_data = df.tail(24) if len(df) >= 24 else df
            
            # Vibration trend
            if len(recent_data) > 1:
                vibration_trend = np.polyfit(range(len(recent_data)), recent_data['vibration_magnitude'], 1)[0]
                indicators['vibration_trend'] = float(vibration_trend)
            else:
                indicators['vibration_trend'] = 0.0
            
            # Tilt trend
            if len(recent_data) > 1:
                tilt_trend = np.polyfit(range(len(recent_data)), recent_data['tilt_magnitude'], 1)[0]
                indicators['tilt_trend'] = float(tilt_trend)
            else:
                indicators['tilt_trend'] = 0.0
            
            # Seismic activity level
            indicators['seismic_level'] = float(recent_data['seismic_activity'].mean())
            
            # Weather risk factor
            indicators['weather_risk'] = float(recent_data['weather_severity_index'].mean())
            
            # Overall stability score
            indicators['stability_score'] = float(recent_data['stability_index'].mean())
            
            # Anomaly detection (simple threshold-based)
            vibration_threshold = recent_data['vibration_magnitude'].quantile(0.95)
            indicators['vibration_anomaly'] = float(
                (recent_data['vibration_magnitude'] > vibration_threshold).sum() / len(recent_data)
            )
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating risk indicators: {e}")
            return {}
    
    def prepare_prediction_input(self, sensor_data: List[Dict]) -> Tuple[np.ndarray, Dict]:
        """
        Prepare sensor data for ML model prediction
        """
        try:
            # Clean and process data
            df = self.clean_sensor_data(sensor_data)
            df = self.engineer_features(df)
            
            # Calculate risk indicators for interpretability
            risk_indicators = self.calculate_risk_indicators(df)
            
            # Get the latest reading for point prediction
            latest_features = self.feature_columns + self.engineered_features
            
            # Ensure all features exist
            for feature in latest_features:
                if feature not in df.columns:
                    df[feature] = 0.0
            
            # Get the most recent data point
            prediction_input = df[latest_features].iloc[-1].values.reshape(1, -1)
            
            return prediction_input, risk_indicators
            
        except Exception as e:
            logger.error(f"Error preparing prediction input: {e}")
            raise

class GeospatialProcessor:
    """
    Processor for geospatial data including DEM and drone imagery
    """
    
    def __init__(self):
        self.supported_formats = ['.tif', '.tiff', '.jpg', '.jpeg', '.png']
    
    def process_dem_data(self, dem_file_path: str) -> Dict:
        """
        Process Digital Elevation Model data
        """
        try:
            # For demo purposes, return mock processed DEM data
            # In real implementation, would use libraries like rasterio, GDAL
            
            dem_analysis = {
                'slope_analysis': {
                    'mean_slope': 35.2,
                    'max_slope': 78.5,
                    'high_risk_areas': 0.15  # 15% of area
                },
                'elevation_stats': {
                    'min_elevation': 1250.0,
                    'max_elevation': 1680.0,
                    'mean_elevation': 1465.0
                },
                'geological_features': {
                    'fracture_density': 0.23,
                    'rock_type_distribution': {
                        'limestone': 0.6,
                        'sandstone': 0.3,
                        'shale': 0.1
                    }
                },
                'stability_zones': {
                    'stable': 0.7,
                    'moderately_stable': 0.2,
                    'unstable': 0.1
                }
            }
            
            return dem_analysis
            
        except Exception as e:
            logger.error(f"Error processing DEM data: {e}")
            return {}
    
    def analyze_drone_imagery(self, image_path: str) -> Dict:
        """
        Analyze drone imagery for rockfall risk assessment
        """
        try:
            # For demo purposes, return mock analysis
            # In real implementation, would use computer vision libraries
            
            imagery_analysis = {
                'crack_detection': {
                    'total_cracks': 23,
                    'major_cracks': 5,
                    'crack_density': 0.12  # cracks per m²
                },
                'rock_face_condition': {
                    'loose_rocks': 0.08,  # 8% of face area
                    'weathering_score': 0.6,
                    'vegetation_coverage': 0.15
                },
                'temporal_changes': {
                    'new_cracks_detected': 2,
                    'crack_propagation_rate': 0.05,  # mm/day
                    'displacement_detected': True
                },
                'risk_assessment': {
                    'immediate_risk_zones': ['Zone_A', 'Zone_C'],
                    'monitoring_recommended': ['Zone_B', 'Zone_D'],
                    'overall_risk_score': 0.65
                }
            }
            
            return imagery_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing drone imagery: {e}")
            return {}

# Global preprocessor instances
sensor_preprocessor = SensorDataPreprocessor()
geospatial_processor = GeospatialProcessor()

def preprocess_sensor_data(data: List[Dict]) -> Tuple[np.ndarray, Dict]:
    """
    Main preprocessing function for sensor data
    """
    return sensor_preprocessor.prepare_prediction_input(data)

def process_geospatial_data(dem_path: str = None, imagery_path: str = None) -> Dict:
    """
    Main processing function for geospatial data
    """
    results = {}
    
    if dem_path:
        results['dem_analysis'] = geospatial_processor.process_dem_data(dem_path)
    
    if imagery_path:
        results['imagery_analysis'] = geospatial_processor.analyze_drone_imagery(imagery_path)
    
    return results