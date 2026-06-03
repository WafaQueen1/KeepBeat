"""FastAPI main application for Smart TwinPac telemetry."""

from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db, init_db
from backend.models.telemetry import (
    BatteryTelemetry,
    ECGTelemetry,
    GlucoseTelemetry,
    TelemetryPostRequest,
    TelemetryPostResponse,
)
from backend.services.telemetry_storage_service import TelemetryStorageService
from backend.services.battery_prediction_service import get_battery_service
from backend.services.metabolic_prediction_service import get_metabolic_service
from backend.services.cardiac_prediction_service import get_cardiac_service

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for parallel model inference
executor = ThreadPoolExecutor(max_workers=3)


app = FastAPI(
    title="Smart TwinPac API",
    description="Digital Twin Backend for Pacemaker Monitoring",
    version="1.0.0",
)

# Mount frontend
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    
    @app.get("/")
    def serve_dashboard():
        return FileResponse("frontend/dashboard.html")
    
    print("[OK] Dashboard mounted at /")
else:
    @app.get("/")
    def root():
        return {"message": "Smart TwinPac API running", "docs": "/docs"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

telemetry_service = TelemetryStorageService()


class TelemetryQuery(BaseModel):
    patient_id: str
    hours_ago: Optional[int] = 24

class PrototypeRequest(BaseModel):
    hr: Optional[float] = None
    arrhythmia: Optional[str] = None
    sequence: Optional[list] = None


@app.on_event("startup")
async def load_models() -> None:
    print("Starting Smart TwinPac Backend...")
    init_db()
    print("Backend ready")
    
    print("\n[INFO] Loading AI Models...")
    try:
        import os
        
        # Only load if model files exist
        battery_path = 'backend/models/battery_rul_pinn_lstm.keras'
        cardiac_path = 'models/cardiac/cardiac_bilstm.keras'
        metabolic_path = 'backend/models/metabolic_lstm.keras'
        
        if os.path.exists(battery_path):
            get_battery_service()
            print("   [OK] Battery PINN-LSTM loaded")
        else:
            print(f"   [WARN] Battery model not found: {battery_path}")
        
        if os.path.exists(cardiac_path):
            get_cardiac_service()
            print("   [OK] Cardiac BiLSTM loaded")
        else:
            print(f"   [WARN] Cardiac model not found: {cardiac_path}")
        
        if os.path.exists(metabolic_path):
            get_metabolic_service()
            print("   [OK] Metabolic LSTM loaded")
        else:
            print(f"   [WARN] Metabolic model not found: {metabolic_path}")
        
        print("[INFO] Model loading complete\n")
    
    except Exception as e:
        print(f"   [ERROR] Model loading error: {e}")
        print("   Backend will run without AI predictions until models are added")


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Smart TwinPac Backend",
    }


@app.post("/api/v1/telemetry", response_model=TelemetryPostResponse)
def post_telemetry(payload: TelemetryPostRequest, db: Session = Depends(get_db)) -> TelemetryPostResponse:
    telemetry_data: dict = {"timestamp": payload.timestamp}

    if payload.telemetry_type == "ecg":
        if payload.ecg_samples:
            telemetry_data["ecg_samples"] = payload.ecg_samples
        elif payload.heart_rate is not None:
            telemetry_data["heart_rate"] = payload.heart_rate
    elif payload.telemetry_type == "glucose":
        telemetry_data["glucose_value"] = payload.glucose_value
    elif payload.telemetry_type == "battery":
        telemetry_data["battery_voltage"] = payload.battery_voltage

    analysis = telemetry_service.process_and_store(db, payload.patient_id, telemetry_data)
    return TelemetryPostResponse(
        patient_id=payload.patient_id,
        telemetry_type=payload.telemetry_type,
        stored=True,
        analysis=analysis,
    )


@app.post("/api/v1/telemetry/ecg/latest")
def get_latest_ecg(query: TelemetryQuery, db: Session = Depends(get_db)) -> dict:
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=query.hours_ago or 24)
    records = (
        db.query(ECGTelemetry)
        .filter(ECGTelemetry.patient_id == query.patient_id, ECGTelemetry.timestamp >= cutoff_time)
        .order_by(ECGTelemetry.timestamp.desc())
        .limit(100)
        .all()
    )
    return {
        "patient_id": query.patient_id,
        "count": len(records),
        "data": [
            {
                "heart_rate": row.heart_rate,
                "arrhythmia": row.arrhythmia_type,
                "r_peak_count": row.r_peak_count,
                "timestamp": row.timestamp.isoformat(),
            }
            for row in records
        ],
    }


@app.post("/api/v1/telemetry/glucose/latest")
def get_latest_glucose(query: TelemetryQuery, db: Session = Depends(get_db)) -> dict:
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=query.hours_ago or 24)
    records = (
        db.query(GlucoseTelemetry)
        .filter(GlucoseTelemetry.patient_id == query.patient_id, GlucoseTelemetry.timestamp >= cutoff_time)
        .order_by(GlucoseTelemetry.timestamp.desc())
        .limit(100)
        .all()
    )
    return {
        "patient_id": query.patient_id,
        "count": len(records),
        "data": [
            {
                "glucose_level": row.glucose_level,
                "alert_state": row.alert_state,
                "alert_confirmed": row.alert_confirmed,
                "severity": row.severity,
                "recommendation": row.recommendation,
                "timestamp": row.timestamp.isoformat(),
            }
            for row in records
        ],
    }


@app.post("/api/v1/telemetry/battery/latest")
def get_latest_battery(query: TelemetryQuery, db: Session = Depends(get_db)) -> dict:
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=query.hours_ago or 24)
    records = (
        db.query(BatteryTelemetry)
        .filter(BatteryTelemetry.patient_id == query.patient_id, BatteryTelemetry.timestamp >= cutoff_time)
        .order_by(BatteryTelemetry.timestamp.desc())
        .limit(100)
        .all()
    )
    return {
        "patient_id": query.patient_id,
        "count": len(records),
        "data": [
            {
                "voltage": row.voltage,
                "soc_percent": row.soc_percent,
                "rul_days_local": row.rul_days_local,
                "rul_days_cloud": row.rul_days_cloud,
                "health_status": row.health_status,
                "low_battery_alert": row.low_battery_alert,
                "timestamp": row.timestamp.isoformat(),
            }
            for row in records
        ],
    }


@app.get("/api/v1/dashboard/{patient_id}")
def get_dashboard_summary(patient_id: str, db: Session = Depends(get_db)) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

    latest_ecg = (
        db.query(ECGTelemetry)
        .filter(ECGTelemetry.patient_id == patient_id, ECGTelemetry.timestamp >= cutoff)
        .order_by(ECGTelemetry.timestamp.desc())
        .first()
    )
    latest_glucose = (
        db.query(GlucoseTelemetry)
        .filter(GlucoseTelemetry.patient_id == patient_id, GlucoseTelemetry.timestamp >= cutoff)
        .order_by(GlucoseTelemetry.timestamp.desc())
        .first()
    )
    latest_battery = (
        db.query(BatteryTelemetry)
        .filter(BatteryTelemetry.patient_id == patient_id, BatteryTelemetry.timestamp >= cutoff)
        .order_by(BatteryTelemetry.timestamp.desc())
        .first()
    )

    return {
        "patient_id": patient_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ecg": {
            "heart_rate": latest_ecg.heart_rate if latest_ecg else None,
            "arrhythmia": latest_ecg.arrhythmia_type if latest_ecg else "unknown",
            "r_peak_count": latest_ecg.r_peak_count if latest_ecg else 0,
            "last_update": latest_ecg.timestamp.isoformat() if latest_ecg else None,
        },
        "glucose": {
            "level": latest_glucose.glucose_level if latest_glucose else None,
            "alert_state": latest_glucose.alert_state if latest_glucose else "unknown",
            "alert_confirmed": latest_glucose.alert_confirmed if latest_glucose else False,
            "severity": latest_glucose.severity if latest_glucose else None,
            "last_update": latest_glucose.timestamp.isoformat() if latest_glucose else None,
        },
        "battery": {
            "voltage": latest_battery.voltage if latest_battery else None,
            "soc_percent": latest_battery.soc_percent if latest_battery else None,
            "rul_days": latest_battery.rul_days_local if latest_battery else None,
            "status": latest_battery.health_status if latest_battery else "unknown",
            "low_battery_alert": latest_battery.low_battery_alert if latest_battery else False,
            "last_update": latest_battery.timestamp.isoformat() if latest_battery else None,
        },
    }

@app.get("/api/v1/predictions/battery/{patient_id}")
def predict_battery_rul(patient_id: str, db: Session = Depends(get_db)):
    """
    Predict battery RUL using PINN-LSTM model
    """
    try:
        battery_service = get_battery_service()
        prediction = battery_service.predict_from_db(db, patient_id)
        
        return {
            "patient_id": patient_id,
            "model": "PINN-LSTM Hybrid",
            "prediction": prediction
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/predictions/cardiac/prototype")
def prototype_cardiac_prediction(req: PrototypeRequest):
    """
    On-demand cardiac prediction for prototyping dashboard.
    """
    import numpy as np
    try:
        cardiac_service = get_cardiac_service()
        if req.sequence and len(req.sequence) == 187:
            seq = np.array(req.sequence, dtype=np.float32).reshape(1, 187, 1)
        else:
            hr = req.hr if req.hr is not None else 70.0
            arrhythmia = req.arrhythmia if req.arrhythmia is not None else 'normal'
            seq = cardiac_service.generate_synthetic_ecg(hr, arrhythmia)
        
        result = cardiac_service.predict_from_sequence(seq)
        result['sequence'] = seq.flatten().tolist()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/predictions/metabolic/{patient_id}")
def predict_glucose_1h(patient_id: str, db: Session = Depends(get_db)):
    """
    Predict glucose level 1 hour ahead using Stacked LSTM
    """
    try:
        metabolic_service = get_metabolic_service()
        prediction = metabolic_service.predict_from_db(db, patient_id)
        
        return {
            "patient_id": patient_id,
            "model": "Stacked LSTM (Bergman Model)",
            "prediction": prediction
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/predictions/all/{patient_id}")
def get_all_predictions(patient_id: str, db: Session = Depends(get_db)):
    """
    Run all 3 AI models in parallel and return unified predictions.
    
    Used by dashboard for single-call refresh (every 5s).
    
    Returns:
        - battery: PINN-LSTM RUL prediction
        - cardiac: BiLSTM risk prediction
        - metabolic: Stacked LSTM glucose prediction
        - alerts: Any critical conditions detected
    """
    import os
    
    results = {
        'patient_id': patient_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'battery': None,
        'cardiac': None,
        'metabolic': None,
        'alerts': []
    }
    
    # ===== BATTERY PREDICTION =====
    try:
        if os.path.exists('backend/models/battery_rul_pinn_lstm.keras'):
            battery_service = get_battery_service()
            results['battery'] = battery_service.predict_from_db(db, patient_id)
            
            # Alert if battery critical
            if results['battery'] and results['battery'].get('rul_days'):
                rul = results['battery']['rul_days']
                if rul < 30:
                    results['alerts'].append({
                        'type': 'battery_critical',
                        'severity': 'critical',
                        'message': f'Battery RUL: {rul:.0f} days — Replacement URGENT',
                        'value': rul
                    })
                elif rul < 90:
                    results['alerts'].append({
                        'type': 'battery_low',
                        'severity': 'warning',
                        'message': f'Battery RUL: {rul:.0f} days — Schedule replacement',
                        'value': rul
                    })
    except Exception as e:
        results['battery'] = {'error': str(e)}
    
    # ===== CARDIAC PREDICTION =====
    try:
        if os.path.exists('backend/models/cardiac_risk_lstm.keras'):
            cardiac_service = get_cardiac_service()
            results['cardiac'] = cardiac_service.predict_from_db(db, patient_id)
            
            # Alert if high cardiac risk
            if results['cardiac'] and results['cardiac'].get('risk_probability'):
                prob = results['cardiac']['risk_probability']
                if prob > 0.7:
                    results['alerts'].append({
                        'type': 'cardiac_high_risk',
                        'severity': 'critical',
                        'message': f'Cardiac risk: {prob*100:.0f}% — Arrhythmia likely in 24h',
                        'value': prob
                    })
                elif prob > 0.5:
                    results['alerts'].append({
                        'type': 'cardiac_moderate_risk',
                        'severity': 'warning',
                        'message': f'Cardiac risk: {prob*100:.0f}% — Monitor closely',
                        'value': prob
                    })
    except Exception as e:
        results['cardiac'] = {'error': str(e)}
    
    # ===== METABOLIC PREDICTION =====
    try:
        if os.path.exists('backend/models/metabolic_lstm.keras'):
            metabolic_service = get_metabolic_service()
            results['metabolic'] = metabolic_service.predict_from_db(db, patient_id)
            
            # Alert if glucose risk predicted
            if results['metabolic'] and results['metabolic'].get('risk_level'):
                risk = results['metabolic']['risk_level']
                glucose = results['metabolic'].get('glucose_1h_ahead_mgdl', 0)
                
                if risk == 'hypoglycemia_risk':
                    results['alerts'].append({
                        'type': 'glucose_hypo',
                        'severity': 'critical' if glucose < 60 else 'warning',
                        'message': f'Glucose in 1h: {glucose:.0f} mg/dL — Hypoglycemia predicted',
                        'value': glucose
                    })
                elif risk == 'hyperglycemia_risk':
                    results['alerts'].append({
                        'type': 'glucose_hyper',
                        'severity': 'critical' if glucose > 250 else 'warning',
                        'message': f'Glucose in 1h: {glucose:.0f} mg/dL — Hyperglycemia predicted',
                        'value': glucose
                    })
    except Exception as e:
        results['metabolic'] = {'error': str(e)}
    
    # Sort alerts by severity
    severity_order = {'critical': 0, 'warning': 1, 'info': 2}
    results['alerts'].sort(key=lambda x: severity_order.get(x['severity'], 99))
    
    return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
