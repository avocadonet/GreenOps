import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis
import asyncpg
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
from typing import Optional

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

@app.get("/api/v1/analytics/{building_id}/statistics")
async def get_statistics(building_id: int, hours: int = 24):
    async with pg_pool.acquire() as conn:
        stats = await conn.fetchrow("""
            SELECT 
                AVG(value) as avg_value,
                MAX(value) as max_value,
                MIN(value) as min_value,
                COUNT(*) as readings_count
            FROM energy_metrics
            WHERE building_id = $1
                AND timestamp >= NOW() - INTERVAL '1 hour' * $2
        """, building_id, hours)
        
        return {
            "building_id": building_id,
            "hours": hours,
            "average_consumption": stats['avg_value'],
            "max_consumption": stats['max_value'],
            "min_consumption": stats['min_value'],
            "readings_count": stats['readings_count']
        }

@app.get("/api/v1/analytics/{building_id}/threshold")
async def get_threshold(building_id: int):
    threshold = await redis.get(f"building:{building_id}:threshold")
    avg = await redis.get(f"building:{building_id}:average_consumption")
    updated_at = await redis.get(f"building:{building_id}:threshold_updated_at")
    
    if not threshold:
        raise HTTPException(status_code=404, detail="Threshold not found")
    
    return {
        "building_id": building_id,
        "current_threshold": float(threshold),
        "average_consumption": float(avg) if avg else None,
        "anomaly_percentage": 30,
        "last_updated": updated_at,
        "is_active": True
    }

@app.get("/api/v1/analytics/all_thresholds")
async def get_all_thresholds():
    keys = await redis.keys("building:*:threshold")
    thresholds = {}
    
    for key in keys:
        building_id = key.split(":")[1]
        threshold = await redis.get(key)
        avg = await redis.get(f"building:{building_id}:average_consumption")
        
        thresholds[building_id] = {
            "threshold": float(threshold) if threshold else None,
            "average_consumption": float(avg) if avg else None
        }
    
    return thresholds

@app.post("/api/v1/analytics/{building_id}/threshold/refresh")
async def refresh_threshold(building_id: int):
    async with pg_pool.acquire() as conn:
        avg = await conn.fetchval("""
            SELECT AVG(value)
            FROM energy_metrics
            WHERE building_id = $1
                AND timestamp >= NOW() - INTERVAL '24 hours'
        """, building_id)
        
        if not avg:
            raise HTTPException(status_code=404, detail="No data available for calculation")
        
        new_threshold = avg * 1.3
        
        await redis.set(f"building:{building_id}:threshold", new_threshold)
        await redis.set(f"building:{building_id}:average_consumption", avg)
        await redis.set(f"building:{building_id}:threshold_updated_at", datetime.now().isoformat())
        
        return {
            "building_id": building_id,
            "new_threshold": new_threshold,
            "average_consumption": avg,
            "anomaly_percentage": 30,
            "message": "Threshold refreshed successfully"
        }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.delete("/api/v1/analytics/{building_id}/history")
async def delete_history(building_id: int):
    async with pg_pool.acquire() as conn:
        await conn.execute("DELETE FROM energy_metrics WHERE building_id = $1", building_id)
    return {"message": f"History for building {building_id} deleted successfully"}

@app.put("/api/v1/analytics/{building_id}/threshold")
async def update_threshold(building_id: int, threshold: float):
    await redis.set(f"building:{building_id}:threshold", threshold)
    await redis.set(f"building:{building_id}:threshold_updated_at", datetime.now().isoformat())
    return {"building_id": building_id, "new_threshold": threshold}