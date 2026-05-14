"""
Adapter runner — loads Tuya sensor mappings from PostgreSQL and streams
telemetry to the Kafka topic `telemetry.raw`.

Environment variables
---------------------
  DATABASE_URL              asyncpg connection string (shared with workers)
  KAFKA_BOOTSTRAP_SERVERS   e.g. localhost:9092
  TUYA_CLIENT_ID            Tuya IoT project Access ID
  TUYA_CLIENT_SECRET        Tuya IoT project Access Secret
  TUYA_BASE_URL             Regional endpoint (default: https://openapi.tuyaeu.com)
  TUYA_POLL_INTERVAL        Seconds between device sweeps (default: 60)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal

from adapters.base import TelemetryMessage
from adapters.loader import load_tuya_mappings
from adapters.tuya.adapter import TuyaAdapter
from adapters.tuya.client import TuyaClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

KAFKA_TOPIC = "telemetry.raw"


async def kafka_publisher(
    queue: asyncio.Queue[TelemetryMessage | None],
    bootstrap_servers: str,
) -> None:
    from aiokafka import AIOKafkaProducer  # type: ignore[import]

    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()
    logger.info("Kafka producer started  topic=%s", KAFKA_TOPIC)

    try:
        while True:
            msg = await queue.get()
            if msg is None:
                break
            try:
                await producer.send(KAFKA_TOPIC, {
                    "sensor_id":        msg.sensor_id,
                    "value":            msg.value,
                    "measurement_unit": msg.measurement_unit,
                    "voltage":          msg.voltage,
                    "current":          msg.current,
                    "recorded_at":      msg.recorded_at,
                })
                logger.debug("→ Kafka  sensor=%s  %.4f kWh", msg.sensor_id, msg.value)
            except Exception as exc:
                logger.error("Kafka send failed: %s", exc)
    finally:
        await producer.stop()


async def run_adapter(
    adapter: TuyaAdapter,
    queue: asyncio.Queue[TelemetryMessage | None],
) -> None:
    async with adapter:
        async for msg in adapter.stream():
            await queue.put(msg)


async def main() -> None:
    database_url      = os.environ["DATABASE_URL"]
    bootstrap_servers = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
    client_id         = os.environ["TUYA_CLIENT_ID"]
    client_secret     = os.environ["TUYA_CLIENT_SECRET"]
    base_url          = os.getenv("TUYA_BASE_URL", "https://openapi.tuyaeu.com")
    poll_interval     = int(os.getenv("TUYA_POLL_INTERVAL", "60"))

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as session:
        mappings = await load_tuya_mappings(session)

    await engine.dispose()

    if not mappings:
        logger.warning("No Tuya sensors found in the database (provider='tuya') — exiting")
        return

    logger.info("Loaded %d Tuya sensor mapping(s) from database", len(mappings))

    client  = TuyaClient(client_id, client_secret, base_url)
    adapter = TuyaAdapter(mappings, client, poll_interval)

    queue: asyncio.Queue[TelemetryMessage | None] = asyncio.Queue(maxsize=1000)

    adapter_task   = asyncio.create_task(run_adapter(adapter, queue), name="tuya")
    publisher_task = asyncio.create_task(
        kafka_publisher(queue, bootstrap_servers), name="kafka-publisher"
    )

    stop = asyncio.Event()

    def _shutdown(*_: object) -> None:
        logger.info("Shutdown signal received")
        stop.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _shutdown)

    await stop.wait()

    logger.info("Stopping adapter …")
    adapter_task.cancel()
    await asyncio.gather(adapter_task, return_exceptions=True)

    await queue.put(None)
    await publisher_task
    logger.info("Adapter runner stopped.")


if __name__ == "__main__":
    asyncio.run(main())
