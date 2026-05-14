# greenops-shared

Shared kernel package used by all three GreenOps microservices. Contains the single source of truth for domain enums, entities, DTOs, SQLAlchemy models, and Alembic migrations.

## Contents

```
src/shared/
├── enums.py            # StrEnum classes for all domain types
├── exceptions.py       # Base GreenOpsException hierarchy
├── entities/           # @dataclass domain objects (pure Python, no ORM)
├── dtos/               # @dataclass transfer objects (create / update / events)
├── db/                 # SQLAlchemy 2.0 Mapped models + DeclarativeBase
└── migrations/         # Alembic env.py + initial migration (all 9 tables)
```

## Domain model

| Entity | Table | Key relations |
|--------|-------|---------------|
| `Building` | `buildings` | — |
| `Unit` | `units` | → Building |
| `Sensor` | `sensors` | → Building (COMMON) or → Unit (INDIVIDUAL) |
| `Metric` | `metrics` | → Sensor |
| `Threshold` | `thresholds` | → Sensor |
| `EnergyBalance` | `energy_balances` | → Building |
| `AverageLoad` | `average_loads` | → Sensor |
| `PeakLoad` | `peak_loads` | → Sensor |
| `Incident` | `incidents` | → Threshold (nullable), → PeakLoad (nullable) |

## Installation

Each service declares this package as a path dependency in its `pyproject.toml`:

```toml
greenops-shared = { path = "../shared", develop = true }
```

## Running migrations

Migrations are run from the **CRUD service container**, not from here. To run them manually:

```bash
cd services/shared
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/greenops_db \
  alembic upgrade head
```

`alembic.ini` lives at the package root; `script_location` points to `src/shared/migrations`.

## Design rules

- **Never** name a field `id`, `type`, `list`, `dict` — use domain-prefixed names (`building_id`, `sensor_type`).
- All inter-service communication uses `@dataclass` DTOs parsed by Adaptix, never raw dicts.
- The `measurement_unit` field on `Metric` is intentionally renamed from the spec's `unit` to avoid collision with the `Unit` entity.
- Sensor attachment (COMMON → `building_id`, INDIVIDUAL → `unit_id`) is an XOR constraint enforced in the CRUD service layer, not at DB level (MVP trade-off).
