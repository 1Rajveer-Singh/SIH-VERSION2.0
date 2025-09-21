"""
Tests for ML models and prediction functionality
"""
import pytest
import numpy as np
import torch
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Add ML models path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ml_models"))

from conftest import TestUtils

from ml_models.rockfall_prediction import (
    RockfallLSTMModel,
    RockfallCNNModel,
    RockfallEnsembleModel,
    RockfallPredictor
)
from ml_models.preprocessing import DataPreprocessor
from ml_models.explainable_ai import ExplainableAI

class TestDataPreprocessor:
    """Test data preprocessing functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.preprocessor = DataPreprocessor()
        
        # Create sample sensor data
        self.sample_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='15min'),
            'vibration_x': np.random.normal(0.01, 0.005, 100),
            'vibration_y': np.random.normal(0.01, 0.005, 100),
            'vibration_z': np.random.normal(0.01, 0.005, 100),
            'tilt_x': np.random.normal(0, 0.5, 100),
            'tilt_y': np.random.normal(0, 0.5, 100),
            'temperature': np.random.normal(20, 5, 100),
            'humidity': np.random.uniform(30, 80, 100),
            'wind_speed': np.random.exponential(5, 100),
            'precipitation': np.random.exponential(2, 100)
        })
    
    def test_normalize_features(self):
        """Test feature normalization."""
        # Select numeric columns for normalization
        numeric_cols = ['vibration_x', 'vibration_y', 'vibration_z', 'temperature']
        data_subset = self.sample_data[numeric_cols].copy()
        
        normalized_data, scaler = self.preprocessor.normalize_features(data_subset)
        
        # Check that data is normalized
        assert normalized_data.shape == data_subset.shape
        
        # Check that mean is close to 0 and std is close to 1 (within tolerance)
        for col in normalized_data.columns:
            assert abs(normalized_data[col].mean()) < 0.1
            assert abs(normalized_data[col].std() - 1.0) < 0.1
        
        # Check that scaler is returned
        assert scaler is not None
    
    def test_create_sequences(self):
        """Test sequence creation for LSTM."""
        data = self.sample_data[['vibration_x', 'vibration_y', 'temperature']].values
        sequence_length = 10
        
        sequences, targets = self.preprocessor.create_sequences(data, sequence_length)
        
        # Check shapes
        expected_sequences = len(data) - sequence_length
        assert sequences.shape == (expected_sequences, sequence_length, 3)
        assert targets.shape == (expected_sequences, 3)
        
        # Check that sequences are properly created
        # First sequence should be data[0:sequence_length]
        np.testing.assert_array_equal(sequences[0], data[:sequence_length])
        # First target should be data[sequence_length]
        np.testing.assert_array_equal(targets[0], data[sequence_length])
    
    def test_extract_statistical_features(self):
        """Test statistical feature extraction."""
        data = self.sample_data[['vibration_x', 'vibration_y', 'vibration_z']].copy()
        
        features = self.preprocessor.extract_statistical_features(data)
        
        # Check that features are extracted
        assert isinstance(features, pd.DataFrame)
        assert len(features) > 0
        
        # Check for expected feature types
        feature_names = features.columns.tolist()
        assert any('mean' in name for name in feature_names)
        assert any('std' in name for name in feature_names)
        assert any('max' in name for name in feature_names)
        assert any('min' in name for name in feature_names)
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        # Create data with some obvious anomalies
        data = self.sample_data['vibration_x'].copy()
        # Add some anomalies
        data.iloc[10] = 0.1  # Very high value
        data.iloc[20] = -0.1  # Very low value
        
        anomalies = self.preprocessor.detect_anomalies(data, threshold=2.0)
        
        # Check that anomalies are detected
        assert isinstance(anomalies, pd.Series)
        assert anomalies.dtype == bool
        assert anomalies.sum() > 0  # Should detect some anomalies
        
        # Check that our injected anomalies are detected
        assert anomalies.iloc[10] == True
        assert anomalies.iloc[20] == True

class TestRockfallLSTMModel:
    """Test LSTM model functionality."""
    
    def setup_method(self):
        """Set up test model."""
        self.input_size = 5
        self.hidden_size = 32
        self.num_layers = 2
        self.output_size = 1
        
        self.model = RockfallLSTMModel(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            output_size=self.output_size
        )
    
    def test_model_initialization(self):
        """Test model initialization."""
        assert isinstance(self.model, RockfallLSTMModel)
        assert isinstance(self.model.lstm, torch.nn.LSTM)
        assert isinstance(self.model.fc, torch.nn.Linear)
        assert isinstance(self.model.dropout, torch.nn.Dropout)
    
    def test_forward_pass(self):
        """Test forward pass."""
        batch_size = 8
        sequence_length = 20
        
        # Create random input
        x = torch.randn(batch_size, sequence_length, self.input_size)
        
        # Forward pass
        output = self.model(x)
        
        # Check output shape
        assert output.shape == (batch_size, self.output_size)
        
        # Check output is in valid range (after sigmoid)
        assert torch.all(output >= 0)
        assert torch.all(output <= 1)
    
    def test_model_parameters(self):
        """Test that model has trainable parameters."""
        params = list(self.model.parameters())
        assert len(params) > 0
        
        # Check that parameters require gradients
        for param in params:
            assert param.requires_grad

class TestRockfallCNNModel:
    """Test CNN model functionality."""
    
    def setup_method(self):
        """Set up test model."""
        self.input_channels = 3
        self.sequence_length = 50
        
        self.model = RockfallCNNModel(
            input_channels=self.input_channels,
            sequence_length=self.sequence_length
        )
    
    def test_model_initialization(self):
        """Test model initialization."""
        assert isinstance(self.model, RockfallCNNModel)
        assert hasattr(self.model, 'conv_layers')
        assert hasattr(self.model, 'classifier')
    
    def test_forward_pass(self):
        """Test forward pass."""
        batch_size = 4
        
        # Create random input (batch_size, channels, sequence_length)
        x = torch.randn(batch_size, self.input_channels, self.sequence_length)
        
        # Forward pass
        output = self.model(x)
        
        # Check output shape
        assert output.shape == (batch_size, 1)
        
        # Check output is in valid range
        assert torch.all(output >= 0)
        assert torch.all(output <= 1)

class TestRockfallEnsembleModel:
    """Test ensemble model functionality."""
    
    def setup_method(self):
        """Set up test ensemble."""
        self.lstm_model = RockfallLSTMModel(5, 32, 2, 1)
        self.cnn_model = RockfallCNNModel(3, 50)
        
        self.ensemble = RockfallEnsembleModel(
            lstm_model=self.lstm_model,
            cnn_model=self.cnn_model
        )
    
    def test_ensemble_initialization(self):
        """Test ensemble initialization."""
        assert isinstance(self.ensemble, RockfallEnsembleModel)
        assert self.ensemble.lstm_model is self.lstm_model
        assert self.ensemble.cnn_model is self.cnn_model
    
    def test_ensemble_prediction(self):
        """Test ensemble prediction."""
        batch_size = 4
        
        # Create inputs for both models
        lstm_input = torch.randn(batch_size, 20, 5)
        cnn_input = torch.randn(batch_size, 3, 50)
        
        # Ensemble prediction
        output = self.ensemble(lstm_input, cnn_input)
        
        # Check output shape
        assert output.shape == (batch_size, 1)
        
        # Check output is in valid range
        assert torch.all(output >= 0)
        assert torch.all(output <= 1)

class TestRockfallPredictor:
    """Test the main predictor class."""
    
    def setup_method(self):
        """Set up predictor."""
        self.predictor = RockfallPredictor()
    
    @patch('ml_models.rockfall_prediction.torch.load')
    def test_load_models(self, mock_load):
        """Test model loading."""
        # Mock loaded models
        mock_lstm = MagicMock()
        mock_cnn = MagicMock()
        mock_load.side_effect = [mock_lstm, mock_cnn]
        
        # Load models
        self.predictor.load_models("dummy_lstm_path", "dummy_cnn_path")
        
        # Check models are set
        assert self.predictor.lstm_model is mock_lstm
        assert self.predictor.cnn_model is mock_cnn
        assert mock_load.call_count == 2
    
    def test_predict_without_models(self):
        """Test prediction without loaded models."""
        sensor_data = pd.DataFrame({
            'vibration_x': [0.01, 0.02, 0.015],
            'vibration_y': [0.012, 0.018, 0.014],
            'vibration_z': [0.016, 0.022, 0.019]
        })
        
        with pytest.raises(ValueError, match="Models not loaded"):
            self.predictor.predict(sensor_data)
    
    @patch('ml_models.rockfall_prediction.RockfallPredictor.load_models')
    def test_predict_with_mocked_models(self, mock_load_models):
        """Test prediction with mocked models."""
        # Create mock models
        mock_lstm = MagicMock()
        mock_cnn = MagicMock()
        mock_ensemble = MagicMock()
        
        # Set up mock returns
        mock_lstm.return_value = torch.tensor([[0.7]])
        mock_cnn.return_value = torch.tensor([[0.6]])
        mock_ensemble.return_value = torch.tensor([[0.65]])
        
        # Set models
        self.predictor.lstm_model = mock_lstm
        self.predictor.cnn_model = mock_cnn
        self.predictor.ensemble_model = mock_ensemble
        
        # Test data
        sensor_data = pd.DataFrame({
            'vibration_x': np.random.normal(0.01, 0.005, 50),
            'vibration_y': np.random.normal(0.01, 0.005, 50),
            'vibration_z': np.random.normal(0.01, 0.005, 50),
            'temperature': np.random.normal(20, 5, 50),
            'humidity': np.random.uniform(30, 80, 50)
        })
        
        # Make prediction
        result = self.predictor.predict(sensor_data)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert 'confidence' in result
        assert 'model_outputs' in result
        
        # Check risk score is valid
        assert 0 <= result['risk_score'] <= 1
        assert result['risk_level'] in ['low', 'medium', 'high', 'critical']
        assert 0 <= result['confidence'] <= 1

class TestExplainableAI:
    """Test explainable AI functionality."""
    
    def setup_method(self):
        """Set up explainable AI."""
        self.explainer = ExplainableAI()
    
    def test_calculate_feature_importance(self):
        """Test feature importance calculation."""
        # Create mock model
        mock_model = MagicMock()
        mock_model.return_value = torch.tensor([[0.7]])
        
        # Test data
        data = np.random.randn(10, 5)
        feature_names = ['vibration_x', 'vibration_y', 'vibration_z', 'temperature', 'humidity']
        
        # Calculate importance
        importance = self.explainer.calculate_feature_importance(
            mock_model, data, feature_names
        )
        
        # Check result
        assert isinstance(importance, dict)
        assert len(importance) == len(feature_names)
        
        for feature in feature_names:
            assert feature in importance
            assert isinstance(importance[feature], (int, float))
    
    def test_explain_prediction(self):
        """Test prediction explanation."""
        # Create test prediction result
        prediction_result = {
            'risk_score': 0.75,
            'risk_level': 'high',
            'confidence': 0.85,
            'model_outputs': {
                'lstm': 0.8,
                'cnn': 0.7,
                'ensemble': 0.75
            }
        }
        
        feature_importance = {
            'vibration_x': 0.3,
            'vibration_y': 0.25,
            'vibration_z': 0.2,
            'temperature': 0.15,
            'humidity': 0.1
        }
        
        explanation = self.explainer.explain_prediction(
            prediction_result, feature_importance
        )
        
        # Check explanation structure
        assert isinstance(explanation, dict)
        assert 'summary' in explanation
        assert 'key_factors' in explanation
        assert 'model_confidence' in explanation
        assert 'recommendations' in explanation
        
        # Check key factors
        assert isinstance(explanation['key_factors'], list)
        assert len(explanation['key_factors']) > 0
        
        # Check recommendations
        assert isinstance(explanation['recommendations'], list)
        assert len(explanation['recommendations']) > 0

@pytest.mark.asyncio
class TestPredictionAPI:
    """Test prediction API endpoints."""
    
    async def test_predict_rockfall_risk(self, client, auth_headers_operator, test_site, test_sensor):
        """Test rockfall risk prediction endpoint."""
        # Create test sensor readings
        sensor_readings = [
            {
                "sensor_id": test_sensor["_id"],
                "timestamp": "2024-01-15T12:00:00Z",
                "readings": {
                    "vibration_x": 0.015,
                    "vibration_y": 0.012,
                    "vibration_z": 0.018,
                    "temperature": 22.5,
                    "humidity": 65.0
                }
            },
            {
                "sensor_id": test_sensor["_id"],
                "timestamp": "2024-01-15T12:15:00Z",
                "readings": {
                    "vibration_x": 0.020,
                    "vibration_y": 0.016,
                    "vibration_z": 0.024,
                    "temperature": 23.0,
                    "humidity": 67.0
                }
            }
        ]
        
        # Mock the ML prediction
        with patch('routers.predictions.RockfallPredictor') as mock_predictor_class:
            mock_predictor = MagicMock()
            mock_predictor.predict.return_value = {
                'risk_score': 0.65,
                'risk_level': 'medium',
                'confidence': 0.82,
                'model_outputs': {
                    'lstm': 0.7,
                    'cnn': 0.6,
                    'ensemble': 0.65
                }
            }
            mock_predictor_class.return_value = mock_predictor
            
            response = await client.post(
                f"/predictions/predict/{test_site['_id']}",
                headers=auth_headers_operator,
                json={"sensor_readings": sensor_readings}
            )
            
            data = TestUtils.assert_valid_response(response, 201)
            
            # Check prediction result
            assert data["site_id"] == test_site["_id"]
            assert data["risk_score"] == 0.65
            assert data["risk_level"] == "medium"
            assert data["confidence"] == 0.82
            assert "model_version" in data
            assert "contributing_factors" in data
            assert "recommended_actions" in data
    
    async def test_get_predictions(self, client, auth_headers_viewer, test_site):
        """Test getting predictions for a site."""
        response = await client.get(
            f"/predictions/site/{test_site['_id']}",
            headers=auth_headers_viewer
        )
        
        data = TestUtils.assert_valid_response(response)
        TestUtils.assert_pagination_response(data)
    
    async def test_predict_unauthorized(self, client, auth_headers_viewer, test_site):
        """Test that viewer cannot create predictions."""
        sensor_readings = [
            {
                "sensor_id": "test_sensor",
                "timestamp": "2024-01-15T12:00:00Z",
                "readings": {"vibration_x": 0.015}
            }
        ]
        
        response = await client.post(
            f"/predictions/predict/{test_site['_id']}",
            headers=auth_headers_viewer,
            json={"sensor_readings": sensor_readings}
        )
        
        TestUtils.assert_error_response(response, 403, "Not enough permissions")