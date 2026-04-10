import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect(user='postgres', password='password', host='127.0.0.1', ssl=False)
        print("Successfully connected to postgres default DB")
        await conn.close()
    except Exception as e:
        print(f"Failed: {e}")

asyncio.run(test())
