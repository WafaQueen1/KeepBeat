from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncpg
import os
import datetime

app = FastAPI(title="KeepBeat Cloud Server", version="1.1.0")

# Allow requests from the web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"API_TRACE: {request.method} {request.url.path}")
    return await call_next(request)

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
        self.pool = None
        self.sqlite_conn = None
        self.engine = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(DATABASE_URL, ssl=False, timeout=5)
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            self.engine = "postgres"
            print("Connected to TimescaleDB")
            return True
        except Exception:
            try:
                self.sqlite_conn = await aiosqlite.connect(SQLITE_DB_PATH)
                self.sqlite_conn.row_factory = aiosqlite.Row
                self.engine = "sqlite"
                return True
            except Exception:
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
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    CREATE TABLE IF NOT EXISTS admins (
                        id TEXT PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                # Migrations
                try: await conn.execute("ALTER TABLE doctors ADD COLUMN role TEXT DEFAULT 'doctor';")
                except: pass
                try: await conn.execute("ALTER TABLE doctors ADD COLUMN status TEXT DEFAULT 'pending';")
                except: pass

                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        id TEXT PRIMARY KEY,
                        doctor_id TEXT REFERENCES doctors(id),
                        full_name TEXT NOT NULL,
                        dob TEXT NOT NULL,
                        medical_id TEXT NOT NULL,
                        affiliation TEXT,
                        diagnosis_notes TEXT,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                try: await conn.execute("ALTER TABLE patients ADD COLUMN status TEXT DEFAULT 'pending';")
                except: pass

                await conn.execute("CREATE TABLE IF NOT EXISTS telemetry (time TIMESTAMPTZ NOT NULL, patient_id TEXT NOT NULL, device_id TEXT NOT NULL, sensor_type TEXT NOT NULL, value DOUBLE PRECISION NOT NULL, unit TEXT NOT NULL);")
                try: await conn.execute("SELECT create_hypertable('telemetry', 'time', if_not_exists => TRUE);")
                except: pass

                # Seed
                await conn.execute("INSERT INTO doctors (id, full_name, email, password, status) VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123', 'approved') ON CONFLICT (id) DO UPDATE SET status = 'approved';")
                await conn.execute("INSERT INTO admins (id, full_name, email, password) VALUES ('admin_001', 'System Admin', 'admin@keepbeat.com', 'admin123') ON CONFLICT (id) DO UPDATE SET password = EXCLUDED.password;")

        else: # SQLite
            async with self.sqlite_conn.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS doctors (id TEXT PRIMARY KEY, full_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'doctor', status TEXT DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);")
                await cursor.execute("CREATE TABLE IF NOT EXISTS admins (id TEXT PRIMARY KEY, full_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);")
                try: await cursor.execute("ALTER TABLE doctors ADD COLUMN role TEXT DEFAULT 'doctor';")
                except: pass
                try: await cursor.execute("ALTER TABLE doctors ADD COLUMN status TEXT DEFAULT 'pending';")
                except: pass
                
                await cursor.execute("CREATE TABLE IF NOT EXISTS patients (id TEXT PRIMARY KEY, doctor_id TEXT, full_name TEXT NOT NULL, dob TEXT NOT NULL, medical_id TEXT NOT NULL, affiliation TEXT, diagnosis_notes TEXT, status TEXT DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (doctor_id) REFERENCES doctors(id));")
                try: await cursor.execute("ALTER TABLE patients ADD COLUMN status TEXT DEFAULT 'pending';")
                except: pass

                await cursor.execute("CREATE TABLE IF NOT EXISTS telemetry (time DATETIME NOT NULL, patient_id TEXT NOT NULL, device_id TEXT NOT NULL, sensor_type TEXT NOT NULL, value REAL NOT NULL, unit TEXT NOT NULL);")
                await cursor.execute("INSERT OR IGNORE INTO doctors (id, full_name, email, password, status) VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123', 'approved')")
                await cursor.execute("UPDATE doctors SET status = 'approved' WHERE id = 'doc_sterling_001'")
                await cursor.execute("INSERT OR IGNORE INTO admins (id, full_name, email, password) VALUES ('admin_001', 'System Admin', 'admin@keepbeat.com', 'admin123')")
                await self.sqlite_conn.commit()

    async def fetch_one(self, query: str, *args):
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        else:
            q = query.replace("$1", "?").replace("$2", "?").replace("$3", "?")
            async with self.sqlite_conn.execute(q, args) as cursor:
                return await cursor.fetchone()

    async def fetch_all(self, query: str, *args):
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        else:
            import re
            q = re.sub(r'\$\d+', '?', query)
            async with self.sqlite_conn.execute(q, args) as cursor:
                return await cursor.fetchall()

    async def execute(self, query: str, *args):
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        else:
            import re
            q = re.sub(r'\$\d+', '?', query)
            async with self.sqlite_conn.execute(q, args) as cursor:
                await self.sqlite_conn.commit()

db = DBManager()

@app.on_event("startup")
async def startup():
    if await db.connect():
        await db.initialize_tables()

# --- Models ---
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

class PatientReassign(BaseModel):
    doctor_id: str

# --- Endpoints ---
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "engine": db.engine}

@app.post("/api/v1/auth/login")
async def login(credentials: DoctorLogin):
    # Admins
    admin = await db.fetch_one("SELECT id, full_name, email FROM admins WHERE email = $1 AND password = $2", credentials.email, credentials.password)
    if admin: return {"id": admin["id"], "full_name": admin["full_name"], "email": admin["email"], "role": "admin"}
        
    # Doctors
    doctor = await db.fetch_one("SELECT id, full_name, email, status FROM doctors WHERE email = $1 AND password = $2", credentials.email, credentials.password)
    if not doctor: raise HTTPException(status_code=401, detail="Invalid credentials")
    
    status = doctor["status"]
    if status == "pending": raise HTTPException(status_code=403, detail="Account pending admin approval")
    elif status == "rejected": raise HTTPException(status_code=403, detail="Account request rejected")
        
    return {"id": doctor["id"], "full_name": doctor["full_name"], "email": doctor["email"], "role": "doctor"}

@app.get("/api/v1/patients")
async def get_patients(doctor_id: str):
    # Strictly Approved Only for Clinicians
    rows = await db.fetch_all("SELECT p.* FROM patients p WHERE p.doctor_id = $1 AND p.status = 'approved' ORDER BY p.full_name ASC", doctor_id)
    return [dict(r) for r in rows]

@app.post("/api/v1/patients", status_code=201)
async def create_patient(data: PatientCreate):
    import uuid
    new_id = f"PT_{uuid.uuid4().hex[:8]}"
    await db.execute("INSERT INTO patients (id, doctor_id, full_name, dob, medical_id, affiliation, diagnosis_notes, status) VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')", new_id, data.doctor_id, data.full_name, data.dob, data.medical_id, data.affiliation, data.diagnosis_notes)
    return {"id": new_id, "status": "pending"}

@app.get("/api/v1/patients/all")
async def get_all_patients():
    rows = await db.fetch_all("SELECT p.*, (SELECT full_name FROM doctors WHERE id = p.doctor_id) as doctor_name FROM patients p ORDER BY p.full_name ASC")
    return [{**dict(r), "doctor_name": r["doctor_name"] or "Unknown"} for r in rows]

@app.delete("/api/v1/patients/{id}")
async def delete_patient(id: str):
    await db.execute("DELETE FROM telemetry WHERE patient_id = $1", id)
    await db.execute("DELETE FROM patients WHERE id = $1", id)
    return {"status": "deleted"}

@app.get("/api/v1/doctors")
async def get_doctors():
    # Only show approved clinical professionals in management list (or show all with badges)
    rows = await db.fetch_all("SELECT id, full_name, email, status FROM doctors ORDER BY status ASC, full_name ASC")
    return [dict(r) for r in rows]

@app.post("/api/v1/doctors", status_code=201)
async def create_doctor(data: DoctorCreate):
    import uuid
    new_id = f"doc_{uuid.uuid4().hex[:8]}"
    await db.execute("INSERT INTO doctors (id, full_name, email, password, status) VALUES ($1, $2, $3, $4, $5)", new_id, data.full_name, data.email, data.password, data.status)
    return {"id": new_id, "status": data.status}

@app.delete("/api/v1/doctors/{id}")
async def delete_doctor(id: str):
    # Safety: Move patients to pending/unassigned instead of deleting them
    await db.execute("UPDATE patients SET doctor_id = NULL, status = 'pending' WHERE doctor_id = $1", id)
    await db.execute("DELETE FROM doctors WHERE id = $1", id)
    return {"status": "deleted", "message": "Doctor removed. Patients moved to pending pool."}

# --- Administrative Approval Endpoints ---
@app.get("/api/v1/admin/pending_doctors")
async def get_pending_doctors():
    rows = await db.fetch_all("SELECT id, full_name, email, status, created_at FROM doctors WHERE status = 'pending' ORDER BY created_at ASC")
    return [{**dict(r), "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else r["created_at"]} for r in rows]

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
    rows = await db.fetch_all("SELECT p.*, (SELECT full_name FROM doctors WHERE id = p.doctor_id) as doctor_name FROM patients p WHERE p.status = 'pending' ORDER BY p.created_at ASC")
    return [{**dict(r), "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else r["created_at"]} for r in rows]

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
    # Update doctor and automatically approve to ensure visibility
    await db.execute("UPDATE patients SET doctor_id = $1, status = 'approved' WHERE id = $2", data.doctor_id, id)
    return {"status": "reassigned"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)