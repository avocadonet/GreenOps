# crud — Control Plane Service

FastAPI service that manages infrastructure entities and configuration. The only service that runs Alembic migrations.

## Responsibilities

- Full CRUD for: `Building`, `Unit`, `Sensor`, `Threshold`
- Enforces sensor attachment constraint (COMMON sensors attach to buildings, INDIVIDUAL sensors attach to units)
- Runs Alembic migrations on startup (via `migrations.dockerfile`)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/buildings` | Create building |
| `GET` | `/buildings/{id}` | Read building |
| `PUT` | `/buildings/{id}` | Update building |
| `DELETE` | `/buildings/{id}` | Delete building |
| `POST` | `/units` | Create unit |
| `GET` | `/units/{id}` | Read unit |
| `PUT` | `/units/{id}` | Update unit |
| `DELETE` | `/units/{id}` | Delete unit |
| `POST` | `/sensors` | Create sensor (validates XOR attachment) |
| `GET` | `/sensors/{id}` | Read sensor |
| `DELETE` | `/sensors/{id}` | Delete sensor |
| `POST` | `/thresholds` | Create threshold |
| `GET` | `/thresholds/{id}` | Read threshold |
| `DELETE` | `/thresholds/{id}` | Delete threshold |

Interactive docs available at `http://localhost:8000/docs`.

## Stack

| Layer | Technology |
|-------|-----------|
| Web | FastAPI + uvicorn |
| DI | Dishka (`DishkaRoute`, `FromDishka`) |
| ORM | SQLAlchemy 2.0 (`Mapped`, `mapped_column`) |
| DB driver | asyncpg |
| CRUD helpers | crudx (`@decorators.create/read/update/delete`) |
| DTO mapping | Adaptix `ConversionRetort` |
| Migrations | Alembic (shared package) |

## Architecture

```
src/
├── domain/          # ABCs + exceptions per resource (no framework imports)
├── application/     # Service classes: business logic, transaction boundary
└── infrastructure/
    ├── api/         # Pydantic schemas, mappers, FastAPI routers
    ├── db/          # crudx repositories + Adaptix mappers per resource
    ├── configs/     # Config dataclass reading os.environ
    └── providers/   # Dishka providers (Config, Database, Repositories, Services)
```

Import rule: `infrastructure` → `application` → `domain` (one direction only).

## Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async URL, e.g. `postgresql+asyncpg://user:pass@host:5432/db` |

## Running locally

```bash
cd services/crud
poetry install
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/greenops_db \
  poetry run uvicorn infrastructure.api.app:create_app --factory --reload --app-dir src
```

## Running tests

```bash
cd services/crud
poetry run python -m pytest src/tests/
```

## Running migrations

```bash
cd services/shared
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/greenops_db \
  alembic upgrade head
```
