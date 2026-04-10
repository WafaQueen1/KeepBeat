import asyncpg
import aiosqlite
import os
import re
from typing import Optional, List, Any

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@127.0.0.1:5433/twinpacemaker")
SQLITE_DB_PATH = "keepbeat_fallback.db"

class DBManager:
    """
    Manages database connections and basic abstraction between 
    PostgreSQL (TimescaleDB) and SQLite for fallback.
    """
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.sqlite_conn: Optional[aiosqlite.Connection] = None
        self.engine: Optional[str] = None

    async def connect(self) -> bool:
        """Establishes connection to the primary or fallback database."""
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
                print("Connected to SQLite Fallback")
                return True
            except Exception as e:
                print(f"Database connection failed: {e}")
                return False

    async def initialize_tables(self):
        """Initializes system tables and seeds initial metadata."""
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
                    CREATE TABLE IF NOT EXISTS patients (
                        id TEXT PRIMARY KEY,
                        doctor_id TEXT REFERENCES doctors(id),
                        full_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        dob TEXT NOT NULL,
                        medical_id TEXT NOT NULL,
                        affiliation TEXT,
                        diagnosis_notes TEXT,
                        status TEXT DEFAULT 'pending',
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
                
                # TimescaleDB Hypertable
                try: 
                    await conn.execute("SELECT create_hypertable('telemetry', 'time', if_not_exists => TRUE);")
                except: 
                    pass

                # Seeding Initial Accounts
                await conn.execute("""
                    INSERT INTO doctors (id, full_name, email, password, status) 
                    VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123', 'approved') 
                    ON CONFLICT (id) DO UPDATE SET status = 'approved';
                """)
                await conn.execute("""
                    INSERT INTO admins (id, full_name, email, password) 
                    VALUES ('admin_001', 'System Admin', 'admin@keepbeat.com', 'admin123') 
                    ON CONFLICT (id) DO UPDATE SET password = EXCLUDED.password;
                """)
                await conn.execute("""
                    INSERT INTO patients (id, doctor_id, full_name, email, password, dob, medical_id, status) 
                    VALUES ('pat_jenkins_001', 'doc_sterling_001', 'Sarah Jenkins', 'sarah.jenkins@keepbeat.com', 'patient123', '1985-05-12', 'KB-8821', 'approved') 
                    ON CONFLICT (id) DO UPDATE SET status = 'approved';
                """)

        else: # SQLite
            async with self.sqlite_conn.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS doctors (
                        id TEXT PRIMARY KEY, 
                        full_name TEXT NOT NULL, 
                        email TEXT UNIQUE NOT NULL, 
                        password TEXT NOT NULL, 
                        role TEXT DEFAULT 'doctor', 
                        status TEXT DEFAULT 'pending', 
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        id TEXT PRIMARY KEY, 
                        full_name TEXT NOT NULL, 
                        email TEXT UNIQUE NOT NULL, 
                        password TEXT NOT NULL, 
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        id TEXT PRIMARY KEY, 
                        doctor_id TEXT, 
                        full_name TEXT NOT NULL, 
                        email TEXT UNIQUE NOT NULL, 
                        password TEXT NOT NULL, 
                        dob TEXT NOT NULL, 
                        medical_id TEXT NOT NULL, 
                        affiliation TEXT, 
                        diagnosis_notes TEXT, 
                        status TEXT DEFAULT 'pending', 
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
                        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                    );
                """)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS telemetry (
                        time DATETIME NOT NULL, 
                        patient_id TEXT NOT NULL, 
                        device_id TEXT NOT NULL, 
                        sensor_type TEXT NOT NULL, 
                        value REAL NOT NULL, 
                        unit TEXT NOT NULL
                    );
                """)
                
                # Seeding
                await cursor.execute("INSERT OR IGNORE INTO doctors (id, full_name, email, password, status) VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123', 'approved')")
                await cursor.execute("UPDATE doctors SET status = 'approved' WHERE id = 'doc_sterling_001'")
                await cursor.execute("INSERT OR IGNORE INTO admins (id, full_name, email, password) VALUES ('admin_001', 'System Admin', 'admin@keepbeat.com', 'admin123')")
                await cursor.execute("INSERT OR IGNORE INTO patients (id, doctor_id, full_name, email, password, dob, medical_id, status) VALUES ('pat_jenkins_001', 'doc_sterling_001', 'Sarah Jenkins', 'sarah.jenkins@keepbeat.com', 'patient123', '1985-05-12', 'KB-8821', 'approved')")
                await cursor.execute("UPDATE patients SET status = 'approved' WHERE id = 'pat_jenkins_001'")
                await self.sqlite_conn.commit()

    async def fetch_one(self, query: str, *args) -> Optional[Any]:
        """Fetches a single row from the active database."""
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        else:
            q = re.sub(r'\$\d+', '?', query)
            async with self.sqlite_conn.execute(q, args) as cursor:
                return await cursor.fetchone()

    async def fetch_all(self, query: str, *args) -> List[Any]:
        """Fetches all matching rows from the active database."""
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        else:
            q = re.sub(r'\$\d+', '?', query)
            async with self.sqlite_conn.execute(q, args) as cursor:
                return await cursor.fetchall()

    async def execute(self, query: str, *args):
        """Executes a command (INSERT, UPDATE, DELETE) on the active database."""
        if self.engine == "postgres":
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        else:
            q = re.sub(r'\$\d+', '?', query)
            async with self.sqlite_conn.execute(q, args) as cursor:
                await self.sqlite_conn.commit()

db = DBManager()
