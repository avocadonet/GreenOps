import argparse
import asyncio
import json
import math
import os
import random
from datetime import datetime, timezone

import aiohttp
import nats

# ── metric helpers ────────────────────────────────────────────────────────────

SPIKE_PROB = 0.06

def _diurnal(hour: int, minute: int, is_residential: bool) -> float:
    t = hour + minute / 60.0
    if is_residential:
        morning = max(0.0, math.sin(math.pi * (t - 5.0) / 4.0))
        evening = max(0.0, math.sin(math.pi * (t - 17.0) / 5.0))
        return max(0.12, min(1.0, 0.20 + 0.45 * morning + 0.35 * evening))
    if 7.0 <= t <= 18.0:
        return 0.65 + 0.35 * math.sin(math.pi * (t - 7.0) / 11.0)
    return 0.45 if 18.0 < t <= 22.0 else 0.15

def _gen_reading(
    dt: datetime, baseline: float, is_residential: bool, upper: float
) -> tuple[float, float, float]:
    is_spike = random.random() < SPIKE_PROB
    if is_spike:
        value = round(upper * random.uniform(1.55, 2.40), 4)
    else:
        factor = _diurnal(dt.hour, dt.minute, is_residential) * random.gauss(1.0, 0.12)
        value = round(max(0.5, baseline * factor), 4)
    voltage = round(random.gauss(220.0, 2.0), 2)
    current = round(value / max(voltage, 1.0), 4)
    return value, voltage, current

# ── api client ────────────────────────────────────────────────────────────────

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = aiohttp.ClientSession()
        self.token = None

    async def close(self):
        await self.session.close()

    async def login(self, email: str, password: str):
        url = f"{self.base_url}/api/v1/auth/login"
        print(f"Attempting login to {url} with email {email}")
        async with self.session.post(url, json={"email": email, "password": password}) as resp:
            if resp.status != 200:
                text = await resp.text()
                print(f"Login failed with status {resp.status}: {text}")
            resp.raise_for_status()
            data = await resp.json()
            self.token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("Login successful.")

    async def fetch_all(self, endpoint: str) -> list[dict]:
        url = f"{self.base_url}{endpoint}"
        items = []
        page = 1
        while True:
            async with self.session.get(url, params={"page": page, "page_size": 100}) as resp:
                resp.raise_for_status()
                data = await resp.json()
                items.extend(data["items"])
                if len(data["items"]) < 100:
                    break
                page += 1
        return items

# ── worker ────────────────────────────────────────────────────────────────────

async def worker(
    sensor_id: str,
    baseline: float,
    is_residential: bool,
    upper: float,
    js,
    subject: str,
    rate: float,
):
    delay = 1.0 / rate
    print(f"[Worker {sensor_id[:8]}] Started (baseline={baseline}, res={is_residential}, upper={upper})")
    
    while True:
        try:
            now = datetime.now(tz=timezone.utc)
            value, voltage, current = _gen_reading(now, baseline, is_residential, upper)
            
            message = {
                "sensor_id": sensor_id,
                "value": value,
                "measurement_unit": "kWh",
                "voltage": voltage,
                "current": current,
                "recorded_at": now.isoformat(),
            }
            
            await js.publish(subject, json.dumps(message).encode())
            print(f"[Worker {sensor_id[:8]}] Published reading: value={value:.2f}, voltage={voltage:.2f}, current={current:.2f}")
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Worker {sensor_id[:8]}] Error: {e}")
            await asyncio.sleep(delay)

# ── main admin@example.com ──────────────────────────────────────────────────────────────────────

async def run(api_url: str, nats_url: str, rate: float):
    email = os.environ.get("SUPERUSER_EMAIL")
    password = os.environ.get("SUPERUSER_PASSWORD")
    
    if not email or not password:
        print("Error: SUPERUSER_EMAIL and SUPERUSER_PASSWORD environment variables must be set.")
        return

    api = ApiClient(api_url)
    try:
        print("Logging in to API...")
        await api.login(email, password)
        
        print("Fetching metadata...")
        sensors = await api.fetch_all("/api/v1/sensors")
        buildings = await api.fetch_all("/api/v1/buildings")
        units = await api.fetch_all("/api/v1/units")
        thresholds = await api.fetch_all("/api/v1/thresholds")
        
        print(f"Fetched {len(sensors)} sensors, {len(buildings)} buildings, {len(units)} units, {len(thresholds)} thresholds.")
        
        # Build maps
        bld_map = {b["building_id"]: b for b in buildings}
        unit_map = {u["unit_id"]: u for u in units}
        
        # Map sensor_id -> upper threshold (DAY)
        upper_map = {}
        for t in thresholds:
            if t["threshold_type"] == "UPPER" and t["tariff_zone"] == "DAY":
                upper_map[t["sensor_id"]] = t["limit_value"]
                
        # Prepare worker tasks
        tasks = []
        
        print(f"Connecting to NATS at {nats_url}...")
        nc = await nats.connect(nats_url)
        js = nc.jetstream()
        subject = "telemetry.raw"
        
        try:
            await js.add_stream(name="telemetry", subjects=[subject])
        except Exception:
            pass  # stream already exists
            
        print("Starting workers...")
        for s in sensors:
            sensor_id = s["sensor_id"]
            sensor_type = s["sensor_type"]
            
            # Determine building type
            b_type = None
            if s.get("building_id"):
                b_type = bld_map.get(s["building_id"], {}).get("building_type")
            elif s.get("unit_id"):
                u = unit_map.get(s["unit_id"])
                if u and u.get("building_id"):
                    b_type = bld_map.get(u["building_id"], {}).get("building_type")
                    
            is_residential = (b_type == "RESIDENTIAL")
            
            # Determine baseline
            if sensor_type == "COMMON":
                baseline = 75.0 if is_residential else 450.0
            else:
                baseline = 15.0
                
            # Determine upper threshold
            upper = upper_map.get(sensor_id, 100.0) # Default fallback
            
            tasks.append(
                asyncio.create_task(
                    worker(sensor_id, baseline, is_residential, upper, js, subject, rate)
                )
            )
            
        print(f"Spawned {len(tasks)} worker tasks. Press Ctrl+C to stop.")
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        if 'tasks' in locals():
            for t in tasks:
                t.cancel()
        await api.close()
        if 'nc' in locals():
            await nc.drain()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time Telemetry Simulator")
    parser.add_argument("--api-url", default="http://localhost:8000", help="CRUD API URL")
    parser.add_argument("--nats-url", default="nats://localhost:4222", help="NATS server URL")
    parser.add_argument("--rate", type=float, default=1.0, help="Messages per second per sensor")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run(args.api_url, args.nats_url, args.rate))
    except KeyboardInterrupt:
        pass
