"""FastAPI main application for Smart TwinPac telemetry."""

from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db, init_db, SessionLocal
from backend.models.doctor import Doctor
from backend.models.patient import Patient
from backend.models.telemetry import (
    BatteryTelemetry,
    ECGTelemetry,
    GlucoseTelemetry,
    TelemetryPostRequest,
    TelemetryPostResponse,
)
from backend.security.auth import PasswordManager
from pydantic import Field
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


class LoginRequest(BaseModel):
    email: str
    password: str


class DoctorCreateRequest(BaseModel):
    full_name: str
    email: str
    password: str
    status: str = "pending"
    role: str = "doctor"


class PatientCreateRequest(BaseModel):
    doctor_id: str
    full_name: str
    dob: str
    medical_id: str
    affiliation: str
    diagnosis_notes: str | None = None


class ReassignRequest(BaseModel):
    doctor_id: str


def doctor_to_dict(doctor: Doctor) -> dict:
    return {
        "id": doctor.id,
        "full_name": doctor.full_name,
        "email": doctor.email,
        "role": doctor.role,
        "status": doctor.status,
        "created_at": doctor.created_at.isoformat() if doctor.created_at else None,
    }


def patient_to_dict(patient: Patient) -> dict:
    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "dob": patient.dob.date().isoformat() if patient.dob else None,
        "medical_id": patient.medical_id,
        "affiliation": patient.affiliation,
        "diagnosis_notes": patient.diagnosis_notes,
        "doctor_id": patient.doctor_id,
        "status": patient.status,
        "last_sync": patient.last_sync.isoformat() if patient.last_sync else None,
        "created_at": patient.created_at.isoformat() if patient.created_at else None,
    }


def seed_initial_accounts() -> None:
    db = SessionLocal()
    try:
        admin = db.query(Doctor).filter_by(email="julian.sterling@keepbeat.com").first()
        if not admin:
            admin = Doctor(
                id=str(uuid.uuid4()),
                full_name="Julian Sterling",
                email="julian.sterling@keepbeat.com",
                password_hash=PasswordManager.hash_password("password123"),
                role="admin",
                status="approved",
            )
            db.add(admin)

        clinician = db.query(Doctor).filter_by(email="emma.clark@keepbeat.com").first()
        if not clinician:
            clinician = Doctor(
                id=str(uuid.uuid4()),
                full_name="Emma Clark",
                email="emma.clark@keepbeat.com",
                password_hash=PasswordManager.hash_password("password123"),
                role="doctor",
                status="approved",
            )
            db.add(clinician)

        patient = db.query(Patient).filter_by(id="srarah.jenkins@keepbeat.com").first()
        if not patient:
            patient = Patient(
                id="srarah.jenkins@keepbeat.com",
                full_name="Sarah Jenkins",
                dob=datetime(1985, 6, 18, tzinfo=timezone.utc),
                medical_id="TP-0001",
                affiliation="KeepBeat Cardiology",
                diagnosis_notes="Type 2 Diabetes, Dual-chamber pacemaker",
                doctor_id=clinician.id,
                status="approved",
                last_sync=datetime.now(timezone.utc),
            )
            db.add(patient)

        db.commit()
    finally:
        db.close()


class TelemetryQuery(BaseModel):
    patient_id: str
    hours_ago: Optional[int] = 24

class PrototypeRequest(BaseModel):
    hr: Optional[float] = None
    arrhythmia: Optional[str] = None
    sequence: Optional[list] = None

# --- IoT Bluetooth & WebSocket State ---
latest_ecg_window = []
latest_prediction = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for d in disconnected:
            self.disconnect(d)

manager = ConnectionManager()


@app.on_event("startup")
async def load_models() -> None:
    print("Starting Smart TwinPac Backend...")
    init_db()
    seed_initial_accounts()
    print("Backend ready")
    
    print("\n[INFO] Loading AI Models...")
    try:
        import os
        
        # Only load if model files exist
        battery_paths = [
            'backend/models/battery_rul_pinn_lstm.keras',
            'models/battery/battery_pinn_lstm.keras',
            'models/battery_rul_pinn_lstm.keras'
        ]
        cardiac_paths = [
            'models/cardiac/cardiac_bilstm.keras',
            'models/cardiac/cardiac2/best_model_cnn_lstm.keras',
            'backend/models/cardiac_risk_lstm.keras',
            'models/cardiac_bilstm.keras'
        ]
        metabolic_paths = [
            'models/metabolic/metabolic_stacked_lstm.keras',
            'models/metabolic/metabolic_stacked_lstm_best.keras',
            'models/metabolic_stacked_lstm_best.keras',
            'models/metabolic_stacked_lstm.keras',
            'backend/models/metabolic_lstm.keras'
        ]

        if any(os.path.exists(path) for path in battery_paths):
            battery_service = get_battery_service()
            if getattr(battery_service, 'model', None) is not None:
                print("   [OK] Battery PINN-LSTM loaded")
            else:
                print("   [WARN] Battery model file found but failed to load; using fallback predictions")
        else:
            print(f"   [WARN] Battery model not found in any known path")

        if any(os.path.exists(path) for path in cardiac_paths):
            cardiac_service = get_cardiac_service()
            if getattr(cardiac_service, 'model', None) is not None:
                print("   [OK] Cardiac BiLSTM loaded")
            else:
                print("   [WARN] Cardiac model file found but failed to load; using fallback predictions")
        else:
            print(f"   [WARN] Cardiac model not found in any known path")

        if any(os.path.exists(path) for path in metabolic_paths):
            metabolic_service = get_metabolic_service()
            if getattr(metabolic_service, 'model', None) is not None:
                print("   [OK] Metabolic LSTM loaded")
            else:
                print("   [WARN] Metabolic model file found but failed to load; using fallback predictions")
        else:
            print(f"   [WARN] Metabolic model not found in any known path")
        
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


@app.get("/api/model/status")
def model_status() -> dict:
    """Report which trained model files are active for prototype testing."""
    services = {
        "battery": get_battery_service(),
        "cardiac": get_cardiac_service(),
        "metabolic": get_metabolic_service(),
    }
    return {
        name: {
            "loaded": getattr(service, "model", None) is not None,
            "model_path": getattr(service, "model_path", None),
            "info_path": getattr(service, "info_path", None),
            "fallback": getattr(service, "model", None) is None,
        }
        for name, service in services.items()
    }


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    doctor = db.query(Doctor).filter(Doctor.email == payload.email.strip().lower()).first()
    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if doctor.status != "approved":
        raise HTTPException(status_code=403, detail="Account not approved")
    if not PasswordManager.verify_password(payload.password, doctor.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "id": doctor.id,
        "full_name": doctor.full_name,
        "email": doctor.email,
        "role": doctor.role,
        "status": doctor.status,
    }


@app.get("/api/v1/doctors")
def list_doctors(db: Session = Depends(get_db)) -> list[dict]:
    doctors = db.query(Doctor).order_by(Doctor.created_at.desc()).all()
    return [doctor_to_dict(d) for d in doctors]


@app.post("/api/v1/doctors")
def create_doctor(payload: DoctorCreateRequest, db: Session = Depends(get_db)) -> dict:
    existing = db.query(Doctor).filter(Doctor.email == payload.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="A doctor with that email already exists")
    doctor = Doctor(
        id=str(uuid.uuid4()),
        full_name=payload.full_name.strip(),
        email=payload.email.strip().lower(),
        password_hash=PasswordManager.hash_password(payload.password),
        role=payload.role,
        status=payload.status,
    )
    db.add(doctor)
    db.commit()
    return doctor_to_dict(doctor)


@app.get("/api/v1/admin/pending_doctors")
def list_pending_doctors(db: Session = Depends(get_db)) -> list[dict]:
    doctors = db.query(Doctor).filter(Doctor.status == "pending").order_by(Doctor.created_at.asc()).all()
    return [doctor_to_dict(d) for d in doctors]


@app.put("/api/v1/admin/approve_doctor/{doctor_id}")
def approve_doctor(doctor_id: str, db: Session = Depends(get_db)) -> dict:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.status = "approved"
    db.commit()
    return doctor_to_dict(doctor)


@app.put("/api/v1/admin/refuse_doctor/{doctor_id}")
def refuse_doctor(doctor_id: str, db: Session = Depends(get_db)) -> dict:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.status = "rejected"
    db.commit()
    return doctor_to_dict(doctor)


@app.delete("/api/v1/doctors/{doctor_id}")
def delete_doctor(doctor_id: str, db: Session = Depends(get_db)) -> dict:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.query(Patient).filter(Patient.doctor_id == doctor.id).update({Patient.doctor_id: None})
    db.delete(doctor)
    db.commit()
    return {"message": "Doctor removed"}


@app.post("/api/v1/patients")
def create_patient(payload: PatientCreateRequest, db: Session = Depends(get_db)) -> dict:
    if db.query(Patient).filter(Patient.medical_id == payload.medical_id.strip()).first():
        raise HTTPException(status_code=400, detail="A patient with that medical ID already exists")

    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor or doctor.status != "approved":
        raise HTTPException(status_code=400, detail="Assigned doctor is not approved or does not exist")

    try:
        dob = datetime.fromisoformat(payload.dob)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format for dob")

    patient = Patient(
        id=str(uuid.uuid4()),
        full_name=payload.full_name.strip(),
        dob=dob,
        medical_id=payload.medical_id.strip(),
        affiliation=payload.affiliation.strip(),
        diagnosis_notes=(payload.diagnosis_notes or "").strip(),
        doctor_id=doctor.id,
        status="approved",
    )
    db.add(patient)
    db.commit()
    return patient_to_dict(patient)


@app.get("/api/v1/patients")
def list_patients(doctor_id: str, db: Session = Depends(get_db)) -> list[dict]:
    patients = db.query(Patient).filter(Patient.doctor_id == doctor_id).order_by(Patient.created_at.desc()).all()
    return [patient_to_dict(p) for p in patients]


@app.get("/api/v1/patients/all")
def list_all_patients(db: Session = Depends(get_db)) -> list[dict]:
    patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
    return [patient_to_dict(p) for p in patients]


@app.get("/api/v1/admin/pending_patients")
def list_pending_patients(db: Session = Depends(get_db)) -> list[dict]:
    patients = db.query(Patient).filter(Patient.status == "pending").order_by(Patient.created_at.asc()).all()
    return [patient_to_dict(p) for p in patients]


@app.put("/api/v1/admin/approve_patient/{patient_id}")
def approve_patient(patient_id: str, db: Session = Depends(get_db)) -> dict:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.status = "approved"
    db.commit()
    return patient_to_dict(patient)


@app.put("/api/v1/admin/refuse_patient/{patient_id}")
def refuse_patient(patient_id: str, db: Session = Depends(get_db)) -> dict:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.status = "rejected"
    db.commit()
    return patient_to_dict(patient)


@app.put("/api/v1/admin/reassign_patient/{patient_id}")
def reassign_patient(patient_id: str, payload: ReassignRequest, db: Session = Depends(get_db)) -> dict:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id, Doctor.status == "approved").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not doctor:
        raise HTTPException(status_code=400, detail="Target doctor not found or not approved")
    patient.doctor_id = doctor.id
    db.commit()
    return patient_to_dict(patient)


@app.delete("/api/v1/patients/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)) -> dict:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"message": "Patient removed"}


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

class TelemetryBulkItem(BaseModel):
    timestamp: str
    patient_id: str
    device_id: str
    sensor_type: str
    value: float
    unit: str

class TelemetryBulkRequest(BaseModel):
    items: list[TelemetryBulkItem]

@app.post("/api/v1/telemetry/bulk")
def post_telemetry_bulk(payload: TelemetryBulkRequest, db: Session = Depends(get_db)):
    processed = 0
    for item in payload.items:
        telemetry_data = {"timestamp": item.timestamp}
        if item.sensor_type == "pacemaker" or item.sensor_type == "ecg":
            # Just store heart rate for bulk
            telemetry_data["heart_rate"] = item.value
        elif item.sensor_type == "cgm" or item.sensor_type == "glucose":
            telemetry_data["glucose_value"] = item.value
        elif item.sensor_type == "battery":
            telemetry_data["battery_voltage"] = item.value
        
        telemetry_service.process_and_store(db, item.patient_id, telemetry_data)
        processed += 1
        
    return {"message": "Bulk sync successful", "processed": processed}


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

class PredictRequest(BaseModel):
    samples: list[float]

@app.post("/api/model/cardiac/predict")
async def predict_cardiac_risk(req: PredictRequest):
    global latest_ecg_window, latest_prediction
    if len(req.samples) != 187:
        raise HTTPException(status_code=400, detail="Must provide exactly 187 samples")
    
    latest_ecg_window = req.samples
    
    try:
        import numpy as np
        cardiac_service = get_cardiac_service()
        seq = np.array(req.samples, dtype=np.float32).reshape(1, 187, 1)
        result = cardiac_service.predict_from_sequence(seq)
        
        # Ensure result has standard keys for frontend
        prob = result.get('risk_probability', 0.0)
        risk_level = result.get('risk_level', 'low')
        
        res = {
            "prediction_class": 1 if risk_level in ['high', 'moderate'] else 0,
            "label": risk_level.capitalize(),
            "risk_level": risk_level,
            "risk_probability": prob,
            "confidence_percent": prob * 100,
            "raw_scores": [],
            "model_version": "CNN-LSTM v1.0",
            "sequence": req.samples
        }
        latest_prediction = res
        
        await manager.broadcast({
            "type": "prediction",
            "data": res
        })
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class BatteryPredictRequest(BaseModel):
    # Shape: 30 steps, 4 features (voltage, current, capacity, temperature)
    sequence: list[list[float]]

# === ADD THIS ENDPOINT TO main.py ===

@app.get("/api/model/cardiac/smart_predict")
async def smart_cardiac_prediction(patient_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Intelligent Prediction Endpoint:
    1. Tries Live Ubidots (Friend's ESP32).
    2. If offline, tries Local Database History.
    3. If empty, generates Synthetic Demo Data.
    """
    try:
        service = get_cardiac_service()
        
        # Call the smart logic from your service
        # We pass db and patient_id so it can check history if live fails
        result = service.predict_smart(db=db, patient_id=patient_id)
        
        # The result contains 'data_source' which tells the UI where data came from
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/model/battery/predict")
async def predict_battery_rul_proto(req: BatteryPredictRequest):
    if len(req.sequence) != 30 or any(len(step) != 4 for step in req.sequence):
        raise HTTPException(status_code=400, detail="Must provide exactly 30 steps of 4 features")
    
    try:
        import numpy as np
        from backend.services.battery_prediction_service import get_battery_service
        service = get_battery_service()
        
        seq = np.array(req.sequence, dtype=np.float32).reshape(1, 30, 4)
        result = service.predict_from_sequence(seq)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MetabolicPredictRequest(BaseModel):
    # Shape: timeseries (12 steps of 1 feature), metadata (5 features)
    timeseries: list[float]
    metadata: list[float]

@app.post("/api/model/metabolic/predict")
async def predict_metabolic_proto(req: MetabolicPredictRequest):
    if len(req.timeseries) != 12 or len(req.metadata) != 5:
        raise HTTPException(status_code=400, detail="Must provide exactly 12 timeseries steps and 5 metadata features")
    
    try:
        from backend.services.metabolic_prediction_service import get_metabolic_service
        service = get_metabolic_service()
        
        result = service.predict_from_sequence(req.timeseries, req.metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/iot/ecg/latest")
async def get_latest_ecg():
    if not latest_ecg_window:
        return {"error": "No ECG data available yet"}
    return {
        "sequence": latest_ecg_window,
        "prediction": latest_prediction
    }

@app.websocket("/ws/ecg")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        if latest_prediction:
            await websocket.send_json({
                "type": "prediction",
                "data": latest_prediction
            })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

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
        battery_available = any(os.path.exists(path) for path in [
            'backend/models/battery_rul_pinn_lstm.keras',
            'models/battery/battery_pinn_lstm.keras',
            'models/battery_rul_pinn_lstm.keras'
        ])
        if battery_available:
            battery_service = get_battery_service()
            results['battery'] = battery_service.predict_from_db(db, patient_id)
            
            # Alert if battery critical
            if results['battery'] and results['battery'].get('rul_days') is not None:
                rul = results['battery']['rul_days']
                if rul < 30:
                    results['alerts'].append({
                        'type': 'battery_critical',
                        'severity': 'critical',
                        'message': f'Battery RUL: {rul:.0f} days - Replacement URGENT',
                        'value': rul
                    })
                elif rul < 90:
                    results['alerts'].append({
                        'type': 'battery_low',
                        'severity': 'warning',
                        'message': f'Battery RUL: {rul:.0f} days - Schedule replacement',
                        'value': rul
                    })
    except Exception as e:
        results['battery'] = {'error': str(e)}
    
    # ===== CARDIAC PREDICTION =====
    try:
        cardiac_available = any(os.path.exists(path) for path in [
            'models/cardiac/cardiac_bilstm.keras',
            'models/cardiac/cardiac2/best_model_cnn_lstm.keras',
            'backend/models/cardiac_risk_lstm.keras',
            'models/cardiac_bilstm.keras'
        ])
        if cardiac_available:
            cardiac_service = get_cardiac_service()
            results['cardiac'] = cardiac_service.predict_from_db(db, patient_id)
            
            # Alert if high cardiac risk
            if results['cardiac'] and results['cardiac'].get('risk_probability') is not None:
                prob = results['cardiac']['risk_probability']
                if prob > 0.7:
                    results['alerts'].append({
                        'type': 'cardiac_high_risk',
                        'severity': 'critical',
                        'message': f'Cardiac risk: {prob*100:.0f}% - Arrhythmia likely in 24h',
                        'value': prob
                    })
                elif prob > 0.5:
                    results['alerts'].append({
                        'type': 'cardiac_moderate_risk',
                        'severity': 'warning',
                        'message': f'Cardiac risk: {prob*100:.0f}% - Monitor closely',
                        'value': prob
                    })
    except Exception as e:
        results['cardiac'] = {'error': str(e)}
    
    # ===== METABOLIC PREDICTION =====
    try:
        metabolic_available = any(os.path.exists(path) for path in [
            'models/metabolic/metabolic_stacked_lstm.keras',
            'models/metabolic/metabolic_stacked_lstm_best.keras',
            'models/metabolic_stacked_lstm_best.keras',
            'models/metabolic_stacked_lstm.keras',
            'backend/models/metabolic_lstm.keras'
        ])
        if metabolic_available:
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
                        'message': f'Glucose in 1h: {glucose:.0f} mg/dL - Hypoglycemia predicted',
                        'value': glucose
                    })
                elif risk == 'hyperglycemia_risk':
                    results['alerts'].append({
                        'type': 'glucose_hyper',
                        'severity': 'critical' if glucose > 250 else 'warning',
                        'message': f'Glucose in 1h: {glucose:.0f} mg/dL - Hyperglycemia predicted',
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
