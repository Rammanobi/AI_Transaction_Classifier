from fastapi import FastAPI
from app.api.v1 import jobs
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="AI Transaction Classifier")

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/health/db")
async def health_db():
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import text
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"postgres": "healthy"}
    except Exception as e:
        return {"postgres": "unhealthy", "error": str(e)}

@app.get("/health/redis")
async def health_redis():
    import redis.asyncio as redis
    from app.core.config import settings
    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        await r.ping()
        await r.close()
        return {"redis": "healthy"}
    except Exception as e:
        return {"redis": "unhealthy", "error": str(e)}
