"""
GreenOps telemetry simulator (UC-10).

Publishes fake sensor readings to the `telemetry.raw` Kafka topic so that
the full end-to-end pipeline can be exercised without real IoT hardware.

Usage examples:
  # Default: 10 msg/s, 10 % spikes, random sensor UUID
  python simulator.py --sensor-id <UUID>

  # Load test only (no spikes)
  python simulator.py --sensor-id <UUID> --mode normal --rate 1000

  # Spike storm
  python simulator.py --sensor-id <UUID> --mode spike --threshold 100
"""

import argparse
import asyncio
import json
import random
import uuid
from datetime import datetime, timezone


async def run(
    sensor_id: str,
    mode: str,
    rate: int,
    threshold: float,
    bootstrap_servers: str,
) -> None:
    from aiokafka import AIOKafkaProducer

    topic = "telemetry.raw"
    delay = 1.0 / rate

    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()
    sent = 0
    try:
        print(
            f"Simulator started: sensor={sensor_id} mode={mode} "
            f"rate={rate}/s threshold={threshold} topic={topic}"
        )
        while True:
            is_spike = mode == "spike" or (mode == "default" and random.random() < 0.10)
            if is_spike:
                value = threshold * random.uniform(1.5, 3.0)
            else:
                value = threshold * random.uniform(0.2, 0.85)

            message = {
                "sensor_id": sensor_id,
                "value": round(value, 4),
                "measurement_unit": "kWh",
                "voltage": round(random.uniform(215.0, 225.0), 2),
                "current": round(value / random.uniform(215.0, 225.0), 4),
                "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
            }
            await producer.send(topic, message)
            sent += 1
            if sent % 100 == 0:
                print(f"  sent {sent} messages (last value={message['value']:.2f})")
            await asyncio.sleep(delay)
    except KeyboardInterrupt:
        print(f"\nStopped after {sent} messages.")
    finally:
        await producer.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="GreenOps telemetry simulator")
    parser.add_argument(
        "--sensor-id",
        default=str(uuid.uuid4()),
        help="Sensor UUID to simulate (default: random UUID)",
    )
    parser.add_argument(
        "--mode",
        choices=["default", "normal", "spike"],
        default="default",
        help=(
            "default = 10%% random spikes; "
            "normal = no spikes (load test); "
            "spike = every message is a spike"
        ),
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=10,
        help="Messages per second (default: 10)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=100.0,
        help="Threshold value used to generate spike magnitudes (default: 100.0)",
    )
    parser.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
        help="Kafka bootstrap servers (default: localhost:9092)",
    )

    args = parser.parse_args()
    asyncio.run(
        run(
            sensor_id=args.sensor_id,
            mode=args.mode,
            rate=args.rate,
            threshold=args.threshold,
            bootstrap_servers=args.bootstrap_servers,
        )
    )


if __name__ == "__main__":
    main()
