"""
Battery RUL Prediction Service
Loads PINN-LSTM model and provides inference
"""
import numpy as np
import json
from tensorflow import keras
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.telemetry import BatteryTelemetry

class BatteryPredictionService:
    def __init__(self, 
                 model_path='models/battery_rul_pinn_lstm.keras',
                 info_path='models/battery_rul_model_info.json'):
        """
        Initialize battery RUL prediction service
        
        Args:
            model_path: Path to trained PINN-LSTM model
            info_path: Path to model metadata
        """
        self.model = keras.models.load_model(
            model_path,
            custom_objects={'PhysicsLayer': self._create_physics_layer()}
        )
        
        with open(info_path, 'r') as f:
            self.model_info = json.load(f)
        
        self.feature_cols = self.model_info['feature_columns']
        self.norm_stats = self.model_info['normalization_stats']
        
        print(f"✅ Battery PINN-LSTM model loaded: {model_path}")
        print(f"   Features: {self.feature_cols}")
        print(f"   Test MAE: {self.model_info['metrics']['mae_days']:.1f} days")
    
    def _create_physics_layer(self):
        """Create PhysicsLayer class for model loading"""
        from tensorflow.keras import layers
        
        class PhysicsLayer(layers.Layer):
            def __init__(self, **kwargs):
                super(PhysicsLayer, self).__init__(**kwargs)
            
            def build(self, input_shape):
                self.R = self.add_weight(name='resistance', shape=(1,), trainable=True)
                self.K = self.add_weight(name='polarization', shape=(1,), trainable=True)
                self.A = self.add_weight(name='exponential_A', shape=(1,), trainable=True)
                self.B = self.add_weight(name='exponential_B', shape=(1,), trainable=True)
                super(PhysicsLayer, self).build(input_shape)
            
            def call(self, inputs):
                import tensorflow as tf
                voltage_mean = inputs[:, 0:1]
                current_mean = inputs[:, 4:5]
                capacity_end = inputs[:, 8:9]
                
                E0 = 3.7
                Q = 1.85
                q = Q - capacity_end
                q_safe = tf.clip_by_value(q, 0.01, Q)
                
                V_physics = (
                    E0 
                    - self.R * tf.abs(current_mean)
                    - self.K * (Q / (Q - q_safe + 0.01)) * q_safe
                    + self.A * tf.exp(-self.B * q_safe)
                )
                return V_physics
            
            def get_config(self):
                return super(PhysicsLayer, self).get_config()
        
        return PhysicsLayer
    
    def extract_features_from_db(self, db: Session, patient_id: str, window_days=180):
        """
        Extract battery features from telemetry database
        
        Args:
            db: Database session
            patient_id: Patient ID
            window_days: Look-back window (default 180 days = 6 months)
        
        Returns:
            Feature dict or None if insufficient data
        """
        cutoff = datetime.now() - timedelta(days=window_days)
        
        # Get battery telemetry
        records = db.query(BatteryTelemetry).filter(
            BatteryTelemetry.patient_id == patient_id,
            BatteryTelemetry.timestamp >= cutoff
        ).order_by(BatteryTelemetry.timestamp.asc()).all()
        
        if len(records) < 30:  # Need at least 30 days of data
            return None
        
        # Calculate aggregate features
        voltages = [r.voltage for r in records]
        socs = [r.soc_percent for r in records]
        
        # Mock capacity (in production, calculate from SoC)
        capacity_start = 1.85 * (socs[0] / 100)
        capacity_end = 1.85 * (socs[-1] / 100)
        
        features = {
            'voltage_mean': np.mean(voltages),
            'voltage_std': np.std(voltages),
            'voltage_min': np.min(voltages),
            'voltage_max': np.max(voltages),
            'current_mean': -0.00001,  # Constant discharge (mock)
            'temperature_mean': 37.0,  # Body temp (mock)
            'temperature_std': 0.5,
            'capacity_start': capacity_start,
            'capacity_end': capacity_end,
            'capacity_fade_rate': (capacity_start - capacity_end) / len(records),
            'soh_current': socs[-1]
        }
        
        return features
    
    def predict_rul(self, features: Dict) -> Dict:
        """
        Predict battery RUL from features
        
        Args:
            features: Dict with required feature keys
        
        Returns:
            Prediction dict with rul_days, confidence, timestamp
        """
        # Normalize features
        feature_vector = np.zeros(len(self.feature_cols))
        
        for i, col in enumerate(self.feature_cols):
            value = features[col]
            mean = self.norm_stats[col]['mean']
            std = self.norm_stats[col]['std']
            
            if std == 0:
                std = 1
            
            feature_vector[i] = (value - mean) / std
        
        # Reshape for LSTM (batch_size=1, timesteps=1, features)
        X = feature_vector.reshape(1, 1, len(self.feature_cols))
        
        # Predict (model returns [rul, physics_voltage])
        predictions = self.model.predict(X, verbose=0)
        rul_days = float(predictions[0][0][0])
        physics_voltage = float(predictions[1][0][0])
        
        # Ensure non-negative
        rul_days = max(0, rul_days)
        
        # Confidence based on model's test MAE
        mae = self.model_info['metrics']['mae_days']
        confidence = max(0, min(100, 100 * (1 - mae / rul_days))) if rul_days > 0 else 0
        
        return {
            'rul_days': rul_days,
            'rul_months': rul_days / 30,
            'physics_voltage': physics_voltage,
            'confidence_percent': confidence,
            'model_mae': mae,
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_from_db(self, db: Session, patient_id: str) -> Dict:
        """
        End-to-end RUL prediction from database
        
        Args:
            db: Database session
            patient_id: Patient ID
        
        Returns:
            Prediction dict or error
        """
        features = self.extract_features_from_db(db, patient_id)
        
        if features is None:
            return {
                'error': 'Insufficient data (need 30+ days of battery readings)',
                'rul_days': None
            }
        
        return self.predict_rul(features)

# Global singleton
_battery_service = None

def get_battery_service():
    """Get singleton battery prediction service"""
    global _battery_service
    if _battery_service is None:
        _battery_service = BatteryPredictionService()
    return _battery_service
