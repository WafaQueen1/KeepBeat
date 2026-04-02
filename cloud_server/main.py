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

# --- Configuration ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@127.0.0.1:5432/twinpacemaker"
)

# --- Database Setup ---
pool: asyncpg.Pool = None

@app.on_event("startup")
async def startup():
    global pool
    max_retries = 5
    retry_delay = 2
    for i in range(max_retries):
        try:
            # Explicitly disable SSL for local development on Windows
            pool = await asyncpg.create_pool(DATABASE_URL, ssl=False)
            print("Connected to TimescaleDB")
            break
        except Exception as e:
            if i == max_retries - 1:
                print(f"CRITICAL: Failed to initialize Postgres connection pool after {max_retries} attempts: {e}")
                with open("db_error.log", "a") as f:
                    f.write(f"{datetime.datetime.now()} - FATAL DB ERROR: {e}\n")
                return
            print(f"Database connection attempt {i+1} failed, retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)

    try:
        # Ensure the telemetry table exists and is a hypertable
        async with pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id          TEXT PRIMARY KEY,
                    full_name   TEXT NOT NULL,
                    email       TEXT UNIQUE NOT NULL,
                    password    TEXT NOT NULL,
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS patients (
                    id              TEXT PRIMARY KEY,
                    doctor_id       TEXT REFERENCES doctors(id),
                    full_name       TEXT NOT NULL,
                    dob             TEXT NOT NULL,
                    medical_id      TEXT NOT NULL,
                    affiliation     TEXT,
                    diagnosis_notes TEXT,
                    created_at      TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS telemetry (
                    time        TIMESTAMPTZ       NOT NULL,
                    patient_id  TEXT              NOT NULL,
                    device_id   TEXT              NOT NULL,
                    sensor_type TEXT              NOT NULL,
                    value       DOUBLE PRECISION  NOT NULL,
                    unit        TEXT              NOT NULL
                );
            """)
            
            # Since create hypertable raises an error if it already is one, we handle it conditionally
            await connection.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM timescaledb_information.hypertables 
                        WHERE hypertable_name = 'telemetry'
                    ) THEN
                        PERFORM create_hypertable('telemetry', 'time');
                    END IF;
                END
                $$;
            """)
            
            # Seed a default realistic doctor and ensure password is up to date
            await connection.execute("""
                INSERT INTO doctors (id, full_name, email, password)
                VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123')
                ON CONFLICT (id) DO UPDATE SET password = EXCLUDED.password;
            """)
    except Exception as e:
        print(f"CRITICAL: Failed to initialize Postgres connection pool: {e}")
        # Log to a file for deeper debugging if uvicorn logs are clipped
        with open("db_error.log", "a") as f:
            f.write(f"{datetime.datetime.now()} - DB INIT ERROR: {e}\n")

@app.on_event("shutdown")
async def shutdown():
    global pool
    if pool:
        await pool.close()

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

@app.post("/api/v1/auth/login")
async def login(credentials: DoctorLogin):
    if not pool:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    async with pool.acquire() as connection:
        doctor = await connection.fetchrow("""
            SELECT id, full_name, email FROM doctors 
            WHERE email = $1 AND password = $2
        """, credentials.email, credentials.password)
        if not doctor:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"id": doctor["id"], "full_name": doctor["full_name"], "email": doctor["email"]}

@app.get("/api/v1/auth/seed")
async def seed_doctor():
    """Manual trigger to ensure the default doctor exists."""
    if not pool:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    async with pool.acquire() as connection:
        await connection.execute("""
            INSERT INTO doctors (id, full_name, email, password)
            VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123')
            ON CONFLICT (id) DO NOTHING;
        """)
        return {"status": "success", "message": "Default doctor seeded or already exists."}

@app.post("/api/v1/auth/register")
async def register_doctor(data: DoctorLogin):
    """Allow doctors to register themselves (Realistic extension)."""
    if not pool:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
    import uuid
    new_id = f"DOC_{uuid.uuid4().hex[:8]}"
    async with pool.acquire() as connection:
        try:
            await connection.execute("""
                INSERT INTO doctors (id, full_name, email, password)
                VALUES ($1, $2, $3, $4)
            """, new_id, "New Physician", data.email, data.password)
            return {"id": new_id, "status": "registered"}
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=400, detail="Email already registered")

@app.get("/api/v1/patients")
async def get_patients(doctor_id: str):
    if not pool:
        raise HTTPException(status_code=503, detail="Database unavailable")
    async with pool.acquire() as connection:
        rows = await connection.fetch("""
            SELECT p.*, 
                   (SELECT MAX(time) FROM telemetry WHERE patient_id = p.id) as last_sync
            FROM patients p
            WHERE p.doctor_id = $1
            ORDER BY p.full_name ASC
        """, doctor_id)
        
        return [
            {
                "id": r["id"],
                "doctor_id": r["doctor_id"],
                "full_name": r["full_name"],
                "dob": r["dob"],
                "medical_id": r["medical_id"],
                "affiliation": r["affiliation"],
                "diagnosis_notes": r["diagnosis_notes"],
                "last_sync": r["last_sync"].isoformat() if r["last_sync"] else None
            } for r in rows
        ]

@app.post("/api/v1/patients", status_code=201)
async def create_patient(data: PatientCreate):
    if not pool:
        raise HTTPException(status_code=503, detail="Database unavailable")
        
    import uuid
    new_id = f"PT_{uuid.uuid4().hex[:8]}"
    
    async with pool.acquire() as connection:
        await connection.execute("""
            INSERT INTO patients (id, doctor_id, full_name, dob, medical_id, affiliation, diagnosis_notes)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, new_id, data.doctor_id, data.full_name, data.dob, data.medical_id, data.affiliation, data.diagnosis_notes)
    
    return {"id": new_id, "status": "created"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "message": "KeepBeat API is running."}

@app.post("/api/v1/telemetry", status_code=201)
async def post_telemetry(data: TelemetryBatch):
    """
    Ingest a batch of telemetry data (e.g. from the mobile app).
    """
    if not pool:
        raise HTTPException(status_code=503, detail="Database connection unavailable")

    async with pool.acquire() as connection:
        # Prepare batch insert
        records = [
            (item.timestamp, item.patient_id, item.device_id, item.sensor_type, item.value, item.unit)
            for item in data.items
        ]
        
        await connection.copy_records_to_table(
            'telemetry',
            records=records,
            columns=['time', 'patient_id', 'device_id', 'sensor_type', 'value', 'unit']
        )
    return {"status": "success", "inserted": len(records)}

@app.get("/api/v1/telemetry/{patient_id}")
async def get_patient_telemetry(patient_id: str, limit: int = 100):
    """
    Retrieve recent telemetry for a patient (e.g. for the web dashboard).
    """
    if not pool:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
        
    async with pool.acquire() as connection:
        rows = await connection.fetch("""
            SELECT time, sensor_type, value, unit 
            FROM telemetry 
            WHERE patient_id = $1 
            ORDER BY time DESC 
            LIMIT $2
        """, patient_id, limit)
        
        return [
            {
                "timestamp": row["time"].isoformat(),
                "sensor_type": row["sensor_type"],
                "value": row["value"],
                "unit": row["unit"]
            }
            for row in rows
        ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
