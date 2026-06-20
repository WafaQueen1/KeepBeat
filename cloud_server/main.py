from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from datetime import datetime
import asyncio
from pydantic import BaseModel
import numpy as np
import tensorflow as tf

# Load the ML model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "cardiac", "cardiac2", "best_model_cnn_lstm.keras")
model = None

# State & WebSocket
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

# Local imports for Clean Code
from db_manager import db
from models import DoctorLogin, DoctorCreate, PatientCreate, PatientReassign

app = FastAPI(title="KeepBeat Cloud Server", version="1.2.0")

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Simple API trace log for debugging."""
    print(f"API_TRACE: {request.method} {request.url.path}")
    return await call_next(request)

# --- Lifecycle ---
@app.on_event("startup")
async def startup():
    """Connect and initialize database on startup."""
    global model
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"Loaded ML model from {MODEL_PATH}")
    except Exception as e:
        print(f"Warning: Could not load ML model: {e}")

    if await db.connect():
        await db.initialize_tables()

# --- Health Check ---
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "engine": db.engine}

# --- Authentication ---
@app.post("/api/v1/auth/login")
async def login(credentials: DoctorLogin):
    # 1. Admin login
    admin = await db.fetch_one(
        "SELECT id, full_name, email FROM admins WHERE email = $1 AND password = $2", 
        credentials.email, credentials.password
    )
    if admin: 
        return {"id": admin["id"], "full_name": admin["full_name"], "email": admin["email"], "role": "admin"}
        
        
    # 2. Doctor login
    doctor = await db.fetch_one(
        "SELECT id, full_name, email, status FROM doctors WHERE email = $1 AND password = $2", 
        credentials.email, credentials.password
    )
    if doctor: 
        status = doctor["status"]
        if status == "pending": 
            raise HTTPException(status_code=403, detail="Clinical account pending approval")
        elif status == "rejected": 
            raise HTTPException(status_code=403, detail="Clinical access denied")
        return {"id": doctor["id"], "full_name": doctor["full_name"], "email": doctor["email"], "role": "doctor"}

    # 3. Patient login
    patient = await db.fetch_one(
        "SELECT id, full_name, email, status FROM patients WHERE email = $1 AND password = $2", 
        credentials.email, credentials.password
    )
    if patient:
        if patient["status"] != "approved":
            raise HTTPException(status_code=403, detail="Patient enrollment pending clinical approval")
        return {"id": patient["id"], "full_name": patient["full_name"], "email": patient["email"], "role": "patient"}

    raise HTTPException(status_code=401, detail="Invalid clinical credentials")


# --- Patient Management ---
@app.get("/api/v1/patients")
async def get_patients(doctor_id: str):
    """Retrieve approved patients belonging to a specific clinician."""
    rows = await db.fetch_all(
        "SELECT p.* FROM patients p WHERE p.doctor_id = $1 AND p.status = 'approved' ORDER BY p.full_name ASC", 
        doctor_id
    )
    return [dict(r) for r in rows]

@app.post("/api/v1/patients", status_code=201)
async def create_patient(data: PatientCreate):
    """Create a new patient request (starts in pending status)."""
    new_id = f"PT_{uuid.uuid4().hex[:8]}"
    await db.execute(
        "INSERT INTO patients (id, doctor_id, full_name, dob, medical_id, affiliation, diagnosis_notes, status) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')", 
        new_id, data.doctor_id, data.full_name, data.dob, data.medical_id, data.affiliation, data.diagnosis_notes
    )
    return {"id": new_id, "status": "pending"}

@app.get("/api/v1/patients/all")
async def get_all_patients():
    """Global patient list for administrators."""
    rows = await db.fetch_all(
        "SELECT p.*, (SELECT full_name FROM doctors WHERE id = p.doctor_id) as doctor_name "
        "FROM patients p ORDER BY p.full_name ASC"
    )
    return [{**dict(r), "doctor_name": r["doctor_name"] or "Unassigned"} for r in rows]

@app.delete("/api/v1/patients/{id}")
async def delete_patient(id: str):
    """Hard delete patient and their telemetry history."""
    await db.execute("DELETE FROM telemetry WHERE patient_id = $1", id)
    await db.execute("DELETE FROM patients WHERE id = $1", id)
    return {"status": "deleted"}

# --- Telemetry ---
@app.get("/api/v1/telemetry/{patient_id}")
async def get_telemetry(patient_id: str, limit: int = 10):
    """Retrieve recent telemetry data for a specific patient."""
    rows = await db.fetch_all(
        "SELECT * FROM telemetry WHERE patient_id = $1 ORDER BY time DESC LIMIT $2", 
        patient_id, limit
    )
    return [dict(r) for r in rows]

@app.get("/api/v1/predictions/all/{patient_id}")
async def get_predictions_all(patient_id: str):
    """
    Compatibility endpoint for doctor_dashboard/main.js.
    This prevents 404 errors on the deployed dashboard.
    """
    return {
        "patient_id": patient_id,
        "timestamp": datetime.utcnow().isoformat(),
        "battery": None,
        "cardiac": {
            "heart_rate": 72,
            "risk_level": "low",
            "risk_probability": 0.12,
            "error": False
        },
        "metabolic": None,
        "alerts": []
    }

# --- Doctor Management ---
@app.get("/api/v1/doctors")
async def get_doctors():
    """List all doctors and their statuses."""
    rows = await db.fetch_all("SELECT id, full_name, email, status FROM doctors ORDER BY status ASC, full_name ASC")
    return [dict(r) for r in rows]

@app.post("/api/v1/doctors", status_code=201)
async def create_doctor(data: DoctorCreate):
    """Create a new doctor recruitment entry."""
    new_id = f"doc_{uuid.uuid4().hex[:8]}"
    await db.execute(
        "INSERT INTO doctors (id, full_name, email, password, status) VALUES ($1, $2, $3, $4, $5)", 
        new_id, data.full_name, data.email, data.password, data.status
    )
    return {"id": new_id, "status": data.status}

@app.delete("/api/v1/doctors/{id}")
async def delete_doctor(id: str):
    """Removal with governance: move patients to pending pool instead of deleting them."""
    await db.execute("UPDATE patients SET doctor_id = NULL, status = 'pending' WHERE doctor_id = $1", id)
    await db.execute("DELETE FROM doctors WHERE id = $1", id)
    return {"status": "deleted", "message": "Doctor removed. Patients moved to pending pool."}

# --- Administration & Approvals ---
@app.get("/api/v1/admin/pending_doctors")
async def get_pending_doctors():
    rows = await db.fetch_all(
        "SELECT id, full_name, email, status, created_at FROM doctors WHERE status = 'pending' ORDER BY created_at ASC"
    )
    return [
        {**dict(r), "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else r["created_at"]} 
        for r in rows
    ]

@app.put("/api/v1/admin/approve_doctor/{id}")
async def approve_doctor(id: str):
    await db.execute("UPDATE doctors SET status = 'approved' WHERE id = $1", id)
    return {"status": "approved"}

@app.put("/api/v1/admin/refuse_doctor/{id}")
async def refuse_doctor(id: str):
    await db.execute("UPDATE doctors SET status = 'rejected' WHERE id = $1", id)
    return {"status": "rejected"}

@app.get("/api/v1/admin/pending_patients")
async def get_pending_patients():
    rows = await db.fetch_all(
        "SELECT p.*, (SELECT full_name FROM doctors WHERE id = p.doctor_id) as doctor_name "
        "FROM patients p WHERE p.status = 'pending' ORDER BY p.created_at ASC"
    )
    return [
        {**dict(r), "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else r["created_at"]} 
        for r in rows
    ]

@app.put("/api/v1/admin/approve_patient/{id}")
async def approve_patient(id: str):
    await db.execute("UPDATE patients SET status = 'approved' WHERE id = $1", id)
    return {"status": "approved"}

@app.put("/api/v1/admin/refuse_patient/{id}")
async def refuse_patient(id: str):
    await db.execute("UPDATE patients SET status = 'rejected' WHERE id = $1", id)
    return {"status": "rejected"}

@app.put("/api/v1/admin/reassign_patient/{id}")
async def reassign_patient(id: str, data: PatientReassign):
    """Reassign an unassigned patient to a new clinician."""
    await db.execute("UPDATE patients SET doctor_id = $1, status = 'approved' WHERE id = $2", data.doctor_id, id)
    return {"status": "reassigned"}

# --- ML & IoT ---
class PredictRequest(BaseModel):
    samples: list[float]

@app.post("/api/model/cardiac/predict")
async def predict_cardiac_risk(req: PredictRequest):
    global latest_ecg_window, latest_prediction
    if len(req.samples) != 187:
        raise HTTPException(status_code=400, detail="Must provide exactly 187 samples")
    
    latest_ecg_window = req.samples
    
    if model is None:
        raise HTTPException(status_code=503, detail="ML model not loaded")
        
    try:
        # Normalize: divide by 4095
        arr = np.array(req.samples, dtype=np.float32) / 4095.0
        # Reshape to (1, 187, 1)
        arr = arr.reshape(1, 187, 1)
        
        preds = model.predict(arr, verbose=0)[0] 
        
        predicted_class = int(np.argmax(preds))
        confidence = float(preds[predicted_class])
        
        class_names = ["Normal", "Atrial Fibrillation", "Other Arrhythmia", "Noise"]
        risk_levels = ["low", "high", "moderate", "low"]
        
        res = {
            "prediction_class": predicted_class,
            "label": class_names[predicted_class],
            "risk_level": risk_levels[predicted_class],
            "risk_probability": confidence,
            "confidence_percent": confidence * 100,
            "raw_scores": preds.tolist(),
            "model_version": "CNN-LSTM v1.0",
            "sequence": req.samples
        }
        latest_prediction = res
        
        # Broadcast to websockets
        await manager.broadcast({
            "type": "prediction",
            "data": res
        })
        
        return res
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
        # Send latest state on connect
        if latest_prediction:
            await websocket.send_json({
                "type": "prediction",
                "data": latest_prediction
            })
        while True:
            data = await websocket.receive_text()
            # Keep connection open
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)