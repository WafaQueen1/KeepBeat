import asyncio
import asyncpg
import os

DATABASE_URL = "postgresql://postgres:password@127.0.0.1:5433/twinpacemaker"

async def migrate():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("Connected. Auditing 'patients' schema...")
        
        # Add missing columns
        await conn.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;")
        await conn.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS password TEXT;")
        await conn.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS dob TEXT DEFAULT '';")
        await conn.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS medical_id TEXT;")
        await conn.execute("ALTER TABLE patients ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending';")
        print("Schema columns synchronized.")

        # Seed Sarah Jenkins
        await conn.execute("""
            INSERT INTO patients (id, doctor_id, full_name, email, password, dob, medical_id, status) 
            VALUES ('pat_jenkins_001', 'doc_sterling_001', 'Sarah Jenkins', 'sarah.jenkins@keepbeat.com', 'patient123', '1985-05-12', 'KB-8821', 'approved') 
            ON CONFLICT (id) DO UPDATE SET status = 'approved', email = EXCLUDED.email, password = EXCLUDED.password;
        """)
        print("Clinical account 'Sarah Jenkins' re-seeded and approved.")
        
        await conn.close()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
