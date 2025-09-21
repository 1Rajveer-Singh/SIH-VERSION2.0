"""
PyTorch-based rockfall prediction models
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
import joblib
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class RockfallLSTMModel(nn.Module):
    """
    LSTM-based model for time-series rockfall prediction
    """
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2, output_size: int = 1):
        super(RockfallLSTMModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8, dropout=0.1)
        
        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, output_size),
            nn.Sigmoid()  # Output probability between 0 and 1
        )
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        
        # LSTM forward pass
        lstm_out, (hn, cn) = self.lstm(x, (h0, c0))
        
        # Apply attention mechanism
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Use the last output for prediction
        final_out = attn_out[:, -1, :]
        
        # Pass through fully connected layers
        output = self.fc_layers(final_out)
        
        return output

class RockfallCNNModel(nn.Module):
    """
    CNN-based model for spatial pattern recognition in rockfall prediction
    """
    def __init__(self, input_channels: int = 1, num_classes: int = 4):
        super(RockfallCNNModel, self).__init__()
        
        # Convolutional layers
        self.conv_layers = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.MaxPool2d(2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.MaxPool2d(2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),
            nn.MaxPool2d(2),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(256),
            nn.AdaptiveAvgPool2d((4, 4))
        )
        
        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
            nn.Softmax(dim=1)
        )
        
    def forward(self, x):
        x = self.conv_layers(x)
        x = self.fc_layers(x)
        return x

class RockfallEnsembleModel:
    """
    Ensemble model combining multiple approaches for robust predictions
    """
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize models
        self.lstm_model = None
        self.cnn_model = None
        self.rf_model = None
        self.gb_model = None
        
        # Scalers
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        
        # Feature columns
        self.feature_columns = [
            'vibration_x', 'vibration_y', 'vibration_z',
            'tilt_x', 'tilt_y', 'temperature',
            'wind_speed', 'wind_direction', 'precipitation',
            'atmospheric_pressure', 'humidity',
            'seismic_activity', 'displacement_x', 'displacement_y', 'displacement_z'
        ]
        
        self.risk_levels = ['low', 'medium', 'high', 'critical']
        
    def initialize_models(self):
        """Initialize all models"""
        try:
            # LSTM Model (for time-series data)
            self.lstm_model = RockfallLSTMModel(
                input_size=len(self.feature_columns),
                hidden_size=128,
                num_layers=2,
                output_size=4  # 4 risk levels
            ).to(self.device)
            
            # CNN Model (for spatial data)
            self.cnn_model = RockfallCNNModel(
                input_channels=1,
                num_classes=4
            ).to(self.device)
            
            # Traditional ML models
            self.rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.gb_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            logger.info("All models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def preprocess_sensor_data(self, sensor_data: List[Dict]) -> np.ndarray:
        """
        Preprocess sensor data for model input
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(sensor_data)
            
            # Ensure all feature columns exist
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0.0
            
            # Select only feature columns
            feature_data = df[self.feature_columns].fillna(0)
            
            # Scale the data
            scaled_data = self.scaler.fit_transform(feature_data)
            
            return scaled_data
            
        except Exception as e:
            logger.error(f"Error preprocessing sensor data: {e}")
            raise
    
    def generate_synthetic_training_data(self, n_samples: int = 10000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data for model development
        """
        np.random.seed(42)
        
        # Generate synthetic sensor readings
        data = []
        labels = []
        
        for i in range(n_samples):
            # Base values for different risk scenarios
            risk_level = np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1])
            
            if risk_level == 0:  # Low risk
                vibration_base = np.random.normal(0.01, 0.005)
                tilt_base = np.random.normal(0, 0.5)
                seismic_base = np.random.normal(0, 0.01)
            elif risk_level == 1:  # Medium risk
                vibration_base = np.random.normal(0.03, 0.01)
                tilt_base = np.random.normal(0, 1.0)
                seismic_base = np.random.normal(0.02, 0.01)
            elif risk_level == 2:  # High risk
                vibration_base = np.random.normal(0.06, 0.02)
                tilt_base = np.random.normal(0, 2.0)
                seismic_base = np.random.normal(0.05, 0.02)
            else:  # Critical risk
                vibration_base = np.random.normal(0.1, 0.03)
                tilt_base = np.random.normal(0, 3.0)
                seismic_base = np.random.normal(0.1, 0.03)
            
            # Generate sample data
            sample = {
                'vibration_x': max(0, vibration_base + np.random.normal(0, 0.01)),
                'vibration_y': max(0, vibration_base + np.random.normal(0, 0.01)),
                'vibration_z': max(0, vibration_base + np.random.normal(0, 0.01)),
                'tilt_x': tilt_base + np.random.normal(0, 0.5),
                'tilt_y': tilt_base + np.random.normal(0, 0.5),
                'temperature': np.random.normal(15, 5),
                'wind_speed': max(0, np.random.normal(10, 5)),
                'wind_direction': np.random.uniform(0, 360),
                'precipitation': max(0, np.random.exponential(2)),
                'atmospheric_pressure': np.random.normal(1013, 20),
                'humidity': np.clip(np.random.normal(60, 20), 0, 100),
                'seismic_activity': max(0, seismic_base + np.random.normal(0, 0.01)),
                'displacement_x': np.random.normal(0, 0.001),
                'displacement_y': np.random.normal(0, 0.001),
                'displacement_z': np.random.normal(0, 0.0005)
            }
            
            data.append(sample)
            labels.append(risk_level)
        
        # Convert to arrays
        feature_data = self.preprocess_sensor_data(data)
        label_data = np.array(labels)
        
        return feature_data, label_data
    
    def train_models(self):
        """
        Train all models with synthetic data
        """
        try:
            logger.info("Generating training data...")
            X, y = self.generate_synthetic_training_data()
            
            # Train traditional ML models
            logger.info("Training Random Forest model...")
            self.rf_model.fit(X, y)
            
            logger.info("Training Gradient Boosting model...")
            self.gb_model.fit(X, y)
            
            # Convert data for PyTorch models
            X_tensor = torch.FloatTensor(X).to(self.device)
            y_tensor = torch.LongTensor(y).to(self.device)
            
            # Train LSTM model
            logger.info("Training LSTM model...")
            self._train_lstm_model(X_tensor, y_tensor)
            
            # Save all trained models
            self.save_models()
            
            logger.info("All models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    def _train_lstm_model(self, X: torch.Tensor, y: torch.Tensor, epochs: int = 100):
        """
        Train the LSTM model
        """
        # Reshape data for LSTM (batch_size, seq_len, features)
        # For simplicity, we'll use a sequence length of 1
        X_seq = X.unsqueeze(1)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.lstm_model.parameters(), lr=0.001)
        
        self.lstm_model.train()
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            outputs = self.lstm_model(X_seq)
            loss = criterion(outputs, y)
            
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 20 == 0:
                logger.info(f'LSTM Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
    
    def predict(self, sensor_data: List[Dict]) -> Dict:
        """
        Generate ensemble prediction from all models
        """
        try:
            # Preprocess data
            X = self.preprocess_sensor_data(sensor_data)
            
            predictions = {}
            
            # Random Forest prediction
            if self.rf_model:
                rf_pred = self.rf_model.predict_proba(X)
                predictions['random_forest'] = rf_pred[0]
            
            # Gradient Boosting prediction (convert to probabilities)
            if self.gb_model:
                gb_pred = self.gb_model.predict(X)
                # Convert regression output to classification probabilities
                gb_prob = self._convert_to_probabilities(gb_pred[0])
                predictions['gradient_boosting'] = gb_prob
            
            # LSTM prediction
            if self.lstm_model:
                self.lstm_model.eval()
                with torch.no_grad():
                    X_tensor = torch.FloatTensor(X).unsqueeze(1).to(self.device)
                    lstm_pred = self.lstm_model(X_tensor)
                    predictions['lstm'] = lstm_pred.cpu().numpy()[0]
            
            # Ensemble prediction (weighted average)
            ensemble_weights = {'random_forest': 0.3, 'gradient_boosting': 0.3, 'lstm': 0.4}
            
            final_prediction = np.zeros(4)
            total_weight = 0
            
            for model_name, pred in predictions.items():
                weight = ensemble_weights.get(model_name, 0.25)
                final_prediction += weight * pred
                total_weight += weight
            
            if total_weight > 0:
                final_prediction /= total_weight
            
            # Get risk level and confidence
            predicted_class = np.argmax(final_prediction)
            confidence = final_prediction[predicted_class]
            
            # Calculate contributing factors
            factors = self._calculate_contributing_factors(sensor_data[0] if sensor_data else {})
            
            # Generate recommendations
            recommendations = self._generate_recommendations(predicted_class, factors)
            
            return {
                'risk_level': {
                    'level': self.risk_levels[predicted_class],
                    'probability': float(confidence),
                    'confidence': float(confidence)
                },
                'factors': factors,
                'recommendations': recommendations,
                'model_predictions': {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in predictions.items()}
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    def _convert_to_probabilities(self, value: float) -> np.ndarray:
        """Convert regression output to classification probabilities"""
        # Simple conversion method
        probs = np.zeros(4)
        value = np.clip(value, 0, 3)
        
        if value < 1:
            probs[0] = 1 - value
            probs[1] = value
        elif value < 2:
            probs[1] = 2 - value
            probs[2] = value - 1
        elif value < 3:
            probs[2] = 3 - value
            probs[3] = value - 2
        else:
            probs[3] = 1
        
        return probs / np.sum(probs)
    
    def _calculate_contributing_factors(self, sensor_data: Dict) -> Dict[str, float]:
        """Calculate contributing factors for explainable AI"""
        factors = {}
        
        # Vibration intensity
        vibration_intensity = (
            sensor_data.get('vibration_x', 0) +
            sensor_data.get('vibration_y', 0) +
            sensor_data.get('vibration_z', 0)
        ) / 3
        factors['vibration_intensity'] = min(1.0, vibration_intensity * 10)
        
        # Slope stability (based on tilt)
        tilt_magnitude = np.sqrt(
            sensor_data.get('tilt_x', 0)**2 +
            sensor_data.get('tilt_y', 0)**2
        )
        factors['slope_stability'] = min(1.0, tilt_magnitude / 5)
        
        # Weather conditions
        weather_risk = (
            (sensor_data.get('wind_speed', 0) / 30) +
            (sensor_data.get('precipitation', 0) / 10)
        ) / 2
        factors['weather_conditions'] = min(1.0, weather_risk)
        
        # Geological stress
        seismic_risk = sensor_data.get('seismic_activity', 0) * 10
        factors['geological_stress'] = min(1.0, seismic_risk)
        
        # Historical patterns (simulated)
        factors['historical_patterns'] = np.random.uniform(0.2, 0.7)
        
        return factors
    
    def _generate_recommendations(self, risk_level: int, factors: Dict[str, float]) -> List[str]:
        """Generate safety recommendations based on prediction"""
        recommendations = []
        
        if risk_level >= 3:  # Critical
            recommendations.extend([
                "IMMEDIATE EVACUATION REQUIRED - Clear all personnel from danger zones",
                "Activate emergency response protocols",
                "Deploy real-time monitoring systems",
                "Contact emergency services and mining authorities"
            ])
        elif risk_level >= 2:  # High
            recommendations.extend([
                "Restrict access to high-risk areas",
                "Increase monitoring frequency to every 15 minutes",
                "Prepare evacuation procedures",
                "Alert all site personnel of elevated risk"
            ])
        elif risk_level >= 1:  # Medium
            recommendations.extend([
                "Increase vigilance and monitoring frequency",
                "Review safety protocols with personnel",
                "Prepare contingency plans"
            ])
        else:  # Low
            recommendations.extend([
                "Continue normal operations with standard monitoring",
                "Regular equipment maintenance checks"
            ])
        
        # Add factor-specific recommendations
        if factors.get('vibration_intensity', 0) > 0.7:
            recommendations.append("Install vibration dampening systems")
        
        if factors.get('weather_conditions', 0) > 0.6:
            recommendations.append("Monitor weather forecasts and postpone operations if conditions worsen")
        
        return recommendations[:4]  # Limit to 4 recommendations
    
    def save_models(self):
        """Save all trained models"""
        try:
            os.makedirs(self.model_dir, exist_ok=True)
            
            # Save PyTorch models
            if self.lstm_model:
                torch.save(self.lstm_model.state_dict(), f"{self.model_dir}/lstm_model.pth")
            
            if self.cnn_model:
                torch.save(self.cnn_model.state_dict(), f"{self.model_dir}/cnn_model.pth")
            
            # Save scikit-learn models
            if self.rf_model:
                joblib.dump(self.rf_model, f"{self.model_dir}/random_forest_model.pkl")
            
            if self.gb_model:
                joblib.dump(self.gb_model, f"{self.model_dir}/gradient_boosting_model.pkl")
            
            # Save scalers
            joblib.dump(self.scaler, f"{self.model_dir}/scaler.pkl")
            joblib.dump(self.minmax_scaler, f"{self.model_dir}/minmax_scaler.pkl")
            
            logger.info("All models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
            raise
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            # Initialize models first
            self.initialize_models()
            
            # Load PyTorch models
            lstm_path = f"{self.model_dir}/lstm_model.pth"
            if os.path.exists(lstm_path):
                self.lstm_model.load_state_dict(torch.load(lstm_path, map_location=self.device))
                self.lstm_model.eval()
            
            # Load scikit-learn models
            rf_path = f"{self.model_dir}/random_forest_model.pkl"
            if os.path.exists(rf_path):
                self.rf_model = joblib.load(rf_path)
            
            gb_path = f"{self.model_dir}/gradient_boosting_model.pkl"
            if os.path.exists(gb_path):
                self.gb_model = joblib.load(gb_path)
            
            # Load scalers
            scaler_path = f"{self.model_dir}/scaler.pkl"
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            # If loading fails, initialize and train new models
            self.initialize_models()
            self.train_models()

# Global model instance
ml_model = RockfallEnsembleModel()

def initialize_ml_models():
    """Initialize and train ML models"""
    try:
        ml_model.load_models()
        logger.info("ML models initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing ML models: {e}")
        # Fall back to training new models
        ml_model.initialize_models()
        ml_model.train_models()

def predict_rockfall_risk(sensor_data: List[Dict]) -> Dict:
    """
    Main prediction function to be called from the API
    """
    return ml_model.predict(sensor_data)