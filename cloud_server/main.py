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
    "postgresql://postgres:password@localhost:5432/twinpacemaker"
)

# --- Database Setup ---
pool: asyncpg.Pool = None

@app.on_event("startup")
async def startup():
    global pool
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
        print("Connected to TimescaleDB")
        # Ensure the telemetry table exists and is a hypertable
        async with pool.acquire() as connection:
            await connection.execute("""
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
    except Exception as e:
        print(f"Failed to connect to or initialize database: {e}")

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


# --- Endpoints ---

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
