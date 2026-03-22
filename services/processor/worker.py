import asyncio
import json
import os
import logging
from aiokafka import AIOKafkaConsumer
from redis import asyncio as aioredis
import asyncpg
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge, Histogram
from threshold import ThresholdManager

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
THRESHOLD_VALUE = Gauge(
    'greenops_building_threshold_kwh',
    'Current dynamic threshold for building in kWh',
    ['building_id']
)
AVERAGE_CONSUMPTION = Gauge(
    'greenops_building_average_kwh',
    'Average consumption for building in kWh',
    ['building_id']
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

async def process_message(msg, redis, pg_conn, threshold_manager):
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
            
            if raw_threshold is None:
                threshold = 50.0
                logger.warning(f"No threshold found for building {building_id}, using fallback: {threshold}")
                
                avg = await threshold_manager.calculate_building_average(building_id)
                if avg:
                    threshold = threshold_manager.calculate_dynamic_threshold(avg)
                    await redis.set(f"building:{building_id}:threshold", threshold)
                    logger.info(f"Calculated and set new threshold for {building_id}: {threshold}")
            else:
                threshold = float(raw_threshold)

            MESSAGES_TOTAL.inc()
            CURRENT_LOAD.labels(building_id=building_id).set(value)
            THRESHOLD_VALUE.labels(building_id=building_id).set(threshold)
            
            avg_raw = await redis.get(f"building:{building_id}:average_consumption")
            if avg_raw:
                AVERAGE_CONSUMPTION.labels(building_id=building_id).set(float(avg_raw))

            if value > threshold:
                ANOMALIES_TOTAL.inc()
                excess_percentage = ((value - threshold) / threshold) * 100
                logger.warning(
                    f"ANOMALY DETECTED: Building {building_id} consumed {value:.2f} kWh "
                    f"(Threshold: {threshold:.2f} kWh, Excess: {excess_percentage:.1f}%)"
                )

            redis_key = f"building:{building_id}:latest"
            await redis.set(redis_key, json.dumps(payload, default=str))

            await save_to_postgres(pg_conn, payload)

            logger.debug(f"Processed building {building_id}: {value:.2f} kWh (threshold: {threshold:.2f} kWh)")

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)


async def main():
    start_http_server(8000)
    logger.info("Prometheus metrics server started on port 8000")

    threshold_manager = ThresholdManager()
    if not await threshold_manager.initialize():
        logger.error("Failed to initialize ThresholdManager, exiting")
        return

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

    await pg_conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_energy_metrics_building_timestamp 
        ON energy_metrics (building_id, timestamp DESC)
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
        threshold_update_task = asyncio.create_task(
            threshold_manager.run_periodic_updates()
        )

        async for msg in consumer:
            await process_message(msg, redis, pg_conn, threshold_manager)
    except Exception as e:
        logger.error(f"Main loop error: {e}")
    finally:
        logger.info("Shutting down...")
        threshold_update_task.cancel()
        await consumer.stop()
        await redis.close()
        await pg_conn.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass