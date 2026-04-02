import asyncio
import asyncpg
import sys

# Try 127.0.0.1 instead of localhost for Windows reliability
DATABASE_URL = "postgresql://postgres:password@127.0.0.1:5432/twinpacemaker"

async def seed():
    conn = None
    try:
        print(f"Connecting to {DATABASE_URL}...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("Connected successfully.")
        
        # Create table if missing
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id          TEXT PRIMARY KEY,
                full_name   TEXT NOT NULL,
                email       TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        doctor_email = 'julian.sterling@keepbeat.com'
        exists = await conn.fetchval("SELECT id FROM doctors WHERE email = $1", doctor_email)
        
        if not exists:
            await conn.execute("""
                INSERT INTO doctors (id, full_name, email, password)
                VALUES ($1, $2, $3, $4)
            """, 'doc_sterling_001', 'Dr. Julian Sterling', doctor_email, 'password123')
            print(f"Doctor {doctor_email} seeded.")
        else:
            # Update password just in case it was different
            await conn.execute("UPDATE doctors SET password = $1 WHERE email = $2", 'password123', doctor_email)
            print(f"Doctor {doctor_email} already exists (password verified).")
            
    except Exception as e:
        print(f"FAILED TO SEED: {e}", file=sys.stderr)
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())
