import asyncio
import json
import os
import logging
from aiokafka import AIOKafkaConsumer
from redis import asyncio as aioredis
import asyncpg
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "raw_energy_data"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/greenops_db")

MESSAGES_PROCESSED = Counter('energy_messages_total', 'Total processed energy messages')
CURRENT_VALUE_GAUGE = Gauge('energy_current_value', 'Current energy value being processed', ['building_id'])

logging.basicConfig(level=logging.INFO)

async def save_to_postgres(conn, data):
    query = """
        INSERT INTO energy_metrics (building_id, sensor_id, value, timestamp)
        VALUES ($1, $2, $3, $4)
    """
    await conn.execute(query, data['building_id'], data['sensor_id'], data['value'], data['timestamp'])

async def process_message(msg, redis, pg_conn):
    data = json.loads(msg.value.decode('utf-8'))
    
    if isinstance(data.get('timestamp'), str):
        try:
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        except ValueError:
            data['timestamp'] = datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S.%f")

    redis_key = f"building:{data['building_id']}:latest"
    await redis.set(redis_key, msg.value.decode('utf-8')) 
    
    await save_to_postgres(pg_conn, data)
        
    if data['value'] > 50.0:
        logging.warning(f"!!! ANOMALY DETECTED in Building {data['building_id']}: {data['value']} kWh")
    
    logging.info(f"Processed: Building {data['building_id']} - {data['value']} kWh")

async def main():
    start_http_server(8000)
    logging.info("Metrics server started on port 8000")
    
    redis = aioredis.from_url(REDIS_URL)
    
    pg_conn = await asyncpg.connect(DATABASE_URL)
    
    await pg_conn.execute("""
        CREATE TABLE IF NOT EXISTS energy_metrics (
            id SERIAL PRIMARY KEY,
            building_id INTEGER,
            sensor_id VARCHAR(50),
            value FLOAT,
            timestamp TIMESTAMP
        )
    """)

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="processor-group"
    )

    await consumer.start()
    logging.info("Processor started, waiting for messages...")
    
    try:
        async for msg in consumer:
            await process_message(msg, redis, pg_conn)
            MESSAGES_PROCESSED.inc()
    finally:
        await consumer.stop()
        await pg_conn.close()

if __name__ == "__main__":
    asyncio.run(main())