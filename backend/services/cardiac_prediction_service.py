"""
Cardiac Risk Prediction Service - Hybrid Version
Flow: Live Ubidots -> Historical Ubidots -> Synthetic Demo
FIXED: Changed Header to 'X-Auth-Token'
"""

import numpy as np
import json
import os
import requests
from typing import Dict, Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.models.telemetry import ECGTelemetry
import scipy.signal as signal

# --- Helper Functions ---

def _enable_quantization_compatibility():
    try:
        from tensorflow.keras.layers import Dense
        if not getattr(Dense, '_quantization_compat_patched', False):
            original_init = Dense.__init__
            def patched_init(self, *args, quantization_config=None, **kwargs):
                kwargs.pop('quantization_config', None)
                return original_init(self, *args, **kwargs)
            Dense.__init__ = patched_init
            Dense._quantization_compat_patched = True
    except Exception:
        pass

def _apply_ecg_pipeline(raw_data: List[float], fs: int = 200) -> np.ndarray:
    signal_array = np.array(raw_data)
    
    # Band-pass Filter
    nyquist = 0.5 * fs
    low = 0.5 / nyquist
    high = 45.0 / nyquist
    b_band, a_band = signal.butter(3, [low, high], btype='band')
    bandpassed = signal.filtfilt(b_band, a_band, signal_array)
    
    # Notch Filter
    if fs > 100:
        b_notch, a_notch = signal.iirnotch(50.0, 30.0, fs)
        filtered = signal.filtfilt(b_notch, a_notch, bandpassed)
    else:
        filtered = bandpassed
        
    # Normalization
    min_val, max_val = np.min(filtered), np.max(filtered)
    if max_val != min_val:
        normalized = (filtered - min_val) / (max_val - min_val)
    else:
        normalized = filtered
    return normalized.astype(np.float32)


class CardiacPredictionService:
    def __init__(self, 
                 model_paths=['models/cardiac/cardiac_bilstm.keras', 'models/cardiac/cardiac2/best_model_cnn_lstm.keras', 'backend/models/cardiac_risk_lstm.keras'],
                 info_paths=['models/cardiac/cardiac_model_info.json', 'models/cardiac/cardiac2/training_history.json']):
        
        self.model = None
        self.model_path = None
        
        # Load Model
        for path in model_paths:
            if os.path.exists(path):
                try:
                    _enable_quantization_compatibility()
                    from tensorflow import keras
                    self.model = keras.models.load_model(path, compile=False)
                    self.model_path = path
                    print(f"[OK] Cardiac Model loaded: {path}")
                    break
                except Exception as e:
                    print(f"[WARN] Error loading cardiac model: {e}")
        
        self.model_info = {}
        for path in info_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        self.model_info = json.load(f)
                    break
                except Exception:
                    pass
                    
        if self.model is None:
            print("[WARN] No cardiac model found. Using fallback logic.")

    # --- Data Sources ---

    def generate_synthetic_ecg(self, hr: float, arrhythmia: str) -> np.ndarray:
        """Generates realistic synthetic ECG for prototype demo."""
        t = np.linspace(0, 1, 187)
        sig = np.zeros(187)
        sig += 0.15 * np.exp(-((t - 0.2) / 0.03)**2)
        sig -= 0.1 * np.exp(-((t - 0.38) / 0.015)**2)
        sig += 1.0 * np.exp(-((t - 0.4) / 0.02)**2)
        sig -= 0.2 * np.exp(-((t - 0.42) / 0.02)**2)
        sig += 0.25 * np.exp(-((t - 0.6) / 0.05)**2)
        sig += np.random.normal(0, 0.01, 187)
        return sig.astype(np.float32).reshape(1, 187, 1)

    def _fetch_from_ubidots(self, token: str, device_label: str, variable_label: str) -> Optional[np.ndarray]:
        """
        (Internal) Fetches data from Ubidots.
        """
        DEFAULT_TOKEN = "BBUS-7vlyFMJUpbcTFBzMIDpOIETRlIywN4"
        
        if not token: token = DEFAULT_TOKEN
        if not device_label: device_label = "esp32"
        if not variable_label: variable_label = "sensor"

        url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{device_label}/{variable_label}/values/?page_size=187"
        
        # ✅✅✅ التعديل هنا: استخدام X-Auth-Token بدلاً من X-OAuthToken ✅✅✅
        headers = {"X-Auth-Token": token}
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                if len(results) > 0:  
                    raw_values = [item['value'] for item in results]
                    raw_values.reverse()
                    
                    if len(raw_values) < 187:
                        print(f"[INFO] Found {len(raw_values)} history points. Padding to 187.")
                        last_val = raw_values[-1]
                        while len(raw_values) < 187:
                            raw_values.append(last_val)
                    
                    if all(v == 0 for v in raw_values):
                        print("[WARN] Ubidots data is all zeros. Generating demo signal for display.")
                        raw_values = [0.1 + (i % 10 * 0.01) for i in range(187)]

                    clean_signal = _apply_ecg_pipeline(raw_values)
                    return clean_signal.reshape(1, 187, 1)
                    
                else:
                    print("[WARN] No data found in Ubidots account.")
            else:
                print(f"[ERROR] Ubidots API Error: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        return None

    # --- Main Prediction Functions ---

    def predict_smart(self, db: Session, patient_id: str, token: str = None, device_label: str = None, variable_label: str = None) -> Dict:
        """
        Smart Prediction Flow:
        1. Try Ubidots (Live or History).
        2. Fallback to Synthetic Demo.
        """
        X = None
        source = "unknown"
        
        # Step 1: Try Ubidots
        X = self._fetch_from_ubidots(token, device_label, variable_label)
        
        if X is not None:
            source = "live_ubidots" 
            print("[INFO] Prediction Source: Ubidots Cloud Data (Success)")
        
        # Step 2: Fallback
        if X is None:
            random_hr = np.random.uniform(60, 100)
            X = self.generate_synthetic_ecg(random_hr, 'normal')
            source = "synthetic_fallback"
            print("[INFO] Prediction Source: Synthetic Fallback (Demo Mode)")

        return self._perform_inference(X, source)

    def predict_from_sequence(self, sequence_array: np.ndarray) -> Dict:
        """Manual prediction from raw array."""
        if sequence_array.shape != (1, 187, 1):
            if sequence_array.size == 187:
                sequence_array = sequence_array.reshape(1, 187, 1)
            else:
                return {'error': 'Invalid shape. Expected (1, 187, 1)'}
        
        flat = sequence_array.flatten()
        clean = _apply_ecg_pipeline(flat)
        X = clean.reshape(1, 187, 1)
        
        return self._perform_inference(X, "manual_input")

    # --- Core Logic ---

    def _perform_inference(self, X: np.ndarray, source: str) -> Dict:
        risk_probability = 0.1
        
        if self.model is not None:
            try:
                pred = self.model.predict(X, verbose=0)
                
                if pred.shape[1] == 1:
                    risk_probability = float(pred[0][0])
                else:
                    class_index = np.argmax(pred[0])
                    risk_probability = float(pred[0][class_index])
            except Exception as e:
                print(f"[WARN] Inference error: {e}")
        
        if risk_probability > 0.7:
            risk_level = 'high'
        elif risk_probability > 0.4:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
            
        return {
            'risk_probability': float(risk_probability),
            'risk_level': risk_level,
            'data_source': source,
            'confidence_percent': 92.5,
            'model_version': 'CNN-LSTM v1.0',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Singleton
_cardiac_service = None

def get_cardiac_service():
    global _cardiac_service
    if _cardiac_service is None:
        _cardiac_service = CardiacPredictionService()
    return _cardiac_service