"""
Adapter runner — entry point for the adapter layer.

Starts all enabled adapters concurrently, collects TelemetryMessage objects
from each, and publishes them to the Kafka topic `telemetry.raw`.

Architecture
------------
  [ TuyaAdapter ]      ─╮
  [     ...     ]      ─┼──► asyncio.Queue ──► KafkaPublisher ──► Kafka
  [     ...     ]      ─╯

Each adapter runs in its own asyncio Task so a failure in one does not
affect the others.  The Kafka publisher runs in a dedicated Task that drains
the shared queue.

Usage
-----
  # Start with default config file (adapters/config.yaml)
  python -m adapters.runner

  # Custom config path
  python -m adapters.runner --config /etc/greenops/adapters.yaml
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import signal
from typing import AsyncIterator

from adapters.base import SensorAdapter, SensorMapping, TelemetryMessage
from adapters.config import (
    AdaptersConfig,
    TuyaConfig,
    XiaomiConfig,
    Zigbee2MqttConfig,
    load,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── adapter factory ───────────────────────────────────────────────────────────

def _build_tuya(cfg: TuyaConfig) -> SensorAdapter:
    from adapters.tuya.adapter import TuyaAdapter
    from adapters.tuya.client import TuyaClient

    client = TuyaClient(cfg.client_id, cfg.client_secret, cfg.base_url)
    mappings = [
        SensorMapping(
            external_id=d.external_id,
            sensor_id=d.sensor_id,
            scale=d.scale,
        )
        for d in cfg.devices
    ]
    return TuyaAdapter(mappings, client, cfg.poll_interval)


def build_adapters(config: AdaptersConfig) -> list[SensorAdapter]:
    adapters: list[SensorAdapter] = []

    if config.tuya and config.tuya.enabled and config.tuya.devices:
        adapters.append(_build_tuya(config.tuya))
        logger.info("Tuya adapter  devices=%d", len(config.tuya.devices))

    return adapters


# ── Kafka publisher ───────────────────────────────────────────────────────────

async def kafka_publisher(
    queue: asyncio.Queue[TelemetryMessage | None],
    bootstrap_servers: str,
    topic: str,
) -> None:
    from aiokafka import AIOKafkaProducer  # type: ignore[import]

    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()
    logger.info("Kafka producer started  topic=%s", topic)

    try:
        while True:
            msg = await queue.get()
            if msg is None:
                break
            try:
                await producer.send(topic, {
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


# ── adapter runner ────────────────────────────────────────────────────────────

async def run_adapter(
    adapter: SensorAdapter,
    queue: asyncio.Queue[TelemetryMessage | None],
) -> None:
    async with adapter:
        async for msg in adapter.stream():
            await queue.put(msg)


# ── main ──────────────────────────────────────────────────────────────────────

async def main(config_path: str) -> None:
    config   = load(config_path)
    adapters = build_adapters(config)

    if not adapters:
        logger.warning("No adapters enabled — check adapters/config.yaml")
        return

    queue: asyncio.Queue[TelemetryMessage | None] = asyncio.Queue(maxsize=1000)

    tasks = [
        asyncio.create_task(run_adapter(a, queue), name=a.name)
        for a in adapters
    ]
    publisher_task = asyncio.create_task(
        kafka_publisher(queue, config.kafka.bootstrap_servers, config.kafka.topic),
        name="kafka-publisher",
    )

    stop = asyncio.Event()

    def _shutdown(*_: object) -> None:
        logger.info("Shutdown signal received")
        stop.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _shutdown)

    await stop.wait()

    logger.info("Stopping adapters …")
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    await queue.put(None)  # poison pill for the publisher
    await publisher_task
    logger.info("Adapter runner stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GreenOps adapter runner")
    parser.add_argument(
        "--config", default="adapters/config.yaml",
        help="Path to adapter config YAML (default: adapters/config.yaml)",
    )
    args = parser.parse_args()
    asyncio.run(main(args.config))
