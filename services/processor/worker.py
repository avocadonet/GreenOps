import asyncio
import json
import os
import logging
from aiokafka import AIOKafkaConsumer
from redis import asyncio as aioredis
import asyncpg
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge, Histogram

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "raw_energy_data"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/greenops_db")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataProcessor")

MESSAGES_TOTAL = Counter(
    'greenops_processed_messages_total', 
    'Total energy messages processed by worker'
)
CURRENT_LOAD = Gauge(
    'greenops_building_consumption_kwh', 
    'Current energy load in kWh', 
    ['building_id']
)
ANOMALIES_TOTAL = Counter(
    'greenops_anomalies_total', 
    'Total anomalies detected (>50kWh)'
)
PROCESS_TIME = Histogram(
    'greenops_processing_duration_seconds', 
    'Time spent processing a single Kafka message'
)

async def save_to_postgres(conn, data):
    query = """
        INSERT INTO energy_metrics (building_id, sensor_id, value, timestamp)
        VALUES ($1, $2, $3, $4)
    """
    await conn.execute(
        query, 
        data['building_id'], 
        data['sensor_id'], 
        data['value'], 
        data['timestamp']
    )

async def process_message(msg, redis, pg_conn):
    with PROCESS_TIME.time():
        try:
            payload = json.loads(msg.value.decode('utf-8'))
            
            if isinstance(payload.get('timestamp'), str):
                try:
                    payload['timestamp'] = datetime.fromisoformat(payload['timestamp'])
                except ValueError:
                    payload['timestamp'] = datetime.utcnow()

            building_id = payload['building_id']
            value = payload['value']

            raw_threshold = await redis.get(f"building:{building_id}:threshold")
            threshold = float(raw_threshold) if raw_threshold else 50.0

            MESSAGES_TOTAL.inc()
            CURRENT_LOAD.labels(building_id=building_id).set(value)

            if value > threshold:
                ANOMALIES_TOTAL.inc()
                logger.warning(f"ANOMALY: Building {building_id} consumed {value} kWh! (Limit: {threshold})")

            redis_key = f"building:{building_id}:latest"
            await redis.set(redis_key, json.dumps(payload, default=str))

            await save_to_postgres(pg_conn, payload)

            logger.info(f"Processed building {building_id}: {value} kWh")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

async def main():
    start_http_server(8000)
    logger.info("Prometheus metrics server started on port 8000")

    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    
    pg_conn = None
    while not pg_conn:
        try:
            pg_conn = await asyncpg.connect(DATABASE_URL)
            logger.info("Connected to PostgreSQL")
        except Exception:
            logger.info("Waiting for PostgreSQL...")
            await asyncio.sleep(2)

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
        group_id="greenops-processor-group",
        auto_offset_reset="earliest"
    )
    connected = False
    while not connected:
        try:
            await consumer.start()
            connected = True
            logger.info(f"Kafka Consumer started on topic '{KAFKA_TOPIC}'")
        except Exception as e:
            logger.info(f"Waiting for Kafka... {e}")
            await asyncio.sleep(2)

    logger.info(f"Kafka Consumer started on topic '{KAFKA_TOPIC}'")

    try:
        async for msg in consumer:
            await process_message(msg, redis, pg_conn)
    except Exception as e:
        logger.error(f"Main loop error: {e}")
    finally:
        logger.info("Shutting down...")
        await consumer.stop()
        await redis.close()
        await pg_conn.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass