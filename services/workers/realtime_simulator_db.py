import argparse
import asyncio
import json
import math
import os
import random
from datetime import datetime, timezone

import asyncpg
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

# ── main ──────────────────────────────────────────────────────────────────────

async def run(db_url: str, nats_url: str, rate: float):
    print(f"Connecting to database at {db_url}...")
    conn = await asyncpg.connect(db_url)
    
    try:
        print("Fetching sensors metadata...")
        query = """
            SELECT 
                s.sensor_id,
                s.sensor_type,
                COALESCE(b.building_type, ub.building_type) as building_type,
                t.limit_value as upper_threshold
            FROM sensors s
            LEFT JOIN buildings b ON s.building_id = b.building_id
            LEFT JOIN units u ON s.unit_id = u.unit_id
            LEFT JOIN buildings ub ON u.building_id = ub.building_id
            LEFT JOIN thresholds t ON s.sensor_id = t.sensor_id 
                AND t.threshold_type = 'UPPER' 
                AND t.tariff_zone = 'DAY'
        """
        rows = await conn.fetch(query)
        print(f"Fetched {len(rows)} sensors.")
        
        print(f"Connecting to NATS at {nats_url}...")
        nc = await nats.connect(nats_url)
        js = nc.jetstream()
        subject = "telemetry.raw"
        
        try:
            await js.add_stream(name="telemetry", subjects=[subject])
        except Exception:
            pass  # stream already exists
            
        tasks = []
        print("Starting workers...")
        for row in rows:
            sensor_id = str(row["sensor_id"])
            sensor_type = row["sensor_type"]
            b_type = row["building_type"]
            upper = row["upper_threshold"] or 100.0
            
            is_residential = (b_type == "RESIDENTIAL")
            
            if sensor_type == "COMMON":
                baseline = 75.0 if is_residential else 450.0
            else:
                baseline = 15.0
                
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
        await conn.close()
        if 'nc' in locals():
            await nc.drain()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time Telemetry Simulator")
    parser.add_argument(
        "--database-url",
        default=f"postgresql://{os.environ.get('POSTGRES_USER', 'user')}:{os.environ.get('POSTGRES_PASSWORD', 'password')}@postgres:5432/greenops_db",
        help="Database URL"
    )
    parser.add_argument("--nats-url", default="nats://nuts:4222", help="NATS server URL")
    parser.add_argument("--rate", type=float, default=1.0, help="Messages per second per sensor")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run(args.database_url, args.nats_url, args.rate))
    except KeyboardInterrupt:
        pass
