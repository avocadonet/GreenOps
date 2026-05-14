"""
Abstract base for all GreenOps sensor platform adapters.

Each adapter is responsible for:
  1. Connecting to an external platform (Tuya Cloud, Mi Home, Zigbee2MQTT, …)
  2. Receiving or polling raw sensor readings in the platform's native format
  3. Normalising them into GreenOps TelemetryMessage objects
  4. Publishing the messages to the Kafka topic `telemetry.raw`

Implementing a new adapter
--------------------------
1. Subclass SensorAdapter.
2. Implement connect(), disconnect(), and stream().
3. Register it in runner.py.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import AsyncIterator
from uuid import UUID

logger = logging.getLogger(__name__)

KAFKA_TOPIC = "telemetry.raw"


@dataclass
class SensorMapping:
    """
    Maps an external-platform device channel to a GreenOps sensor UUID.

    external_id   — device or channel identifier on the external platform
                    (Tuya device_id, miio DID, Zigbee friendly name, …)
    sensor_id     — GreenOps sensor UUID (must exist in the database)
    channel       — sub-channel within a device, e.g. "L1" for phase 1;
                    None means the device exposes a single energy channel
    scale         — multiply raw value by this factor to get kWh
                    (e.g. 0.001 if the platform reports Wh)
    """

    external_id: str
    sensor_id: UUID
    channel: str | None = None
    scale: float = 1.0


@dataclass
class TelemetryMessage:
    """Wire format published to Kafka topic `telemetry.raw` (matches CreateMetricDTO)."""

    sensor_id: str          # UUID as string — aiokafka serialises to JSON
    value: float            # kWh
    measurement_unit: str   # always "kWh"
    voltage: float          # V
    current: float          # A
    recorded_at: str        # ISO-8601 UTC

    @classmethod
    def build(
        cls,
        sensor_id: UUID,
        value_kwh: float,
        voltage: float,
        current: float,
        ts: datetime | None = None,
    ) -> "TelemetryMessage":
        if ts is None:
            ts = datetime.now(tz=timezone.utc)
        return cls(
            sensor_id=str(sensor_id),
            value=round(value_kwh, 6),
            measurement_unit="kWh",
            voltage=round(voltage, 2),
            current=round(current, 4),
            recorded_at=ts.isoformat(),
        )

    def to_json_bytes(self) -> bytes:
        return json.dumps(asdict(self)).encode()


class SensorAdapter(ABC):
    """
    Base class for all platform adapters.

    Subclasses must implement:
      connect()     — establish session / subscribe to broker
      disconnect()  — clean up resources
      stream()      — async generator yielding TelemetryMessage objects
    """

    name: str = "base"

    def __init__(self, mappings: list[SensorMapping]) -> None:
        self._mappings: dict[str, SensorMapping] = {
            m.external_id: m for m in mappings
        }

    def resolve(self, external_id: str) -> SensorMapping | None:
        """Return the GreenOps mapping for an external device ID, or None if unknown."""
        mapping = self._mappings.get(external_id)
        if mapping is None:
            logger.warning("[%s] unmapped device: %s — skipping", self.name, external_id)
        return mapping

    @abstractmethod
    async def connect(self) -> None:
        """Open connection / authenticate with the external platform."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Release all resources."""

    @abstractmethod
    async def stream(self) -> AsyncIterator[TelemetryMessage]:
        """
        Yield TelemetryMessage objects as readings become available.
        May be polling-based or event-driven depending on the platform.
        """

    async def __aenter__(self) -> "SensorAdapter":
        await self.connect()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.disconnect()
