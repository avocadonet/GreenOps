import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis
import asyncpg
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="GreenOps Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/greenops_db")

redis = None
pg_pool = None

@app.on_event("startup")
async def startup():
    global redis, pg_pool
    redis = aioredis.from_url(REDIS_URL)
    pg_pool = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await redis.close()
    await pg_pool.close()

@app.get("/api/v1/analytics/{building_id}/current")
async def get_current_data(building_id: int):
    data = await redis.get(f"building:{building_id}:latest")
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    return json.loads(data)

@app.get("/api/v1/analytics/{building_id}/history")
async def get_history(building_id: int):
    async with pg_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT value, timestamp 
            FROM energy_metrics 
            WHERE building_id = $1 
            ORDER BY timestamp DESC 
            LIMIT 20
            """, 
            building_id
        )
        return [dict(row) for row in rows]

@app.get("/health")
async def health():
    return {"status": "ok"}