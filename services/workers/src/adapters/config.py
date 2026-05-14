"""
Adapter configuration loader.

Reads adapters/config.yaml and returns typed config objects used by runner.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

import yaml


@dataclass
class TuyaDeviceConfig:
    external_id: str   # Tuya device_id (alphanumeric, ~22 chars)
    sensor_id: UUID    # GreenOps sensor UUID
    scale: float = 1.0


@dataclass
class TuyaConfig:
    enabled: bool
    client_id: str
    client_secret: str
    base_url: str = "https://openapi.tuyaeu.com"
    poll_interval: int = 60
    devices: list[TuyaDeviceConfig] = field(default_factory=list)


@dataclass
class KafkaConfig:
    bootstrap_servers: str = "localhost:9092"
    topic: str = "telemetry.raw"


@dataclass
class AdaptersConfig:
    kafka: KafkaConfig
    tuya: TuyaConfig | None = None


def load(path: str | Path = "adapters/config.yaml") -> AdaptersConfig:
    raw = yaml.safe_load(Path(path).read_text())

    kafka = KafkaConfig(**raw.get("kafka", {}))

    tuya = None
    if "tuya" in raw:
        t = raw["tuya"]
        tuya = TuyaConfig(
            enabled=t.get("enabled", True),
            client_id=t["client_id"],
            client_secret=t["client_secret"],
            base_url=t.get("base_url", "https://openapi.tuyaeu.com"),
            poll_interval=t.get("poll_interval", 60),
            devices=[
                TuyaDeviceConfig(
                    external_id=d["external_id"],
                    sensor_id=UUID(d["sensor_id"]),
                    scale=d.get("scale", 1.0),
                )
                for d in t.get("devices", [])
            ],
        )

    return AdaptersConfig(kafka=kafka, tuya=tuya)
