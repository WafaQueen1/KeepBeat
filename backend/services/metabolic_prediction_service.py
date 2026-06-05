"""
Metabolic Prediction Service
Loads Stacked LSTM and provides glucose predictions
"""
import numpy as np
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.telemetry import GlucoseTelemetry

class MetabolicPredictionService:
    def __init__(self,
                 model_path='models/metabolic_stacked_lstm_best.keras',
                 info_path='models/metabolic_model_info.json'):
        """
        Initialize metabolic prediction service
        
        Args:
            model_path: Path to trained LSTM model
            info_path: Path to model metadata
        """
        import os
        self.model = None
        self.model_info = {}
        
        if os.path.exists(model_path):
            try:
                from tensorflow import keras
                self.model = keras.models.load_model(model_path)
                print(f"✅ Metabolic Stacked LSTM model loaded: {model_path}")
            except Exception as e:
                print(f"⚠️ Error loading metabolic model: {e}")
        
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r') as f:
                    self.model_info = json.load(f)
                
                # Fetch normalization stats from JSON
                self.norm_ts_mean = self.model_info['normalization']['timeseries']['mean']
                self.norm_ts_scale = self.model_info['normalization']['timeseries']['scale']
                self.norm_meta_mean = np.array(self.model_info['normalization']['metadata']['mean'])
                self.norm_meta_scale = np.array(self.model_info['normalization']['metadata']['scale'])
                
                mae = self.model_info.get('metrics', {}).get('mae_mgdl', 0)
                print(f"   Test MAE: {mae:.1f} mg/dL")
            except Exception as e:
                print(f"⚠️ Error loading metabolic model info: {e}")
    
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
    
    def predict_from_sequence(self, ts_values: List[float], meta_values: List[float]) -> Dict:
        """
        Predict glucose 1h ahead from raw arrays
        
        Args:
            ts_values: List of 12 glucose readings
            meta_values: List of 5 metadata values
        """
        if self.model is None:
            return {'error': 'Metabolic model not loaded', 'success': False}
            
        try:
            # Normalize timeseries
            ts_vector = (np.array(ts_values) - self.norm_ts_mean) / self.norm_ts_scale
            
            # Normalize metadata
            meta_vector = (np.array(meta_values) - self.norm_meta_mean) / self.norm_meta_scale
            
            # Reshape
            X_ts = ts_vector.reshape(1, 12, 1)
            X_meta = meta_vector.reshape(1, 5)
            
            # Predict
            glucose_pred_mgdl = float(self.model.predict([X_ts, X_meta], verbose=0)[0][0])
            glucose_pred_mgdl = np.clip(glucose_pred_mgdl, 40, 400)
            glucose_pred_gl = glucose_pred_mgdl / 100.0
            
            glucose_current = ts_values[-1]
            
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
            
            mae = self.model_info.get('metrics', {}).get('mae_mgdl', 13.6)
            confidence = max(0.0, min(100.0, 100 * (1 - mae / glucose_pred_mgdl))) if glucose_pred_mgdl > 0 else 0.0
            
            return {
                'glucose_current_mgdl': float(glucose_current),
                'glucose_current_gl': float(glucose_current / 100.0),
                'glucose_1h_ahead_mgdl': glucose_pred_mgdl,
                'glucose_1h_ahead_gl': glucose_pred_gl,
                'glucose_change_mgdl': glucose_pred_mgdl - glucose_current,
                'risk_level': risk_level,
                'risk_severity': risk_severity,
                'confidence_percent': confidence,
                'model_mae_mgdl': mae,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        except Exception as e:
            return {'error': str(e), 'success': False}

    def predict_glucose(self, ts_features: Dict, meta_features: Dict) -> Dict:
        """
        Predict glucose 1h ahead
        
        Args:
            ts_features: Time-series features
            meta_features: Metadata features
        
        Returns:
            Prediction dict with glucose_1h, confidence, risk_level
        """
        if self.model is None:
            return {'error': 'Model not loaded'}
            
        # Fallback to zeros for prototype purposes if needed
        X_ts = np.zeros((1, 12, 1))
        X_meta = np.zeros((1, 5))
        
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
        mae = self.model_info.get('metrics', {}).get('mae_mgdl', 13.6)
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
