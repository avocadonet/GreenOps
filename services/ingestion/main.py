import json
import asyncio
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from aiokafka import AIOKafkaProducer
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="GreenOps Ingestion Service")

Instrumentator().instrument(app).expose(app)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "raw_energy_data"

producer = None

class SensorData(BaseModel):
    building_id: int
    sensor_id: str
    value: float = Field(..., gt=0)
    unit: str = "kWh"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

@app.on_event("startup")
async def startup_event():
    global producer
    for i in range(10):
        try:
            producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            await producer.start()
            print("Successfully connected to Kafka!")
            break
        except Exception as e:
            print(f"Waiting for Kafka... Attempt {i+1}/10. Error: {e}")
            await asyncio.sleep(5)
    else:
        print("Could not connect to Kafka. Exiting.")

@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()

@app.post("/ingest")
async def ingest_data(data: SensorData):
    try:
        await producer.send_and_wait(KAFKA_TOPIC, data.model_dump())
        return {"status": "sent", "topic": KAFKA_TOPIC}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "alive"}