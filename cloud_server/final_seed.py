import asyncio
import asyncpg
import sys

async def main():
    try:
        # Use 127.0.0.1 and explicit credentials
        conn = await asyncpg.connect(
            user='postgres',
            password='password',
            database='twinpacemaker',
            host='127.0.0.1',
            port=5433,
            ssl=False
        )
        print("Connected to database.")
        
        # Ensure table exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id          TEXT PRIMARY KEY,
                full_name   TEXT NOT NULL,
                email       TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Insert or update doctor
        await conn.execute("""
            INSERT INTO doctors (id, full_name, email, password)
            VALUES ('doc_sterling_001', 'Dr. Julian Sterling', 'julian.sterling@keepbeat.com', 'password123')
            ON CONFLICT (id) DO UPDATE SET password = EXCLUDED.password;
        """)
        
        print("Doctor account seeded/verified: julian.sterling@keepbeat.com / password123")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
