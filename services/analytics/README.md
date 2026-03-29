# analytics — CRON Service

APScheduler service that runs two periodic aggregation jobs. No REST API, no Kafka consumers.

## Responsibilities

| Job | Schedule | Logic |
|-----|----------|-------|
| `average_load_hourly` | Every hour at :05 | For each sensor: compute mean of all metrics in the last 60 minutes, persist `AverageLoad` |
| `energy_balance_daily` | Every day at 00:10 | For each building: common meter sum − Σ(individual unit meters) for yesterday, persist `EnergyBalance` |

Schedules fire a few minutes past the boundary to avoid thundering-herd contention and give the workers service time to flush the last Kafka messages before reads.

## Energy balance formula

```
loss_kwh    = common_meter_kwh - sum(individual_unit_meters_kwh)
loss_percent = loss_kwh / common_meter_kwh * 100
```

A building is skipped if it has no COMMON sensor. A negative `loss_kwh` is valid and indicates sensor miscalibration.

## Stack

| Layer | Technology |
|-------|-----------|
| Scheduler | APScheduler 3.x `AsyncIOScheduler` + `CronTrigger` |
| DI | Dishka (fresh request-scoped container per job run) |
| ORM | SQLAlchemy 2.0 |
| DB driver | asyncpg |
| DTO mapping | Adaptix |

## Architecture

```
src/
├── domain/
│   ├── energy_balance_calculator.py   # Pure: (common_kwh, individual_sum) → result
│   └── average_load_calculator.py     # Pure: list[float] → mean or None
├── application/
│   ├── energy_balance/service.py      # run_daily(): iterates buildings, calls calculator
│   └── average_load/service.py        # run_hourly(): iterates sensors, calls calculator
└── infrastructure/
    ├── db/                            # Read-only repositories (raw SQLAlchemy select)
    │   ├── building/                  # list_all()
    │   ├── sensor/                    # list_all(), list_by_building()
    │   ├── metric/                    # list_by_sensor_in_range()
    │   ├── energy_balance/            # create() via Adaptix mapper
    │   └── average_load/              # create() via Adaptix mapper
    ├── scheduler/jobs.py              # register_jobs(): wires APScheduler + Dishka
    ├── configs/                       # Config dataclass
    └── providers/                     # Dishka providers
```

Each scheduled job opens `async with container() as request_container` to get a fresh SQLAlchemy session, ensuring no cross-run session state. Per-entity errors are caught and logged without aborting the rest of the run.

## Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async URL |

## Running locally

```bash
cd services/analytics
poetry install
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/greenops_db \
  PYTHONPATH=src poetry run python main.py
```

## Running tests

```bash
cd services/analytics
poetry run python -m pytest src/tests/
```
