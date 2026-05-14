"""
GreenOps DB seeder — creates users, orgs, buildings, units, sensors,
thresholds and N days of metrics directly in PostgreSQL.

Usage:
  python seed_db.py
  python seed_db.py --database-url postgresql://user:password@localhost:5432/greenops_db
  python seed_db.py --days 14
  python seed_db.py --clean       # wipe all tables, then re-seed
"""

from __future__ import annotations

import argparse
import asyncio
import math
import random
import uuid
from datetime import date, datetime, timedelta

import asyncpg
import bcrypt


# ── fixtures ──────────────────────────────────────────────────────────────────

USERS = [
    dict(email="super@greenops.io",        fullname="Super Admin",          password="greenops2024", role="SUPER_USER"),
    dict(email="admin@ecoresidence.io",    fullname="EcoRes Admin",         password="admin123",     role="PUBLIC"),
    dict(email="admin@industrialops.io",   fullname="IndustrialOps Admin",  password="admin123",     role="PUBLIC"),
    dict(email="redactor@ecoresidence.io", fullname="EcoRes Redactor",      password="redactor123",  role="PUBLIC"),
    dict(email="owner@ecoresidence.io",    fullname="Unit Owner",           password="owner123",     role="PUBLIC"),
]

ORGS = [
    dict(
        name="EcoResidence Management",
        description="Residential property management across the metro area",
        contact_email="ops@ecoresidence.io",
        owner_email="admin@ecoresidence.io",
    ),
    dict(
        name="IndustrialOps Corp",
        description="Industrial facility monitoring & energy optimisation",
        contact_email="energy@industrialops.com",
        owner_email="admin@industrialops.io",
    ),
]

# email → list of (org_name, role)
ORG_ROLES: dict[str, list[tuple[str, str]]] = {
    "admin@ecoresidence.io":    [("EcoResidence Management", "ADMIN")],
    "admin@industrialops.io":   [("IndustrialOps Corp",      "ADMIN")],
    "redactor@ecoresidence.io": [("EcoResidence Management", "REDACTOR")],
    "owner@ecoresidence.io":    [("EcoResidence Management", "OWNER")],
}

BUILDINGS = [
    dict(
        org="EcoResidence Management",
        address="12 Oak Street, Building A",
        building_type="RESIDENTIAL",
        total_area=4500.0,
        units=[("101", 1, "John Smith"), ("102", 1, "Maria Garcia"),
               ("201", 2, "Robert Johnson"), ("202", 2, "Emily Davis")],
    ),
    dict(
        org="EcoResidence Management",
        address="48 Maple Avenue",
        building_type="RESIDENTIAL",
        total_area=3200.0,
        units=[("A1", 1, "Carlos Ruiz"), ("A2", 1, "Ling Wei"), ("B1", 2, "Natasha Ivanova")],
    ),
    dict(
        org="EcoResidence Management",
        address="7 Birch Lane, Complex C",
        building_type="RESIDENTIAL",
        total_area=6100.0,
        units=[("1A", 1, "Michael Brown"), ("1B", 1, "Sarah Connor"),
               ("2A", 2, "David Park"),    ("2B", 2, "Amara Osei")],
    ),
    dict(
        org="IndustrialOps Corp",
        address="14 Harbor Industrial Park",
        building_type="INDUSTRIAL",
        total_area=12000.0,
        units=[],
    ),
    dict(
        org="IndustrialOps Corp",
        address="2 Westgate Factory",
        building_type="INDUSTRIAL",
        total_area=8500.0,
        units=[],
    ),
]

SENSOR_MODELS = ["SmartMeter Pro X1", "EnergyNode 500", "GridSense v3", "PowerEye 2000"]

THRESHOLDS = {
    "RESIDENTIAL": {
        "UPPER": {"DAY": 120.0, "NIGHT": 80.0},
        "LOWER": {"DAY": 2.0,   "NIGHT": 1.0},
    },
    "INDUSTRIAL": {
        "UPPER": {"DAY": 600.0, "NIGHT": 350.0},
        "LOWER": {"DAY": 20.0,  "NIGHT": 10.0},
    },
}
INDIV_THRESHOLDS = {
    "UPPER": {"DAY": 40.0, "NIGHT": 25.0},
    "LOWER": {"DAY": 0.5,  "NIGHT": 0.2},
}

SPIKE_PROB = 0.06


# ── metric helpers ────────────────────────────────────────────────────────────

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


# ── seeder ────────────────────────────────────────────────────────────────────

async def seed(conn: asyncpg.Connection, days: int) -> None:
    now = datetime.utcnow()

    # ── users ──────────────────────────────────────────────────────────────────
    print("Creating users …")
    user_ids: dict[str, int] = {}
    for u in USERS:
        hashed = bcrypt.hashpw(u["password"].encode(), bcrypt.gensalt()).decode()
        row = await conn.fetchrow(
            """
            INSERT INTO users (email, fullname, is_active, hashed_password, salt, role, created_at)
            VALUES ($1, $2, TRUE, $3, '', $4, $5)
            ON CONFLICT (email) DO UPDATE SET hashed_password = EXCLUDED.hashed_password
            RETURNING id
            """,
            u["email"], u["fullname"], hashed, u["role"], now,
        )
        user_ids[u["email"]] = row["id"]
        print(f"  [{u['role']:20s}] {u['email']}  password={u['password']}")

    # ── organizations ──────────────────────────────────────────────────────────
    print("\nCreating organizations …")
    org_ids: dict[str, int] = {}
    for o in ORGS:
        owner_id = user_ids[o["owner_email"]]
        row = await conn.fetchrow(
            """
            INSERT INTO organizations (name, description, contact_email, owner_id, created_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT DO NOTHING
            RETURNING id
            """,
            o["name"], o["description"], o["contact_email"], owner_id, now,
        )
        if row is None:
            row = await conn.fetchrow("SELECT id FROM organizations WHERE name = $1", o["name"])
        org_ids[o["name"]] = row["id"]
        print(f"  {o['name']}  id={row['id']}")

    # ── user_organization_roles ────────────────────────────────────────────────
    print("\nAssigning org roles …")
    for email, pairs in ORG_ROLES.items():
        uid = user_ids[email]
        for org_name, role in pairs:
            oid = org_ids[org_name]
            await conn.execute(
                """
                INSERT INTO user_organization_roles (user_id, organization_id, role)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, organization_id) DO UPDATE SET role = EXCLUDED.role
                """,
                uid, oid, role,
            )
            print(f"  {email:40s} → {org_name} ({role})")

    # ── buildings / units / sensors / thresholds ───────────────────────────────
    print("\nCreating buildings, units, sensors, thresholds …")
    serial = 1
    calib = date.today() + timedelta(days=365)

    # sensor_id → {baseline, is_residential, upper_threshold}
    sensor_meta: list[dict] = []

    for b in BUILDINGS:
        org_id = org_ids[b["org"]]
        building_id = uuid.uuid4()
        btype = b["building_type"]

        await conn.execute(
            """
            INSERT INTO buildings (building_id, address, building_type, total_area, organization_id)
            VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING
            """,
            building_id, b["address"], btype, b["total_area"], org_id,
        )

        # COMMON sensor (building meter)
        row = await conn.fetchrow(
            """
            INSERT INTO sensors
                (sensor_id, serial_number, model, calibration_date, sensor_type, building_id, organization_id)
            VALUES ($1, $2, $3, $4, 'COMMON', $5, $6)
            ON CONFLICT (serial_number) DO UPDATE SET model = EXCLUDED.model
            RETURNING sensor_id
            """,
            uuid.uuid4(), f"SN-{serial:04d}", SENSOR_MODELS[(serial - 1) % len(SENSOR_MODELS)],
            calib, building_id, org_id,
        )
        common_id = row["sensor_id"]
        thr = THRESHOLDS[btype]
        upper = thr["UPPER"]["DAY"]
        for ttype, zones in thr.items():
            for zone, val in zones.items():
                await conn.execute(
                    """
                    INSERT INTO thresholds
                        (threshold_id, sensor_id, limit_value, threshold_type, tariff_zone, organization_id)
                    VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING
                    """,
                    uuid.uuid4(), common_id, val, ttype, zone, org_id,
                )
        sensor_meta.append(dict(
            sensor_id=common_id,
            sensor_type="COMMON",
            building_id=building_id,
            baseline=75.0 if btype == "RESIDENTIAL" else 450.0,
            is_residential=(btype == "RESIDENTIAL"),
            upper=upper,
        ))
        serial += 1

        # units + INDIVIDUAL sensors
        for unit_num, floor, owner in b["units"]:
            unit_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO units (unit_id, building_id, unit_number, floor, owner_name, organization_id)
                VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING
                """,
                unit_id, building_id, unit_num, floor, owner, org_id,
            )
            row = await conn.fetchrow(
                """
                INSERT INTO sensors
                    (sensor_id, serial_number, model, calibration_date, sensor_type, unit_id, organization_id)
                VALUES ($1, $2, $3, $4, 'INDIVIDUAL', $5, $6)
                ON CONFLICT (serial_number) DO UPDATE SET model = EXCLUDED.model
                RETURNING sensor_id
                """,
                uuid.uuid4(), f"SN-{serial:04d}", SENSOR_MODELS[(serial - 1) % len(SENSOR_MODELS)],
                calib, unit_id, org_id,
            )
            indiv_id = row["sensor_id"]
            for ttype, zones in INDIV_THRESHOLDS.items():
                for zone, val in zones.items():
                    await conn.execute(
                        """
                        INSERT INTO thresholds
                            (threshold_id, sensor_id, limit_value, threshold_type, tariff_zone, organization_id)
                        VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING
                        """,
                        uuid.uuid4(), indiv_id, val, ttype, zone, org_id,
                    )
            sensor_meta.append(dict(
                sensor_id=indiv_id,
                sensor_type="INDIVIDUAL",
                building_id=building_id,
                baseline=15.0,
                is_residential=True,
                upper=INDIV_THRESHOLDS["UPPER"]["DAY"],
            ))
            serial += 1

        print(f"  {b['address'][:45]}  ({len(b['units'])} units, {1 + len(b['units'])} sensors)")

    # ── metrics ───────────────────────────────────────────────────────────────
    print(f"\nGenerating {days} days of metrics (30-min intervals) …")
    start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
    slots = [start + timedelta(minutes=i * 30) for i in range(days * 48)]

    total_metrics = 0
    sensor_readings: dict[str, list[float]] = {}
    for s in sensor_meta:
        readings: list[float] = []
        rows = []
        for dt in slots:
            val, volt, curr = _gen_reading(dt, s["baseline"], s["is_residential"], s["upper"])
            readings.append(val)
            rows.append((uuid.uuid4(), s["sensor_id"], val, volt, curr, "kWh", dt))
        await conn.executemany(
            """
            INSERT INTO metrics
                (metric_id, sensor_id, value, voltage, current, measurement_unit, recorded_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT DO NOTHING
            """,
            rows,
        )
        sensor_readings[str(s["sensor_id"])] = readings
        total_metrics += len(rows)

    print(f"  {total_metrics} rows across {len(sensor_meta)} sensors")

    # ── analytics: average_loads, energy_balances, peak_loads, incidents ──────
    print("\nGenerating analytics tables …")
    rpd = 48  # readings per day (30-min slots)

    # average_loads
    avg_rows = []
    for s in sensor_meta:
        vals = sensor_readings[str(s["sensor_id"])]
        for day_i in range(days):
            day_vals = vals[day_i * rpd : (day_i + 1) * rpd]
            if day_vals:
                avg_rows.append((
                    uuid.uuid4(), s["sensor_id"], "DAY",
                    round(sum(day_vals) / len(day_vals), 4),
                    start + timedelta(days=day_i + 1),
                ))
    await conn.executemany(
        """
        INSERT INTO average_loads (avg_load_id, sensor_id, window_size, mean_value, calculated_at)
        VALUES ($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING
        """,
        avg_rows,
    )
    print(f"  {len(avg_rows)} average_load rows")

    # group sensors by building for energy_balance
    bld_sensors: dict[str, dict[str, list]] = {}
    for s in sensor_meta:
        bid = str(s["building_id"])
        bld_sensors.setdefault(bid, {"COMMON": [], "INDIVIDUAL": []})
        bld_sensors[bid][s["sensor_type"]].append(str(s["sensor_id"]))

    eb_rows = []
    for bid_str, grp in bld_sensors.items():
        bid_uuid = uuid.UUID(bid_str)
        for day_i in range(days):
            sl = slice(day_i * rpd, (day_i + 1) * rpd)
            day_start = start + timedelta(days=day_i)
            day_end   = day_start + timedelta(days=1)
            common_kwh = sum(sum(sensor_readings[sid][sl]) for sid in grp["COMMON"])
            indiv_kwh  = sum(sum(sensor_readings[sid][sl]) for sid in grp["INDIVIDUAL"])
            if common_kwh <= 0:
                continue
            if indiv_kwh > 0:
                loss_kwh = round(max(0.0, common_kwh - indiv_kwh), 2)
            else:
                loss_kwh = round(common_kwh * random.uniform(0.05, 0.18), 2)
            loss_pct = round(loss_kwh / common_kwh * 100, 2)
            eb_rows.append((uuid.uuid4(), bid_uuid, day_start, day_end, loss_kwh, loss_pct))
    await conn.executemany(
        """
        INSERT INTO energy_balances
            (balance_id, building_id, period_start, period_end, loss_kwh, loss_percent)
        VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING
        """,
        eb_rows,
    )
    print(f"  {len(eb_rows)} energy_balance rows")

    # peak_loads + incidents  (readings > upper threshold)
    peak_rows = []
    for s in sensor_meta:
        vals = sensor_readings[str(s["sensor_id"])]
        for i, val in enumerate(vals):
            if val > s["upper"]:
                peak_rows.append((
                    uuid.uuid4(), s["sensor_id"], val,
                    round(random.uniform(120, 900), 1),
                    slots[i],
                ))
    # keep at most ~5 peaks per week to avoid flooding the table
    budget = max(5, days // 7 * 5 * len(sensor_meta))
    if len(peak_rows) > budget:
        peak_rows = random.sample(peak_rows, budget)
    peak_rows.sort(key=lambda r: r[4])

    await conn.executemany(
        """
        INSERT INTO peak_loads (peak_id, sensor_id, max_value, duration_seconds, detected_at)
        VALUES ($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING
        """,
        peak_rows,
    )
    print(f"  {len(peak_rows)} peak_load rows")

    cutoff = now - timedelta(days=2)
    sensor_upper = {str(s["sensor_id"]): s["upper"] for s in sensor_meta}
    inc_rows = [
        (
            uuid.uuid4(),
            "OVERLOAD" if random.random() > 0.25 else "LEAK",
            "HIGH" if pk[2] > sensor_upper.get(str(pk[1]), 100) * 1.5 else "LOW",
            "RESOLVED" if pk[4] < cutoff else "OPEN",
            None,
            pk[0],
        )
        for pk in peak_rows
    ]
    await conn.executemany(
        """
        INSERT INTO incidents
            (incident_id, incident_type, severity, status, threshold_id, peak_load_id)
        VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING
        """,
        inc_rows,
    )
    print(f"  {len(inc_rows)} incident rows")

    print("\nDone.")
    print("\nCredentials summary:")
    print(f"  {'email':40s} {'password':15s} {'role'}")
    print(f"  {'-'*72}")
    for u in USERS:
        org_info = ", ".join(f"{org}({r})" for org, r in ORG_ROLES.get(u["email"], []))
        print(f"  {u['email']:40s} {u['password']:15s} {u['role']}  {org_info}")


async def clean(conn: asyncpg.Connection) -> None:
    print("Cleaning all tables …")
    tables = [
        "incidents", "peak_loads", "energy_balances", "average_loads",
        "metrics", "thresholds", "sensors", "units", "buildings",
        "user_organization_roles", "organizations", # "users",
    ]
    for t in tables:
        await conn.execute(f"DELETE FROM {t}")
        print(f"  cleared {t}")
    print()


async def run(db_url: str, days: int, do_clean: bool) -> None:
    conn = await asyncpg.connect(db_url, server_settings={"timezone": "UTC"})
    try:
        if do_clean:
            await clean(conn)
        await seed(conn, days)
    finally:
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GreenOps DB seeder")
    parser.add_argument(
        "--database-url",
        default="postgresql://user:password@127.0.0.1:5432/greenops_db",
    )
    parser.add_argument("--days", type=int, default=7, help="Days of metric history")
    parser.add_argument("--clean", action="store_true", help="Wipe all tables before seeding")
    args = parser.parse_args()
    asyncio.run(run(args.database_url, args.days, args.clean))
