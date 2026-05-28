"""
Metabolic Prediction Service
Loads Stacked LSTM and provides glucose predictions
"""
import numpy as np
import json
from tensorflow import keras
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.telemetry import GlucoseTelemetry

class MetabolicPredictionService:
    def __init__(self,
                 model_path='backend/models/metabolic_lstm.keras',
                 info_path='backend/models/metabolic_model_info.json'):
        """
        Initialize metabolic prediction service
        
        Args:
            model_path: Path to trained LSTM model
            info_path: Path to model metadata
        """
        self.model = keras.models.load_model(model_path)
        
        with open(info_path, 'r') as f:
            self.model_info = json.load(f)
        
        self.ts_features = self.model_info['timeseries_features']
        self.meta_features = self.model_info['metadata_features']
        self.norm_stats = self.model_info['normalization_stats']
        
        print(f"✅ Metabolic LSTM loaded: {model_path}")
        print(f"   Prediction horizon: {self.model_info['prediction_horizon_minutes']} min")
        print(f"   Test MAE: {self.model_info['metrics']['mae_mgdl']:.1f} mg/dL")
    
    def extract_features_from_db(self, db: Session, patient_id: str, hours=2):
        """
        Extract metabolic features from glucose telemetry
        
        Args:
            db: Database session
            patient_id: Patient ID
            hours: Look-back window (default 2h)
        
        Returns:
            Feature dicts (timeseries, metadata) or None
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Get glucose readings
        records = db.query(GlucoseTelemetry).filter(
            GlucoseTelemetry.patient_id == patient_id,
            GlucoseTelemetry.timestamp >= cutoff
        ).order_by(GlucoseTelemetry.timestamp.asc()).all()
        
        if len(records) < 10:  # Need at least 10 readings (10 min)
            return None, None
        
        # Extract glucose values
        glucose_values = [r.glucose_level * 100 for r in records]  # Convert g/L → mg/dL
        
        # Calculate time-series features
        ts_features = {
            'glucose_mean': np.mean(glucose_values),
            'glucose_std': np.std(glucose_values),
            'glucose_min': np.min(glucose_values),
            'glucose_max': np.max(glucose_values),
            'glucose_current': glucose_values[-1],
            'glucose_trend': (glucose_values[-1] - glucose_values[0]) / len(glucose_values),
            'insulin_mean': 10.0,  # Mock (would come from CGM or pump)
            'insulin_std': 2.0,
            'insulin_current': 10.0
        }
        
        # Metadata features (mock - would come from meal/exercise logs)
        meta_features = {
            'time_since_meal': 120,  # 2h (mock)
            'exercise_active': 0
        }
        
        return ts_features, meta_features
    
    def predict_glucose(self, ts_features: Dict, meta_features: Dict) -> Dict:
        """
        Predict glucose 1h ahead
        
        Args:
            ts_features: Time-series features
            meta_features: Metadata features
        
        Returns:
            Prediction dict with glucose_1h, confidence, risk_level
        """
        # Normalize time-series features
        ts_vector = np.zeros(len(self.ts_features))
        for i, col in enumerate(self.ts_features):
            value = ts_features[col]
            mean = self.norm_stats[col]['mean']
            std = self.norm_stats[col]['std']
            
            if std == 0:
                std = 1
            
            ts_vector[i] = (value - mean) / std
        
        # Normalize metadata features
        meta_vector = np.zeros(len(self.meta_features))
        for i, col in enumerate(self.meta_features):
            value = meta_features[col]
            mean = self.norm_stats[col]['mean']
            std = self.norm_stats[col]['std']
            
            if std == 0:
                std = 1
            
            meta_vector[i] = (value - mean) / std
        
        # Reshape for model (batch_size=1, timesteps=1, features)
        X_ts = ts_vector.reshape(1, 1, len(self.ts_features))
        X_meta = meta_vector.reshape(1, len(self.meta_features))
        
        # Predict
        glucose_pred_mgdl = float(self.model.predict([X_ts, X_meta], verbose=0)[0][0])
        
        # Ensure physiological range
        glucose_pred_mgdl = np.clip(glucose_pred_mgdl, 40, 400)
        
        # Convert to g/L
        glucose_pred_gl = glucose_pred_mgdl / 100
        
        # Risk classification
        if glucose_pred_mgdl < 70:
            risk_level = 'hypoglycemia_risk'
            risk_severity = 'high' if glucose_pred_mgdl < 60 else 'moderate'
        elif glucose_pred_mgdl > 180:
            risk_level = 'hyperglycemia_risk'
            risk_severity = 'high' if glucose_pred_mgdl > 250 else 'moderate'
        else:
            risk_level = 'normal'
            risk_severity = 'low'
        
        # Confidence (inverse of model MAE)
        mae = self.model_info['metrics']['mae_mgdl']
        confidence = max(0, min(100, 100 * (1 - mae / glucose_pred_mgdl))) if glucose_pred_mgdl > 0 else 0
        
        return {
            'glucose_current_mgdl': float(ts_features['glucose_current']),
            'glucose_current_gl': float(ts_features['glucose_current'] / 100),
            'glucose_1h_ahead_mgdl': glucose_pred_mgdl,
            'glucose_1h_ahead_gl': glucose_pred_gl,
            'glucose_change_mgdl': glucose_pred_mgdl - ts_features['glucose_current'],
            'risk_level': risk_level,
            'risk_severity': risk_severity,
            'confidence_percent': confidence,
            'model_mae_mgdl': mae,
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_from_db(self, db: Session, patient_id: str) -> Dict:
        """
        End-to-end glucose prediction from database
        
        Args:
            db: Database session
            patient_id: Patient ID
        
        Returns:
            Prediction dict or error
        """
        ts_features, meta_features = self.extract_features_from_db(db, patient_id)
        
        if ts_features is None:
            return {
                'error': 'Insufficient data (need 2h of glucose readings)',
                'glucose_1h_ahead_mgdl': None
            }
        
        return self.predict_glucose(ts_features, meta_features)

# Global singleton
_metabolic_service = None

def get_metabolic_service():
    """Get singleton metabolic prediction service"""
    global _metabolic_service
    if _metabolic_service is None:
        _metabolic_service = MetabolicPredictionService()
    return _metabolic_service
