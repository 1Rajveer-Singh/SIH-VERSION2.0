"""
Explainable AI utilities for model interpretability
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ExplainableAI:
    """
    Utilities for making ML predictions interpretable and explainable
    """
    
    def __init__(self):
        self.feature_importance_weights = {
            'vibration_magnitude': 0.25,
            'tilt_magnitude': 0.20,
            'seismic_activity': 0.18,
            'displacement_magnitude': 0.15,
            'weather_severity_index': 0.12,
            'stability_index': 0.10
        }
        
        self.risk_thresholds = {
            'vibration_magnitude': {'low': 0.01, 'medium': 0.03, 'high': 0.06, 'critical': 0.1},
            'tilt_magnitude': {'low': 1.0, 'medium': 2.0, 'high': 4.0, 'critical': 6.0},
            'seismic_activity': {'low': 0.01, 'medium': 0.03, 'high': 0.05, 'critical': 0.1},
            'displacement_magnitude': {'low': 0.001, 'medium': 0.003, 'high': 0.005, 'critical': 0.01}
        }
    
    def generate_feature_importance(self, sensor_data: Dict, prediction_result: Dict) -> Dict[str, float]:
        """
        Generate feature importance scores for the prediction
        """
        try:
            importance_scores = {}
            
            # Calculate normalized feature values
            vibration_mag = np.sqrt(
                sensor_data.get('vibration_x', 0)**2 +
                sensor_data.get('vibration_y', 0)**2 +
                sensor_data.get('vibration_z', 0)**2
            )
            
            tilt_mag = np.sqrt(
                sensor_data.get('tilt_x', 0)**2 +
                sensor_data.get('tilt_y', 0)**2
            )
            
            displacement_mag = np.sqrt(
                sensor_data.get('displacement_x', 0)**2 +
                sensor_data.get('displacement_y', 0)**2 +
                sensor_data.get('displacement_z', 0)**2
            )
            
            seismic_activity = sensor_data.get('seismic_activity', 0)
            
            # Weather severity (simplified calculation)
            weather_severity = (
                (sensor_data.get('wind_speed', 0) / 30.0) * 0.3 +
                (sensor_data.get('precipitation', 0) / 20.0) * 0.5 +
                (abs(sensor_data.get('atmospheric_pressure', 1013) - 1013) / 50.0) * 0.2
            )
            
            # Calculate importance based on contribution to risk
            importance_scores['vibration_intensity'] = min(1.0, vibration_mag * 10) * self.feature_importance_weights['vibration_magnitude']
            importance_scores['slope_stability'] = min(1.0, tilt_mag / 5) * self.feature_importance_weights['tilt_magnitude']
            importance_scores['geological_stress'] = min(1.0, seismic_activity * 10) * self.feature_importance_weights['seismic_activity']
            importance_scores['displacement_pattern'] = min(1.0, displacement_mag * 1000) * self.feature_importance_weights['displacement_magnitude']
            importance_scores['weather_conditions'] = min(1.0, weather_severity) * self.feature_importance_weights['weather_severity_index']
            
            # Add historical pattern (simulated)
            importance_scores['historical_patterns'] = np.random.uniform(0.1, 0.3)
            
            # Normalize to sum to 1
            total_importance = sum(importance_scores.values())
            if total_importance > 0:
                importance_scores = {k: v / total_importance for k, v in importance_scores.items()}
            
            return importance_scores
            
        except Exception as e:
            logger.error(f"Error generating feature importance: {e}")
            return {}
    
    def generate_risk_explanation(self, sensor_data: Dict, prediction_result: Dict) -> Dict[str, Any]:
        """
        Generate human-readable explanation of the risk assessment
        """
        try:
            risk_level = prediction_result.get('risk_level', {}).get('level', 'unknown')
            probability = prediction_result.get('risk_level', {}).get('probability', 0)
            
            explanation = {
                'summary': self._generate_risk_summary(risk_level, probability),
                'contributing_factors': self._analyze_contributing_factors(sensor_data),
                'threshold_analysis': self._analyze_thresholds(sensor_data),
                'trend_analysis': self._generate_trend_analysis(sensor_data),
                'confidence_factors': self._analyze_confidence(prediction_result)
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating risk explanation: {e}")
            return {}
    
    def _generate_risk_summary(self, risk_level: str, probability: float) -> str:
        """Generate human-readable risk summary"""
        summaries = {
            'low': f"Low rockfall risk detected ({probability:.1%} probability). Current conditions are stable with minimal threat indicators.",
            'medium': f"Medium rockfall risk identified ({probability:.1%} probability). Some concerning indicators detected - increased monitoring recommended.",
            'high': f"High rockfall risk warning ({probability:.1%} probability). Multiple risk factors present - immediate safety measures required.",
            'critical': f"CRITICAL rockfall risk alert ({probability:.1%} probability). Imminent danger detected - IMMEDIATE EVACUATION recommended."
        }
        
        return summaries.get(risk_level, f"Unknown risk level ({probability:.1%} probability)")
    
    def _analyze_contributing_factors(self, sensor_data: Dict) -> List[Dict[str, Any]]:
        """Analyze which factors are contributing most to the risk"""
        factors = []
        
        # Vibration analysis
        vibration_mag = np.sqrt(
            sensor_data.get('vibration_x', 0)**2 +
            sensor_data.get('vibration_y', 0)**2 +
            sensor_data.get('vibration_z', 0)**2
        )
        
        if vibration_mag > 0.05:
            factors.append({
                'factor': 'High Vibration Levels',
                'severity': 'high',
                'description': f'Vibration magnitude ({vibration_mag:.3f}g) exceeds safe thresholds',
                'impact': 'Indicates potential structural instability'
            })
        elif vibration_mag > 0.03:
            factors.append({
                'factor': 'Elevated Vibration',
                'severity': 'medium',
                'description': f'Vibration levels ({vibration_mag:.3f}g) above normal range',
                'impact': 'May indicate increasing instability'
            })
        
        # Tilt analysis
        tilt_mag = np.sqrt(
            sensor_data.get('tilt_x', 0)**2 +
            sensor_data.get('tilt_y', 0)**2
        )
        
        if tilt_mag > 3.0:
            factors.append({
                'factor': 'Significant Slope Movement',
                'severity': 'high',
                'description': f'Tilt magnitude ({tilt_mag:.1f}°) indicates slope deformation',
                'impact': 'Suggests ongoing slope failure processes'
            })
        
        # Seismic analysis
        seismic_activity = sensor_data.get('seismic_activity', 0)
        if seismic_activity > 0.05:
            factors.append({
                'factor': 'High Seismic Activity',
                'severity': 'high',
                'description': f'Seismic readings ({seismic_activity:.3f}) well above background',
                'impact': 'May trigger rockfall events'
            })
        
        # Weather analysis
        wind_speed = sensor_data.get('wind_speed', 0)
        precipitation = sensor_data.get('precipitation', 0)
        
        if wind_speed > 20 or precipitation > 10:
            factors.append({
                'factor': 'Adverse Weather Conditions',
                'severity': 'medium',
                'description': f'High winds ({wind_speed:.1f} m/s) or precipitation ({precipitation:.1f} mm)',
                'impact': 'Weather can accelerate rockfall processes'
            })
        
        return factors
    
    def _analyze_thresholds(self, sensor_data: Dict) -> Dict[str, Any]:
        """Analyze which safety thresholds are being approached or exceeded"""
        threshold_status = {}
        
        # Check vibration thresholds
        vibration_mag = np.sqrt(
            sensor_data.get('vibration_x', 0)**2 +
            sensor_data.get('vibration_y', 0)**2 +
            sensor_data.get('vibration_z', 0)**2
        )
        
        vibration_thresholds = self.risk_thresholds['vibration_magnitude']
        if vibration_mag >= vibration_thresholds['critical']:
            threshold_status['vibration'] = 'critical_exceeded'
        elif vibration_mag >= vibration_thresholds['high']:
            threshold_status['vibration'] = 'high_exceeded'
        elif vibration_mag >= vibration_thresholds['medium']:
            threshold_status['vibration'] = 'medium_exceeded'
        else:
            threshold_status['vibration'] = 'within_safe_limits'
        
        # Check tilt thresholds
        tilt_mag = np.sqrt(
            sensor_data.get('tilt_x', 0)**2 +
            sensor_data.get('tilt_y', 0)**2
        )
        
        tilt_thresholds = self.risk_thresholds['tilt_magnitude']
        if tilt_mag >= tilt_thresholds['critical']:
            threshold_status['tilt'] = 'critical_exceeded'
        elif tilt_mag >= tilt_thresholds['high']:
            threshold_status['tilt'] = 'high_exceeded'
        elif tilt_mag >= tilt_thresholds['medium']:
            threshold_status['tilt'] = 'medium_exceeded'
        else:
            threshold_status['tilt'] = 'within_safe_limits'
        
        return threshold_status
    
    def _generate_trend_analysis(self, sensor_data: Dict) -> Dict[str, str]:
        """Generate analysis of recent trends (simulated for single data point)"""
        # In real implementation, this would analyze historical data
        trends = {
            'vibration_trend': 'Increasing over last 6 hours - requires attention',
            'tilt_trend': 'Stable with minor fluctuations',
            'seismic_trend': 'Elevated above baseline levels',
            'weather_trend': 'Improving conditions expected'
        }
        
        return trends
    
    def _analyze_confidence(self, prediction_result: Dict) -> Dict[str, Any]:
        """Analyze factors affecting prediction confidence"""
        confidence = prediction_result.get('risk_level', {}).get('confidence', 0)
        
        confidence_analysis = {
            'overall_confidence': confidence,
            'confidence_level': 'high' if confidence > 0.8 else 'medium' if confidence > 0.6 else 'low',
            'factors_affecting_confidence': []
        }
        
        if confidence < 0.7:
            confidence_analysis['factors_affecting_confidence'].extend([
                'Limited historical data for this site',
                'Sensor calibration may need verification',
                'Weather conditions affecting sensor accuracy'
            ])
        
        if 'model_predictions' in prediction_result:
            model_agreement = self._calculate_model_agreement(prediction_result['model_predictions'])
            confidence_analysis['model_agreement'] = model_agreement
            
            if model_agreement < 0.7:
                confidence_analysis['factors_affecting_confidence'].append(
                    'Models show some disagreement - manual verification recommended'
                )
        
        return confidence_analysis
    
    def _calculate_model_agreement(self, model_predictions: Dict) -> float:
        """Calculate agreement between different ML models"""
        if not model_predictions or len(model_predictions) < 2:
            return 1.0
        
        # Convert predictions to risk level indices
        risk_indices = []
        for model_name, predictions in model_predictions.items():
            if isinstance(predictions, list) and len(predictions) >= 4:
                risk_indices.append(np.argmax(predictions))
        
        if len(risk_indices) < 2:
            return 1.0
        
        # Calculate variance in predictions
        variance = np.var(risk_indices)
        # Convert to agreement score (lower variance = higher agreement)
        agreement = max(0, 1 - variance / 2)
        
        return agreement
    
    def generate_actionable_insights(self, sensor_data: Dict, prediction_result: Dict) -> List[Dict[str, str]]:
        """Generate actionable insights based on the prediction"""
        insights = []
        
        risk_level = prediction_result.get('risk_level', {}).get('level', 'unknown')
        factors = prediction_result.get('factors', {})
        
        # High priority insights
        if risk_level in ['high', 'critical']:
            insights.append({
                'priority': 'critical',
                'category': 'immediate_action',
                'insight': 'Immediate safety measures required - restrict access to danger zones',
                'action': 'Implement emergency protocols and evacuate personnel if necessary'
            })
        
        # Vibration-specific insights
        vibration_intensity = factors.get('vibration_intensity', 0)
        if vibration_intensity > 0.7:
            insights.append({
                'priority': 'high',
                'category': 'monitoring',
                'insight': 'Excessive vibration detected - potential equipment or geological source',
                'action': 'Investigate vibration source and consider increasing monitoring frequency'
            })
        
        # Weather-related insights
        weather_conditions = factors.get('weather_conditions', 0)
        if weather_conditions > 0.6:
            insights.append({
                'priority': 'medium',
                'category': 'environmental',
                'insight': 'Adverse weather conditions increasing rockfall risk',
                'action': 'Monitor weather forecasts and consider operational adjustments'
            })
        
        # Slope stability insights
        slope_stability = factors.get('slope_stability', 0)
        if slope_stability > 0.5:
            insights.append({
                'priority': 'high',
                'category': 'geological',
                'insight': 'Slope stability concerns detected through tilt measurements',
                'action': 'Consider geotechnical assessment and additional stabilization measures'
            })
        
        return insights

# Global explainable AI instance
explainable_ai = ExplainableAI()

def explain_prediction(sensor_data: Dict, prediction_result: Dict) -> Dict[str, Any]:
    """
    Main function to generate comprehensive explanation of prediction
    """
    try:
        explanation = {
            'feature_importance': explainable_ai.generate_feature_importance(sensor_data, prediction_result),
            'risk_explanation': explainable_ai.generate_risk_explanation(sensor_data, prediction_result),
            'actionable_insights': explainable_ai.generate_actionable_insights(sensor_data, prediction_result),
            'timestamp': datetime.utcnow().isoformat(),
            'explanation_version': '1.0'
        }
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        return {
            'error': 'Unable to generate explanation',
            'timestamp': datetime.utcnow().isoformat()
        }