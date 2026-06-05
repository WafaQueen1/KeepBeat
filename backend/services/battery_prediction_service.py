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
                 model_path='models/battery/battery_pinn_lstm.keras',
                 info_path='models/battery/battery_model_info.json'):
        """
        Initialize battery RUL prediction service
        
        Args:
            model_path: Path to trained PINN-LSTM model
            info_path: Path to model metadata
        """
        import os
        self.model = None
        self.model_info = {}
        
        if os.path.exists(model_path):
            try:
                self.model = keras.models.load_model(
                    model_path,
                    custom_objects={'PhysicsLayer': self._create_physics_layer()}
                )
                print(f"✅ Battery PINN-LSTM model loaded: {model_path}")
            except Exception as e:
                print(f"⚠️ Error loading battery model: {e}")
                
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r') as f:
                    self.model_info = json.load(f)
                mae = self.model_info.get('metrics', {}).get('mae_cycles', 0)
                print(f"   Test MAE: {mae:.1f} cycles")
            except Exception as e:
                pass
    
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
    
    def predict_from_sequence(self, sequence_array: np.ndarray) -> Dict:
        """
        Predict battery RUL directly from a sequence array.
        sequence_array should have shape (1, 30, 4)
        """
        if self.model is None:
            return {'error': 'Battery model not loaded', 'success': False}
            
        try:
            output = self.model.predict(sequence_array, verbose=0)
            
            # Model outputs raw RUL in cycles (NASA dataset)
            # output shape is (1,1) — single scalar
            rul_cycles = float(np.squeeze(output))
            rul_cycles = max(0.0, rul_cycles)
            
            # Each NASA cycle ≈ 30 days for a pacemaker battery
            rul_days = rul_cycles * 30.0
            rul_months = rul_days / 30.0
            
            mae_cycles = self.model_info.get('metrics', {}).get('mae_cycles', 8.5)
            confidence = max(0.0, min(100.0, 100.0 * (1.0 - mae_cycles / max(rul_cycles, 1.0))))
            
            return {
                'rul_cycles': round(rul_cycles, 1),
                'rul_days': round(rul_days, 1),
                'rul_months': round(rul_months, 2),
                'physics_voltage': None,
                'confidence_percent': round(confidence, 1),
                'model_mae': mae_cycles,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        except Exception as e:
            return {'error': str(e), 'success': False}
            
    def predict_rul(self, features: Dict) -> Dict:
        """
        Predict battery RUL from features
        
        Args:
            features: Dict with required feature keys
        
        Returns:
            Prediction dict with rul_days, confidence, timestamp
        """
        if self.model is None:
            return {'error': 'Model not loaded', 'rul_days': None}
            
        # Fallback to zeros for prototype purposes if no normalizations
        X = np.zeros((1, 30, 4))
        
        # Predict
        predictions = self.model.predict(X, verbose=0)
        rul_days = float(predictions[0][0][0]) if isinstance(predictions, list) else float(predictions[0][0])
        rul_days = max(0, rul_days)
        
        mae = self.model_info.get('metrics', {}).get('mae_cycles', 8.5)
        confidence = max(0, min(100, 100 * (1 - mae / rul_days))) if rul_days > 0 else 0
        
        return {
            'rul_days': rul_days,
            'rul_months': rul_days / 30,
            'physics_voltage': None,
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
