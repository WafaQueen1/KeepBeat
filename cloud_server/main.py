from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncpg
import os
import datetime

app = FastAPI(title="KeepBeat Cloud Server", version="1.0.0")

# Allow requests from the web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import asyncio
import sqlite3
import aiosqlite
import logging

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@127.0.0.1:5432/twinpacemaker")
SQLITE_DB_PATH = "keepbeat_fallback.db"

# --- Database Abstraction Layer ---
class DBManager:
    def __init__(self):
        self.pool = None  # For Postgres
        self.sqlite_conn = None  # For SQLite
        self.engine = None  # 'postgres' or 'sqlite'

    async def connect(self):
        # 1. Try Postgres
        try:
            self.pool = await asyncpg.create_pool(DATABASE_URL, ssl=False, timeout=5)
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            self.engine = "postgres"
            print("Successfully connected to TimescaleDB (Postgres)")
            return True
        except Exception as e:
            print(f"Postgres connection failed: {e}. Falling back to SQLite.")

        # 2. Try SQLite
        try:
            self.sqlite_conn = await aiosqlite.connect(SQLITE_DB_PATH)
            self.sqlite_conn.row_factory = aiosqlite.Row
            self.engine = "sqlite"
            print(f"Successfully connected to local SQLite: {SQLITE_DB_PATH}")
            return True
        except Exception as e:
            print(f"CRITICAL: SQLite connection also failed: {e}")
            return False

    async def initialize_tables(self):
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS doctors (
                        id TEXT PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT DEFAULT 'doctor',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                # Safe migration attempt
                try:
                    await conn.execute("ALTER TABLE doctors ADD COLUMN role TEXT DEFAULT 'doctor';")
                except Exception:
                    pass
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        id TEXT PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                # Safe migration attempt
                try:
                    await conn.execute("ALTER TABLE doctors ADD COLUMN status TEXT DEFAULT 'approved';")
                    await conn.execute("ALTER TABLE patients ADD COLUMN status TEXT DEFAULT 'approved';")
                except Exception:
                    pass
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        id TEXT PRIMARY KEY,
                        doctor_id TEXT REFERENCES doctors(id),
                        full_name TEXT NOT NULL,
                        dob TEXT NOT NULL,
                        medical_id TEXT NOT NULL,
                        affiliation TEXT,
                        diagnosis_notes TEXT,
                        status TEXT DEFAULT 'approved',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    CREATE TABLE IF NOT EXISTS telemetry (
                        time TIMESTAMPTZ NOT NULL,
                        patient_id TEXT NOT NULL,
                        device_id TEXT NOT NULL,
                        sensor_type TEXT NOT NULL,
                        value DOUBLE PRECISION NOT NULL,
                        unit TEXT NOT NULL
                    );
                """)
                # Handle TimescaleDB hypertable
                try:
                    await conn.execute("SELECT create_hypertable('telemetry', 'time', if_not_exists => TRUE);")
                except: pass # Ignore if already exists or not a timescale instance

                # Seed default doctor
                await conn.execute("""
                    INSERT INTO doctors (id, full_name, email, password, status)
                    VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123', 'approved')
                    ON CONFLICT (id) DO UPDATE SET password = EXCLUDED.password;
                """)

                # Seed default admin to admins table
                await conn.execute("""
                    INSERT INTO admins (id, full_name, email, password)
                    VALUES ('admin_001', 'System Admin', 'admin@keepbeat.com', 'admin123')
                    ON CONFLICT (id) DO UPDATE SET password = EXCLUDED.password;
                """)

        elif self.engine == "sqlite":
            async with self.sqlite_conn.cursor() as cursor:
                await cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS doctors (
                        id TEXT PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT DEFAULT 'doctor',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Safe migration attempt
                try:
                    await cursor.execute("ALTER TABLE doctors ADD COLUMN role TEXT DEFAULT 'doctor';")
                except Exception:
                    pass
                await cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS admins (
                        id TEXT PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Safe migration attempt
                try:
                    await cursor.execute("ALTER TABLE doctors ADD COLUMN status TEXT DEFAULT 'approved';")
                    await cursor.execute("ALTER TABLE patients ADD COLUMN status TEXT DEFAULT 'approved';")
                except Exception:
                    pass
                await cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS patients (
                        id TEXT PRIMARY KEY,
                        doctor_id TEXT,
                        full_name TEXT NOT NULL,
                        dob TEXT NOT NULL,
                        medical_id TEXT NOT NULL,
                        affiliation TEXT,
                        diagnosis_notes TEXT,
                        status TEXT DEFAULT 'approved',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                    );
                    CREATE TABLE IF NOT EXISTS telemetry (
                        time DATETIME NOT NULL,
                        patient_id TEXT NOT NULL,
                        device_id TEXT NOT NULL,
                        sensor_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT NOT NULL
                    );
                """)
                # Seed default doctor
                await cursor.execute("""
                    INSERT OR REPLACE INTO doctors (id, full_name, email, password, status)
                    VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123', 'approved')
                """)

                # Seed default admin
                await cursor.execute("""
                    INSERT OR REPLACE INTO admins (id, full_name, email, password)
                    VALUES ('admin_001', 'System Admin', 'admin@keepbeat.com', 'admin123')
                """)
                await self.sqlite_conn.commit()

    async def fetch_one(self, query: str, *args):
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        else:
            # Convert $1, $2 to ? for SQLite
            q = query.replace("$1", "?").replace("$2", "?").replace("$3", "?").replace("$4", "?").replace("$5", "?")
            async with self.sqlite_conn.execute(q, args) as cursor:
                return await cursor.fetchone()

    async def fetch_all(self, query: str, *args):
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        else:
            q = query.replace("$1", "?").replace("$2", "?").replace("$3", "?")
            async with self.sqlite_conn.execute(q, args) as cursor:
                return await cursor.fetchall()

    async def execute(self, query: str, *args):
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        else:
            # Convert $1, $2, etc to ? for SQLite placeholder syntax
            import re
            q = re.sub(r'\$\d+', '?', query)
            async with self.sqlite_conn.execute(q, args) as cursor:
                await self.sqlite_conn.commit()

    async def copy_telemetry(self, records):
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                await conn.copy_records_to_table(
                    'telemetry',
                    records=records,
                    columns=['time', 'patient_id', 'device_id', 'sensor_type', 'value', 'unit']
                )
        else:
            async with self.sqlite_conn.cursor() as cursor:
                await cursor.executemany("""
                    INSERT INTO telemetry (time, patient_id, device_id, sensor_type, value, unit)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, records)
                await self.sqlite_conn.commit()

db = DBManager()

@app.on_event("startup")
async def startup():
    if await db.connect():
        await db.initialize_tables()

@app.on_event("shutdown")
async def shutdown():
    if db.pool:
        await db.pool.close()
    if db.sqlite_conn:
        await db.sqlite_conn.close()

# --- Models ---
class TelemetryData(BaseModel):
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    patient_id: str
    device_id: str
    sensor_type: str
    value: float
    unit: str

class TelemetryBatch(BaseModel):
    items: List[TelemetryData]

class DoctorLogin(BaseModel):
    email: str
    password: str

class DoctorCreate(BaseModel):
    full_name: str
    email: str
    password: str
    status: Optional[str] = 'pending'

class PatientCreate(BaseModel):
    doctor_id: str
    full_name: str
    dob: str
    medical_id: str
    affiliation: str
    diagnosis_notes: str

class PatientResponse(BaseModel):
    id: str
    doctor_id: str
    full_name: str
    dob: str
    medical_id: str
    affiliation: str
    diagnosis_notes: str
    last_sync: Optional[str] = None

# --- Endpoints ---

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok", 
        "message": "KeepBeat API is running.",
        "database_engine": db.engine
    }

@app.post("/api/v1/auth/login")
async def login(credentials: DoctorLogin):
    # 1. Check Admins Table
    admin = await db.fetch_one("""
        SELECT id, full_name, email FROM admins 
        WHERE email = $1 AND password = $2
    """, credentials.email, credentials.password)
    
    if admin:
        return {"id": admin["id"], "full_name": admin["full_name"], "email": admin["email"], "role": "admin"}
        
    # 2. Check Doctors Table
    doctor = await db.fetch_one("""
        SELECT id, full_name, email, status FROM doctors 
        WHERE email = $1 AND password = $2
    """, credentials.email, credentials.password)
    
    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    status = doctor["status"] if "status" in dict(doctor) else "approved"
    if status == "pending":
        raise HTTPException(status_code=403, detail="Account pending admin approval")
    elif status == "rejected":
        raise HTTPException(status_code=403, detail="Account request rejected")
        
    return {"id": doctor["id"], "full_name": doctor["full_name"], "email": doctor["email"], "role": "doctor"}

@app.get("/api/v1/patients")
async def get_patients(doctor_id: str):
    # Cross-engine query for patient list with last sync time
    # Note: SQLite and Postgres have slightly different subquery handling for timestamps but this should work for both
    query = """
        SELECT p.*, 
               (SELECT MAX(time) FROM telemetry WHERE patient_id = p.id) as last_sync
        FROM patients p
        WHERE p.doctor_id = $1 AND (p.status = 'approved' OR p.status = 'pending' OR p.status IS NULL)
        ORDER BY p.full_name ASC
    """
    rows = await db.fetch_all(query, doctor_id)
    
    patients = []
    for r in rows:
        last_sync = r["last_sync"]
        if isinstance(last_sync, str): # SQLite format
            pass 
        elif last_sync and hasattr(last_sync, "isoformat"): # Postgres/datetime
            last_sync = last_sync.isoformat()

        patients.append({
            "id": r["id"],
            "doctor_id": r["doctor_id"],
            "full_name": r["full_name"],
            "dob": r["dob"],
            "medical_id": r["medical_id"],
            "affiliation": r["affiliation"],
            "diagnosis_notes": r["diagnosis_notes"],
            "last_sync": last_sync
        })
    return patients

@app.post("/api/v1/patients", status_code=201)
async def create_patient(data: PatientCreate):
    import uuid
    new_id = f"PT_{uuid.uuid4().hex[:8]}"
    await db.execute("""
        INSERT INTO patients (id, doctor_id, full_name, dob, medical_id, affiliation, diagnosis_notes, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')
    """, new_id, data.doctor_id, data.full_name, data.dob, data.medical_id, data.affiliation, data.diagnosis_notes)
    return {"id": new_id, "status": "pending_approval"}

@app.get("/api/v1/patients/all")
async def get_all_patients():
    query = """
        SELECT p.*, 
               (SELECT MAX(time) FROM telemetry WHERE patient_id = p.id) as last_sync,
               (SELECT full_name FROM doctors WHERE id = p.doctor_id) as doctor_name
        FROM patients p
        ORDER BY p.full_name ASC
    """
    rows = await db.fetch_all(query)
    
    patients = []
    for r in rows:
        last_sync = r["last_sync"]
        if isinstance(last_sync, str):
            pass 
        elif last_sync and hasattr(last_sync, "isoformat"):
            last_sync = last_sync.isoformat()

        patients.append({
            "id": r["id"],
            "doctor_id": r["doctor_id"],
            "doctor_name": r["doctor_name"] or "Unknown",
            "full_name": r["full_name"],
            "dob": r["dob"],
            "medical_id": r["medical_id"],
            "affiliation": r["affiliation"],
            "diagnosis_notes": r["diagnosis_notes"],
            "last_sync": last_sync
        })
    return patients

@app.delete("/api/v1/patients/{patient_id}")
async def delete_patient(patient_id: str):
    # Deep Delete: Telemetry then Patient
    await db.execute("DELETE FROM telemetry WHERE patient_id = $1", patient_id)
    await db.execute("DELETE FROM patients WHERE id = $1", patient_id)
    return {"status": "deleted"}

@app.get("/api/v1/doctors")
async def get_doctors():
    rows = await db.fetch_all("SELECT id, full_name, email, status FROM doctors WHERE status = 'approved' AND (role = 'doctor' OR role IS NULL) ORDER BY full_name ASC")
    
    doctors = []
    for r in rows:
        r_dict = dict(r)
        status = r_dict.get("status", "approved")
        doctors.append({"id": r["id"], "full_name": r["full_name"], "email": r["email"], "status": status})
    return doctors

@app.post("/api/v1/doctors", status_code=201)
async def create_doctor(data: DoctorCreate):
    import uuid
    new_id = f"doc_{uuid.uuid4().hex[:8]}"
    await db.execute("""
        INSERT INTO doctors (id, full_name, email, password, status)
        VALUES ($1, $2, $3, $4, $5)
    """, new_id, data.full_name, data.email, data.password, data.status)
    return {"id": new_id, "status": "pending_approval"}

@app.delete("/api/v1/doctors/{doc_id}")
async def delete_doctor(doc_id: str):
    # Deep Delete: Telemetry of patients -> Patients -> Doctor
    await db.execute("DELETE FROM telemetry WHERE patient_id IN (SELECT id FROM patients WHERE doctor_id = $1)", doc_id)
    await db.execute("DELETE FROM patients WHERE doctor_id = $1", doc_id)
    await db.execute("DELETE FROM doctors WHERE id = $1", doc_id)
    return {"status": "deleted"}

@app.post("/api/v1/telemetry", status_code=201)
async def post_telemetry(data: TelemetryBatch):
    records = [
        (item.timestamp, item.patient_id, item.device_id, item.sensor_type, item.value, item.unit)
        for item in data.items
    ]
    await db.copy_telemetry(records)
    return {"status": "success", "inserted": len(records)}

@app.get("/api/v1/telemetry/{patient_id}")
async def get_patient_telemetry(patient_id: str, limit: int = 100):
    rows = await db.fetch_all("""
        SELECT time, sensor_type, value, unit 
        FROM telemetry 
        WHERE patient_id = $1 
        ORDER BY time DESC 
        LIMIT $2
    """, patient_id, limit)
    
    return [
        {
            "timestamp": r["time"].isoformat() if hasattr(r["time"], "isoformat") else r["time"],
            "sensor_type": r["sensor_type"],
            "value": r["value"],
            "unit": r["unit"]
        } for r in rows
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/api/v1/admin/pending_doctors")
async def get_pending_doctors():
    rows = await db.fetch_all("SELECT id, full_name, email, status, created_at FROM doctors WHERE status = 'pending' ORDER BY created_at ASC")
    doctors = []
    for r in rows:
        r_dict = dict(r)
        created_at = r_dict.get("created_at")
        if isinstance(created_at, str):
            pass 
        elif created_at and hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()
            
        status = r_dict.get("status", "pending")
        doctors.append({"id": r["id"], "full_name": r["full_name"], "email": r["email"], "status": status, "created_at": created_at})
    return doctors

@app.put("/api/v1/admin/approve_doctor/{doc_id}")
async def approve_doctor(doc_id: str):
    await db.execute("UPDATE doctors SET status = 'approved' WHERE id = $1", doc_id)
    return {"status": "approved"}

@app.delete("/api/v1/admin/reject_doctor/{doc_id}")
async def reject_doctor(doc_id: str):
    # Robust Reject: Handle patients if any (unlikely for pending but safe)
    await db.execute("DELETE FROM telemetry WHERE patient_id IN (SELECT id FROM patients WHERE doctor_id = $1)", doc_id)
    await db.execute("DELETE FROM patients WHERE doctor_id = $1", doc_id)
    await db.execute("DELETE FROM doctors WHERE id = $1", doc_id)
    return {"status": "removed"}

@app.get("/api/v1/admin/pending_patients")
async def get_pending_patients():
    rows = await db.fetch_all("SELECT id, doctor_id, full_name, dob, medical_id, affiliation, diagnosis_notes, status, created_at FROM patients WHERE status = 'pending' ORDER BY created_at ASC")
    patients = []
    for r in rows:
        r_dict = dict(r)
        created_at = r_dict.get("created_at")
        if isinstance(created_at, str):
            pass
        elif created_at and hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()
        r_dict["created_at"] = created_at
        patients.append(r_dict)
    return patients

@app.put("/api/v1/admin/approve_patient/{patient_id}")
async def approve_patient(patient_id: str):
    await db.execute("UPDATE patients SET status = 'approved' WHERE id = $1", patient_id)
    return {"status": "approved"}

@app.delete("/api/v1/admin/reject_patient/{patient_id}")
async def reject_patient(patient_id: str):
    # Robust Reject: Telemetry then Patient
    await db.execute("DELETE FROM telemetry WHERE patient_id = $1", patient_id)
    await db.execute("DELETE FROM patients WHERE id = $1", patient_id)
    return {"status": "removed"}