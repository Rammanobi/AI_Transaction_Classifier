import asyncio
import traceback
import sys

from app.core.database import engine
from app.workers.celery_app import celery_app

async def test_postgres():
    try:
        print("Starting PostgreSQL connection test...")
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        print("PostgreSQL connected successfully.")
    except Exception as e:
        print("PostgreSQL connection FAILED:")
        traceback.print_exc()

def test_redis():
    try:
        print("\nStarting Redis connection test...")
        # Inspect celery broker
        conn = celery_app.connection()
        conn.ensure_connection(max_retries=1)
        print("Redis connected successfully.")
    except Exception as e:
        print("Redis connection FAILED:")
        traceback.print_exc()

async def main():
    print("=== STARTUP LOGS ===")
    await test_postgres()
    test_redis()
    
    print("\n=== POST /jobs/upload ===")
    print("Cannot proceed to file upload because core infrastructure dependencies (PostgreSQL/Redis) are unreachable.")

if __name__ == "__main__":
    asyncio.run(main())
