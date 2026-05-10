"""
Tuya Cloud adapter for GreenOps.

Supported device types
----------------------
  Smart energy monitors / smart plugs with power metering:
    - Tuya Wi-Fi Energy Meter (1/3 phase)  — codes: cur_power, add_ele, cur_voltage, cur_current
    - Tuya Smart Plug with power monitoring — same data-point codes
    - Tongou / NOUS / BlitzWolf energy meters — same codes, differ only in unit scale

Data-point code reference
--------------------------
  cur_power   : current power consumption (0.1 W)  → divide by 10 000 for kWh rate
  add_ele     : accumulated energy counter   (kWh)  → use delta between polls
  cur_voltage : current voltage              (0.1 V) → divide by 10 for V
  cur_current : current current              (mA)    → divide by 1 000 for A

Setup
-----
1. Create an account at https://iot.tuya.com
2. Create a Cloud Development project (select "Smart Home" or "Industry")
3. Copy your Access ID (client_id) and Access Secret (client_secret)
4. Link your devices under "Devices" → "Link Tuya App Account"
5. Note each device_id and map it to the corresponding GreenOps sensor UUID
   in adapters/config.yaml
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import AsyncIterator

from adapters.base import SensorAdapter, SensorMapping, TelemetryMessage
from adapters.tuya.client import TuyaClient

logger = logging.getLogger(__name__)

# Tuya data-point codes that carry energy/power readings
_DP_ENERGY    = "add_ele"      # accumulated kWh (float)
_DP_POWER     = "cur_power"    # current power in 0.1 W
_DP_VOLTAGE   = "cur_voltage"  # voltage in 0.1 V
_DP_CURRENT   = "cur_current"  # current in mA

# Fallback values when a device does not expose voltage/current
_DEFAULT_VOLTAGE = 220.0
_DEFAULT_CURRENT = 0.0


class TuyaAdapter(SensorAdapter):
    """
    Polls the Tuya Cloud API on a fixed interval and converts readings to
    GreenOps TelemetryMessage objects.

    Parameters
    ----------
    mappings      List of SensorMapping (external_id = Tuya device_id)
    client        Pre-configured TuyaClient (or pass client_id/secret instead)
    poll_interval Seconds between full device sweeps (default: 60)
    """

    name = "tuya"

    def __init__(
        self,
        mappings: list[SensorMapping],
        client: TuyaClient,
        poll_interval: int = 60,
    ) -> None:
        super().__init__(mappings)
        self._client = client
        self._poll_interval = poll_interval
        # Track last energy counter per device to compute delta kWh
        self._last_energy: dict[str, float] = {}

    async def connect(self) -> None:
        await self._client.open()
        logger.info("[tuya] connected  devices=%d", len(self._mappings))

    async def disconnect(self) -> None:
        await self._client.close()
        logger.info("[tuya] disconnected")

    async def stream(self) -> AsyncIterator[TelemetryMessage]:
        while True:
            for external_id, mapping in self._mappings.items():
                try:
                    msg = await self._poll_device(external_id, mapping)
                    if msg is not None:
                        yield msg
                except Exception as exc:
                    logger.warning("[tuya] device %s error: %s", external_id, exc)

            await asyncio.sleep(self._poll_interval)

    # ── private ───────────────────────────────────────────────────────────────

    async def _poll_device(
        self, device_id: str, mapping: SensorMapping
    ) -> TelemetryMessage | None:
        status = await self._client.get_device_status(device_id)

        # Parse data-point codes into a flat dict
        dp: dict[str, float] = {
            item["code"]: float(item["value"])
            for item in status
            if item["code"] in (_DP_ENERGY, _DP_POWER, _DP_VOLTAGE, _DP_CURRENT)
        }

        if not dp:
            logger.debug("[tuya] device %s has no energy DPs", device_id)
            return None

        # Prefer accumulated energy counter (delta between polls)
        if _DP_ENERGY in dp:
            raw_energy = dp[_DP_ENERGY]            # already in kWh
            last = self._last_energy.get(device_id, raw_energy)
            delta_kwh = max(0.0, raw_energy - last) * mapping.scale
            self._last_energy[device_id] = raw_energy
        else:
            # Fall back to instantaneous power → estimate kWh for the interval
            power_w = dp.get(_DP_POWER, 0.0) / 10.0    # 0.1 W → W
            delta_kwh = (power_w / 1000.0) * (self._poll_interval / 3600.0) * mapping.scale

        voltage = dp.get(_DP_VOLTAGE, _DEFAULT_VOLTAGE * 10) / 10.0  # 0.1 V → V
        current = dp.get(_DP_CURRENT, _DEFAULT_CURRENT * 1000) / 1000.0  # mA → A

        logger.debug(
            "[tuya] device=%s  %.4f kWh  %sV  %sA",
            device_id, delta_kwh, voltage, current,
        )
        return TelemetryMessage.build(
            sensor_id=mapping.sensor_id,
            value_kwh=delta_kwh,
            voltage=voltage,
            current=current,
            ts=datetime.now(tz=timezone.utc),
        )
